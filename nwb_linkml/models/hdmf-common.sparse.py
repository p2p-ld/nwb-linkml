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
version = "None"

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
