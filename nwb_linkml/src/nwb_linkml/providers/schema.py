"""
Class for managing, building, and caching built schemas.

The nwb.core and hdmf-common schema are statically built and stored in this repository,
but to make it feasible to use arbitrary schema, eg. those stored inside of
an NWB file, we need a bit of infrastructure for generating and caching
pydantic models on the fly.

Relationship to other modules:
- :mod:`.adapters` manage the conversion from NWB schema language to linkML.
- :mod:`.generators` create models like pydantic models from the linkML schema
- :mod:`.providers` then use ``adapters`` and ``generators`` to provide models
  from generated schema!
"""
from typing import Dict, TypedDict, List, Optional, Literal, TypeVar, Any, Dict
from pathlib import Path
import os
from abc import abstractmethod

from linkml_runtime.linkml_model import SchemaDefinition
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime import SchemaView

from nwb_linkml.config import Config
from nwb_linkml import io
from nwb_linkml import adapters
from nwb_linkml.adapters.adapter import BuildResult
from nwb_linkml.maps.naming import module_case, version_module_case, relative_path
from nwb_schema_language import Namespaces
from nwb_linkml.generators.pydantic import NWBPydanticGenerator

class NamespaceVersion(TypedDict):
    namespace: str
    version: str

P = TypeVar('P')

class Provider:
    """
    Metaclass for different kind of providers!
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

    @abstractmethod
    @property
    def path(self) -> Path:
        """
        Base path for this kind of provider
        """

    @abstractmethod
    def build(self, *args: Any):
        """
        Whatever needs to be done to build this thing, if applicable
        """


    def namespace_path(
            self,
            namespace: str,
            version: Optional[str] = None) -> Path:
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
        """
        namespace_module = module_case(namespace)
        namespace_path = self.path / namespace_module
        if not namespace_path.exists() and namespace in ('core', 'hdmf-common'):
            # return builtins
            if self.PROVIDES == 'linkml':
                from nwb_linkml import schema
                namespace_path =  Path(schema.__file__)
            elif self.PROVIDES == 'pydantic':
                from nwb_linkml import models
                namespace_path = Path(models.__file__)

        if version is not None:
            version_path = namespace_path / version_module_case(version)
        else:
            # or find the most recently built one
            versions = sorted(namespace_path.iterdir(), key=os.path.getmtime)
            if len(versions) == 0:
                raise FileNotFoundError('No version provided, and no existing schema found')
            version_path = versions[-1]

        return version_path




class LinkMLProvider(Provider):
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
        sch = {}
        ns_dict = io.schema.load_yaml(path)
        sch['namespace'] = ns_dict
        namespace = Namespaces(**ns_dict)

        for ns in namespace.namespaces:
            for schema in ns.schema_:
                if schema.source is None:
                    # this is normal, we'll resolve later
                    continue
                yml_file = path.parent / schema.source
                sch[yml_file.stem] = (io.schema.load_yaml(yml_file))

        return self.build(schemas=sch, **kwargs)

    def build(
        self,
        schemas:Dict[str, dict],
        versions: Optional[List[NamespaceVersion]] = None,
        dump: bool = True,
    ) -> BuildResult:
        """
        Arguments:
            schemas (dict): A dictionary of ``{'schema_name': {:schema_definition}}``.
                The "namespace" schema should have the key ``namespace``, which is used
                to infer version and schema name. Post-load maps should have already
                been applied
            versions (List[NamespaceVersion]): List of specific versions to use
                for cross-namespace imports. If none is provided, use the most recent version
                available.
            dump (bool): If ``True`` (default), dump generated schema to YAML. otherwise just return
        """
        ns = Namespaces(**schemas['namespace'])
        typed_schemas = [
            io.schema.load_schema_file(
                path=Path(key + ".yaml"),
                yaml=val)
            for key,val in schemas.items()
            if key != 'namespace'
        ]
        ns_adapter = adapters.NamespacesAdapter(
            namespaces=ns,
            schemas=typed_schemas
        )
        self._find_imports(ns_adapter, versions, populate=True)
        built = ns_adapter.build()

        # write schemas to yaml files
        namespace_sch = [sch for sch in built.schemas if 'namespace' in sch.annotations.keys()]
        for ns_linkml in namespace_sch:
            version = ns_adapter.versions[ns_linkml.name]
            version_path = self.namespace_path(ns_linkml.name, version)
            with open(version_path / 'namespace.yaml', 'w') as ns_f:
                yaml_dumper.dump(ns_linkml, version_path)
            # write the schemas for this namespace
            ns_schema_names = ns_adapter.namespace_schemas(ns_linkml.name)
            other_schema = [sch for sch in built.schemas if sch.name in ns_schema_names]
            for sch in other_schema:
                output_file = version_path / (sch.name + '.yaml')
                yaml_dumper.dump(sch, output_file)

        return built

    def get(self, namespace: str, version: Optional[str] = None) -> SchemaView:
        """
        Get a schema view over the namespace
        """
        path = self.namespace_path(namespace, version) / 'namespace.yaml'
        return SchemaView(path)


    def _find_imports(self,
                      ns: adapters.NamespacesAdapter,
                      versions: Optional[List[NamespaceVersion]] = None,
                      populate: bool=True) -> Dict[str, List[str]]:
        """
        Find relative paths to other linkml schema that need to be
        imported, but lack an explicit source

        Arguments:
            ns (:class:`.NamespacesAdapter`): Namespaces to find imports to
            versions (List[:class:`.NamespaceVersion`]): Specific versions to import
            populate (bool): If ``True`` (default), modify the namespace adapter to include the imports,
                otherwise just return

        Returns:
            dict of lists for relative paths to other schema namespaces
        """
        import_paths = {}
        for ns_name, needed_imports in ns.needed_imports.items():
            our_path = self.namespace_path(ns_name, ns.versions[ns_name]) / 'namespace.yaml'
            import_paths[ns_name] = []
            for needed_import in needed_imports:
                needed_version = None
                if versions:
                    needed_versions = [v['version'] for v in versions if v['namespace'] == needed_import]
                    if len(needed_versions) > 0:
                        needed_version = needed_versions[0]

                version_path = self.namespace_path(needed_import, needed_version) / 'namespace.yaml'
                import_paths[ns_name].append(str(relative_path(version_path, our_path)))

            if populate:
                for sch in ns.schemas:
                    sch.imports.extend(import_paths)

        return import_paths


