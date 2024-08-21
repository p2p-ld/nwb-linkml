"""
Provider for pydantic models.
"""

import importlib
import multiprocessing as mp
import re
import sys
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, List, Optional, Type

from linkml.generators.pydanticgen.pydanticgen import SplitMode, _ensure_inits, _import_to_path
from pydantic import BaseModel

from nwb_linkml.generators.pydantic import NWBPydanticGenerator
from nwb_linkml.maps.naming import module_case, version_module_case
from nwb_linkml.providers import LinkMLProvider, Provider

if TYPE_CHECKING:
    from linkml_runtime.linkml_model.meta import SchemaDefinition


class PydanticProvider(Provider):
    """
    Provider for pydantic models built from linkml-style nwb schema
    (ie. as provided by :class:`.LinkMLProvider`)

    Generates pydantic models into a :attr:`~.PydanticProvider.path` that can be imported
    as if they were within the `nwb_linkml` namespace using an :class:`.EctopicModelFinder` .

    .. todo::

        Documentation of directory structure and caching will be completed once it is finalized :)

    """

    PROVIDES = "pydantic"
    SPLIT_PATTERN = (
        "...{% if schema.annotations.namespace %}"
        "{{ schema.annotations.namespace.value | replace('.', '_') }}"
        "{% else %}unknown{% endif %}"
        "."
        "v{{ schema.version | replace('.', '_') }}"
        "."
        "{% if schema.annotations.is_namespace and schema.annotations.is_namespace.value %}"
        "namespace"
        "{% else %}"
        "{{ schema.name | replace('.', '_') }}"
        "{% endif %}"
    )
    """See :attr:`~linkml.generators.PydanticGenerator.split_pattern"""

    def __init__(self, path: Optional[Path] = None, verbose: bool = True):
        super().__init__(path, verbose)

    @property
    def path(self) -> Path:
        """``pydantic_dir`` provided by :class:`.Config`"""
        return self.config.pydantic_dir

    def build(
        self,
        namespace: str | Path,
        version: Optional[str] = None,
        split: bool = True,
        dump: bool = True,
        force: bool = False,
        parallel: bool = False,
        **kwargs: dict,
    ) -> str | List[str]:
        """

        Notes:
            We currently infer namespace and version from the path when ``namespace`` is a Path,
            which is a patently Bad Thing To Do. This is a temporary measure until we decide on
            a permanent means by which we want to cache built artifacts <3. Hierarchies of folders
            is not the target design.


        Args:
            namespace (Union[str, :class:`pathlib.Path`]): If a string, use a
                :class:`.LinkMLProvider` to get the converted schema. If a path,
                assume we have been given an explicit ``namespace.yaml`` from a converted
                NWB -> LinkML schema to load from.
            split (bool): If ``False`` (default), generate a single ``namespace.py`` file,
                otherwise generate a python file for each schema in the namespace
                in addition to a ``namespace.py`` that imports from them
            dump (bool): If ``True`` (default), dump the model to the cache,
                otherwise just return the serialized string of built pydantic model
            force (bool): If ``False`` (default), don't build the model if it already exists,
                if ``True`` , delete and rebuild any model
            parallel (bool): If ``True``, build imported models using multiprocessing,
                if ``False`` (default), don't.
            **kwargs: Passed to :class:`.NWBPydanticGenerator`

        Returns:
            str: The built model file as returned from :meth:`.NWBPydanticGenerator.serialize`
        """

        if isinstance(namespace, str) and not (
            namespace.endswith(".yaml") or namespace.endswith(".yml")
        ):
            # we're given a name of a namespace to build
            provider = LinkMLProvider(path=self.config.cache_dir)
            # ensure we have the schema in question
            _ = provider.get(namespace, version=version)
            path = provider.namespace_path(namespace, version) / "namespace.yaml"

        else:
            # given a path to a namespace linkml yaml file
            path = Path(namespace)

        if split:
            result = self._build_split(path, dump, force, **kwargs)
        else:
            result = self._build_unsplit(path, dump, force, **kwargs)

        self.install_pathfinder()
        return result

    def _build_unsplit(self, path: Path, dump: bool, force: bool, **kwargs) -> str:
        generator = NWBPydanticGenerator(
            str(path), split=False, split_pattern=self.SPLIT_PATTERN, **kwargs
        )
        out_module = generator.generate_module_import(generator.schemaview.schema)
        out_file = (self.path / _import_to_path(out_module)).resolve()
        if out_file.exists() and not force:
            with open(out_file) as ofile:
                serialized = ofile.read()
            return serialized

        serialized = generator.serialize()
        if dump:
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w") as ofile:
                ofile.write(serialized)

            self._make_inits(out_file)

        return serialized

    def _build_split(
        self, path: Path, dump: bool, force: bool, parallel: bool = False, **kwargs
    ) -> List[str]:
        # FIXME: This is messy as all fuck, we're just getting it to work again
        # so we can start iterating on the models themselves
        res = []
        module_paths = []

        # first make the namespace file we were given

        # remove any directory traversal at the head of the pattern for this,
        # we're making relative to the provider's path not the generated schema at first
        root_pattern = re.sub(r"^\.*", "", self.SPLIT_PATTERN)
        gen = NWBPydanticGenerator(
            schema=path, split=True, split_pattern=root_pattern, split_mode=SplitMode.FULL
        )
        mod_name = gen.generate_module_import(gen.schemaview.schema)
        ns_file = (self.path / _import_to_path(mod_name)).resolve()

        # now replace the real import path so the generated module has it
        gen.split_pattern = self.SPLIT_PATTERN
        # always render since we need to at least render to know what we're importing
        rendered = gen.render()

        if not ns_file.exists() or force:
            ns_file.parent.mkdir(exist_ok=True, parents=True)
            serialized = gen.serialize(rendered_module=rendered)
            if dump:
                with open(ns_file, "w") as ofile:
                    ofile.write(serialized)
                module_paths.append(ns_file)
        else:
            with open(ns_file) as ofile:
                serialized = ofile.read()
        res.append(serialized)

        # then each of the other schemas :)
        imported_schema: dict[str, SchemaDefinition] = {
            gen.generate_module_import(sch): sch for sch in gen.schemaview.schema_map.values()
        }
        generated_imports = [i for i in rendered.python_imports if i.is_schema]
        # each task has an expected output file a corresponding SchemaDefinition
        import_paths = [
            (ns_file.parent / _import_to_path(an_import.module)).resolve()
            for an_import in generated_imports
        ]
        import_schemas = [
            Path(path).parent / imported_schema[an_import.module].source_file
            for an_import in generated_imports
        ]

        tasks = [
            (
                import_path,
                import_schema,
                force,
                self.SPLIT_PATTERN,
                dump,
            )
            for import_path, import_schema in zip(import_paths, import_schemas)
        ]

        if parallel:
            with mp.Pool(min(mp.cpu_count(), len(tasks))) as pool:
                mp_results = [pool.apply_async(self._generate_single, t) for t in tasks]
                for result in mp_results:
                    res.append(result.get())  # noqa: PERF401 - false positive
        else:
            for task in tasks:
                res.append(self._generate_single(*task))  # noqa: PERF401 - false positive

        # make __init__.py files if we generated any files
        if len(module_paths) > 0:
            _ensure_inits(import_paths)
            # then extra_inits that usually aren't generated bc we're one layer deeper
            self._make_inits(ns_file)

        return res

    @staticmethod
    def _generate_single(
        import_file: Path,
        # schema: "SchemaDefinition",
        schema: Path,
        force: bool,
        split_pattern: str,
        dump: bool,
    ) -> str:
        """
        Interior generator method for _build_split to be called in parallel

        .. TODO::

            split up and consolidate this build behavior, very spaghetti.

        """

        if not import_file.exists() or force:
            import_file.parent.mkdir(exist_ok=True, parents=True)

            import_gen = NWBPydanticGenerator(
                schema,
                split=True,
                split_pattern=split_pattern,
            )
            serialized = import_gen.serialize()
            if dump:
                with open(import_file, "w") as ofile:
                    ofile.write(serialized)

        else:
            with open(import_file) as ofile:
                serialized = ofile.read()
        return serialized

    def _make_inits(self, out_file: Path) -> None:
        """
        Make __init__.py files for the directory a model is output to and its immediate parent.
        (ig this could be generalized in depth but lets not go nuts in here with the nesting)
        """
        initfile = out_file.parent / "__init__.py"
        parent_init = out_file.parent.parent / "__init__.py"
        for ifile in (initfile, parent_init):
            if not ifile.exists():
                with open(ifile, "w") as ifile_open:
                    ifile_open.write(" ")

    @classmethod
    def module_name(self, namespace: str, version: str) -> str:
        """Module name for the built module

        e.g.::

            nwb_models.models.pydantic.{namespace}.{version}
        """
        name_pieces = [
            "nwb_linkml",
            "models",
            "pydantic",
            module_case(namespace),
            version_module_case(version),
        ]
        module_name = ".".join(name_pieces)
        return module_name

    def import_module(self, namespace: str, version: Optional[str] = None) -> ModuleType:
        """
        Import a module within the temporary directory from its namespace and version

        In most cases, you're looking for :meth:`.PydanticProvider.get`, this method is
        made available in case you don't want to accidentally build something
        or invoke the rest of the provisioning system.

        Args:
            namespace (str): Name of namespace
            version (Optional[str]): Version to import, if None,
                try and get the most recently built version.

        Returns:
            :class:`types.ModuleType`
        """
        # get latest version if None
        if version is None:
            version = self.available_versions[namespace][-1]

        path = self.namespace_path(namespace, version) / "namespace.py"
        if not path.exists():
            raise ImportError(f"Module has not been built yet {path}")
        module_name = self.module_name(namespace, version)

        # import module level first - when python does relative imports,
        # it needs to have the parent modules imported separately
        # this breaks split model creation when they are outside of the
        # package repository (ie. loaded from an nwb file) because it tries
        # to look for the containing namespace folder within the nwb_linkml package and fails
        init_spec = importlib.util.spec_from_file_location(module_name, path.parent / "__init__.py")
        init_module = importlib.util.module_from_spec(init_spec)
        sys.modules[module_name] = init_module
        init_spec.loader.exec_module(init_module)

        # then the namespace package
        module_name = module_name + ".namespace"
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def get(
        self, namespace: str, version: Optional[str] = None, allow_repo: Optional[bool] = None
    ) -> ModuleType:
        """
        Get the imported module for a given namespace and version.

        A given namespace will be stored in :data:`sys.modules` as
        ``nwb_models.models.{namespace}``,
        so first check if there is any already-imported module, and return that if so.

        Then we check in the temporary directory for an already-built ``namespace.py`` file

        Otherwise we pass arguments to :meth:`.PydanticProvider.build` and attempt to build them
        before returning.

        Notes:
            The imported modules shadow the "actual"
            ``nwb_models.models`` module as would be imported from the usual location
            within the package directory.
            This is intentional, as models can then be used as if they were
            integrated parts of the package,
            and also so the active version of a namespace can be cleanly accessed
            (ie. without ``from nwb_models.models.core import v2_2_0 as core`` ).
            Accordingly, we assume that people will only be using a single version of NWB in a given
            Python session.


        Args:
            namespace (str): Name of namespace to import. Must have either been previously built
                with :meth:`.PydanticProvider.build` or
                a matching namespace/version combo must be available to the
                :class:`.LinkMLProvider`
            version (Optional[str]): Version to import. If ``None``,
                get the most recently build module
            allow_repo (bool): Allow getting modules provided within
                :mod:`nwb_models.models.pydantic`

        Returns:
            The imported :class:`types.ModuleType` object that has all the built
            classes at the root level.

        """
        if allow_repo is None:
            allow_repo = self.allow_repo

        if version is None:
            version = self.available_versions[namespace][-1]

        module_name = self.module_name(namespace, version)
        namespace_name = module_name + ".namespace"

        if not allow_repo:
            self._clear_package_imports()

        if namespace_name in sys.modules:
            return sys.modules[namespace_name]

        try:
            path = self.namespace_path(namespace, version, allow_repo)
        except FileNotFoundError:
            path = None

        if path is None or not path.exists():
            _ = self.build(namespace, version=version)

        module = self.import_module(namespace, version)
        return module

    @staticmethod
    def _clear_package_imports() -> None:
        """
        When using allow_repo=False, delete any already-imported
        namespaces from sys.modules that are within the nwb_linkml package
        """
        # make sure we don't have any in-repo modules
        repo_base = Path(__file__).parents[1]
        deletes = []
        for k, v in sys.modules.items():
            if not k.startswith("nwb_models.models.pydantic"):
                continue
            try:
                Path(v.__file__).relative_to(repo_base)
                # if it is a subpath, delete it
                deletes.append(k)
            except ValueError:
                # path is not a subpath
                continue
        for d in deletes:
            del sys.modules[d]

    def get_class(
        self, namespace: str, class_: str, version: Optional[str] = None
    ) -> Type[BaseModel]:
        """
        Get a class from a given namespace and version!

        Args:
            namespace (str): Name of a namespace that has been previously built and cached,
                otherwise we will attempt to build it from the
                :data:`.providers.git.DEFAULT_REPOS`
            class_ (str): Name of class to retrieve
            version (Optional[str]): Optional version of the schema to retrieve from

        Returns:
            :class:`pydantic.BaseModel`
        """
        mod = self.get(namespace, version)
        return getattr(mod, class_)

    def install_pathfinder(self) -> None:
        """
        Add a :class:`.EctopicModelFinder` instance that allows us to import from
        the directory that we are generating models into
        """
        # check if one already exists
        matches = [
            finder
            for finder in sys.meta_path
            if isinstance(finder, EctopicModelFinder) and finder.path == self.path
        ]
        if len(matches) > 0:
            return

        pathfinder = EctopicModelFinder(self.path)
        sys.meta_path.append(pathfinder)


