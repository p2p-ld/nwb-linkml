"""
Namespaces adapter

Wraps the :class:`nwb_schema_language.Namespaces` and other objects with convenience methods
for extracting information and generating translated schema
"""

import contextlib
from copy import copy
from pathlib import Path
from typing import Dict, Generator, List, Optional

from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import Annotation, SchemaDefinition
from pydantic import Field, model_validator

from nwb_linkml.adapters.adapter import Adapter, BuildResult
from nwb_linkml.adapters.schema import SchemaAdapter
from nwb_linkml.lang_elements import NwbLangSchema
from nwb_linkml.ui import AdapterProgress
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

        While this operation does not take care to modify classes in a way that respect their order
        (i.e. roll down ancestor classes first, in order, before the leaf classes),
        it doesn't matter - this method should be both idempotent and order insensitive
        for a given source schema.

        References:
            https://github.com/NeurodataWithoutBorders/pynwb/issues/1954
        """
        for cls in self.walk_types(self, (Group, Dataset)):
            if not cls.neurodata_type_inc:
                continue

            parents = self._get_class_ancestors(cls, include_child=True)

            # merge and cast
            new_cls: dict = {}
            for i, parent in enumerate(parents):
                # we want a full roll-down of all the ancestor classes,
                # but we make an abbreviated leaf class
                complete = False if i == len(parents) - 1 else True
                new_cls = roll_down_nwb_class(new_cls, parent, complete=complete)
            new_cls: Group | Dataset = type(cls)(**new_cls)
            new_cls.parent = cls.parent

            # reinsert
            self._overwrite_class(new_cls, cls)

    def _get_class_ancestors(
        self, cls: Dataset | Group, include_child: bool = True
    ) -> list[Dataset | Group]:
        """
        Get the chain of ancestor classes inherited via ``neurodata_type_inc``

        Args:
            cls (:class:`.Dataset` | :class:`.Group`): The class to get ancestors of
            include_child (bool): If ``True`` (default), include ``cls`` in the output list
        """
        parent = self.get(cls.neurodata_type_inc)
        parents = [parent]
        while parent.neurodata_type_inc:
            parent = self.get(parent.neurodata_type_inc)
            parents.insert(0, parent)

        if include_child:
            parents.append(cls)

        return parents

    def _overwrite_class(self, new_cls: Dataset | Group, old_cls: Dataset | Group) -> None:
        """
        Overwrite the version of a dataset or group that is stored in our schemas
        """
        if old_cls.parent:
            if isinstance(old_cls, Dataset):
                new_cls.parent.datasets[new_cls.parent.datasets.index(old_cls)] = new_cls
            else:
                new_cls.parent.groups[new_cls.parent.groups.index(old_cls)] = new_cls
        else:
            # top level class, need to go and find it
            schema = self.find_type_source(old_cls)
            if isinstance(new_cls, Dataset):
                schema.datasets[schema.datasets.index(old_cls)] = new_cls
            else:
                schema.groups[schema.groups.index(old_cls)] = new_cls

    def find_type_source(self, cls: str | Dataset | Group, fast: bool = False) -> SchemaAdapter:
        """
        Given some type (as `neurodata_type_def`), find the schema that it's defined in.

        Rather than returning as soon as a match is found, ensure that duplicates are
        not found within the primary schema, then so the same for all imported schemas.

        Args:
            cls (str | :class:`.Dataset` | :class:`.Group`): The ``neurodata_type_def``
                to look for the source of. If a Dataset or Group, look for the object itself
                (cls in schema.datasets), otherwise look for a class with a matching name.
            fast (bool): If ``True``, return as soon as a match is found.
                If ``False`, return after checking all schemas for duplicates.

        Returns:
            :class:`.SchemaAdapter`

        Raises:
            KeyError: if multiple schemas or no schemas are found
        """
        matches = []
        for schema in self.all_schemas():
            in_schema = False
            if (
                isinstance(cls, str)
                and cls in [c.neurodata_type_def for c in schema.created_classes]
                or isinstance(cls, Dataset)
                and cls in schema.datasets
                or isinstance(cls, Group)
                and cls in schema.groups
            ):
                in_schema = True

            if in_schema:
                if fast:
                    return schema
                else:
                    matches.append(schema)

        if len(matches) > 1:
            raise KeyError(f"Found multiple schemas in namespace that define {cls}:\n{matches}")
        elif len(matches) == 1:
            return matches[0]
        else:
            raise KeyError(f"No schema found that define {cls}")

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


def roll_down_nwb_class(
    source: Group | Dataset | dict, target: Group | Dataset | dict, complete: bool = False
) -> dict:
    """
    Merge an ancestor (via ``neurodata_type_inc`` ) source class with a
    child ``target`` class.

    On the first recursive pass, only those values that are set on the target are copied from the
    source class - this isn't a true merging, what we are after is to recursively merge all the
    values that are modified in the child class with those of the parent class below the top level,
    the top-level attributes will be carried through via normal inheritance.

    Rather than re-instantiating the child class, we return the dictionary so that this
    function can be used in series to merge a whole ancestry chain within
    :class:`.NamespacesAdapter` , but merging isn't exposed in the function since
    ancestor class definitions can be spread out over many schemas,
    and we need the orchestration of the adapter to have them in all cases we'd be using this.

    Args:
        source (dict): source dictionary
        target (dict): target dictionary (values merged over source)
        complete (bool): (default ``False``)do a complete merge, merging everything
            from source to target without trying to minimize redundancy.
            Used to collapse ancestor classes before the terminal class.

    References:
        https://github.com/NeurodataWithoutBorders/pynwb/issues/1954

    """
    if isinstance(source, (Group, Dataset)):
        source = source.model_dump(exclude_none=True)
    if isinstance(target, (Group, Dataset)):
        target = target.model_dump(exclude_none=True)

    exclude = ("neurodata_type_def",)

    # if we are on the first recursion, we exclude top-level items that are not set in the target
    if complete:
        ret = {k: v for k, v in source.items() if k not in exclude}
    else:
        ret = {k: v for k, v in source.items() if k not in exclude and k in target}

    for key, value in target.items():
        if key not in ret:
            ret[key] = value
        elif isinstance(value, dict):
            if key in ret:
                ret[key] = roll_down_nwb_class(ret[key], value, complete=True)
            else:
                ret[key] = value
        elif isinstance(value, list) and all([isinstance(v, dict) for v in value]):
            src_keys = {v["name"]: ret[key].index(v) for v in ret.get(key, {}) if "name" in v}
            target_keys = {v["name"]: value.index(v) for v in value if "name" in v}

            new_val = []
            # screwy double iteration to preserve dict order
            # all dicts not in target, if in depth > 0
            if complete:
                new_val.extend(
                    [
                        ret[key][src_keys[k]]
                        for k in src_keys
                        if k in set(src_keys.keys()) - set(target_keys.keys())
                    ]
                )
            # all dicts not in source
            new_val.extend(
                [
                    value[target_keys[k]]
                    for k in target_keys
                    if k in set(target_keys.keys()) - set(src_keys.keys())
                ]
            )
            # merge dicts in both
            new_val.extend(
                [
                    roll_down_nwb_class(ret[key][src_keys[k]], value[target_keys[k]], complete=True)
                    for k in target_keys
                    if k in set(src_keys.keys()).intersection(set(target_keys.keys()))
                ]
            )
            new_val = sorted(new_val, key=lambda i: i["name"])
            # add any dicts that don't have the list_key
            # they can't be merged since they can't be matched
            if complete:
                new_val.extend([v for v in ret.get(key, {}) if "name" not in v])
            new_val.extend([v for v in value if "name" not in v])

            ret[key] = new_val

        else:
            ret[key] = value

    return ret
