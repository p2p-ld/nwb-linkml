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


from .nwb_language import (
    Arraylike
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


class SpatialSeriesData(ConfiguredBaseModel):
    """
    1-D or 2-D array storing position or direction relative to some reference frame.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. The default value is 'meters'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    array: Optional[NDArray[Shape["* num_times, 1 x, 2 x_y, 3 x_y_z"], Number]] = Field(None)
    

class SpatialSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    x: Optional[float] = Field(None)
    xy: Optional[float] = Field(None)
    xyz: Optional[float] = Field(None)
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
SpatialSeriesData.update_forward_refs()
SpatialSeriesDataArray.update_forward_refs()
