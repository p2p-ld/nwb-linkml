"""
Class for managing, building, and caching built schemas.

The nwb.core and hdmf-common schema are statically built and stored in this repository,
but to make it feasible to use arbitrary schema, eg. those stored inside of
an NWB file, we need a bit of infrastructure for generating and caching
pydantic models on the fly.

Relationship to other modules:
* :mod:`.adapters` manage the conversion from NWB schema language to linkML.
* :mod:`.generators` create models like pydantic models from the linkML schema
* :mod:`.providers` then use ``adapters`` and ``generators`` to provide models from generated schema!

Providers create a set of directories with namespaces and versions,
so eg. for the linkML and pydantic providers:

    cache_dir
      - linkml
        - nwb_core
          - v0_2_0
            - namespace.yaml
            - nwb.core.file.yaml
            - ...
          - v0_2_1
            - namespace.yaml
            - ...
        - my_schema
          - v0_1_0
            - ...
      - pydantic
        - nwb_core
          - v0_2_0
            - namespace.py
            - ...
          - v0_2_1
            - namespace.py
            - ...


"""
import pdb
import shutil
from typing import Dict, TypedDict, List, Optional, Literal, TypeVar, Any, Dict, Type
from types import ModuleType
from pathlib import Path
import os
from abc import abstractmethod, ABC
import warnings
import importlib
import sys

from pydantic import BaseModel

from linkml_runtime.linkml_model import SchemaDefinition, SchemaDefinitionName
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime import SchemaView

from nwb_linkml.config import Config
from nwb_linkml import io
from nwb_linkml import adapters
from nwb_linkml.adapters.adapter import BuildResult
from nwb_linkml.maps.naming import module_case, version_module_case, relative_path
from nwb_schema_language import Namespaces
from nwb_linkml.generators.pydantic import NWBPydanticGenerator
from nwb_linkml.providers.git import DEFAULT_REPOS
from nwb_linkml.ui import AdapterProgress


P = TypeVar('P')

class Provider(ABC):
    """
    Metaclass for different kind of providers!

    Args:
        path (:class:`pathlib.Path`): Override the temporary directory configured by
            the environment-wide :class:`.Config` object as the base directory that the
            subclasses provide to.
        verbose (bool): If ``True``, print things like progress bars to stdout :)

    Attributes:
        config (:class:`.Config`): Configuration for the directories used by this
            provider, unless overridden by ``path``
        cache_dir (:class:`pathlib.Path`): The main cache directory under which the other
            providers will store the things they provide
    """
    PROVIDES: str
    PROVIDES_CLASS: P = None

    def __init__(self,
                 path: Optional[Path] = None,
                 verbose: bool = True):
        if path is not None:
            config = Config(cache_dir=path)
        else:
            config = Config()
        self.config = config
        self.cache_dir = config.cache_dir
        self.verbose = verbose

    @property
    @abstractmethod
    def path(self) -> Path:
        """
        Base path for this kind of provider
        """

    @abstractmethod
    def build(self, *args: Any):
        """
        Whatever needs to be done to build this thing, if applicable
        """

    @abstractmethod
    def get(self, *args: Any) -> Any:
        """
        Get a cached item.

        Optionally, try any build it if it's possible to do so
        """

    def namespace_path(
            self,
            namespace: str,
            version: Optional[str] = None,
            allow_repo: bool = True
    ) -> Path:
        """
        Get the location for a given namespace of this type.

        Note that we don't check for existence, because this method should
        also be used when generating schema --- this is the canonical location

        Arguments:
            namespace (str): Namespace to get!
            version (str): Optional, version of namespace. If ``None``,
                either get the most recent version built, or if
                ``namespace`` is ``core`` or ``hdmf-common``, use the
                modules provided with the package. We do not use the most
                recent *version*, but the most recently *generated* version
                because it's assumed that's the one you want if you're just
                gesturally reaching for one.
            allow_repo (bool): Allow the pathfinder to return the installed repository/package,
                useful to enforce building into temporary directories, decoupling finding a path
                during loading vs. building. Building into the repo is still possible if both
                namespace and version are provided (ie. the path is fully qualified) and
                :attr:`.config`'s path is the repository path.
        """
        namespace_module = module_case(namespace)
        namespace_path = self.path / namespace_module
        if not namespace_path.exists() and namespace in ('core', 'hdmf-common') and allow_repo:
            # return builtins
            module_path = Path(importlib.util.find_spec('nwb_linkml').origin).parent

            if self.PROVIDES == 'linkml':
                namespace_path = module_path / 'schema' / 'linkml' / namespace
            elif self.PROVIDES == 'pydantic':
                namespace_path = module_path / 'models' / 'pydantic' / namespace

        if version is not None:
            version_path = namespace_path / version_module_case(version)
            #version_path.mkdir(exist_ok=True, parents=True)
        else:
            # or find the most recently built one
            versions = sorted(namespace_path.iterdir(), key=os.path.getmtime)
            versions = [v for v in versions if v.is_dir() and v.name not in ('__pycache__')]
            if len(versions) == 0:
                raise FileNotFoundError('No version provided, and no existing schema found')
            version_path = versions[-1]


        return version_path

    @property
    def versions(self) -> Dict[str,List[str]]:
        """
        Dictionary mapping a namespace to a list of built versions
        """
        versions = {} # type: Dict[str, List[Path]]

        # first get any builtins provided by the package itself
        # these get overwritten by
        module_path = Path(importlib.util.find_spec('nwb_linkml').origin).parent
        builtin_namespaces = []
        if self.PROVIDES == 'linkml':
            namespace_path = module_path / 'schema' / 'linkml'
            builtin_namespaces = list(namespace_path.iterdir())
        elif self.PROVIDES == 'pydantic':
            namespace_path = module_path / 'models' / 'pydantic'
            builtin_namespaces = list(namespace_path.iterdir())

        for ns_dir in builtin_namespaces + list(self.path.iterdir()):
            if not ns_dir.is_dir():
                continue
            if ns_dir.name not in versions.keys():
                versions[ns_dir.name] = []

            versions[ns_dir.name].extend([v for v in ns_dir.iterdir() if v.is_dir()])

        # flatten out in case we got duplicates between the builtins and cache
        res = {
            k: [v.name for v in sorted(set(v_paths), key=os.path.getmtime)]
            for k, v_paths in versions.items()
        }
        return res




