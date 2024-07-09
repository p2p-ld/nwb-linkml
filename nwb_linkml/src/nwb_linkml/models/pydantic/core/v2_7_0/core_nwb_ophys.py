from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import (
    Dict,
    Optional,
    Any,
    Union,
    ClassVar,
    Annotated,
    TypeVar,
    List,
    TYPE_CHECKING,
)
from pydantic import BaseModel as BaseModel, Field
from pydantic import ConfigDict, BeforeValidator

from numpydantic import Shape, NDArray
from numpydantic.dtype import *
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal
if TYPE_CHECKING:
    import numpy as np


from .core_nwb_base import (
    TimeSeries,
    TimeSeriesSync,
    NWBDataInterface,
    TimeSeriesStartingTime,
    NWBContainer,
)

from ...hdmf_common.v1_8_0.hdmf_common_table import (
    DynamicTableRegion,
    DynamicTable,
    VectorData,
    VectorIndex,
)

from .core_nwb_image import ImageSeries, ImageSeriesExternalFile


metamodel_version = "None"
version = "2.7.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="allow",
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )
    hdf5_path: Optional[str] = Field(
        None, description="The absolute path that this object is stored in an NWB file"
    )

    object_id: Optional[str] = Field(None, description="Unique UUID for each object")

    def __getitem__(self, i: slice | int) -> "np.ndarray":
        if hasattr(self, "array"):
            return self.array[i]
        else:
            return super().__getitem__(i)

    def __setitem__(self, i: slice | int, value: Any):
        if hasattr(self, "array"):
            self.array[i] = value
        else:
            super().__setitem__(i, value)


class LinkML_Meta(BaseModel):
    """Extra LinkML Metadata stored as a class attribute"""

    tree_root: bool = False


class OnePhotonSeries(ImageSeries):
    """
    Image stack recorded over time from 1-photon microscope.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    pmt_gain: Optional[float] = Field(None, description="""Photomultiplier gain.""")
    scan_line_rate: Optional[float] = Field(
        None,
        description="""Lines imaged per second. This is also stored in /general/optophysiology but is kept here as it is useful information for analysis, and so good to be stored w/ the actual data.""",
    )
    exposure_time: Optional[float] = Field(
        None,
        description="""Exposure time of the sample; often the inverse of the frequency.""",
    )
    binning: Optional[int] = Field(
        None,
        description="""Amount of pixels combined into 'bins'; could be 1, 2, 4, 8, etc.""",
    )
    power: Optional[float] = Field(
        None, description="""Power of the excitation in mW, if known."""
    )
    intensity: Optional[float] = Field(
        None, description="""Intensity of the excitation in mW/mm^2, if known."""
    )
    data: Union[
        NDArray[Shape["* frame, * x, * y"], float],
        NDArray[Shape["* frame, * x, * y, * z"], float],
    ] = Field(
        ...,
        description="""Binary data representing images across frames. If data are stored in an external file, this should be an empty 3D array.""",
    )
    dimension: Optional[NDArray[Shape["* rank"], int]] = Field(
        None, description="""Number of pixels on x, y, (and z) axes."""
    )
    external_file: Optional[str] = Field(
        None,
        description="""Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.""",
    )
    format: Optional[str] = Field(
        None,
        description="""Format of image. If this is 'external', then the attribute 'external_file' contains the path information to the image files. If this is 'raw', then the raw (single-channel) binary data is stored in the 'data' dataset. If this attribute is not present, then the default format='raw' case is assumed.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of the time series."""
    )
    comments: Optional[str] = Field(
        None,
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
    )
    starting_time: Optional[str] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[NDArray[Shape["* num_times"], float]] = Field(
        None,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
    )
    control: Optional[NDArray[Shape["* num_times"], int]] = Field(
        None,
        description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""",
    )
    control_description: Optional[NDArray[Shape["* num_control_values"], str]] = Field(
        None,
        description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""",
    )
    sync: Optional[str] = Field(
        None,
        description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""",
    )


