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
    DynamicTableRegion,
    VectorIndex,
    VectorData
)

from .core_nwb_image import (
    ImageSeries
)

from .nwb_language import (
    Arraylike
)

from .core_nwb_base import (
    TimeSeries
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


class TwoPhotonSeriesFieldOfView(ConfiguredBaseModel):
    """
    Width, height and depth of image, or imaged area, in meters.
    """
    array: Optional[NDArray[Shape["2 width|height, 3 width|height|depth"], Float32]] = Field(None)
    

class TwoPhotonSeriesFieldOfViewArray(Arraylike):
    
    width|height: Optional[float] = Field(None)
    width|height|depth: Optional[float] = Field(None)
    

class RoiResponseSeriesData(ConfiguredBaseModel):
    """
    Signals from ROIs.
    """
    array: Optional[NDArray[Shape["* num_times, * num_ROIs"], Number]] = Field(None)
    

class RoiResponseSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    num_ROIs: Optional[float] = Field(None)
    

class RoiResponseSeriesRois(DynamicTableRegion):
    """
    DynamicTableRegion referencing into an ROITable containing information on the ROIs stored in this timeseries.
    """
    table: Optional[DynamicTable] = Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class PlaneSegmentationImageMask(VectorData):
    """
    ROI masks for each ROI. Each image mask is the size of the original imaging plane (or volume) and members of the ROI are finite non-zero.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class PlaneSegmentationPixelMaskIndex(VectorIndex):
    """
    Index into pixel_mask.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class PlaneSegmentationVoxelMaskIndex(VectorIndex):
    """
    Index into voxel_mask.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class PlaneSegmentationReferenceImages(ConfiguredBaseModel):
    """
    Image stacks that the segmentation masks apply to.
    """
    ImageSeries: Optional[List[ImageSeries]] = Field(default_factory=list, description="""One or more image stacks that the masks apply to (can be one-element stack).""")
    

class ImagingPlaneManifold(ConfiguredBaseModel):
    """
    DEPRECATED Physical position of each pixel. 'xyz' represents the position of the pixel relative to the defined coordinate space. Deprecated in favor of origin_coords and grid_spacing.
    """
    conversion: Optional[float] = Field(None, description="""Scalar to multiply each element in data to convert it to the specified 'unit'. If the data are stored in acquisition system units or other units that require a conversion to be interpretable, multiply the data by 'conversion' to convert the data to the specified 'unit'. e.g. if the data acquisition system stores values in this object as pixels from x = -500 to 499, y = -500 to 499 that correspond to a 2 m x 2 m range, then the 'conversion' multiplier to get from raw data acquisition pixel units to meters is 2/1000.""")
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. The default value is 'meters'.""")
    array: Optional[NDArray[Shape["* height, * width, 3 x_y_z, * depth"], Float32]] = Field(None)
    

class ImagingPlaneManifoldArray(Arraylike):
    
    height: float = Field(...)
    width: float = Field(...)
    x_y_z: float = Field(...)
    depth: Optional[float] = Field(None)
    

class ImagingPlaneOriginCoords(ConfiguredBaseModel):
    """
    Physical location of the first element of the imaging plane (0, 0) for 2-D data or (0, 0, 0) for 3-D data. See also reference_frame for what the physical location is relative to (e.g., bregma).
    """
    unit: Optional[str] = Field(None, description="""Measurement units for origin_coords. The default value is 'meters'.""")
    array: Optional[NDArray[Shape["2 x_y, 3 x_y_z"], Float32]] = Field(None)
    

class ImagingPlaneOriginCoordsArray(Arraylike):
    
    x_y: Optional[float] = Field(None)
    x_y_z: Optional[float] = Field(None)
    

class ImagingPlaneGridSpacing(ConfiguredBaseModel):
    """
    Space between pixels in (x, y) or voxels in (x, y, z) directions, in the specified unit. Assumes imaging plane is a regular grid. See also reference_frame to interpret the grid.
    """
    unit: Optional[str] = Field(None, description="""Measurement units for grid_spacing. The default value is 'meters'.""")
    array: Optional[NDArray[Shape["2 x_y, 3 x_y_z"], Float32]] = Field(None)
    

class ImagingPlaneGridSpacingArray(Arraylike):
    
    x_y: Optional[float] = Field(None)
    x_y_z: Optional[float] = Field(None)
    

class CorrectedImageStackCorrected(ImageSeries):
    """
    Image stack with frames shifted to the common coordinates.
    """
    data: ImageSeriesData = Field(..., description="""Binary data representing images across frames. If data are stored in an external file, this should be an empty 3D array.""")
    dimension: Optional[ImageSeriesDimension] = Field(None, description="""Number of pixels on x, y, (and z) axes.""")
    external_file: Optional[ImageSeriesExternalFile] = Field(None, description="""Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.""")
    format: Optional[str] = Field(None, description="""Format of image. If this is 'external', then the attribute 'external_file' contains the path information to the image files. If this is 'raw', then the raw (single-channel) binary data is stored in the 'data' dataset. If this attribute is not present, then the default format='raw' case is assumed.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class CorrectedImageStackXyTranslation(TimeSeries):
    """
    Stores the x,y delta necessary to align each frame to the common coordinates, for example, to align each frame to a reference image.
    """
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    data: TimeSeriesData = Field(..., description="""Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension should always represent time. This can also be used to store binary data (e.g., image frames). This can also be a link to data stored in an external file.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
TwoPhotonSeriesFieldOfView.update_forward_refs()
TwoPhotonSeriesFieldOfViewArray.update_forward_refs()
RoiResponseSeriesData.update_forward_refs()
RoiResponseSeriesDataArray.update_forward_refs()
RoiResponseSeriesRois.update_forward_refs()
PlaneSegmentationImageMask.update_forward_refs()
PlaneSegmentationPixelMaskIndex.update_forward_refs()
PlaneSegmentationVoxelMaskIndex.update_forward_refs()
PlaneSegmentationReferenceImages.update_forward_refs()
ImagingPlaneManifold.update_forward_refs()
ImagingPlaneManifoldArray.update_forward_refs()
ImagingPlaneOriginCoords.update_forward_refs()
ImagingPlaneOriginCoordsArray.update_forward_refs()
ImagingPlaneGridSpacing.update_forward_refs()
ImagingPlaneGridSpacingArray.update_forward_refs()
CorrectedImageStackCorrected.update_forward_refs()
CorrectedImageStackXyTranslation.update_forward_refs()
