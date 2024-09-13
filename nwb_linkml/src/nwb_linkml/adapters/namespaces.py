"""
Namespaces adapter

Wraps the :class:`nwb_schema_language.Namespaces` and other objects with convenience methods
for extracting information and generating translated schema
"""

import contextlib
from copy import copy
from pathlib import Path
from pprint import pformat
from typing import Dict, Generator, List, Optional

from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import Annotation, SchemaDefinition
from pydantic import Field, model_validator

from nwb_linkml.adapters.adapter import Adapter, BuildResult
from nwb_linkml.adapters.schema import SchemaAdapter
from nwb_linkml.lang_elements import NwbLangSchema
from nwb_linkml.ui import AdapterProgress
from nwb_linkml.util import merge_dicts
from nwb_schema_language import Dataset, Group, Namespaces


class NamespacesAdapter(Adapter):
    """
    Translate a NWB Namespace to a LinkML Schema
    """

    namespaces: Namespaces
    schemas: List[SchemaAdapter]
    imported: List["NamespacesAdapter"] = Field(default_factory=list)

    _completed: bool = False
    """whether we have run the :meth:`.complete_namespace` method"""

    @classmethod
    def from_yaml(cls, path: Path) -> "NamespacesAdapter":
        """
        Create a NamespacesAdapter from a nwb schema language namespaces yaml file.

        Also attempts to provide imported implicitly imported schema (using the namespace key,
        rather than source, eg. with hdmf-common)
        """
        from nwb_linkml.io import schema as schema_io
        from nwb_linkml.providers.git import DEFAULT_REPOS

        ns_adapter = schema_io.load_namespace_adapter(path)

        # try and find imported schema

        need_imports = []
        for needed in ns_adapter.needed_imports.values():
            # try to locate imports implied by the namespace schema,
            # but are either not provided by the current namespace
            # or are otherwise already provided in `imported` by the loader function
            need_imports.extend(
                [
                    n
                    for n in needed
                    if n not in ns_adapter.needed_imports and n not in ns_adapter.versions
                ]
            )

        for needed in need_imports:
            if needed in DEFAULT_REPOS:
                needed_source_ns = DEFAULT_REPOS[needed].provide_from_git()
                needed_adapter = NamespacesAdapter.from_yaml(needed_source_ns)
                ns_adapter.imported.append(needed_adapter)

        ns_adapter.complete_namespaces()

        return ns_adapter

    def build(
        self, skip_imports: bool = False, progress: Optional[AdapterProgress] = None
    ) -> BuildResult:
        """
        Build the NWB namespace to the LinkML Schema
        """

        if not self._completed:
            self.complete_namespaces()

        sch_result = BuildResult()
        for sch in self.schemas:
            if progress is not None:
                with contextlib.suppress(KeyError):
                    # happens when we skip builds due to caching
                    progress.update(sch.namespace, action=sch.name)
            sch_result += sch.build()
            if progress is not None:
                with contextlib.suppress(KeyError):
                    # happens when we skip builds due to caching
                    progress.update(sch.namespace, advance=1)

        # recursive step
        if not skip_imports:
            for imported in self.imported:
                imported_build = imported.build(progress=progress)
                sch_result += imported_build

        # now generate the top-level namespaces that import everything
        for ns in self.namespaces.namespaces:

            # add in monkeypatch nwb types
            nwb_lang = copy(NwbLangSchema)
            nwb_lang.annotations.update(
                {
                    "is_namespace": Annotation(tag="is_namespace", value="False"),
                    "namespace": Annotation(tag="namespace", value=ns.name),
                }
            )
            lang_schema_name = ".".join([ns.name, "nwb.language"])
            nwb_lang.name = lang_schema_name
            sch_result.schemas.append(nwb_lang)

            ns_schemas = [sch.name for sch in self.schemas if sch.namespace == ns.name]
            ns_schemas.append(lang_schema_name)

            # also add imports bc, well, we need them
            if not skip_imports:
                ns_schemas.extend(
                    [ns.name for imported in self.imported for ns in imported.namespaces.namespaces]
                )
            ns_schema = SchemaDefinition(
                name=ns.name,
                id=ns.name,
                description=ns.doc,
                version=ns.version,
                imports=ns_schemas,
                annotations=[
                    {"tag": "is_namespace", "value": True},
                    {"tag": "namespace", "value": ns.name},
                ],
            )
            sch_result.schemas.append(ns_schema)

        return sch_result

    @model_validator(mode="after")
    def _populate_schema_namespaces(self) -> None:
        """
        annotate for each schema which namespace imports it
        """
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
        return self

    def complete_namespaces(self) -> None:
        """
        After loading the namespace, and after any imports have been added afterwards,
        this must be called to complete the definitions of the contained schema objects.

        This is not automatic because NWB doesn't have a formal dependency resolution system,
        so it is often impossible to know which imports are needed until after the namespace
        adapter has been instantiated.

        It **is** automatically called if it hasn't been already by the :meth:`.build` method.
        """
        self._populate_imports()
        self._roll_down_inheritance()

        for i in self.imported:
            i.complete_namespaces()

        self._completed = True

    def _roll_down_inheritance(self) -> None:
        """
        nwb-schema-language inheritance doesn't work like normal python inheritance -
        instead of inheriting everything at the 'top level' of a class, it also
        recursively merges all properties from the parent objects.

        References:
            https://github.com/NeurodataWithoutBorders/pynwb/issues/1954
        """
        for cls in self.walk_types(self, (Group, Dataset)):
            if not cls.neurodata_type_inc:
                continue

            # get parents
            parent = self.get(cls.neurodata_type_inc)
            parents = [parent]
            while parent.neurodata_type_inc:
                parent = self.get(parent.neurodata_type_inc)
                parents.insert(0, parent)
            parents.append(cls)

            # merge and cast
            # note that we don't want to exclude_none in the model dump here,
            # if the child class has a field completely unset, we want to inherit it
            # from the parent without rolling it down - we are only rolling down
            # the things that need to be modified/merged in the child
            new_cls: dict = {}
            for parent in parents:
                new_cls = merge_dicts(
                    new_cls,
                    parent.model_dump(exclude_unset=True),
                    list_key="name",
                    exclude=["neurodata_type_def"],
                )
            new_cls: Group | Dataset = type(cls)(**new_cls)
            new_cls.parent = cls.parent

            # reinsert
            if new_cls.parent:
                if isinstance(cls, Dataset):
                    new_cls.parent.datasets[new_cls.parent.datasets.index(cls)] = new_cls
                else:
                    new_cls.parent.groups[new_cls.parent.groups.index(cls)] = new_cls
            else:
                # top level class, need to go and find it
                found = False
                for schema in self.all_schemas():
                    if isinstance(cls, Dataset):
                        if cls in schema.datasets:
                            schema.datasets[schema.datasets.index(cls)] = new_cls
                            found = True
                            break
                    else:
                        if cls in schema.groups:
                            schema.groups[schema.groups.index(cls)] = new_cls
                            found = True
                            break
                if not found:
                    raise KeyError(
                        f"Unable to find source schema for {cls} when reinserting after rolling"
                        " down!"
                    )

    def find_type_source(self, name: str) -> SchemaAdapter:
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
                f"Found multiple schemas in namespace that define {name}:\ninternal:"
                f" {pformat(internal_matches)}\nimported:{pformat(internal_matches)}"
            )
        elif len(internal_matches) == 1:
            return internal_matches[0]

        import_matches = []
        for imported_ns in self.imported:
            for schema in imported_ns.schemas:
                class_names = [cls.neurodata_type_def for cls in schema.created_classes]
                if name in class_names:
                    import_matches.append(schema)

        if len(import_matches) > 1:
            raise KeyError(
                f"Found multiple schemas in namespace that define {name}:\ninternal:"
                f" {pformat(internal_matches)}\nimported:{pformat(import_matches)}"
            )
        elif len(import_matches) == 1:
            return import_matches[0]
        else:
            raise KeyError(f"No schema found that define {name}")

    def _populate_imports(self) -> "NamespacesAdapter":
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

        return self

    def to_yaml(self, base_dir: Path) -> None:
        """
        Build the schemas, saving them to ``yaml`` files according to
        their ``name``

        Args:
            base_dir (:class:`.Path`): Directory to save ``yaml`` files
        """
        schemas = self.build().schemas
        base_dir = Path(base_dir)

        base_dir.mkdir(exist_ok=True)

        for schema in schemas:
            output_file = base_dir / (schema.name + ".yaml")
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
        versions = {ns.name: ns.version for ns in self.namespaces.namespaces}
        for imported in self.imported:
            versions.update(imported.versions)
        return versions

    def namespace_schemas(self, name: str) -> List[str]:
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
                raise NameError(f"Couldn't find namespace {name}")
        else:
            ns = ns[0]

        schema_names = [sch.source for sch in ns.schema_ if sch.source is not None]
        return schema_names

    def schema_namespace(self, name: str) -> Optional[str]:
        """
        Inverse of :meth:`.namespace_schemas` - given a schema name, get the namespace it's in
        """
        for ns in self.namespaces.namespaces:
            sources = [sch.source for sch in ns.schema_ if sch.source is not None]
            if name in sources:
                return ns.name
        return None

    def all_schemas(self) -> Generator[SchemaAdapter, None, None]:
        """
        Iterator over all schemas including imports
        """
        for sch in self.schemas:
            yield sch
        for imported in self.imported:
            for sch in imported.schemas:
                yield sch
