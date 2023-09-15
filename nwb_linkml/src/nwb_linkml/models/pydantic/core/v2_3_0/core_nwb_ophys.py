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
    NWBDataInterface,
    TimeSeriesSync,
    TimeSeriesStartingTime,
    TimeSeries,
    NWBContainer
)

from .core_nwb_image import (
    ImageSeriesData,
    ImageSeries
)

from ...hdmf_common.v1_5_0.hdmf_common_table import (
    DynamicTableRegion,
    VectorIndex,
    VectorData,
    DynamicTable
)


metamodel_version = "None"
version = "2.3.0"

class ConfiguredBaseModel(BaseModel,
                validate_assignment = True,
                validate_default = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


class TwoPhotonSeries(ImageSeries):
    """
    Image stack recorded over time from 2-photon microscope.
    """
    name:str= Field(...)
    pmt_gain:Optional[float]= Field(None, description="""Photomultiplier gain.""")
    scan_line_rate:Optional[float]= Field(None, description="""Lines imaged per second. This is also stored in /general/optophysiology but is kept here as it is useful information for analysis, and so good to be stored w/ the actual data.""")
    field_of_view:Optional[TwoPhotonSeriesFieldOfView]= Field(None, description="""Width, height and depth of image, or imaged area, in meters.""")
    data:Optional[ImageSeriesData]= Field(None, description="""Binary data representing images across frames.""")
    dimension:Optional[List[int]]= Field(default_factory=list, description="""Number of pixels on x, y, (and z) axes.""")
    external_file:Optional[List[str]]= Field(default_factory=list, description="""Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.""")
    format:Optional[str]= Field(None, description="""Format of image. If this is 'external', then the attribute 'external_file' contains the path information to the image files. If this is 'raw', then the raw (single-channel) binary data is stored in the 'data' dataset. If this attribute is not present, then the default format='raw' case is assumed.""")
    description:Optional[str]= Field(None, description="""Description of the time series.""")
    comments:Optional[str]= Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time:Optional[TimeSeriesStartingTime]= Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps:Optional[List[float]]= Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control:Optional[List[int]]= Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description:Optional[List[str]]= Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync:Optional[TimeSeriesSync]= Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class TwoPhotonSeriesFieldOfView(ConfiguredBaseModel):
    """
    Width, height and depth of image, or imaged area, in meters.
    """
    name:Literal["field_of_view"]= Field("field_of_view")
    array:Optional[Union[
        NDArray[Shape["2 width_height"], Float32],
        NDArray[Shape["2 width_height, 3 width_height_depth"], Float32]
    ]]= Field(None)
    

class RoiResponseSeries(TimeSeries):
    """
    ROI responses over an imaging plane. The first dimension represents time. The second dimension, if present, represents ROIs.
    """
    name:str= Field(...)
    data:RoiResponseSeriesData= Field(..., description="""Signals from ROIs.""")
    rois:RoiResponseSeriesRois= Field(..., description="""DynamicTableRegion referencing into an ROITable containing information on the ROIs stored in this timeseries.""")
    description:Optional[str]= Field(None, description="""Description of the time series.""")
    comments:Optional[str]= Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time:Optional[TimeSeriesStartingTime]= Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps:Optional[List[float]]= Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control:Optional[List[int]]= Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description:Optional[List[str]]= Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync:Optional[TimeSeriesSync]= Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class RoiResponseSeriesData(ConfiguredBaseModel):
    """
    Signals from ROIs.
    """
    name:Literal["data"]= Field("data")
    array:Optional[Union[
        NDArray[Shape["* num_times"], Number],
        NDArray[Shape["* num_times, * num_ROIs"], Number]
    ]]= Field(None)
    

class RoiResponseSeriesRois(DynamicTableRegion):
    """
    DynamicTableRegion referencing into an ROITable containing information on the ROIs stored in this timeseries.
    """
    name:Literal["rois"]= Field("rois")
    table:Optional[DynamicTable]= Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description:Optional[str]= Field(None, description="""Description of what this table region points to.""")
    array:Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]]= Field(None)
    

class DfOverF(NWBDataInterface):
    """
    dF/F information about a region of interest (ROI). Storage hierarchy of dF/F should be the same as for segmentation (i.e., same names for ROIs and for image planes).
    """
    name:str= Field(...)
    roi_response_series:List[RoiResponseSeries]= Field(default_factory=list, description="""RoiResponseSeries object(s) containing dF/F for a ROI.""")
    

class Fluorescence(NWBDataInterface):
    """
    Fluorescence information about a region of interest (ROI). Storage hierarchy of fluorescence should be the same as for segmentation (ie, same names for ROIs and for image planes).
    """
    name:str= Field(...)
    roi_response_series:List[RoiResponseSeries]= Field(default_factory=list, description="""RoiResponseSeries object(s) containing fluorescence data for a ROI.""")
    

