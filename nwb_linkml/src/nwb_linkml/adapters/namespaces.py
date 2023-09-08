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
from linkml_runtime.linkml_model import SchemaDefinition
from linkml_runtime.dumpers import yaml_dumper


from nwb_schema_language import Namespaces

from nwb_linkml.adapters.adapter import Adapter, BuildResult
from nwb_linkml.adapters.schema import SchemaAdapter
from nwb_linkml.lang_elements import NwbLangSchema

class NamespacesAdapter(Adapter):
    namespaces: Namespaces
    schemas: List[SchemaAdapter]
    imported: List['NamespacesAdapter'] = Field(default_factory=list)

    _imports_populated: bool = PrivateAttr(False)
    _split: bool = PrivateAttr(False)

    def __init__(self, **kwargs):
        super(NamespacesAdapter, self).__init__(**kwargs)
        self._populate_schema_namespaces()
        self.split = self._split

    def build(self, skip_imports:bool=False) -> BuildResult:
        if not self._imports_populated and not skip_imports:
            self.populate_imports()


        sch_result = BuildResult()
        for sch in self.schemas:
            sch_result += sch.build()
        # recursive step
        if not skip_imports:
            for imported in self.imported:
                imported_build = imported.build()
                sch_result += imported_build

        # add in monkeypatch nwb types
        sch_result.schemas.append(NwbLangSchema)

        # now generate the top-level namespaces that import everything
        for ns in self.namespaces.namespaces:
            ns_schemas = [sch.name for sch in self.schemas if sch.namespace == ns.name]
            # also add imports bc, well, we need them
            if not skip_imports:
                ns_schemas.extend([ns.name for imported in self.imported for ns in imported.namespaces.namespaces])
            ns_schema = SchemaDefinition(
                name = ns.name,
                id = ns.name,
                description = ns.doc,
                version = ns.version,
                imports=ns_schemas,
                annotations=[{'tag': 'namespace', 'value': True}]
            )
            sch_result.schemas.append(ns_schema)

        return sch_result

    @property
    def split(self) -> bool:
        """
        Sets the :attr:`.SchemaAdapter.split` attribute for all contained and imported schema

        Args:
            split (bool): Set the generated schema to be split or not

        Returns:
            bool: whether the schema are set to be split!
        """
        return self._split

    @split.setter
    def split(self, split):
        for sch in self.schemas:
            sch.split = split
        for ns in self.imported:
            for sch in ns.schemas:
                sch.split = split

        self._split = split

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
        return {ns['name']:ns['version'] for ns in self.namespaces.namespaces}

    def namespace_schemas(self, name:str) -> List[str]:
        """
        Get the schemas that are defined in a given namespace
        """
        ns = [ns for ns in self.namespaces.namespaces if ns.name == name][0]
        schema_names = []
        for sch in ns.schema_:
            if sch.source is not None:
                schema_names.append(sch.source)
        return schema_names



