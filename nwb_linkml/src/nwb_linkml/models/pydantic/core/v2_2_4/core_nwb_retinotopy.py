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


from .core_nwb_base import (
    NWBDataInterface
)


metamodel_version = "None"
version = "2.2.4"

class ConfiguredBaseModel(BaseModel,
                validate_assignment = True,
                validate_default = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


class ImagingRetinotopy(NWBDataInterface):
    """
    Intrinsic signal optical imaging or widefield imaging for measuring retinotopy. Stores orthogonal maps (e.g., altitude/azimuth; radius/theta) of responses to specific stimuli and a combined polarity map from which to identify visual areas. This group does not store the raw responses imaged during retinotopic mapping or the stimuli presented, but rather the resulting phase and power maps after applying a Fourier transform on the averaged responses. Note: for data consistency, all images and arrays are stored in the format [row][column] and [row, col], which equates to [y][x]. Field of view and dimension arrays may appear backward (i.e., y before x).
    """
    name:str= Field(...)
    axis_1_phase_map:ImagingRetinotopyAxis1PhaseMap= Field(..., description="""Phase response to stimulus on the first measured axis.""")
    axis_1_power_map:Optional[ImagingRetinotopyAxis1PowerMap]= Field(None, description="""Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.""")
    axis_2_phase_map:ImagingRetinotopyAxis2PhaseMap= Field(..., description="""Phase response to stimulus on the second measured axis.""")
    axis_2_power_map:Optional[ImagingRetinotopyAxis2PowerMap]= Field(None, description="""Power response on the second measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.""")
    axis_descriptions:List[str]= Field(default_factory=list, description="""Two-element array describing the contents of the two response axis fields. Description should be something like ['altitude', 'azimuth'] or '['radius', 'theta'].""")
    focal_depth_image:Optional[ImagingRetinotopyFocalDepthImage]= Field(None, description="""Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].""")
    sign_map:Optional[ImagingRetinotopySignMap]= Field(None, description="""Sine of the angle between the direction of the gradient in axis_1 and axis_2.""")
    vasculature_image:ImagingRetinotopyVasculatureImage= Field(..., description="""Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]""")
    

class ImagingRetinotopyAxis1PhaseMap(ConfiguredBaseModel):
    """
    Phase response to stimulus on the first measured axis.
    """
    name:Literal["axis_1_phase_map"]= Field("axis_1_phase_map")
    dimension:Optional[int]= Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view:Optional[float]= Field(None, description="""Size of viewing area, in meters.""")
    unit:Optional[str]= Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array:Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]]= Field(None)
    

class ImagingRetinotopyAxis1PowerMap(ConfiguredBaseModel):
    """
    Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.
    """
    name:Literal["axis_1_power_map"]= Field("axis_1_power_map")
    dimension:Optional[int]= Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view:Optional[float]= Field(None, description="""Size of viewing area, in meters.""")
    unit:Optional[str]= Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array:Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]]= Field(None)
    

class ImagingRetinotopyAxis2PhaseMap(ConfiguredBaseModel):
    """
    Phase response to stimulus on the second measured axis.
    """
    name:Literal["axis_2_phase_map"]= Field("axis_2_phase_map")
    dimension:Optional[int]= Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view:Optional[float]= Field(None, description="""Size of viewing area, in meters.""")
    unit:Optional[str]= Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array:Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]]= Field(None)
    

class ImagingRetinotopyAxis2PowerMap(ConfiguredBaseModel):
    """
    Power response on the second measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.
    """
    name:Literal["axis_2_power_map"]= Field("axis_2_power_map")
    dimension:Optional[int]= Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view:Optional[float]= Field(None, description="""Size of viewing area, in meters.""")
    unit:Optional[str]= Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array:Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]]= Field(None)
    

class ImagingRetinotopyFocalDepthImage(ConfiguredBaseModel):
    """
    Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].
    """
    name:Literal["focal_depth_image"]= Field("focal_depth_image")
    bits_per_pixel:Optional[int]= Field(None, description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value.""")
    dimension:Optional[int]= Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view:Optional[float]= Field(None, description="""Size of viewing area, in meters.""")
    focal_depth:Optional[float]= Field(None, description="""Focal depth offset, in meters.""")
    format:Optional[str]= Field(None, description="""Format of image. Right now only 'raw' is supported.""")
    array:Optional[NDArray[Shape["* num_rows, * num_cols"], UInt16]]= Field(None)
    

class ImagingRetinotopySignMap(ConfiguredBaseModel):
    """
    Sine of the angle between the direction of the gradient in axis_1 and axis_2.
    """
    name:Literal["sign_map"]= Field("sign_map")
    dimension:Optional[int]= Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view:Optional[float]= Field(None, description="""Size of viewing area, in meters.""")
    array:Optional[NDArray[Shape["* num_rows, * num_cols"], Float32]]= Field(None)
    

class ImagingRetinotopyVasculatureImage(ConfiguredBaseModel):
    """
    Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]
    """
    name:Literal["vasculature_image"]= Field("vasculature_image")
    bits_per_pixel:Optional[int]= Field(None, description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value""")
    dimension:Optional[int]= Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view:Optional[float]= Field(None, description="""Size of viewing area, in meters.""")
    format:Optional[str]= Field(None, description="""Format of image. Right now only 'raw' is supported.""")
    array:Optional[NDArray[Shape["* num_rows, * num_cols"], UInt16]]= Field(None)
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ImagingRetinotopy.model_rebuild()
ImagingRetinotopyAxis1PhaseMap.model_rebuild()
ImagingRetinotopyAxis1PowerMap.model_rebuild()
ImagingRetinotopyAxis2PhaseMap.model_rebuild()
ImagingRetinotopyAxis2PowerMap.model_rebuild()
ImagingRetinotopyFocalDepthImage.model_rebuild()
ImagingRetinotopySignMap.model_rebuild()
ImagingRetinotopyVasculatureImage.model_rebuild()
    