class ImageSegmentation(NWBDataInterface):
    """
    Stores pixels in an image that represent different regions of interest (ROIs) or masks. All segmentation for a given imaging plane is stored together, with storage for multiple imaging planes (masks) supported. Each ROI is stored in its own subgroup, with the ROI group containing both a 2D mask and a list of pixels that make up this mask. Segments can also be used for masking neuropil. If segmentation is allowed to change with time, a new imaging plane (or module) is required and ROI names should remain consistent between them.
    """
    name:str= Field(...)
    plane_segmentation:List[PlaneSegmentation]= Field(default_factory=list, description="""Results from image segmentation of a specific imaging plane.""")
    

class PlaneSegmentation(DynamicTable):
    """
    Results from image segmentation of a specific imaging plane.
    """
    name:str= Field(...)
    image_mask:Optional[PlaneSegmentationImageMask]= Field(None, description="""ROI masks for each ROI. Each image mask is the size of the original imaging plane (or volume) and members of the ROI are finite non-zero.""")
    pixel_mask_index:Optional[PlaneSegmentationPixelMaskIndex]= Field(None, description="""Index into pixel_mask.""")
    pixel_mask:Optional[List[Any]]= Field(default_factory=list, description="""Pixel masks for each ROI: a list of indices and weights for the ROI. Pixel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation""")
    voxel_mask_index:Optional[PlaneSegmentationVoxelMaskIndex]= Field(None, description="""Index into voxel_mask.""")
    voxel_mask:Optional[List[Any]]= Field(default_factory=list, description="""Voxel masks for each ROI: a list of indices and weights for the ROI. Voxel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation""")
    reference_images:Optional[List[ImageSeries]]= Field(default_factory=list, description="""Image stacks that the segmentation masks apply to.""")
    colnames:Optional[str]= Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description:Optional[str]= Field(None, description="""Description of what is in this dynamic table.""")
    id:List[int]= Field(default_factory=list, description="""Array of unique identifiers for the rows of this dynamic table.""")
    vector_data:Optional[List[VectorData]]= Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class PlaneSegmentationImageMask(VectorData):
    """
    ROI masks for each ROI. Each image mask is the size of the original imaging plane (or volume) and members of the ROI are finite non-zero.
    """
    name:Literal["image_mask"]= Field("image_mask")
    description:Optional[str]= Field(None, description="""Description of what these vectors represent.""")
    array:Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]]= Field(None)
    

class PlaneSegmentationPixelMaskIndex(VectorIndex):
    """
    Index into pixel_mask.
    """
    name:Literal["pixel_mask_index"]= Field("pixel_mask_index")
    target:Optional[VectorData]= Field(None, description="""Reference to the target dataset that this index applies to.""")
    description:Optional[str]= Field(None, description="""Description of what these vectors represent.""")
    array:Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]]= Field(None)
    

class PlaneSegmentationVoxelMaskIndex(VectorIndex):
    """
    Index into voxel_mask.
    """
    name:Literal["voxel_mask_index"]= Field("voxel_mask_index")
    target:Optional[VectorData]= Field(None, description="""Reference to the target dataset that this index applies to.""")
    description:Optional[str]= Field(None, description="""Description of what these vectors represent.""")
    array:Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]]= Field(None)
    

class ImagingPlane(NWBContainer):
    """
    An imaging plane and its metadata.
    """
    name:str= Field(...)
    description:Optional[str]= Field(None, description="""Description of the imaging plane.""")
    excitation_lambda:float= Field(..., description="""Excitation wavelength, in nm.""")
    imaging_rate:Optional[float]= Field(None, description="""Rate that images are acquired, in Hz. If the corresponding TimeSeries is present, the rate should be stored there instead.""")
    indicator:str= Field(..., description="""Calcium indicator.""")
    location:str= Field(..., description="""Location of the imaging plane. Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""")
    manifold:Optional[ImagingPlaneManifold]= Field(None, description="""DEPRECATED Physical position of each pixel. 'xyz' represents the position of the pixel relative to the defined coordinate space. Deprecated in favor of origin_coords and grid_spacing.""")
    origin_coords:Optional[ImagingPlaneOriginCoords]= Field(None, description="""Physical location of the first element of the imaging plane (0, 0) for 2-D data or (0, 0, 0) for 3-D data. See also reference_frame for what the physical location is relative to (e.g., bregma).""")
    grid_spacing:Optional[ImagingPlaneGridSpacing]= Field(None, description="""Space between pixels in (x, y) or voxels in (x, y, z) directions, in the specified unit. Assumes imaging plane is a regular grid. See also reference_frame to interpret the grid.""")
    reference_frame:Optional[str]= Field(None, description="""Describes reference frame of origin_coords and grid_spacing. For example, this can be a text description of the anatomical location and orientation of the grid defined by origin_coords and grid_spacing or the vectors needed to transform or rotate the grid to a common anatomical axis (e.g., AP/DV/ML). This field is necessary to interpret origin_coords and grid_spacing. If origin_coords and grid_spacing are not present, then this field is not required. For example, if the microscope takes 10 x 10 x 2 images, where the first value of the data matrix (index (0, 0, 0)) corresponds to (-1.2, -0.6, -2) mm relative to bregma, the spacing between pixels is 0.2 mm in x, 0.2 mm in y and 0.5 mm in z, and larger numbers in x means more anterior, larger numbers in y means more rightward, and larger numbers in z means more ventral, then enter the following -- origin_coords = (-1.2, -0.6, -2) grid_spacing = (0.2, 0.2, 0.5) reference_frame = \"Origin coordinates are relative to bregma. First dimension corresponds to anterior-posterior axis (larger index = more anterior). Second dimension corresponds to medial-lateral axis (larger index = more rightward). Third dimension corresponds to dorsal-ventral axis (larger index = more ventral).\"""")
    optical_channel:List[OpticalChannel]= Field(default_factory=list, description="""An optical channel used to record from an imaging plane.""")
    