class EctopicModelFinder(MetaPathFinder):
    """
    A meta path finder that allows the import machinery to find a model
    package even if it might be outside the actual nwb_linkml namespace,
    as occurs when building split models in a temporary directory.

    References:
        - https://docs.python.org/3/reference/import.html#the-meta-path
        - https://docs.python.org/3/library/importlib.html#importlib.abc.MetaPathFinder

    """

    MODEL_STEM = "nwb_models.models.pydantic"

    def __init__(self, path: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path

    def find_spec(
        self, fullname: str, path: Optional[str], target: Optional[ModuleType] = None
    ) -> Optional[ModuleSpec]:
        """If we are loading a generated pydantic module, return an importlib spec"""
        if not fullname.startswith(self.MODEL_STEM):
            return None
        else:
            # get submodule beneath model stem
            submod = fullname.replace(self.MODEL_STEM, "").lstrip(".")
            base_path = Path(self.path, *submod.split("."))

            # switch if we're asked for a package or a module
            mod_path = Path(str(base_path) + ".py")
            pkg_path = base_path / "__init__.py"
            if mod_path.exists():
                import_path = mod_path
            elif pkg_path.exists():
                import_path = pkg_path
            else:
                return None

            spec = importlib.util.spec_from_file_location(fullname, import_path)
            return spec
