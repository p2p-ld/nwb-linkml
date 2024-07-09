from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import (
    Dict,
    Optional,
    Any,
    Union,
    ClassVar,
    Annotated,
    TypeVar,
    List,
    TYPE_CHECKING,
)
from pydantic import BaseModel as BaseModel, Field
from pydantic import ConfigDict, BeforeValidator

from numpydantic import Shape, NDArray
from numpydantic.dtype import *
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal
if TYPE_CHECKING:
    import numpy as np


from .hdmf_common_base import Data, Container


metamodel_version = "None"
version = "1.8.0"


class ConfiguredBaseModel(BaseModel):
    hdf5_path: Optional[str] = Field(
        None, description="The absolute path that this object is stored in an NWB file"
    )

    object_id: Optional[str] = Field(None, description="Unique UUID for each object")

    def __getitem__(self, i: slice | int) -> "np.ndarray":
        if hasattr(self, "array"):
            return self.array[i]
        else:
            return super().__getitem__(i)

    def __setitem__(self, i: slice | int, value: Any):
        if hasattr(self, "array"):
            self.array[i] = value
        else:
            super().__setitem__(i, value)


class VectorData(Data):
    """
    An n-dimensional dataset representing a column of a DynamicTable. If used without an accompanying VectorIndex, first dimension is along the rows of the DynamicTable and each step along the first dimension is a cell of the larger table. VectorData can also be used to represent a ragged array if paired with a VectorIndex. This allows for storing arrays of varying length in a single cell of the DynamicTable by indexing into this VectorData. The first vector is at VectorData[0:VectorIndex[0]]. The second vector is at VectorData[VectorIndex[0]:VectorIndex[1]], and so on.
    """

    name: str = Field(...)
    description: Optional[str] = Field(
        None, description="""Description of what these vectors represent."""
    )
    array: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class VectorIndex(VectorData):
    """
    Used with VectorData to encode a ragged array. An array of indices into the first dimension of the target VectorData, and forming a map between the rows of a DynamicTable and the indices of the VectorData. The name of the VectorIndex is expected to be the name of the target VectorData object followed by \"_index\".
    """

    name: str = Field(...)
    target: Optional[str] = Field(
        None,
        description="""Reference to the target dataset that this index applies to.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of what these vectors represent."""
    )
    array: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class ElementIdentifiers(Data):
    """
    A list of unique identifiers for values within a dataset, e.g. rows of a DynamicTable.
    """

    name: str = Field("element_id")


class DynamicTableRegion(VectorData):
    """
    DynamicTableRegion provides a link from one table to an index or region of another. The `table` attribute is a link to another `DynamicTable`, indicating which table is referenced, and the data is int(s) indicating the row(s) (0-indexed) of the target array. `DynamicTableRegion`s can be used to associate rows with repeated meta-data without data duplication. They can also be used to create hierarchical relationships between multiple `DynamicTable`s. `DynamicTableRegion` objects may be paired with a `VectorIndex` object to create ragged references, so a single cell of a `DynamicTable` can reference many rows of another `DynamicTable`.
    """

    name: str = Field(...)
    table: Optional[str] = Field(
        None,
        description="""Reference to the DynamicTable object that this region applies to.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of what this table region points to."""
    )
    array: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class DynamicTable(Container):
    """
    A group containing multiple datasets that are aligned on the first dimension (Currently, this requirement if left up to APIs to check and enforce). These datasets represent different columns in the table. Apart from a column that contains unique identifiers for each row, there are no other required datasets. Users are free to add any number of custom VectorData objects (columns) here. DynamicTable also supports ragged array columns, where each element can be of a different size. To add a ragged array column, use a VectorIndex type to index the corresponding VectorData type. See documentation for VectorData and VectorIndex for more details. Unlike a compound data type, which is analogous to storing an array-of-structs, a DynamicTable can be thought of as a struct-of-arrays. This provides an alternative structure to choose from when optimizing storage for anticipated access patterns. Additionally, this type provides a way of creating a table without having to define a compound type up front. Although this convenience may be attractive, users should think carefully about how data will be accessed. DynamicTable is more appropriate for column-centric access, whereas a dataset with a compound type would be more appropriate for row-centric access. Finally, data size should also be taken into account. For small tables, performance loss may be an acceptable trade-off for the flexibility of a DynamicTable.
    """

    name: str = Field(...)
    colnames: Optional[str] = Field(
        None,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of what is in this dynamic table."""
    )
    id: NDArray[Shape["* num_rows"], int] = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
    )
    vector_data: Optional[List[str] | str] = Field(
        default_factory=list,
        description="""Vector columns, including index columns, of this dynamic table.""",
    )


class AlignedDynamicTable(DynamicTable):
    """
    DynamicTable container that supports storing a collection of sub-tables. Each sub-table is a DynamicTable itself that is aligned with the main table by row index. I.e., all DynamicTables stored in this group MUST have the same number of rows. This type effectively defines a 2-level table in which the main data is stored in the main table implemented by this type and additional columns of the table are grouped into categories, with each category being represented by a separate DynamicTable stored within the group.
    """

    children: Optional[List[Union[BaseModel, DynamicTable]] | Union[BaseModel, DynamicTable]] = (
        Field(default_factory=dict)
    )
    name: str = Field(...)
    colnames: Optional[str] = Field(
        None,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of what is in this dynamic table."""
    )
    id: NDArray[Shape["* num_rows"], int] = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
    )
    vector_data: Optional[List[str] | str] = Field(
        default_factory=list,
        description="""Vector columns, including index columns, of this dynamic table.""",
    )