class ImagingPlaneManifold(ConfiguredBaseModel):
    """
    DEPRECATED Physical position of each pixel. 'xyz' represents the position of the pixel relative to the defined coordinate space. Deprecated in favor of origin_coords and grid_spacing.
    """
    name:Literal["manifold"]= Field("manifold")
    conversion:Optional[float]= Field(None, description="""Scalar to multiply each element in data to convert it to the specified 'unit'. If the data are stored in acquisition system units or other units that require a conversion to be interpretable, multiply the data by 'conversion' to convert the data to the specified 'unit'. e.g. if the data acquisition system stores values in this object as pixels from x = -500 to 499, y = -500 to 499 that correspond to a 2 m x 2 m range, then the 'conversion' multiplier to get from raw data acquisition pixel units to meters is 2/1000.""")
    unit:Optional[str]= Field(None, description="""Base unit of measurement for working with the data. The default value is 'meters'.""")
    array:Optional[Union[
        NDArray[Shape["* height, * width, 3 x_y_z"], Float32],
        NDArray[Shape["* height, * width, 3 x_y_z, * depth"], Float32]
    ]]= Field(None)
    

class ImagingPlaneOriginCoords(ConfiguredBaseModel):
    """
    Physical location of the first element of the imaging plane (0, 0) for 2-D data or (0, 0, 0) for 3-D data. See also reference_frame for what the physical location is relative to (e.g., bregma).
    """
    name:Literal["origin_coords"]= Field("origin_coords")
    unit:Optional[str]= Field(None, description="""Measurement units for origin_coords. The default value is 'meters'.""")
    array:Optional[Union[
        NDArray[Shape["2 x_y"], Float32],
        NDArray[Shape["2 x_y, 3 x_y_z"], Float32]
    ]]= Field(None)
    

class ImagingPlaneGridSpacing(ConfiguredBaseModel):
    """
    Space between pixels in (x, y) or voxels in (x, y, z) directions, in the specified unit. Assumes imaging plane is a regular grid. See also reference_frame to interpret the grid.
    """
    name:Literal["grid_spacing"]= Field("grid_spacing")
    unit:Optional[str]= Field(None, description="""Measurement units for grid_spacing. The default value is 'meters'.""")
    array:Optional[Union[
        NDArray[Shape["2 x_y"], Float32],
        NDArray[Shape["2 x_y, 3 x_y_z"], Float32]
    ]]= Field(None)
    

class OpticalChannel(NWBContainer):
    """
    An optical channel used to record from an imaging plane.
    """
    name:str= Field(...)
    description:str= Field(..., description="""Description or other notes about the channel.""")
    emission_lambda:float= Field(..., description="""Emission wavelength for channel, in nm.""")
    

class MotionCorrection(NWBDataInterface):
    """
    An image stack where all frames are shifted (registered) to a common coordinate system, to account for movement and drift between frames. Note: each frame at each point in time is assumed to be 2-D (has only x & y dimensions).
    """
    name:str= Field(...)
    corrected_image_stack:List[CorrectedImageStack]= Field(default_factory=list, description="""Reuslts from motion correction of an image stack.""")
    

class CorrectedImageStack(NWBDataInterface):
    """
    Reuslts from motion correction of an image stack.
    """
    name:str= Field(...)
    corrected:ImageSeries= Field(..., description="""Image stack with frames shifted to the common coordinates.""")
    xy_translation:TimeSeries= Field(..., description="""Stores the x,y delta necessary to align each frame to the common coordinates, for example, to align each frame to a reference image.""")
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
TwoPhotonSeries.model_rebuild()
TwoPhotonSeriesFieldOfView.model_rebuild()
RoiResponseSeries.model_rebuild()
RoiResponseSeriesData.model_rebuild()
RoiResponseSeriesRois.model_rebuild()
DfOverF.model_rebuild()
Fluorescence.model_rebuild()
ImageSegmentation.model_rebuild()
PlaneSegmentation.model_rebuild()
PlaneSegmentationImageMask.model_rebuild()
PlaneSegmentationPixelMaskIndex.model_rebuild()
PlaneSegmentationVoxelMaskIndex.model_rebuild()
ImagingPlane.model_rebuild()
ImagingPlaneManifold.model_rebuild()
ImagingPlaneOriginCoords.model_rebuild()
ImagingPlaneGridSpacing.model_rebuild()
OpticalChannel.model_rebuild()
MotionCorrection.model_rebuild()
CorrectedImageStack.model_rebuild()
    