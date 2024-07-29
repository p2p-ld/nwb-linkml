from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
import numpy as np
from numpydantic import NDArray, Shape

metamodel_version = "None"
version = "1.1.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )
    hdf5_path: Optional[str] = Field(None, description="The absolute path that this object is stored in an NWB file")
    object_id: Optional[str] = Field(None, description="Unique UUID for each object")


class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key: str):
        return getattr(self.root, key)

    def __getitem__(self, key: str):
        return self.root[key]

    def __setitem__(self, key: str, value):
        self.root[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.root


NUMPYDANTIC_VERSION = "1.2.1"
linkml_meta = LinkMLMeta(
    {
        "annotations": {
            "is_namespace": {"tag": "is_namespace", "value": False},
            "namespace": {"tag": "namespace", "value": "hdmf-common"},
        },
        "default_prefix": "hdmf-common.table/",
        "id": "hdmf-common.table",
        "imports": ["hdmf-common.nwb.language"],
        "name": "hdmf-common.table",
    }
)


class Data(ConfiguredBaseModel):
    """
    An abstract data type for a dataset.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-common.table", "tree_root": True})

    name: str = Field(...)


class Index(Data):
    """
    Pointers that index data values.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-common.table", "tree_root": True})

    name: str = Field(...)
    target: Optional[Data] = Field(None, description="""Target dataset that this index applies to.""")


class VectorData(Data):
    """
    An n-dimensional dataset representing a column of a DynamicTable. If used without an accompanying VectorIndex, first dimension is along the rows of the DynamicTable and each step along the first dimension is a cell of the larger table. VectorData can also be used to represent a ragged array if paired with a VectorIndex. This allows for storing arrays of varying length in a single cell of the DynamicTable by indexing into this VectorData. The first vector is at VectorData[0:VectorIndex(0)+1]. The second vector is at VectorData[VectorIndex(0)+1:VectorIndex(1)+1], and so on.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-common.table", "tree_root": True})

    name: str = Field(...)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")


class VectorIndex(Index):
    """
    Used with VectorData to encode a ragged array. An array of indices into the first dimension of the target VectorData, and forming a map between the rows of a DynamicTable and the indices of the VectorData.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-common.table", "tree_root": True})

    name: str = Field(...)
    target: Optional[VectorData] = Field(
        None, description="""Reference to the target dataset that this index applies to."""
    )


class ElementIdentifiers(Data):
    """
    A list of unique identifiers for values within a dataset, e.g. rows of a DynamicTable.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-common.table", "tree_root": True})

    name: str = Field("element_id", json_schema_extra={"linkml_meta": {"ifabsent": "string(element_id)"}})


class DynamicTableRegion(VectorData):
    """
    DynamicTableRegion provides a link from one table to an index or region of another. The `table` attribute is a link to another `DynamicTable`, indicating which table is referenced, and the data is int(s) indicating the row(s) (0-indexed) of the target array. `DynamicTableRegion`s can be used to associate rows with repeated meta-data without data duplication. They can also be used to create hierarchical relationships between multiple `DynamicTable`s. `DynamicTableRegion` objects may be paired with a `VectorIndex` object to create ragged references, so a single cell of a `DynamicTable` can reference many rows of another `DynamicTable`.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-common.table", "tree_root": True})

    name: str = Field(...)
    table: Optional[DynamicTable] = Field(
        None, description="""Reference to the DynamicTable object that this region applies to."""
    )
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")


class Container(ConfiguredBaseModel):
    """
    An abstract data type for a generic container storing collections of data and metadata. Base type for all data and metadata containers.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-common.table", "tree_root": True})

    name: str = Field(...)


class DynamicTable(Container):
    """
    A group containing multiple datasets that are aligned on the first dimension (Currently, this requirement if left up to APIs to check and enforce). Apart from a column that contains unique identifiers for each row there are no other required datasets. Users are free to add any number of VectorData objects here. Table functionality is already supported through compound types, which is analogous to storing an array-of-structs. DynamicTable can be thought of as a struct-of-arrays. This provides an alternative structure to choose from when optimizing storage for anticipated access patterns. Additionally, this type provides a way of creating a table without having to define a compound type up front. Although this convenience may be attractive, users should think carefully about how data will be accessed. DynamicTable is more appropriate for column-centric access, whereas a dataset with a compound type would be more appropriate for row-centric access. Finally, data size should also be taken into account. For small tables, performance loss may be an acceptable trade-off for the flexibility of a DynamicTable. For example, DynamicTable was originally developed for storing trial data and spike unit metadata. Both of these use cases are expected to produce relatively small tables, so the spatial locality of multiple datasets present in a DynamicTable is not expected to have a significant performance impact. Additionally, requirements of trial and unit metadata tables are sufficiently diverse that performance implications can be overlooked in favor of usability.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-common.table", "tree_root": True})

    name: str = Field(...)
    colnames: Optional[str] = Field(
        None,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: NDArray[Shape["* num_rows"], int] = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )
    vector_data: Optional[List[VectorData]] = Field(None, description="""Vector columns of this dynamic table.""")
    vector_index: Optional[List[VectorIndex]] = Field(
        None, description="""Indices for the vector columns of this dynamic table."""
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Data.model_rebuild()
Index.model_rebuild()
VectorData.model_rebuild()
VectorIndex.model_rebuild()
ElementIdentifiers.model_rebuild()
DynamicTableRegion.model_rebuild()
Container.model_rebuild()
DynamicTable.model_rebuild()
