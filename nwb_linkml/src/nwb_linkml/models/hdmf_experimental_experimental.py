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


from .hdmf_common_table import (
    VectorData
)


metamodel_version = "None"
version = "None"

class ConfiguredBaseModel(BaseModel,
                validate_assignment = True,
                validate_default = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


class EnumData(VectorData):
    """
    Data that come from a fixed set of values. A data value of i corresponds to the i-th value in the VectorData referenced by the 'elements' attribute.
    """
    name:str= Field(...)
    elements:Optional[VectorData]= Field(None, description="""Reference to the VectorData object that contains the enumerable elements""")
    description:Optional[str]= Field(None, description="""Description of what these vectors represent.""")
    array:Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]]= Field(None)
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
EnumData.model_rebuild()
    