class LinkMLSchemaBuild(TypedDict):
    """Build result from :meth:`.LinkMLProvider.build`"""
    version: str
    namespace: Path
    name: str
    result: Optional[BuildResult]


class LinkMLProvider(Provider):
    """
    Provider for conversions from nwb schema language to linkML.

    By default, generate and manage a nest of temporary cache directories
    (as configured by :class:`.Config`) for each version of a given namespace.

    Like other :class:`.Provider` classes, this model is not a singleton but
    behaves a bit like one in that when instantiated without arguments
    it is stateless (except for configuration by environment-level variables).
    So we don't use ``@classmethod`` s here, but instantiating the class should remain
    cheap.

    Namespaces can be built from:

    * namespace .yaml files: :meth:`.build_from_yaml`
    * dictionaries, as are usually packaged in nwb files: :meth:`.build_from_dicts`

    All of which feed into...

    * :class:`~.adapters.NamespacesAdapter` used throughout the rest of ``nwb_linkml`` - :meth:`.build`

    After a namespace is built, it can be accessed using :meth:`.LinkMLProvider.get`, which
    can also be consumed by other providers, so a given namespace and version should only need
    to be built once.

    Note:
        At the moment there is no checking (eg. by comparing hashes) of different sources that
        purport to be a given version of a namespace. When ambiguous, the class prefers to
        build sets of namespaces together and use the most recently built ones since there is no
        formal system for linking versions of namespaced schemas in nwb schema language.

    Examples:

        >>> provider = LinkMLProvider()
        >>> # Simplest case, get the core nwb schema from the default NWB core repo
        >>> core = provider.get('core')
        >>> # Get a specific version of the core schema
        >>> core_other_version = provider.get('core', '2.2.0')
        >>> # Build a custom schema and then get it
        >>> # provider.build_from_yaml('myschema.yaml')
        >>> # my_schema = provider.get('myschema')
    """
    PROVIDES = 'linkml'
    PROVIDES_CLASS = SchemaDefinition

    @property
    def path(self) -> Path:
        return self.config.linkml_dir

    def build_from_yaml(self, path: Path, **kwargs):
        """
        Build a namespace's schema

        Arguments:
            path (:class:`pathlib.Path`): Path to the namespace .yaml
            kwargs: passed to :meth:`.build`
        """
        ns_adapter = adapters.NamespacesAdapter.from_yaml(path)
        return self.build(ns_adapter, **kwargs)

    def build_from_dicts(
        self,
        schemas:Dict[str, dict],
        **kwargs
    ) -> Dict[str | SchemaDefinitionName, LinkMLSchemaBuild]:
        """
        Build from schema dictionaries, eg. as come from nwb files

        Arguments:
            schemas (dict): A dictionary of ``{'schema_name': {:schema_definition}}``.
                The "namespace" schema should have the key ``namespace``, which is used
                to infer version and schema name. Post-load maps should have already
                been applied
        """
        ns_adapters = {}
        for ns_name, ns_schemas in schemas.items():
            ns = Namespaces(**ns_schemas['namespace'])
            typed_schemas = [
                io.schema.load_schema_file(
                    path=Path(key + ".yaml"),
                    yaml=val)
                for key, val in ns_schemas.items()
                if key != 'namespace'
            ]
            ns_adapter = adapters.NamespacesAdapter(
                namespaces=ns,
                schemas=typed_schemas
            )
            ns_adapters[ns_name] = ns_adapter

        # get the correct imports
        for ns_name, adapter in ns_adapters.items():
            for schema_needs in adapter.needed_imports.values():
                for needed in schema_needs:
                    adapter.imported.append(ns_adapters[needed])

        # then do the build
        res = {}
        for ns_name, adapter in ns_adapters.items():
            res.update(self.build(adapter, **kwargs))

        return res



    def build(
        self,
        ns_adapter: adapters.NamespacesAdapter,
        versions: Optional[dict] = None,
        dump: bool = True,
        force: bool = False
    ) -> Dict[str | SchemaDefinitionName, LinkMLSchemaBuild]:
        """
        Arguments:
            namespaces (:class:`.NamespacesAdapter`): Adapter (populated with any necessary imported namespaces)
                to build
            versions (dict): Dict of specific versions to use
                for cross-namespace imports. as ``{'namespace': 'version'}``
                 If none is provided, use the most recent version
                available.
            dump (bool): If ``True`` (default), dump generated schema to YAML. otherwise just return
            force (bool): If ``False`` (default), don't build schema that already exist. If ``True`` , clear directory and rebuild

        Returns:
            Dict[str, LinkMLSchemaBuild]. For normal builds, :attr:`.LinkMLSchemaBuild.result` will be populated with results
            of the build. If ``force == False`` and the schema already exist, it will be ``None``
        """

        if not force:
            if all([(self.namespace_path(ns, version) / 'namespace.yaml').exists() for ns, version in ns_adapter.versions.items()]):
                return {
                    k: LinkMLSchemaBuild(
                        name=k,
                        result=None,
                        namespace=self.namespace_path(k, v) / 'namespace.yaml',
                        version=v
                    ) for k,v in ns_adapter.versions.items()
                }

        #self._find_imports(ns_adapter, versions, populate=True)
        if self.verbose:
            progress = AdapterProgress(ns_adapter)
            #progress.start()
            with progress:
                built = ns_adapter.build(progress=progress)
        else:
            progress = None
            built = ns_adapter.build()

        # write schemas to yaml files
        build_result = {}

        namespace_sch = [sch for sch in built.schemas if 'namespace' in sch.annotations.keys()]
        for ns_linkml in namespace_sch:
            version = ns_adapter.versions[ns_linkml.name]
            version_path = self.namespace_path(ns_linkml.name, version, allow_repo=False)
            if version_path.exists() and force:
                shutil.rmtree(str(version_path))
            version_path.mkdir(exist_ok=True, parents=True)
            ns_file = version_path / 'namespace.yaml'
            # schema built as part of this namespace that aren't the namespace file
            other_schema = [sch for sch in built.schemas if
                            sch.name.split('.')[0] == ns_linkml.name and sch not in namespace_sch]

            if force or (not force and not ns_file.exists()):
                ns_linkml = self._fix_schema_imports(ns_linkml, ns_adapter, ns_file)
                yaml_dumper.dump(ns_linkml, ns_file)

                # write the schemas for this namespace
                for sch in other_schema:
                    output_file = version_path / (sch.name + '.yaml')
                    # fix the paths for intra-schema imports
                    sch = self._fix_schema_imports(sch, ns_adapter, output_file)
                    yaml_dumper.dump(sch, output_file)

            # make return result for just this namespace
            build_result[ns_linkml.name] = LinkMLSchemaBuild(
                namespace=ns_file,
                name=ns_linkml.name,
                result= BuildResult(schemas=[ns_linkml, *other_schema]),
                version=version
            )

        return build_result

    def _fix_schema_imports(self, sch: SchemaDefinition,
                            ns_adapter: adapters.NamespacesAdapter,
                            output_file: Path) -> SchemaDefinition:
        for animport in sch.imports:
            if animport.split('.')[0] in ns_adapter.versions.keys():
                imported_path = self.namespace_path(animport.split('.')[0], ns_adapter.versions[animport.split('.')[0]]) / 'namespace'
                rel_path = relative_path(imported_path, output_file)
                if str(rel_path) == '.' or str(rel_path) == 'namespace':
                    # same directory, just keep the existing import
                    continue
                idx = sch.imports.index(animport)
                del sch.imports[idx]
                sch.imports.insert(idx, str(rel_path))
        return sch
    def get(self, namespace: str, version: Optional[str] = None) -> SchemaView:
        """
        Get a schema view over the namespace.

        If a matching path for the namespace and version exists in the :attr:`.path`,
        then return the SchemaView over that namespace.

        Otherwise, try and find a source using our :data:`.providers.git.DEFAULT_REPOS`.

        If none is found, then you need to build and cache the (probably custom) schema first with
        :meth:`.build`
        """
        path = self.namespace_path(namespace, version) / 'namespace.yaml'
        if not path.exists():
            path = self._find_source(namespace, version)
        sv = SchemaView(path)
        sv.path = path
        return sv

    def _find_source(self, namespace:str, version: Optional[str] = None) -> Path:
        """Try and find the namespace if it exists in our default repository and build it!"""
        ns_repo = DEFAULT_REPOS.get(namespace, None)
        if ns_repo is None:
            raise KeyError(f"Namespace {namespace} could not be found, and no git repository source has been configured!")
        ns_file = ns_repo.provide_from_git(commit=version)
        res = self.build_from_yaml(ns_file)
        return res[namespace]['namespace']


