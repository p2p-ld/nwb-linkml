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


class GrayscaleImageArray(Arraylike):
    
    x: Optional[float] = Field(None)
    y: Optional[float] = Field(None)
    

class RGBImageArray(Arraylike):
    
    x: Optional[float] = Field(None)
    y: Optional[float] = Field(None)
    r_g_b: Optional[float] = Field(None)
    

class RGBAImageArray(Arraylike):
    
    x: Optional[float] = Field(None)
    y: Optional[float] = Field(None)
    r_g_b_a: Optional[float] = Field(None)
    

class ImageSeriesData(ConfiguredBaseModel):
    """
    Binary data representing images across frames. If data are stored in an external file, this should be an empty 3D array.
    """
    array: Optional[NDArray[Shape["* frame, * x, * y, * z"], Number]] = Field(None)
    

class ImageSeriesDataArray(Arraylike):
    
    frame: float = Field(...)
    x: float = Field(...)
    y: float = Field(...)
    z: Optional[float] = Field(None)
    

class ImageSeriesDimension(ConfiguredBaseModel):
    """
    Number of pixels on x, y, (and z) axes.
    """
    dimension: Optional[List[int]] = Field(default_factory=list, description="""Number of pixels on x, y, (and z) axes.""")
    

class ImageSeriesExternalFile(ConfiguredBaseModel):
    """
    Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.
    """
    starting_frame: Optional[int] = Field(None, description="""Each external image may contain one or more consecutive frames of the full ImageSeries. This attribute serves as an index to indicate which frames each file contains, to facilitate random access. The 'starting_frame' attribute, hence, contains a list of frame numbers within the full ImageSeries of the first frame of each file listed in the parent 'external_file' dataset. Zero-based indexing is used (hence, the first element will always be zero). For example, if the 'external_file' dataset has three paths to files and the first file has 5 frames, the second file has 10 frames, and the third file has 20 frames, then this attribute will have values [0, 5, 15]. If there is a single external file that holds all of the frames of the ImageSeries (and so there is a single element in the 'external_file' dataset), then this attribute should have value [0].""")
    external_file: Optional[List[str]] = Field(default_factory=list, description="""Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.""")
    

class OpticalSeriesFieldOfView(ConfiguredBaseModel):
    """
    Width, height and depth of image, or imaged area, in meters.
    """
    array: Optional[NDArray[Shape["2 width_height, 3 width_height_depth"], Float32]] = Field(None)
    

class OpticalSeriesFieldOfViewArray(Arraylike):
    
    width_height: Optional[float] = Field(None)
    width_height_depth: Optional[float] = Field(None)
    

class OpticalSeriesData(ConfiguredBaseModel):
    """
    Images presented to subject, either grayscale or RGB
    """
    array: Optional[NDArray[Shape["* frame, * x, * y, 3 r_g_b"], Number]] = Field(None)
    

class OpticalSeriesDataArray(Arraylike):
    
    frame: float = Field(...)
    x: float = Field(...)
    y: float = Field(...)
    r_g_b: Optional[float] = Field(None)
    

class IndexSeriesData(ConfiguredBaseModel):
    """
    Index of the image (using zero-indexing) in the linked Images object.
    """
    conversion: Optional[float] = Field(None, description="""This field is unused by IndexSeries.""")
    resolution: Optional[float] = Field(None, description="""This field is unused by IndexSeries.""")
    offset: Optional[float] = Field(None, description="""This field is unused by IndexSeries.""")
    unit: Optional[str] = Field(None, description="""This field is unused by IndexSeries and has the value N/A.""")
    data: List[int] = Field(default_factory=list, description="""Index of the image (using zero-indexing) in the linked Images object.""")
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
GrayscaleImageArray.update_forward_refs()
RGBImageArray.update_forward_refs()
RGBAImageArray.update_forward_refs()
ImageSeriesData.update_forward_refs()
ImageSeriesDataArray.update_forward_refs()
ImageSeriesDimension.update_forward_refs()
ImageSeriesExternalFile.update_forward_refs()
OpticalSeriesFieldOfView.update_forward_refs()
OpticalSeriesFieldOfViewArray.update_forward_refs()
OpticalSeriesData.update_forward_refs()
OpticalSeriesDataArray.update_forward_refs()
IndexSeriesData.update_forward_refs()
