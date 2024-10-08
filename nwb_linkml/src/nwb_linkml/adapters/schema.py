"""
I don't know if NWB necessarily has a term for a single nwb schema file, so we're going
to call them "schema" objects
"""

import pdb
from pathlib import Path
from typing import List, Optional, Type

from linkml_runtime.linkml_model import SchemaDefinition
from pydantic import Field, PrivateAttr

from nwb_linkml.adapters.adapter import Adapter, BuildResult
from nwb_linkml.adapters.dataset import DatasetAdapter
from nwb_linkml.adapters.group import GroupAdapter
from nwb_schema_language import Dataset, Group


class SchemaAdapter(Adapter):
    """
    An individual schema file in nwb_schema_language
    """

    path: Path
    groups: List[Group] = Field(default_factory=list)
    datasets: List[Dataset] = Field(default_factory=list)
    imports: List["SchemaAdapter | str"] = Field(default_factory=list)
    namespace: Optional[str] = Field(
        None, description="""String of containing namespace. Populated by NamespacesAdapter"""
    )
    version: Optional[str] = Field(
        None,
        description=(
            "Version of schema, populated by NamespacesAdapter since individual schema files dont"
            " know their version in NWB Schema Lang"
        ),
    )
    _created_classes: List[Type[Group | Dataset]] = PrivateAttr(default_factory=list)

    @property
    def name(self) -> str:
        """
        The namespace.schema name for a single schema
        """
        namespace = self.namespace if self.namespace is not None else ""
        return ".".join([namespace, self.path.with_suffix("").name])

    def __repr__(self):
        out_str = "\n" + self.name + "\n"
        out_str += "-" * len(self.name) + "\n"
        if len(self.imports) > 0:
            out_str += "Imports:\n"
            out_str += (
                "  "
                + ", ".join([i.name if isinstance(i, SchemaAdapter) else i for i in self.imports])
                + "\n"
            )

        out_str += "Groups:\n"
        out_str += "  " + ", ".join([g.neurodata_type_def for g in self.groups])
        out_str += "\n"
        out_str += "Datasets:\n"
        out_str += "  " + ", ".join([d.neurodata_type_def for d in self.datasets])
        out_str += "\n"

        return out_str

    def build(self) -> BuildResult:
        """
        Make the LinkML representation for this schema file

        Things that will be populated later
        - `id` (but need to have a placeholder to instantiate)
        - `version`

        """
        res = BuildResult()
        for dset in self.datasets:
            new_res = DatasetAdapter(cls=dset).build()
            if len(new_res.slots) > 0:
                pdb.set_trace()
            res += new_res
        for group in self.groups:
            new_res = GroupAdapter(cls=group).build()
            if len(new_res.slots) > 0:
                pdb.set_trace()
            res += new_res

        if (
            len(res.slots) > 0
        ):  # pragma: no cover - hard to induce this because child classes don't fuck up like this
            raise RuntimeError(
                "Generated schema in this translation can only have classes, all slots should be"
                " attributes within a class"
            )

        sch = SchemaDefinition(
            name=self.name,
            id=self.name,
            imports=[i.name if isinstance(i, SchemaAdapter) else i for i in self.imports],
            classes=res.classes,
            slots=res.slots,
            types=res.types,
            version=self.version,
            annotations=[
                {"tag": "is_namespace", "value": False},
                {"tag": "namespace", "value": self.namespace},
            ],
        )
        # every schema needs the language elements
        sch.imports.append(".".join([self.namespace, "nwb.language"]))
        return BuildResult(schemas=[sch])

    @property
    def created_classes(self) -> List[Type[Group | Dataset]]:
        """
        All the group and datasets created in this schema
        """
        if len(self._created_classes) == 0:
            self._created_classes = [
                t
                for t in self.walk_types([self.groups, self.datasets], (Group, Dataset))
                if t.neurodata_type_def is not None
            ]
        return self._created_classes

    @property
    def needed_imports(self) -> List[str]:
        """
        Classes that need to be imported from other namespaces

        TODO:
        - Need to also check classes used in links/references

        """
        type_incs = self.walk_fields(self, ("neurodata_type_inc", "target_type"))

        definitions = [c.neurodata_type_def for c in self.created_classes]
        need = [inc for inc in type_incs if inc not in definitions]
        return need
