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

class ConfiguredBaseModel(BaseModel,
                validate_assignment = True,
                validate_default = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


class GrayscaleImageArray(Arraylike):
    
    x: float = Field(...)
    y: float = Field(...)
    

class RGBImageArray(Arraylike):
    
    x: float = Field(...)
    y: float = Field(...)
    r_g_b: float = Field(...)
    

class RGBAImageArray(Arraylike):
    
    x: float = Field(...)
    y: float = Field(...)
    r_g_b_a: float = Field(...)
    

class ImageSeriesData(ConfiguredBaseModel):
    """
    Binary data representing images across frames. If data are stored in an external file, this should be an empty 3D array.
    """
    name: str = Field("data", const=True)
    array: Optional[Union[
        NDArray[Shape["* frame, * x, * y"], Number],
        NDArray[Shape["* frame, * x, * y, * z"], Number]
    ]] = Field(None)
    

class ImageSeriesDataArray(Arraylike):
    
    frame: float = Field(...)
    x: float = Field(...)
    y: float = Field(...)
    z: Optional[float] = Field(None)
    

class OpticalSeriesFieldOfView(ConfiguredBaseModel):
    """
    Width, height and depth of image, or imaged area, in meters.
    """
    name: str = Field("field_of_view", const=True)
    array: Optional[Union[
        NDArray[Shape["2 width_height"], Float32],
        NDArray[Shape["2 width_height, 3 width_height_depth"], Float32]
    ]] = Field(None)
    

class OpticalSeriesFieldOfViewArray(Arraylike):
    
    width_height: Optional[float] = Field(None)
    width_height_depth: Optional[float] = Field(None)
    

class OpticalSeriesData(ConfiguredBaseModel):
    """
    Images presented to subject, either grayscale or RGB
    """
    name: str = Field("data", const=True)
    array: Optional[Union[
        NDArray[Shape["* frame, * x, * y"], Number],
        NDArray[Shape["* frame, * x, * y, 3 r_g_b"], Number]
    ]] = Field(None)
    

class OpticalSeriesDataArray(Arraylike):
    
    frame: float = Field(...)
    x: float = Field(...)
    y: float = Field(...)
    r_g_b: Optional[float] = Field(None)
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
GrayscaleImageArray.model_rebuild()
RGBImageArray.model_rebuild()
RGBAImageArray.model_rebuild()
ImageSeriesData.model_rebuild()
ImageSeriesDataArray.model_rebuild()
OpticalSeriesFieldOfView.model_rebuild()
OpticalSeriesFieldOfViewArray.model_rebuild()
OpticalSeriesData.model_rebuild()
OpticalSeriesDataArray.model_rebuild()
    