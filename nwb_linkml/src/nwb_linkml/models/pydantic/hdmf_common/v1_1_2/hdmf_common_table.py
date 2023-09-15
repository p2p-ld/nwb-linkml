from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, Field
from nptyping import Shape, Float, Float32, Double, Float64, LongLong, Int64, Int, Int32, Int16, Short, Int8, UInt, UInt32, UInt16, UInt8, UInt64, Number, String, Unicode, Unicode, Unicode, String, Bool, Datetime64
from nwb_linkml.types import NDArray
import sys
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal



metamodel_version = "None"
version = "1.1.2"

class ConfiguredBaseModel(BaseModel,
                validate_assignment = True,
                validate_default = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


class Data(ConfiguredBaseModel):
    """
    An abstract data type for a dataset.
    """
    name:str= Field(...)
    

class Index(Data):
    """
    Pointers that index data values.
    """
    name:str= Field(...)
    target:Optional[Data]= Field(None, description="""Target dataset that this index applies to.""")
    

class VectorData(Data):
    """
    An n-dimensional dataset representing a column of a DynamicTable. If used without an accompanying VectorIndex, first dimension is along the rows of the DynamicTable and each step along the first dimension is a cell of the larger table. VectorData can also be used to represent a ragged array if paired with a VectorIndex. This allows for storing arrays of varying length in a single cell of the DynamicTable by indexing into this VectorData. The first vector is at VectorData[0:VectorIndex(0)+1]. The second vector is at VectorData[VectorIndex(0)+1:VectorIndex(1)+1], and so on.
    """
    name:str= Field(...)
    description:Optional[str]= Field(None, description="""Description of what these vectors represent.""")
    

class VectorIndex(Index):
    """
    Used with VectorData to encode a ragged array. An array of indices into the first dimension of the target VectorData, and forming a map between the rows of a DynamicTable and the indices of the VectorData.
    """
    name:str= Field(...)
    target:Optional[VectorData]= Field(None, description="""Reference to the target dataset that this index applies to.""")
    

class ElementIdentifiers(Data):
    """
    A list of unique identifiers for values within a dataset, e.g. rows of a DynamicTable.
    """
    name:str= Field(...)
    array:Optional[NDArray[Shape["* num_elements"], Int]]= Field(None)
    

class DynamicTableRegion(VectorData):
    """
    DynamicTableRegion provides a link from one table to an index or region of another. The `table` attribute is a link to another `DynamicTable`, indicating which table is referenced, and the data is int(s) indicating the row(s) (0-indexed) of the target array. `DynamicTableRegion`s can be used to associate rows with repeated meta-data without data duplication. They can also be used to create hierarchical relationships between multiple `DynamicTable`s. `DynamicTableRegion` objects may be paired with a `VectorIndex` object to create ragged references, so a single cell of a `DynamicTable` can reference many rows of another `DynamicTable`.
    """
    name:str= Field(...)
    table:Optional[DynamicTable]= Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description:Optional[str]= Field(None, description="""Description of what this table region points to.""")
    

class Container(ConfiguredBaseModel):
    """
    An abstract data type for a generic container storing collections of data and metadata. Base type for all data and metadata containers.
    """
    name:str= Field(...)
    

class DynamicTable(Container):
    """
    A group containing multiple datasets that are aligned on the first dimension (Currently, this requirement if left up to APIs to check and enforce). Apart from a column that contains unique identifiers for each row there are no other required datasets. Users are free to add any number of VectorData objects here. Table functionality is already supported through compound types, which is analogous to storing an array-of-structs. DynamicTable can be thought of as a struct-of-arrays. This provides an alternative structure to choose from when optimizing storage for anticipated access patterns. Additionally, this type provides a way of creating a table without having to define a compound type up front. Although this convenience may be attractive, users should think carefully about how data will be accessed. DynamicTable is more appropriate for column-centric access, whereas a dataset with a compound type would be more appropriate for row-centric access. Finally, data size should also be taken into account. For small tables, performance loss may be an acceptable trade-off for the flexibility of a DynamicTable. For example, DynamicTable was originally developed for storing trial data and spike unit metadata. Both of these use cases are expected to produce relatively small tables, so the spatial locality of multiple datasets present in a DynamicTable is not expected to have a significant performance impact. Additionally, requirements of trial and unit metadata tables are sufficiently diverse that performance implications can be overlooked in favor of usability.
    """
    name:str= Field(...)
    colnames:Optional[str]= Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description:Optional[str]= Field(None, description="""Description of what is in this dynamic table.""")
    id:List[int]= Field(default_factory=list, description="""Array of unique identifiers for the rows of this dynamic table.""")
    vector_data:Optional[List[VectorData]]= Field(default_factory=list, description="""Vector columns of this dynamic table.""")
    vector_index:Optional[List[VectorIndex]]= Field(default_factory=list, description="""Indices for the vector columns of this dynamic table.""")
    


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
    