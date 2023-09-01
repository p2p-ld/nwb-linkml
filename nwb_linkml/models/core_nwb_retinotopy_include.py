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


class ImagingRetinotopyAxis1PhaseMap(ConfiguredBaseModel):
    """
    Phase response to stimulus on the first measured axis.
    """
    name: str = Field("axis_1_phase_map", const=True)
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    unit: Optional[str] = Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]] = Field(None)
    

class ImagingRetinotopyAxis1PhaseMapArray(Arraylike):
    
    num_rows: float = Field(...)
    num_cols: float = Field(...)
    

class ImagingRetinotopyAxis1PowerMap(ConfiguredBaseModel):
    """
    Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.
    """
    name: str = Field("axis_1_power_map", const=True)
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    unit: Optional[str] = Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]] = Field(None)
    

class ImagingRetinotopyAxis1PowerMapArray(Arraylike):
    
    num_rows: float = Field(...)
    num_cols: float = Field(...)
    

class ImagingRetinotopyAxis2PhaseMap(ConfiguredBaseModel):
    """
    Phase response to stimulus on the second measured axis.
    """
    name: str = Field("axis_2_phase_map", const=True)
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    unit: Optional[str] = Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]] = Field(None)
    

class ImagingRetinotopyAxis2PhaseMapArray(Arraylike):
    
    num_rows: float = Field(...)
    num_cols: float = Field(...)
    

class ImagingRetinotopyAxis2PowerMap(ConfiguredBaseModel):
    """
    Power response on the second measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.
    """
    name: str = Field("axis_2_power_map", const=True)
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    unit: Optional[str] = Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]] = Field(None)
    

class ImagingRetinotopyAxis2PowerMapArray(Arraylike):
    
    num_rows: float = Field(...)
    num_cols: float = Field(...)
    

class ImagingRetinotopyFocalDepthImage(ConfiguredBaseModel):
    """
    Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].
    """
    name: str = Field("focal_depth_image", const=True)
    bits_per_pixel: Optional[int] = Field(None, description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value.""")
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    focal_depth: Optional[float] = Field(None, description="""Focal depth offset, in meters.""")
    format: Optional[str] = Field(None, description="""Format of image. Right now only 'raw' is supported.""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], UInt16]] = Field(None)
    

class ImagingRetinotopyFocalDepthImageArray(Arraylike):
    
    num_rows: int = Field(...)
    num_cols: int = Field(...)
    

class ImagingRetinotopySignMap(ConfiguredBaseModel):
    """
    Sine of the angle between the direction of the gradient in axis_1 and axis_2.
    """
    name: str = Field("sign_map", const=True)
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]] = Field(None)
    

class ImagingRetinotopySignMapArray(Arraylike):
    
    num_rows: float = Field(...)
    num_cols: float = Field(...)
    

class ImagingRetinotopyVasculatureImage(ConfiguredBaseModel):
    """
    Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]
    """
    name: str = Field("vasculature_image", const=True)
    bits_per_pixel: Optional[int] = Field(None, description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value""")
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    format: Optional[str] = Field(None, description="""Format of image. Right now only 'raw' is supported.""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], UInt16]] = Field(None)
    

class ImagingRetinotopyVasculatureImageArray(Arraylike):
    
    num_rows: int = Field(...)
    num_cols: int = Field(...)
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ImagingRetinotopyAxis1PhaseMap.model_rebuild()
ImagingRetinotopyAxis1PhaseMapArray.model_rebuild()
ImagingRetinotopyAxis1PowerMap.model_rebuild()
ImagingRetinotopyAxis1PowerMapArray.model_rebuild()
ImagingRetinotopyAxis2PhaseMap.model_rebuild()
ImagingRetinotopyAxis2PhaseMapArray.model_rebuild()
ImagingRetinotopyAxis2PowerMap.model_rebuild()
ImagingRetinotopyAxis2PowerMapArray.model_rebuild()
ImagingRetinotopyFocalDepthImage.model_rebuild()
ImagingRetinotopyFocalDepthImageArray.model_rebuild()
ImagingRetinotopySignMap.model_rebuild()
ImagingRetinotopySignMapArray.model_rebuild()
ImagingRetinotopyVasculatureImage.model_rebuild()
ImagingRetinotopyVasculatureImageArray.model_rebuild()
    