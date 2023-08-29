from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, Field
from nptyping import NDArray, Shape, Float, Float32, Double, Float64, LongLong, Int64, Int, Int32, Int16, Short, Int8, UInt, UInt32, UInt16, UInt8, UInt64, Number, String, Unicode, Unicode, Unicode, String, Bool, Datetime64
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


class CSRMatrixIndices(ConfiguredBaseModel):
    """
    The column indices.
    """
    indices: List[int] = Field(default_factory=list, description="""The column indices.""")
    

class CSRMatrixIndptr(ConfiguredBaseModel):
    """
    The row index pointer.
    """
    indptr: List[int] = Field(default_factory=list, description="""The row index pointer.""")
    

class CSRMatrixData(ConfiguredBaseModel):
    """
    The non-zero values in the matrix.
    """
    data: List[Any] = Field(default_factory=list, description="""The non-zero values in the matrix.""")
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
CSRMatrixIndices.update_forward_refs()
CSRMatrixIndptr.update_forward_refs()
CSRMatrixData.update_forward_refs()
