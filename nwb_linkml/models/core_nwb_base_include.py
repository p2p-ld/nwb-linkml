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

# from .core_nwb_base import (
#     ImageReferences,
#     Image
# )


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


class ImageArray(Arraylike):
    
    x: float = Field(...)
    y: float = Field(...)
    r_g_b: Optional[float] = Field(None)
    r_g_b_a: Optional[float] = Field(None)
    

# class ImageReferencesArray(Arraylike):
#
#     num_images: Image = Field(...)
    

class TimeSeriesData(ConfiguredBaseModel):
    """
    Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension should always represent time. This can also be used to store binary data (e.g., image frames). This can also be a link to data stored in an external file.
    """
    conversion: Optional[float] = Field(None, description="""Scalar to multiply each element in data to convert it to the specified 'unit'. If the data are stored in acquisition system units or other units that require a conversion to be interpretable, multiply the data by 'conversion' to convert the data to the specified 'unit'. e.g. if the data acquisition system stores values in this object as signed 16-bit integers (int16 range -32,768 to 32,767) that correspond to a 5V range (-2.5V to 2.5V), and the data acquisition system gain is 8000X, then the 'conversion' multiplier to get from raw data acquisition values to recorded volts is 2.5/32768/8000 = 9.5367e-9.""")
    offset: Optional[float] = Field(None, description="""Scalar to add to the data after scaling by 'conversion' to finalize its coercion to the specified 'unit'. Two common examples of this include (a) data stored in an unsigned type that requires a shift after scaling to re-center the data, and (b) specialized recording devices that naturally cause a scalar offset with respect to the true units.""")
    resolution: Optional[float] = Field(None, description="""Smallest meaningful difference between values in data, stored in the specified by unit, e.g., the change in value of the least significant bit, or a larger number if signal noise is known to be present. If unknown, use -1.0.""")
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    continuity: Optional[str] = Field(None, description="""Optionally describe the continuity of the data. Can be \"continuous\", \"instantaneous\", or \"step\". For example, a voltage trace would be \"continuous\", because samples are recorded from a continuous process. An array of lick times would be \"instantaneous\", because the data represents distinct moments in time. Times of image presentations would be \"step\" because the picture remains the same until the next timepoint. This field is optional, but is useful in providing information about the underlying data. It may inform the way this data is interpreted, the way it is visualized, and what analysis methods are applicable.""")
    array: Optional[NDArray[Shape["* num_times, ..."], Number]] = Field(None)
    

class TimeSeriesDataArray(Arraylike):
    
    num_times: Any = Field(...)
    num_DIM2: Optional[Any] = Field(None)
    num_DIM3: Optional[Any] = Field(None)
    num_DIM4: Optional[Any] = Field(None)
    

class TimeSeriesStartingTime(ConfiguredBaseModel):
    """
    Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.
    """
    rate: Optional[float] = Field(None, description="""Sampling rate, in Hz.""")
    unit: Optional[str] = Field(None, description="""Unit of measurement for time, which is fixed to 'seconds'.""")
    

class TimeSeriesTimestamps(ConfiguredBaseModel):
    """
    Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.
    """
    interval: Optional[int] = Field(None, description="""Value is '1'""")
    unit: Optional[str] = Field(None, description="""Unit of measurement for timestamps, which is fixed to 'seconds'.""")
    timestamps: Optional[List[float]] = Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    

class TimeSeriesControl(ConfiguredBaseModel):
    """
    Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.
    """
    control: Optional[List[int]] = Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    

class TimeSeriesControlDescription(ConfiguredBaseModel):
    """
    Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.
    """
    control_description: Optional[List[str]] = Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    

class TimeSeriesSync(ConfiguredBaseModel):
    """
    Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.
    """
    None
    

# class ImagesOrderOfImages(ImageReferences):
#     """
#     Ordered dataset of references to Image objects stored in the parent group. Each Image object in the Images group should be stored once and only once, so the dataset should have the same length as the number of images.
#     """
#     array: Optional[List[Image] | Image] = Field(None)
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
ImageArray.update_forward_refs()
# ImageReferencesArray.update_forward_refs()
TimeSeriesData.update_forward_refs()
TimeSeriesDataArray.update_forward_refs()
TimeSeriesStartingTime.update_forward_refs()
TimeSeriesTimestamps.update_forward_refs()
TimeSeriesControl.update_forward_refs()
TimeSeriesControlDescription.update_forward_refs()
TimeSeriesSync.update_forward_refs()
# ImagesOrderOfImages.update_forward_refs()