class TwoPhotonSeries(ImageSeries):
    """
    Image stack recorded over time from 2-photon microscope.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    pmt_gain: Optional[float] = Field(None, description="""Photomultiplier gain.""")
    scan_line_rate: Optional[float] = Field(
        None,
        description="""Lines imaged per second. This is also stored in /general/optophysiology but is kept here as it is useful information for analysis, and so good to be stored w/ the actual data.""",
    )
    field_of_view: Optional[
        Union[
            NDArray[Shape["2 width_height"], float],
            NDArray[Shape["3 width_height_depth"], float],
        ]
    ] = Field(
        None,
        description="""Width, height and depth of image, or imaged area, in meters.""",
    )
    data: Union[
        NDArray[Shape["* frame, * x, * y"], float],
        NDArray[Shape["* frame, * x, * y, * z"], float],
    ] = Field(
        ...,
        description="""Binary data representing images across frames. If data are stored in an external file, this should be an empty 3D array.""",
    )
    dimension: Optional[NDArray[Shape["* rank"], int]] = Field(
        None, description="""Number of pixels on x, y, (and z) axes."""
    )
    external_file: Optional[str] = Field(
        None,
        description="""Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.""",
    )
    format: Optional[str] = Field(
        None,
        description="""Format of image. If this is 'external', then the attribute 'external_file' contains the path information to the image files. If this is 'raw', then the raw (single-channel) binary data is stored in the 'data' dataset. If this attribute is not present, then the default format='raw' case is assumed.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of the time series."""
    )
    comments: Optional[str] = Field(
        None,
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
    )
    starting_time: Optional[str] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[NDArray[Shape["* num_times"], float]] = Field(
        None,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
    )
    control: Optional[NDArray[Shape["* num_times"], int]] = Field(
        None,
        description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""",
    )
    control_description: Optional[NDArray[Shape["* num_control_values"], str]] = Field(
        None,
        description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""",
    )
    sync: Optional[str] = Field(
        None,
        description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""",
    )


class RoiResponseSeries(TimeSeries):
    """
    ROI responses over an imaging plane. The first dimension represents time. The second dimension, if present, represents ROIs.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    data: Union[
        NDArray[Shape["* num_times"], float],
        NDArray[Shape["* num_times, * num_rois"], float],
    ] = Field(..., description="""Signals from ROIs.""")
    rois: str = Field(
        ...,
        description="""DynamicTableRegion referencing into an ROITable containing information on the ROIs stored in this timeseries.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of the time series."""
    )
    comments: Optional[str] = Field(
        None,
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
    )
    starting_time: Optional[str] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[NDArray[Shape["* num_times"], float]] = Field(
        None,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
    )
    control: Optional[NDArray[Shape["* num_times"], int]] = Field(
        None,
        description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""",
    )
    control_description: Optional[NDArray[Shape["* num_control_values"], str]] = Field(
        None,
        description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""",
    )
    sync: Optional[str] = Field(
        None,
        description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""",
    )


class RoiResponseSeriesRois(DynamicTableRegion):
    """
    DynamicTableRegion referencing into an ROITable containing information on the ROIs stored in this timeseries.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["rois"] = Field("rois")
    table: Optional[str] = Field(
        None,
        description="""Reference to the DynamicTable object that this region applies to.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of what this table region points to."""
    )
    array: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class DfOverF(NWBDataInterface):
    """
    dF/F information about a region of interest (ROI). Storage hierarchy of dF/F should be the same as for segmentation (i.e., same names for ROIs and for image planes).
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    children: Optional[List[RoiResponseSeries] | RoiResponseSeries] = Field(
        default_factory=dict
    )
    name: str = Field(...)


class Fluorescence(NWBDataInterface):
    """
    Fluorescence information about a region of interest (ROI). Storage hierarchy of fluorescence should be the same as for segmentation (ie, same names for ROIs and for image planes).
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    children: Optional[List[RoiResponseSeries] | RoiResponseSeries] = Field(
        default_factory=dict
    )
    name: str = Field(...)


class ImageSegmentation(NWBDataInterface):
    """
    Stores pixels in an image that represent different regions of interest (ROIs) or masks. All segmentation for a given imaging plane is stored together, with storage for multiple imaging planes (masks) supported. Each ROI is stored in its own subgroup, with the ROI group containing both a 2D mask and a list of pixels that make up this mask. Segments can also be used for masking neuropil. If segmentation is allowed to change with time, a new imaging plane (or module) is required and ROI names should remain consistent between them.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    children: Optional[List[PlaneSegmentation] | PlaneSegmentation] = Field(
        default_factory=dict
    )
    name: str = Field(...)