class PydanticProvider(Provider):
    """
    Provider for pydantic models built from linkml-style nwb schema (ie. as provided by :class:`.LinkMLProvider`)


    """
    PROVIDES = 'pydantic'

    @property
    def path(self) -> Path:
        return self.config.pydantic_dir

    def build(
            self,
            namespace: str | Path,
            out_file: Optional[Path] = None,
            version: Optional[str] = None,
            versions: Optional[dict] = None,
            split: bool = False,
            dump: bool = True,
            force: bool = False,
            **kwargs
    ) -> str:
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
            out_file (Optional[Path]): Optionally override the output file. If ``None``, generate from namespace and version
            version (Optional[str]): The version of the schema to build, if present.
                Works similarly to ``version`` in :class:`.LinkMLProvider`. Ignored if ``namespace`` is a Path.
            versions (Optional[dict]): An explicit mapping of namespaces and versions to use when
                building the combined pydantic `namespace.py` file. Since NWB doesn't have an explicit
                version dependency system between schema, there is intrinsic ambiguity between which version
                of which schema should be used when imported from another. This mapping allows those ambiguities to be resolved.
                See :class:`.NWBPydanticGenerator` 's ``versions`` argument for more information.
            split (bool): If ``False`` (default), generate a single ``namespace.py`` file, otherwise generate a python file for each schema in the namespace
                in addition to a ``namespace.py`` that imports from them
            dump (bool): If ``True`` (default), dump the model to the cache, otherwise just return the serialized string of built pydantic model
            force (bool): If ``False`` (default), don't build the model if it already exists, if ``True`` , delete and rebuild any model
            **kwargs: Passed to :class:`.NWBPydanticGenerator`

        Returns:
            str: The built model file as returned from :meth:`.NWBPydanticGenerator.serialize`
        """

        if isinstance(namespace, str) and not (namespace.endswith('.yaml') or namespace.endswith('.yml')):
            # we're given a name of a namespace to build
            name = namespace
            path = LinkMLProvider(path=self.config.cache_dir).namespace_path(namespace, version) / 'namespace.yaml'
            if version is None:
                # Get the most recently built version
                version = LinkMLProvider(path=self.config.cache_dir).versions[name][-1]
            fn = path.parts[-1]
        else:
            # given a path to a namespace linkml yaml file
            path = Path(namespace)
            # FIXME: this is extremely fragile, but get the details from the path. this is faster than reading yaml for now
            name = path.parts[-3]
            version = path.parts[-2]
            fn = path.parts[-1]

        version = version_module_case(version)
        # this is extremely fragile, we should not be inferring version number from paths...
        if out_file is None:
            fn = fn.removesuffix('.yaml')
            fn = module_case(fn) + '.py'
            out_file = self.path / name / version / fn

        if out_file.exists() and not force:
            with open(out_file, 'r') as ofile:
                serialized = ofile.read()
            return serialized


        default_kwargs = {
            'split': split,
            'emit_metadata': True,
            'gen_slots': True,
            'pydantic_version': '2'
        }
        default_kwargs.update(kwargs)

        generator = NWBPydanticGenerator(
            str(path),
            versions=versions,
            **default_kwargs
        )
        serialized = generator.serialize()
        if dump:
            out_file.parent.mkdir(parents=True,exist_ok=True)
            with open(out_file, 'w') as ofile:
                ofile.write(serialized)
            with open(out_file.parent / '__init__.py', 'w') as initfile:
                initfile.write(' ')
            # make parent file, being a bit more careful because it could be for another module
            parent_init = out_file.parent.parent / '__init__.py'
            if not parent_init.exists():
                with open(parent_init, 'w') as initfile:
                    initfile.write(' ')

        return serialized

    @classmethod
    def module_name(self, namespace:str, version: Optional[str]=None) -> str:
        name_pieces = ['nwb_linkml', 'models', 'pydantic',  namespace]
        if version is not None:
            name_pieces.append(version_module_case(version))
        module_name = '.'.join(name_pieces)
        return module_name
    def import_module(
        self,
        namespace: str,
        version: Optional[str] = None
    ) -> ModuleType:
        """
        Import a module within the temporary directory from its namespace and version

        In most cases, you're looking for :meth:`.PydanticProvider.get`, this method is
        made available in case you don't want to accidentally build something
        or invoke the rest of the provisioning system.

        Args:
            namespace (str): Name of namespace
            version (Optional[str]): Version to import, if None, try and get the most recently built version.

        Returns:
            :class:`types.ModuleType`
        """
        # get latest version if None
        if version is None:
            version = self.versions[namespace][-1]

        path = self.namespace_path(namespace, version) / 'namespace.py'
        if not path.exists():
            raise ImportError(f'Module has not been built yet {path}')
        module_name = self.module_name(namespace, version)
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def get(self, namespace: str, version: Optional[str] = None) -> ModuleType:
        """
        Get the imported module for a given namespace and version.

        A given namespace will be stored in :data:`sys.modules` as ``nwb_linkml.models.{namespace}``,
        so first check if there is any already-imported module, and return that if so.

        Then we check in the temporary directory for an already-built ``namespace.py`` file

        Otherwise we pass arguments to :meth:`.PydanticProvider.build` and attempt to build them
        before returning.

        Notes:
            The imported modules shadow the "actual"
            ``nwb_linkml.models`` module as would be imported from the usual location within the package directory.
            This is intentional, as models can then be used as if they were integrated parts of the package,
            and also so the active version of a namespace can be cleanly accessed
            (ie. without ``from nwb_linkml.models.core import v2_2_0 as core`` ).
            Accordingly, we assume that people will only be using a single version of NWB in a given
            Python session.


        Args:
            namespace (str): Name of namespace to import. Must have either been previously built with :meth:`.PydanticProvider.build` or
                a matching namespace/version combo must be available to the :class:`.LinkMLProvider`
            version (Optional[str]): Version to import. If ``None``, get the most recently build module

        Returns:
            The imported :class:`types.ModuleType` object that has all the built classes at the root level.

        """
        module_name = self.module_name(namespace, version)
        if module_name in sys.modules:
            return sys.modules[module_name]

        try:
            path = self.namespace_path(namespace, version)
        except FileNotFoundError:
            path = None

        if path is None or not path.exists():
            _ = self.build(namespace, version)
        module = self.import_module(namespace, version)
        return module

    def get_class(self, namespace: str, class_: str, version: Optional[str] = None) -> Type[BaseModel]:
        """
        Get a class from a given namespace and version!

        Args:
            namespace (str): Name of a namespace that has been previously built and cached, otherwise
                we will attempt to build it from the :data:`.providers.git.DEFAULT_REPOS`
            class_ (str): Name of class to retrieve
            version (Optional[str]): Optional version of the schema to retrieve from

        Returns:
            :class:`pydantic.BaseModel`
        """
        mod = self.get(namespace, version)
        return getattr(mod, class_)





class SchemaProvider(Provider):
    """
    Class to manage building and caching linkml and pydantic models generated
    from nwb schema language. Combines :class:`.LinkMLProvider` and :class:`.PydanticProvider`

    Behaves like a singleton without needing to be one - since we're working off
    caches on disk that are indexed by hash in most "normal" conditions you should
    be able to use this anywhere, though no file-level locks are present to ensure
    consistency.

    Store each generated schema in a directory structure indexed by
    schema namespace name and version
    """
    build_from_yaml = LinkMLProvider.build_from_yaml
    """
    Alias for :meth:`.LinkMLProvider.build_from_yaml` that also builds a pydantic model
    """
    build_from_dicts = LinkMLProvider.build_from_dicts
    """
    Alias for :meth:`.LinkMLProvider.build_from_dicts` that also builds a pydantic model
    """

    @property
    def path(self) -> Path:
        return self.config.cache_dir


    def build(
        self,
        ns_adapter: adapters.NamespacesAdapter,
        verbose: bool = True,
        linkml_kwargs: Optional[dict] = None,
        pydantic_kwargs: Optional[dict] = None,
        **kwargs
    ) -> Dict[str, str]:
        """
        Build a namespace, storing its linkML and pydantic models.

        Args:
            ns_adapter:
            verbose (bool): If ``True`` (default), show progress bars
            linkml_kwargs (Optional[dict]): Dictionary of kwargs optionally passed to :meth:`.LinkMLProvider.build`
            pydantic_kwargs (Optional[dict]): Dictionary of kwargs optionally passed to :meth:`.PydanticProvider.build`
            **kwargs: Common options added to both ``linkml_kwargs`` and ``pydantic_kwargs``

        Returns:
            Dict[str,str] mapping namespaces to built pydantic sources
        """
        if linkml_kwargs is None:
            linkml_kwargs = {}
        if pydantic_kwargs is None:
            pydantic_kwargs = {}
        linkml_kwargs.update(kwargs)
        pydantic_kwargs.update(kwargs)

        linkml_provider = LinkMLProvider(path=self.path, verbose=verbose)
        pydantic_provider = PydanticProvider(path=self.path, verbose=verbose)

        linkml_res = linkml_provider.build(ns_adapter=ns_adapter, **linkml_kwargs)
        results = {}
        for ns, ns_result in linkml_res.items():
            results[ns] = pydantic_provider.build(ns_result['namespace'], **pydantic_kwargs)
        return results

    def get(self, namespace: str, version: Optional[str] = None) -> ModuleType:
        """
        Get a built pydantic model for a given namespace and version.

        Wrapper around :meth:`.PydanticProvider.get`
        """
        return PydanticProvider(path=self.path).get(namespace, version)

    def get_class(self, namespace: str, class_: str, version: Optional[str] = None) -> Type[BaseModel]:
        """
        Get a pydantic model class from a given namespace and version!

        Wrapper around :meth:`.PydanticProvider.get_class`
        """
        return PydanticProvider(path=self.path).get_class(namespace, class_, version)
























