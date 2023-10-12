"""
Namespaces adapter

Wraps the :class:`nwb_schema_language.Namespaces` and other objects with convenience methods
for extracting information and generating translated schema
"""
import pdb

from typing import List, Optional, Dict
from pathlib import Path
from pydantic import BaseModel, Field, validator, PrivateAttr
from pprint import pformat
from linkml_runtime.linkml_model import SchemaDefinition, Annotation
from linkml_runtime.dumpers import yaml_dumper
from time import sleep
from copy import copy


from nwb_schema_language import Namespaces

from nwb_linkml.adapters.adapter import Adapter, BuildResult
from nwb_linkml.adapters.schema import SchemaAdapter
from nwb_linkml.lang_elements import NwbLangSchema


from nwb_linkml.ui import AdapterProgress

class NamespacesAdapter(Adapter):
    namespaces: Namespaces
    schemas: List[SchemaAdapter]
    imported: List['NamespacesAdapter'] = Field(default_factory=list)

    _imports_populated: bool = PrivateAttr(False)

    def __init__(self, **kwargs):
        super(NamespacesAdapter, self).__init__(**kwargs)
        self._populate_schema_namespaces()

    @classmethod
    def from_yaml(cls, path:Path) -> 'NamespacesAdapter':
        """
        Create a NamespacesAdapter from a nwb schema language namespaces yaml file.

        Also attempts to provide imported implicitly imported schema (using the namespace key, rather than source, eg.
        with hdmf-common)
        """
        from nwb_linkml.io import schema as schema_io
        from nwb_linkml.providers.git import DEFAULT_REPOS
        ns_adapter = schema_io.load_namespace_adapter(path)

        # try and find imported schema

        need_imports = []
        for needed in ns_adapter.needed_imports.values():
            need_imports.extend([n for n in needed if n not in ns_adapter.needed_imports.keys()])

        for needed in need_imports:
            if needed in DEFAULT_REPOS.keys():
                needed_source_ns = DEFAULT_REPOS[needed].provide_from_git()
                needed_adapter = NamespacesAdapter.from_yaml(needed_source_ns)
                ns_adapter.imported.append(needed_adapter)

        return ns_adapter



    def build(self, skip_imports:bool=False, progress:Optional[AdapterProgress] = None) -> BuildResult:
        if not self._imports_populated and not skip_imports:
            self.populate_imports()

        sch_result = BuildResult()
        for sch in self.schemas:
            if progress is not None:
                try:
                    progress.update(sch.namespace, action=sch.name)
                except KeyError: # pragma: no cover
                    # happens when we skip builds due to caching
                    pass
            sch_result += sch.build()
            if progress is not None:
                try:
                    progress.update(sch.namespace, advance=1)
                except KeyError: # pragma: no cover
                    # happens when we skip builds due to caching
                    pass


        # recursive step
        if not skip_imports:
            for imported in self.imported:
                imported_build = imported.build(progress=progress)
                sch_result += imported_build


        # now generate the top-level namespaces that import everything
        for ns in self.namespaces.namespaces:

            # add in monkeypatch nwb types
            nwb_lang = copy(NwbLangSchema)
            nwb_lang.annotations = {
                'is_namespace': Annotation(tag='is_namespace', value= 'False'),
                'namespace': Annotation(tag='namespace', value= ns.name)
            }
            lang_schema_name = '.'.join([ns.name, 'nwb.language'])
            nwb_lang.name = lang_schema_name
            sch_result.schemas.append(nwb_lang)

            ns_schemas = [sch.name for sch in self.schemas if sch.namespace == ns.name]
            ns_schemas.append(lang_schema_name)

            # also add imports bc, well, we need them
            if not skip_imports:
                ns_schemas.extend([ns.name for imported in self.imported for ns in imported.namespaces.namespaces])
            ns_schema = SchemaDefinition(
                name = ns.name,
                id = ns.name,
                description = ns.doc,
                version = ns.version,
                imports=ns_schemas,
                annotations=[{'tag': 'is_namespace', 'value': True}, {'tag': 'namespace', 'value': ns.name}]
            )
            sch_result.schemas.append(ns_schema)

        return sch_result

    def _populate_schema_namespaces(self):
        # annotate for each schema which namespace imports it
        for sch in self.schemas:
            # imports seem to always be from same folder, so we can just use name part
            sch_name = sch.path.name
            # find which namespace imports this schema file
            for ns in self.namespaces.namespaces:
                sources = [sch.source for sch in ns.schema_]
                if sch_name in sources or sch.path.stem in sources:
                    sch.namespace = ns.name
                    sch.version = ns.version
                    break

    def find_type_source(self, name:str) -> SchemaAdapter:
        """
        Given some neurodata_type_inc, find the schema that it's defined in.

        Rather than returning as soon as a match is found, check all
        """
        # First check within the main schema
        internal_matches = []
        for schema in self.schemas:
            class_names = [cls.neurodata_type_def for cls in schema.created_classes]
            if name in class_names:
                internal_matches.append(schema)

        if len(internal_matches) > 1:
            raise KeyError(
                f"Found multiple schemas in namespace that define {name}:\ninternal: {pformat(internal_matches)}\nimported:{pformat(import_matches)}")
        elif len(internal_matches) == 1:
            return internal_matches[0]

        import_matches = []
        for imported_ns in self.imported:
            for schema in imported_ns.schemas:
                class_names = [cls.neurodata_type_def for cls in schema.created_classes]
                if name in class_names:
                    import_matches.append(schema)

        if len(import_matches)>1:
            raise KeyError(f"Found multiple schemas in namespace that define {name}:\ninternal: {pformat(internal_matches)}\nimported:{pformat(import_matches)}")
        elif len(import_matches) == 1:
            return import_matches[0]
        else:
            raise KeyError(f"No schema found that define {name}")

    def populate_imports(self):
        """
        Populate the imports that are needed for each schema file

        This function adds a string version of imported schema assuming the
        generated schema will live in the same directory. If the path to
        the imported schema needs to be adjusted, that should happen elsewhere
        (eg in :class:`.LinkMLProvider`) because we shouldn't know about
        directory structure or anything like that here.
        """
        for sch in self.schemas:
            for needs in sch.needed_imports:
                # shouldn't be recursive references, since imports should form a tree
                depends_on = self.find_type_source(needs)
                if depends_on not in sch.imports:
                    sch.imports.append(depends_on)

        # do so recursively
        for imported in self.imported:
            imported.populate_imports()

        self._imports_populated = True

    def to_yaml(self, base_dir:Path):
        schemas = self.build().schemas
        base_dir = Path(base_dir)

        base_dir.mkdir(exist_ok=True)

        for schema in schemas:
            output_file = base_dir / (schema.name + '.yaml')
            yaml_dumper.dump(schema, output_file)

    @property
    def needed_imports(self) -> Dict[str, List[str]]:
        """
        List of other, external namespaces that we need to import.
        Usually provided as schema with a namespace but not a source

        Returns:
            {'namespace_name': ['needed_import_0', ...]}
        """
        needed_imports = {}
        for a_ns in self.namespaces.namespaces:
            needed_imports[a_ns.name] = []
            for potential_import in a_ns.schema_:
                if potential_import.namespace and not potential_import.source:
                    needed_imports[a_ns.name].append(potential_import.namespace)

        return needed_imports

    @property
    def versions(self) -> Dict[str, str]:
        """
        versions for each namespace
        """
        versions = {ns.name:ns.version for ns in self.namespaces.namespaces}
        for imported in self.imported:
            versions.update(imported.versions)
        return versions


    def namespace_schemas(self, name:str) -> List[str]:
        """
        Get the schemas that are defined in a given namespace
        """
        ns = [ns for ns in self.namespaces.namespaces if ns.name == name]
        if len(ns) == 0:
            for imported in self.imported:
                ns = [ns for ns in imported.namespaces.namespaces if ns.name == name]
                if len(ns) > 0:
                    ns = ns[0]
                    break
            else:
                raise NameError(f"Couldnt find namespace {name}")
        else:
            ns = ns[0]

        schema_names = []
        for sch in ns.schema_:
            if sch.source is not None:
                schema_names.append(sch.source)
        return schema_names

    def schema_namespace(self, name:str) -> Optional[str]:
        """
        Inverse of :meth:`.namespace_schemas` - given a schema name, get the namespace it's in
        """
        for ns in self.namespaces.namespaces:
            sources = [sch.source for sch in ns.schema_ if sch.source is not None]
            if name in sources:
                return ns.name
        return None