class PlaneSegmentation(DynamicTable):
    """
    Results from image segmentation of a specific imaging plane.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    image_mask: Optional[
        Union[
            NDArray[Shape["* num_roi, * num_x, * num_y"], Any],
            NDArray[Shape["* num_roi, * num_x, * num_y, * num_z"], Any],
        ]
    ] = Field(
        None,
        description="""ROI masks for each ROI. Each image mask is the size of the original imaging plane (or volume) and members of the ROI are finite non-zero.""",
    )
    pixel_mask_index: Optional[str] = Field(
        None, description="""Index into pixel_mask."""
    )
    pixel_mask: Optional[str] = Field(
        None,
        description="""Pixel masks for each ROI: a list of indices and weights for the ROI. Pixel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation""",
    )
    voxel_mask_index: Optional[str] = Field(
        None, description="""Index into voxel_mask."""
    )
    voxel_mask: Optional[str] = Field(
        None,
        description="""Voxel masks for each ROI: a list of indices and weights for the ROI. Voxel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation""",
    )
    reference_images: Optional[List[ImageSeries] | ImageSeries] = Field(
        default_factory=dict,
        description="""Image stacks that the segmentation masks apply to.""",
    )
    colnames: Optional[str] = Field(
        None,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of what is in this dynamic table."""
    )
    id: NDArray[Shape["* num_rows"], int] = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
    )
    vector_data: Optional[List[str] | str] = Field(
        default_factory=list,
        description="""Vector columns, including index columns, of this dynamic table.""",
    )


class PlaneSegmentationPixelMaskIndex(VectorIndex):
    """
    Index into pixel_mask.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["pixel_mask_index"] = Field("pixel_mask_index")
    target: Optional[str] = Field(
        None,
        description="""Reference to the target dataset that this index applies to.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of what these vectors represent."""
    )
    array: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class PlaneSegmentationPixelMask(VectorData):
    """
    Pixel masks for each ROI: a list of indices and weights for the ROI. Pixel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["pixel_mask"] = Field("pixel_mask")
    x: Optional[int] = Field(None, description="""Pixel x-coordinate.""")
    y: Optional[int] = Field(None, description="""Pixel y-coordinate.""")
    weight: Optional[float] = Field(None, description="""Weight of the pixel.""")
    description: Optional[str] = Field(
        None, description="""Description of what these vectors represent."""
    )
    array: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class PlaneSegmentationVoxelMaskIndex(VectorIndex):
    """
    Index into voxel_mask.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["voxel_mask_index"] = Field("voxel_mask_index")
    target: Optional[str] = Field(
        None,
        description="""Reference to the target dataset that this index applies to.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of what these vectors represent."""
    )
    array: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class PlaneSegmentationVoxelMask(VectorData):
    """
    Voxel masks for each ROI: a list of indices and weights for the ROI. Voxel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["voxel_mask"] = Field("voxel_mask")
    x: Optional[int] = Field(None, description="""Voxel x-coordinate.""")
    y: Optional[int] = Field(None, description="""Voxel y-coordinate.""")
    z: Optional[int] = Field(None, description="""Voxel z-coordinate.""")
    weight: Optional[float] = Field(None, description="""Weight of the voxel.""")
    description: Optional[str] = Field(
        None, description="""Description of what these vectors represent."""
    )
    array: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class ImagingPlane(NWBContainer):
    """
    An imaging plane and its metadata.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    children: Optional[List[OpticalChannel] | OpticalChannel] = Field(
        default_factory=dict
    )
    name: str = Field(...)


class OpticalChannel(NWBContainer):
    """
    An optical channel used to record from an imaging plane.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    description: str = Field(
        ..., description="""Description or other notes about the channel."""
    )
    emission_lambda: float = Field(
        ..., description="""Emission wavelength for channel, in nm."""
    )


class MotionCorrection(NWBDataInterface):
    """
    An image stack where all frames are shifted (registered) to a common coordinate system, to account for movement and drift between frames. Note: each frame at each point in time is assumed to be 2-D (has only x & y dimensions).
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    children: Optional[List[CorrectedImageStack] | CorrectedImageStack] = Field(
        default_factory=dict
    )
    name: str = Field(...)


class CorrectedImageStack(NWBDataInterface):
    """
    Results from motion correction of an image stack.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    corrected: str = Field(
        ...,
        description="""Image stack with frames shifted to the common coordinates.""",
    )
    xy_translation: str = Field(
        ...,
        description="""Stores the x,y delta necessary to align each frame to the common coordinates, for example, to align each frame to a reference image.""",
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
OnePhotonSeries.model_rebuild()
TwoPhotonSeries.model_rebuild()
RoiResponseSeries.model_rebuild()
RoiResponseSeriesRois.model_rebuild()
DfOverF.model_rebuild()
Fluorescence.model_rebuild()
ImageSegmentation.model_rebuild()
PlaneSegmentation.model_rebuild()
PlaneSegmentationPixelMaskIndex.model_rebuild()
PlaneSegmentationPixelMask.model_rebuild()
PlaneSegmentationVoxelMaskIndex.model_rebuild()
PlaneSegmentationVoxelMask.model_rebuild()
ImagingPlane.model_rebuild()
OpticalChannel.model_rebuild()
MotionCorrection.model_rebuild()
CorrectedImageStack.model_rebuild()
