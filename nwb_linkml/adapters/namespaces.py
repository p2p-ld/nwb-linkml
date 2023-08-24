"""
Namespaces adapter

Wraps the :class:`nwb_schema_language.Namespaces` and other objects with convenience methods
for extracting information and generating translated schema
"""
import pdb
from typing import List, Optional
from pydantic import BaseModel, Field, validator, PrivateAttr
from pprint import pformat
from linkml_runtime.linkml_model import SchemaDefinition

from nwb_schema_language import Namespaces

from nwb_linkml.adapters.adapter import Adapter, BuildResult
from nwb_linkml.adapters.schema import SchemaAdapter
from nwb_linkml.lang_elements import NwbLangSchema

class NamespacesAdapter(Adapter):
    namespaces: Namespaces
    schemas: List[SchemaAdapter]
    imported: List['NamespacesAdapter'] = Field(default_factory=list)

    _imports_populated = PrivateAttr(False)

    def __init__(self, **kwargs):
        super(NamespacesAdapter, self).__init__(**kwargs)
        self._populate_schema_namespaces()

    def build(self) -> BuildResult:
        if not self._imports_populated:
            self.populate_imports()


        sch_result = BuildResult()
        for sch in self.schemas:
            sch_result += sch.build()
        # recursive step
        for imported in self.imported:
            imported_build = imported.build()
            sch_result += imported_build

        # add in monkeypatch nwb types
        sch_result.schemas.append(NwbLangSchema)

        # now generate the top-level namespaces that import everything
        for ns in self.namespaces.namespaces:
            ns_schemas = [sch for sch in self.schemas if sch.namespace == ns.name]
            ns_schema = SchemaDefinition(
                name = ns.name,
                id = ns.name,
                description = ns.doc,
                version = ns.version,
                imports=[sch.name for sch in ns_schemas]
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
                if sch_name in sources:
                    sch.namespace = ns.name
                    break



    def find_type_source(self, name:str) -> SchemaAdapter:
        """
        Given some neurodata_type_inc, find the schema that it's defined in.
        """
        # First check within the main schema
        internal_matches = []
        for schema in self.schemas:
            class_names = [cls.neurodata_type_def for cls in schema.created_classes]
            if name in class_names:
                internal_matches.append(schema)

        import_matches = []
        for imported_ns in self.imported:
            for schema in imported_ns.schemas:
                class_names = [cls.neurodata_type_def for cls in schema.created_classes]
                if name in class_names:
                    import_matches.append(schema)

        all_matches = [*internal_matches, *import_matches]

        if len(all_matches)>1:
            pdb.set_trace()
            raise KeyError(f"Found multiple schemas in namespace that define {name}:\ninternal: {pformat(internal_matches)}\nimported:{pformat(import_matches)}")
        elif len(all_matches) == 1:
            return all_matches[0]
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


