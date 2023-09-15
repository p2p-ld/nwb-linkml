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
version = "1.1.0"

class ConfiguredBaseModel(BaseModel,
                validate_assignment = True,
                validate_default = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


class CSRMatrix(ConfiguredBaseModel):
    """
    a compressed sparse row matrix
    """
    name:str= Field(...)
    shape:Optional[int]= Field(None, description="""the shape of this sparse matrix""")
    indices:CSRMatrixIndices= Field(..., description="""column indices""")
    indptr:CSRMatrixIndptr= Field(..., description="""index pointer""")
    data:CSRMatrixData= Field(..., description="""values in the matrix""")
    

class CSRMatrixIndices(ConfiguredBaseModel):
    """
    column indices
    """
    name:Literal["indices"]= Field("indices")
    

class CSRMatrixIndptr(ConfiguredBaseModel):
    """
    index pointer
    """
    name:Literal["indptr"]= Field("indptr")
    

class CSRMatrixData(ConfiguredBaseModel):
    """
    values in the matrix
    """
    name:Literal["data"]= Field("data")
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
CSRMatrix.model_rebuild()
CSRMatrixIndices.model_rebuild()
CSRMatrixIndptr.model_rebuild()
CSRMatrixData.model_rebuild()
    