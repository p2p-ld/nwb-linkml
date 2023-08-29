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


from .core_nwb_base_include import (
    TimeSeriesSync,
    TimeSeriesControlDescription,
    # ImageReferencesArray,
    ImageArray,
    TimeSeriesControl,
    TimeSeriesData,
    # ImagesOrderOfImages,
    TimeSeriesTimestamps,
    TimeSeriesStartingTime
)

from .hdmf_common_base import (
    Container,
    Data
)

# from .hdmf_common_table import (
#     DynamicTable,
#     VectorData
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


class NWBData(Data):
    """
    An abstract data type for a dataset.
    """
    None
    

# class TimeSeriesReferenceVectorData(VectorData):
#     """
#     Column storing references to a TimeSeries (rows). For each TimeSeries this VectorData column stores the start_index and count to indicate the range in time to be selected as well as an object reference to the TimeSeries.
#     """
#     description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
#     array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]] = Field(None)
#

class Image(NWBData):
    """
    An abstract data type for an image. Shape can be 2-D (x, y), or 3-D where the third dimension can have three or four elements, e.g. (x, y, (r, g, b)) or (x, y, (r, g, b, a)).
    """
    resolution: Optional[float] = Field(None, description="""Pixel resolution of the image, in pixels per centimeter.""")
    description: Optional[str] = Field(None, description="""Description of the image.""")
    array: Optional[NDArray[Shape["* x, * y, 3 r_g_b, 4 r_g_b_a"], Number]] = Field(None)
    

# class ImageReferences(NWBData):
#     """
#     Ordered dataset of references to Image objects.
#     """
#     array: Optional[List[Image] | Image] = Field(None)
#

class NWBContainer(Container):
    """
    An abstract data type for a generic container storing collections of data and metadata. Base type for all data and metadata containers.
    """
    None
    

class NWBDataInterface(NWBContainer):
    """
    An abstract data type for a generic container storing collections of data, as opposed to metadata.
    """
    None
    

class TimeSeries(NWBDataInterface):
    """
    General purpose time series.
    """
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    data: TimeSeriesData = Field(..., description="""Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension should always represent time. This can also be used to store binary data (e.g., image frames). This can also be a link to data stored in an external file.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

# class ProcessingModule(NWBContainer):
#     """
#     A collection of processed data.
#     """
#     description: Optional[str] = Field(None, description="""Description of this collection of processed data.""")
#     NWBDataInterface: Optional[List[NWBDataInterface]] = Field(default_factory=list, description="""Data objects stored in this collection.""")
#     DynamicTable: Optional[List[DynamicTable]] = Field(default_factory=list, description="""Tables stored in this collection.""")
#

# class Images(NWBDataInterface):
#     """
#     A collection of images with an optional way to specify the order of the images using the \"order_of_images\" dataset. An order must be specified if the images are referenced by index, e.g., from an IndexSeries.
#     """
#     description: Optional[str] = Field(None, description="""Description of this collection of images.""")
#     Image: List[Image] = Field(default_factory=list, description="""Images stored in this collection.""")
#     order_of_images: Optional[ImagesOrderOfImages] = Field(None, description="""Ordered dataset of references to Image objects stored in the parent group. Each Image object in the Images group should be stored once and only once, so the dataset should have the same length as the number of images.""")
#


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
NWBData.update_forward_refs()
# TimeSeriesReferenceVectorData.update_forward_refs()
Image.update_forward_refs()
# ImageReferences.update_forward_refs()
NWBContainer.update_forward_refs()
NWBDataInterface.update_forward_refs()
TimeSeries.update_forward_refs()
# ProcessingModule.update_forward_refs()
# Images.update_forward_refs()
