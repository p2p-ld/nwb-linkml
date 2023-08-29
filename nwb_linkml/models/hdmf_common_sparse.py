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


from .hdmf_common_sparse_include import (
    CSRMatrixData,
    CSRMatrixIndices,
    CSRMatrixIndptr
)

from .hdmf_common_base import (
    Container
)


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


class CSRMatrix(Container):
    """
    A compressed sparse row matrix. Data are stored in the standard CSR format, where column indices for row i are stored in indices[indptr[i]:indptr[i+1]] and their corresponding values are stored in data[indptr[i]:indptr[i+1]].
    """
    shape: Optional[int] = Field(None, description="""The shape (number of rows, number of columns) of this sparse matrix.""")
    indices: CSRMatrixIndices = Field(..., description="""The column indices.""")
    indptr: CSRMatrixIndptr = Field(..., description="""The row index pointer.""")
    data: CSRMatrixData = Field(..., description="""The non-zero values in the matrix.""")
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
CSRMatrix.update_forward_refs()
