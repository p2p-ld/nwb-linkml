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


class ImagingRetinotopyAxis1PhaseMap(ConfiguredBaseModel):
    """
    Phase response to stimulus on the first measured axis.
    """
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    unit: Optional[str] = Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]] = Field(None)
    

class ImagingRetinotopyAxis1PhaseMapArray(Arraylike):
    
    num_rows: Optional[float] = Field(None)
    num_cols: Optional[float] = Field(None)
    

class ImagingRetinotopyAxis1PowerMap(ConfiguredBaseModel):
    """
    Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.
    """
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    unit: Optional[str] = Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]] = Field(None)
    

class ImagingRetinotopyAxis1PowerMapArray(Arraylike):
    
    num_rows: Optional[float] = Field(None)
    num_cols: Optional[float] = Field(None)
    

class ImagingRetinotopyAxis2PhaseMap(ConfiguredBaseModel):
    """
    Phase response to stimulus on the second measured axis.
    """
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    unit: Optional[str] = Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]] = Field(None)
    

class ImagingRetinotopyAxis2PhaseMapArray(Arraylike):
    
    num_rows: Optional[float] = Field(None)
    num_cols: Optional[float] = Field(None)
    

class ImagingRetinotopyAxis2PowerMap(ConfiguredBaseModel):
    """
    Power response on the second measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.
    """
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    unit: Optional[str] = Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]] = Field(None)
    

class ImagingRetinotopyAxis2PowerMapArray(Arraylike):
    
    num_rows: Optional[float] = Field(None)
    num_cols: Optional[float] = Field(None)
    

class ImagingRetinotopyAxisDescriptions(ConfiguredBaseModel):
    """
    Two-element array describing the contents of the two response axis fields. Description should be something like ['altitude', 'azimuth'] or '['radius', 'theta'].
    """
    axis_descriptions: List[str] = Field(default_factory=list, description="""Two-element array describing the contents of the two response axis fields. Description should be something like ['altitude', 'azimuth'] or '['radius', 'theta'].""")
    

class ImagingRetinotopyFocalDepthImage(ConfiguredBaseModel):
    """
    Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].
    """
    bits_per_pixel: Optional[int] = Field(None, description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value.""")
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    focal_depth: Optional[float] = Field(None, description="""Focal depth offset, in meters.""")
    format: Optional[str] = Field(None, description="""Format of image. Right now only 'raw' is supported.""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], UInt16]] = Field(None)
    

class ImagingRetinotopyFocalDepthImageArray(Arraylike):
    
    num_rows: Optional[int] = Field(None)
    num_cols: Optional[int] = Field(None)
    

class ImagingRetinotopySignMap(ConfiguredBaseModel):
    """
    Sine of the angle between the direction of the gradient in axis_1 and axis_2.
    """
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]] = Field(None)
    

class ImagingRetinotopySignMapArray(Arraylike):
    
    num_rows: Optional[float] = Field(None)
    num_cols: Optional[float] = Field(None)
    

class ImagingRetinotopyVasculatureImage(ConfiguredBaseModel):
    """
    Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]
    """
    bits_per_pixel: Optional[int] = Field(None, description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value""")
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    format: Optional[str] = Field(None, description="""Format of image. Right now only 'raw' is supported.""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], UInt16]] = Field(None)
    

class ImagingRetinotopyVasculatureImageArray(Arraylike):
    
    num_rows: Optional[int] = Field(None)
    num_cols: Optional[int] = Field(None)
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
ImagingRetinotopyAxis1PhaseMap.update_forward_refs()
ImagingRetinotopyAxis1PhaseMapArray.update_forward_refs()
ImagingRetinotopyAxis1PowerMap.update_forward_refs()
ImagingRetinotopyAxis1PowerMapArray.update_forward_refs()
ImagingRetinotopyAxis2PhaseMap.update_forward_refs()
ImagingRetinotopyAxis2PhaseMapArray.update_forward_refs()
ImagingRetinotopyAxis2PowerMap.update_forward_refs()
ImagingRetinotopyAxis2PowerMapArray.update_forward_refs()
ImagingRetinotopyAxisDescriptions.update_forward_refs()
ImagingRetinotopyFocalDepthImage.update_forward_refs()
ImagingRetinotopyFocalDepthImageArray.update_forward_refs()
ImagingRetinotopySignMap.update_forward_refs()
ImagingRetinotopySignMapArray.update_forward_refs()
ImagingRetinotopyVasculatureImage.update_forward_refs()
ImagingRetinotopyVasculatureImageArray.update_forward_refs()
