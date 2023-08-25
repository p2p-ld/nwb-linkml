from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, Field
import sys
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


metamodel_version = "None"
version = "1.8.0"

class WeakRefShimBaseModel(BaseModel):
   __slots__ = '__weakref__'

class ConfiguredBaseModel(WeakRefShimBaseModel,
                validate_assignment = True,
                validate_all = True,
                underscore_attrs_are_private = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


class FlatDType(str, Enum):
    
    
    float = "float"
    
    float32 = "float32"
    
    double = "double"
    
    float64 = "float64"
    
    long = "long"
    
    int64 = "int64"
    
    int = "int"
    
    int32 = "int32"
    
    int16 = "int16"
    
    short = "short"
    
    int8 = "int8"
    
    uint = "uint"
    
    uint32 = "uint32"
    
    uint16 = "uint16"
    
    uint8 = "uint8"
    
    uint64 = "uint64"
    
    numeric = "numeric"
    
    text = "text"
    
    utf = "utf"
    
    utf8 = "utf8"
    
    utf_8 = "utf_8"
    
    ascii = "ascii"
    
    bool = "bool"
    
    isodatetime = "isodatetime"
    
    

class CSRMatrixIndices(ConfiguredBaseModel):
    """
    The column indices.
    """
    array: Optional[CSRMatrixIndicesArray] = Field(None)
    

class CSRMatrixIndptr(ConfiguredBaseModel):
    """
    The row index pointer.
    """
    array: Optional[CSRMatrixIndptrArray] = Field(None)
    

class CSRMatrixData(ConfiguredBaseModel):
    """
    The non-zero values in the matrix.
    """
    array: Optional[CSRMatrixDataArray] = Field(None)
    

class Arraylike(ConfiguredBaseModel):
    """
    Container for arraylike information held in the dims, shape, and dtype properties.this is a special case to be interpreted by downstream i/o. this class has no slotsand is abstract by default.- Each slot within a subclass indicates a possible dimension.- Only dimensions that are present in all the dimension specifiers in the  original schema are required.- Shape requirements are indicated using max/min cardinalities on the slot.
    """
    None
    

class CSRMatrixIndicesArray(Arraylike):
    
    number_of_non_zero_values: int = Field(...)
    

class CSRMatrixIndptrArray(Arraylike):
    
    number_of_rows_in_the_matrix_+_1: int = Field(...)
    

class CSRMatrixDataArray(Arraylike):
    
    number_of_non_zero_values: Any = Field(...)
    

class Data(ConfiguredBaseModel):
    """
    An abstract data type for a dataset.
    """
    None
    

class Container(ConfiguredBaseModel):
    """
    An abstract data type for a group storing collections of data and metadata. Base type for all data and metadata containers.
    """
    None
    

class CSRMatrix(Container):
    """
    A compressed sparse row matrix. Data are stored in the standard CSR format, where column indices for row i are stored in indices[indptr[i]:indptr[i+1]] and their corresponding values are stored in data[indptr[i]:indptr[i+1]].
    """
    shape: Optional[int] = Field(None, description="""The shape (number of rows, number of columns) of this sparse matrix.""")
    indices: CSRMatrixIndices = Field(..., description="""The column indices.""")
    indptr: CSRMatrixIndptr = Field(..., description="""The row index pointer.""")
    data: CSRMatrixData = Field(..., description="""The non-zero values in the matrix.""")
    

class SimpleMultiContainer(Container):
    """
    A simple Container for holding onto multiple containers.
    """
    Data: Optional[List[Data]] = Field(default_factory=list, description="""Data objects held within this SimpleMultiContainer.""")
    Container: Optional[List[Container]] = Field(default_factory=list, description="""Container objects held within this SimpleMultiContainer.""")
    

class VectorData(Data):
    """
    An n-dimensional dataset representing a column of a DynamicTable. If used without an accompanying VectorIndex, first dimension is along the rows of the DynamicTable and each step along the first dimension is a cell of the larger table. VectorData can also be used to represent a ragged array if paired with a VectorIndex. This allows for storing arrays of varying length in a single cell of the DynamicTable by indexing into this VectorData. The first vector is at VectorData[0:VectorIndex[0]]. The second vector is at VectorData[VectorIndex[0]:VectorIndex[1]], and so on.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class VectorDataArray(Arraylike):
    
    dim0: Any = Field(...)
    dim1: Optional[Any] = Field(None)
    dim2: Optional[Any] = Field(None)
    dim3: Optional[Any] = Field(None)
    

class VectorIndex(VectorData):
    """
    Used with VectorData to encode a ragged array. An array of indices into the first dimension of the target VectorData, and forming a map between the rows of a DynamicTable and the indices of the VectorData. The name of the VectorIndex is expected to be the name of the target VectorData object followed by \"_index\".
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class VectorIndexArray(Arraylike):
    
    num_rows: int = Field(...)
    

class ElementIdentifiers(Data):
    """
    A list of unique identifiers for values within a dataset, e.g. rows of a DynamicTable.
    """
    array: Optional[ElementIdentifiersArray] = Field(None)
    

class ElementIdentifiersArray(Arraylike):
    
    num_elements: int = Field(...)
    

class DynamicTableRegion(VectorData):
    """
    DynamicTableRegion provides a link from one table to an index or region of another. The `table` attribute is a link to another `DynamicTable`, indicating which table is referenced, and the data is int(s) indicating the row(s) (0-indexed) of the target array. `DynamicTableRegion`s can be used to associate rows with repeated meta-data without data duplication. They can also be used to create hierarchical relationships between multiple `DynamicTable`s. `DynamicTableRegion` objects may be paired with a `VectorIndex` object to create ragged references, so a single cell of a `DynamicTable` can reference many rows of another `DynamicTable`.
    """
    table: Optional[DynamicTable] = Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class DynamicTableRegionArray(Arraylike):
    
    num_rows: int = Field(...)
    

class DynamicTable(Container):
    """
    A group containing multiple datasets that are aligned on the first dimension (Currently, this requirement if left up to APIs to check and enforce). These datasets represent different columns in the table. Apart from a column that contains unique identifiers for each row, there are no other required datasets. Users are free to add any number of custom VectorData objects (columns) here. DynamicTable also supports ragged array columns, where each element can be of a different size. To add a ragged array column, use a VectorIndex type to index the corresponding VectorData type. See documentation for VectorData and VectorIndex for more details. Unlike a compound data type, which is analogous to storing an array-of-structs, a DynamicTable can be thought of as a struct-of-arrays. This provides an alternative structure to choose from when optimizing storage for anticipated access patterns. Additionally, this type provides a way of creating a table without having to define a compound type up front. Although this convenience may be attractive, users should think carefully about how data will be accessed. DynamicTable is more appropriate for column-centric access, whereas a dataset with a compound type would be more appropriate for row-centric access. Finally, data size should also be taken into account. For small tables, performance loss may be an acceptable trade-off for the flexibility of a DynamicTable.
    """
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class DynamicTableId(ElementIdentifiers):
    """
    Array of unique identifiers for the rows of this dynamic table.
    """
    array: Optional[DynamicTableIdArray] = Field(None)
    

class DynamicTableIdArray(Arraylike):
    
    num_rows: int = Field(...)
    

class AlignedDynamicTable(DynamicTable):
    """
    DynamicTable container that supports storing a collection of sub-tables. Each sub-table is a DynamicTable itself that is aligned with the main table by row index. I.e., all DynamicTables stored in this group MUST have the same number of rows. This type effectively defines a 2-level table in which the main data is stored in the main table implemented by this type and additional columns of the table are grouped into categories, with each category being represented by a separate DynamicTable stored within the group.
    """
    categories: Optional[str] = Field(None, description="""The names of the categories in this AlignedDynamicTable. Each category is represented by one DynamicTable stored in the parent group. This attribute should be used to specify an order of categories and the category names must match the names of the corresponding DynamicTable in the group.""")
    DynamicTable: Optional[List[DynamicTable]] = Field(default_factory=list, description="""A DynamicTable representing a particular category for columns in the AlignedDynamicTable parent container. The table MUST be aligned with (i.e., have the same number of rows) as all other DynamicTables stored in the AlignedDynamicTable parent container. The name of the category is given by the name of the DynamicTable and its description by the description attribute of the DynamicTable.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
CSRMatrixIndices.update_forward_refs()
CSRMatrixIndptr.update_forward_refs()
CSRMatrixData.update_forward_refs()
Arraylike.update_forward_refs()
CSRMatrixIndicesArray.update_forward_refs()
CSRMatrixIndptrArray.update_forward_refs()
CSRMatrixDataArray.update_forward_refs()
Data.update_forward_refs()
Container.update_forward_refs()
CSRMatrix.update_forward_refs()
SimpleMultiContainer.update_forward_refs()
VectorData.update_forward_refs()
VectorDataArray.update_forward_refs()
VectorIndex.update_forward_refs()
VectorIndexArray.update_forward_refs()
ElementIdentifiers.update_forward_refs()
ElementIdentifiersArray.update_forward_refs()
DynamicTableRegion.update_forward_refs()
DynamicTableRegionArray.update_forward_refs()
DynamicTable.update_forward_refs()
DynamicTableId.update_forward_refs()
DynamicTableIdArray.update_forward_refs()
AlignedDynamicTable.update_forward_refs()
