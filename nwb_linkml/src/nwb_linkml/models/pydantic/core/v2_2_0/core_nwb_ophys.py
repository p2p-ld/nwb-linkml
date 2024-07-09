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

from nptyping import (
    Shape,
    Float,
    Float32,
    Double,
    Float64,
    LongLong,
    Int64,
    Int,
    Int32,
    Int16,
    Short,
    Int8,
    UInt,
    UInt32,
    UInt16,
    UInt8,
    UInt64,
    Number,
    String,
    Unicode,
    Unicode,
    Unicode,
    String,
    Bool,
    Datetime64,
)
from nwb_linkml.types import NDArray
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal
if TYPE_CHECKING:
    import numpy as np


from .core_nwb_base import (
    NWBDataInterface,
    TimeSeriesStartingTime,
    TimeSeriesSync,
    TimeSeries,
    NWBContainer,
)

from .core_nwb_image import ImageSeriesExternalFile, ImageSeries

from ...hdmf_common.v1_1_0.hdmf_common_table import DynamicTable, DynamicTableRegion


metamodel_version = "None"
version = "2.2.0"


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
            NDArray[Shape["3 width_height"], float],
        ]
    ] = Field(
        None,
        description="""Width, height and depth of image, or imaged area, in meters.""",
    )
    data: Optional[
        Union[
            NDArray[Shape["* frame, * x, * y"], float],
            NDArray[Shape["* frame, * x, * y, * z"], float],
        ]
    ] = Field(None, description="""Binary data representing images across frames.""")
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
    children: Optional[
        List[Union[BaseModel, DynamicTable]] | Union[BaseModel, DynamicTable]
    ] = Field(default_factory=dict)
    name: str = Field(...)


class ImagingPlane(NWBContainer):
    """
    An imaging plane and its metadata.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    description: Optional[str] = Field(
        None, description="""Description of the imaging plane."""
    )
    excitation_lambda: float = Field(
        ..., description="""Excitation wavelength, in nm."""
    )
    imaging_rate: float = Field(
        ..., description="""Rate that images are acquired, in Hz."""
    )
    indicator: str = Field(..., description="""Calcium indicator.""")
    location: str = Field(
        ...,
        description="""Location of the imaging plane. Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""",
    )
    manifold: Optional[str] = Field(
        None,
        description="""DEPRECATED Physical position of each pixel. 'xyz' represents the position of the pixel relative to the defined coordinate space. Deprecated in favor of origin_coords and grid_spacing.""",
    )
    origin_coords: Optional[str] = Field(
        None,
        description="""Physical location of the first element of the imaging plane (0, 0) for 2-D data or (0, 0, 0) for 3-D data. See also reference_frame for what the physical location is relative to (e.g., bregma).""",
    )
    grid_spacing: Optional[str] = Field(
        None,
        description="""Space between pixels in (x, y) or voxels in (x, y, z) directions, in the specified unit. Assumes imaging plane is a regular grid. See also reference_frame to interpret the grid.""",
    )
    reference_frame: Optional[str] = Field(
        None,
        description="""Describes reference frame of origin_coords and grid_spacing. For example, this can be a text description of the anatomical location and orientation of the grid defined by origin_coords and grid_spacing or the vectors needed to transform or rotate the grid to a common anatomical axis (e.g., AP/DV/ML). This field is necessary to interpret origin_coords and grid_spacing. If origin_coords and grid_spacing are not present, then this field is not required. For example, if the microscope takes 10 x 10 x 2 images, where the first value of the data matrix (index (0, 0, 0)) corresponds to (-1.2, -0.6, -2) mm relative to bregma, the spacing between pixels is 0.2 mm in x, 0.2 mm in y and 0.5 mm in z, and larger numbers in x means more anterior, larger numbers in y means more rightward, and larger numbers in z means more ventral, then enter the following -- origin_coords = (-1.2, -0.6, -2) grid_spacing = (0.2, 0.2, 0.5) reference_frame = \"Origin coordinates are relative to bregma. First dimension corresponds to anterior-posterior axis (larger index = more anterior). Second dimension corresponds to medial-lateral axis (larger index = more rightward). Third dimension corresponds to dorsal-ventral axis (larger index = more ventral).\"""",
    )
    optical_channel: str = Field(
        ..., description="""An optical channel used to record from an imaging plane."""
    )


class ImagingPlaneManifold(ConfiguredBaseModel):
    """
    DEPRECATED Physical position of each pixel. 'xyz' represents the position of the pixel relative to the defined coordinate space. Deprecated in favor of origin_coords and grid_spacing.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["manifold"] = Field("manifold")
    conversion: Optional[float] = Field(
        None,
        description="""Scalar to multiply each element in data to convert it to the specified 'unit'. If the data are stored in acquisition system units or other units that require a conversion to be interpretable, multiply the data by 'conversion' to convert the data to the specified 'unit'. e.g. if the data acquisition system stores values in this object as pixels from x = -500 to 499, y = -500 to 499 that correspond to a 2 m x 2 m range, then the 'conversion' multiplier to get from raw data acquisition pixel units to meters is 2/1000.""",
    )
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. The default value is 'meters'.""",
    )
    array: Optional[
        Union[
            NDArray[Shape["* height, * width, * depth, 3 x_y_z"], float],
            NDArray[Shape["* height, * width, 3 x_y_z"], float],
        ]
    ] = Field(None)


class ImagingPlaneOriginCoords(ConfiguredBaseModel):
    """
    Physical location of the first element of the imaging plane (0, 0) for 2-D data or (0, 0, 0) for 3-D data. See also reference_frame for what the physical location is relative to (e.g., bregma).
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["origin_coords"] = Field("origin_coords")
    unit: Optional[str] = Field(
        None,
        description="""Measurement units for origin_coords. The default value is 'meters'.""",
    )
    array: Optional[NDArray[Shape["2 x_y, 3 x_y_z"], float]] = Field(None)


class ImagingPlaneGridSpacing(ConfiguredBaseModel):
    """
    Space between pixels in (x, y) or voxels in (x, y, z) directions, in the specified unit. Assumes imaging plane is a regular grid. See also reference_frame to interpret the grid.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["grid_spacing"] = Field("grid_spacing")
    unit: Optional[str] = Field(
        None,
        description="""Measurement units for grid_spacing. The default value is 'meters'.""",
    )
    array: Optional[NDArray[Shape["2 x_y, 3 x_y_z"], float]] = Field(None)


class OpticalChannel(NWBContainer):
    """
    An optical channel used to record from an imaging plane.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
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
    children: Optional[List[NWBDataInterface] | NWBDataInterface] = Field(
        default_factory=dict
    )
    name: str = Field(...)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
TwoPhotonSeries.model_rebuild()
RoiResponseSeries.model_rebuild()
RoiResponseSeriesRois.model_rebuild()
DfOverF.model_rebuild()
Fluorescence.model_rebuild()
ImageSegmentation.model_rebuild()
ImagingPlane.model_rebuild()
ImagingPlaneManifold.model_rebuild()
ImagingPlaneOriginCoords.model_rebuild()
ImagingPlaneGridSpacing.model_rebuild()
OpticalChannel.model_rebuild()
MotionCorrection.model_rebuild()