class PydanticProvider(Provider):
    PROVIDES = 'pydantic'

    @property
    def path(self) -> Path:
        return self.config.pydantic_dir

    def build(
            self,
            namespace: str | Path,
            version: Optional[str] = None,
            versions: Optional[List[NamespaceVersion]] = None,
            dump: bool = True
    ) -> str:
        if isinstance(namespace, str) and not (namespace.endswith('.yaml') or namespace.endswith('.yml')):
            # we're given a name of a namespace to build
            path = LinkMLProvider(path=self.config.cache_dir).namespace_path(namespace, version) / 'namespace.yaml'
        else:
            # given a path to a namespace linkml yaml file
            path = Path(namespace)

        generator = NWBPydanticGenerator(
            str(path),
            split=False,
            versions=versions,
            emit_metadata=True,
            gen_slots=True,
            pydantic_version='2'
        )
        serialized = generator.serialize()
        if dump:
            out_file = self.path / path.parts[-3] / path.parts[-2] / 'namespace.py'
            with open(out_file, 'w') as ofile:
                ofile.write(serialized)

        return serialized


class SchemaProvider:
    """
    Class to manage building and caching linkml and pydantic models generated
    from nwb schema language

    Behaves like a singleton without needing to be one - since we're working off
    caches on disk that are indexed by hash in most "normal" conditions you should
    be able to use this anywhere, though no file-level locks are present to ensure
    consistency.

    Store each generated schema in a directory structure indexed by
    schema namespace name and a truncated hash of the loaded schema dictionaries
    (not the hash of the .yaml file, since we are also provided schema in nwbfiles)

    eg:

        cache_dir
          - linkml
            - nwb_core
              - hash_532gn90f
                - nwb.core.namespace.yaml
                - nwb.fore.file.yaml
                - ...
              - hash_fuia082f
                - nwb.core.namespace.yaml
                - ...
            - my_schema
              - hash_t3tn908h
                - ...
          - pydantic
            - nwb_core
              - hash_532gn90f
                - core.py
                - ...
              - hash_fuia082f
                - core.py
                - ...

    """

    def __init__(self,
                 path: Optional[Path] = None,
                 verbose: bool = True):
        """
        Arguments:
            path (bool): If provided, output to an explicit base directory.
                Otherwise use that provided in ``NWB_LINKML_CACHE_DIR``
            verbose (bool): If ``True`` (default), show progress bars and other messages
                useful for interactive use
        """
        if path is not None:
            config = Config(cache_dir=path)
        else:
            config = Config()
        self.cache_dir = config.cache_dir
        self.pydantic_dir = config.pydantic_dir
        self.linkml_dir = config.linkml_dir

        self.verbose = verbose



    def generate_linkml(
            self,
            schemas:Dict[str, dict],
            versions: Optional[List[NamespaceVersion]] = None
    ):
        """
        Generate linkml from loaded nwb schemas, either from yaml or from an
        nwb file's ``/specifications`` group.

        Arguments:
            schemas (dict): A dictionary of ``{'schema_name': {:schema_definition}}``.
                The "namespace" schema should have the key ``namespace``, which is used
                to infer version and schema name. Post-load maps should have already
                been applied
            versions (List[NamespaceVersion]): List of specific versions to use
                for cross-namespace imports. If none is provided, use the most recent version
                available.
        """














