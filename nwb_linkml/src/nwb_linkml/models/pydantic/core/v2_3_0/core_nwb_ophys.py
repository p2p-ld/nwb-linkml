from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
import numpy as np
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union, Annotated, Type, TypeVar
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator,
    ValidationInfo,
    BeforeValidator,
)
from ...hdmf_common.v1_5_0.hdmf_common_table import (
    DynamicTableRegion,
    DynamicTable,
    VectorIndex,
    VectorData,
)
from numpydantic import NDArray, Shape
from ...core.v2_3_0.core_nwb_image import ImageSeries, ImageSeriesExternalFile
from ...core.v2_3_0.core_nwb_base import (
    TimeSeriesStartingTime,
    TimeSeriesSync,
    TimeSeries,
    NWBDataInterface,
    NWBContainer,
)

metamodel_version = "None"
version = "2.3.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )
    hdf5_path: Optional[str] = Field(
        None, description="The absolute path that this object is stored in an NWB file"
    )
    object_id: Optional[str] = Field(None, description="Unique UUID for each object")


class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key: str):
        return getattr(self.root, key)

    def __getitem__(self, key: str):
        return self.root[key]

    def __setitem__(self, key: str, value):
        self.root[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.root


NUMPYDANTIC_VERSION = "1.2.1"

ModelType = TypeVar("ModelType", bound=Type[BaseModel])


def _get_name(item: ModelType | dict, info: ValidationInfo) -> Union[ModelType, dict]:
    """Get the name of the slot that refers to this object"""
    assert isinstance(item, (BaseModel, dict))
    name = info.field_name
    if isinstance(item, BaseModel):
        item.name = name
    else:
        item["name"] = name
    return item


Named = Annotated[ModelType, BeforeValidator(_get_name)]
linkml_meta = LinkMLMeta(
    {
        "annotations": {
            "is_namespace": {"tag": "is_namespace", "value": False},
            "namespace": {"tag": "namespace", "value": "core"},
        },
        "default_prefix": "core.nwb.ophys/",
        "id": "core.nwb.ophys",
        "imports": [
            "core.nwb.image",
            "core.nwb.base",
            "../../hdmf_common/v1_5_0/namespace",
            "core.nwb.device",
            "core.nwb.language",
        ],
        "name": "core.nwb.ophys",
    }
)


class TwoPhotonSeries(ImageSeries):
    """
    Image stack recorded over time from 2-photon microscope.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    name: str = Field(...)
    pmt_gain: Optional[np.float32] = Field(None, description="""Photomultiplier gain.""")
    scan_line_rate: Optional[np.float32] = Field(
        None,
        description="""Lines imaged per second. This is also stored in /general/optophysiology but is kept here as it is useful information for analysis, and so good to be stored w/ the actual data.""",
    )
    field_of_view: Optional[
        Union[
            NDArray[Shape["2 width_height"], np.float32],
            NDArray[Shape["3 width_height_depth"], np.float32],
        ]
    ] = Field(None, description="""Width, height and depth of image, or imaged area, in meters.""")
    data: Optional[
        Union[
            NDArray[Shape["* frame, * x, * y"], np.number],
            NDArray[Shape["* frame, * x, * y, * z"], np.number],
        ]
    ] = Field(None, description="""Binary data representing images across frames.""")
    dimension: Optional[NDArray[Shape["* rank"], np.int32]] = Field(
        None,
        description="""Number of pixels on x, y, (and z) axes.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "rank"}]}}},
    )
    external_file: Optional[ImageSeriesExternalFile] = Field(
        None,
        description="""Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.""",
    )
    format: Optional[str] = Field(
        None,
        description="""Format of image. If this is 'external', then the attribute 'external_file' contains the path information to the image files. If this is 'raw', then the raw (single-channel) binary data is stored in the 'data' dataset. If this attribute is not present, then the default format='raw' case is assumed.""",
    )
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(
        None,
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
    )
    starting_time: Optional[TimeSeriesStartingTime] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[NDArray[Shape["* num_times"], np.float64]] = Field(
        None,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
    )
    control: Optional[NDArray[Shape["* num_times"], np.uint8]] = Field(
        None,
        description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
    )
    control_description: Optional[NDArray[Shape["* num_control_values"], str]] = Field(
        None,
        description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""",
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "num_control_values"}]}}
        },
    )
    sync: Optional[TimeSeriesSync] = Field(
        None,
        description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""",
    )


class RoiResponseSeries(TimeSeries):
    """
    ROI responses over an imaging plane. The first dimension represents time. The second dimension, if present, represents ROIs.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    name: str = Field(...)
    data: Union[
        NDArray[Shape["* num_times"], np.number],
        NDArray[Shape["* num_times, * num_rois"], np.number],
    ] = Field(..., description="""Signals from ROIs.""")
    rois: Named[DynamicTableRegion] = Field(
        ...,
        description="""DynamicTableRegion referencing into an ROITable containing information on the ROIs stored in this timeseries.""",
        json_schema_extra={
            "linkml_meta": {"annotations": {"named": {"tag": "named", "value": True}}}
        },
    )
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(
        None,
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
    )
    starting_time: Optional[TimeSeriesStartingTime] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[NDArray[Shape["* num_times"], np.float64]] = Field(
        None,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
    )
    control: Optional[NDArray[Shape["* num_times"], np.uint8]] = Field(
        None,
        description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
    )
    control_description: Optional[NDArray[Shape["* num_control_values"], str]] = Field(
        None,
        description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""",
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "num_control_values"}]}}
        },
    )
    sync: Optional[TimeSeriesSync] = Field(
        None,
        description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""",
    )


class DfOverF(NWBDataInterface):
    """
    dF/F information about a region of interest (ROI). Storage hierarchy of dF/F should be the same as for segmentation (i.e., same names for ROIs and for image planes).
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    children: Optional[List[RoiResponseSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "RoiResponseSeries"}]}}
    )
    name: str = Field(...)


class Fluorescence(NWBDataInterface):
    """
    Fluorescence information about a region of interest (ROI). Storage hierarchy of fluorescence should be the same as for segmentation (ie, same names for ROIs and for image planes).
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    children: Optional[List[RoiResponseSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "RoiResponseSeries"}]}}
    )
    name: str = Field(...)


class ImageSegmentation(NWBDataInterface):
    """
    Stores pixels in an image that represent different regions of interest (ROIs) or masks. All segmentation for a given imaging plane is stored together, with storage for multiple imaging planes (masks) supported. Each ROI is stored in its own subgroup, with the ROI group containing both a 2D mask and a list of pixels that make up this mask. Segments can also be used for masking neuropil. If segmentation is allowed to change with time, a new imaging plane (or module) is required and ROI names should remain consistent between them.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    children: Optional[List[PlaneSegmentation]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "PlaneSegmentation"}]}}
    )
    name: str = Field(...)


class PlaneSegmentation(DynamicTable):
    """
    Results from image segmentation of a specific imaging plane.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    name: str = Field(...)
    image_mask: Optional[PlaneSegmentationImageMask] = Field(
        None,
        description="""ROI masks for each ROI. Each image mask is the size of the original imaging plane (or volume) and members of the ROI are finite non-zero.""",
    )
    pixel_mask_index: Named[Optional[VectorIndex]] = Field(
        None,
        description="""Index into pixel_mask.""",
        json_schema_extra={
            "linkml_meta": {"annotations": {"named": {"tag": "named", "value": True}}}
        },
    )
    pixel_mask: Optional[PlaneSegmentationPixelMask] = Field(
        None,
        description="""Pixel masks for each ROI: a list of indices and weights for the ROI. Pixel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation""",
    )
    voxel_mask_index: Named[Optional[VectorIndex]] = Field(
        None,
        description="""Index into voxel_mask.""",
        json_schema_extra={
            "linkml_meta": {"annotations": {"named": {"tag": "named", "value": True}}}
        },
    )
    voxel_mask: Optional[PlaneSegmentationVoxelMask] = Field(
        None,
        description="""Voxel masks for each ROI: a list of indices and weights for the ROI. Voxel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation""",
    )
    reference_images: Optional[List[ImageSeries]] = Field(
        None,
        description="""Image stacks that the segmentation masks apply to.""",
        json_schema_extra={"linkml_meta": {"any_of": [{"range": "ImageSeries"}]}},
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
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )
    vector_data: Optional[List[VectorData]] = Field(
        None, description="""Vector columns, including index columns, of this dynamic table."""
    )


class PlaneSegmentationImageMask(VectorData):
    """
    ROI masks for each ROI. Each image mask is the size of the original imaging plane (or volume) and members of the ROI are finite non-zero.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.ophys"})

    name: Literal["image_mask"] = Field(
        "image_mask",
        json_schema_extra={
            "linkml_meta": {"equals_string": "image_mask", "ifabsent": "string(image_mask)"}
        },
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

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.ophys"})

    name: Literal["pixel_mask"] = Field(
        "pixel_mask",
        json_schema_extra={
            "linkml_meta": {"equals_string": "pixel_mask", "ifabsent": "string(pixel_mask)"}
        },
    )
    x: Optional[np.uint32] = Field(None, description="""Pixel x-coordinate.""")
    y: Optional[np.uint32] = Field(None, description="""Pixel y-coordinate.""")
    weight: Optional[np.float32] = Field(None, description="""Weight of the pixel.""")
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

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.ophys"})

    name: Literal["voxel_mask"] = Field(
        "voxel_mask",
        json_schema_extra={
            "linkml_meta": {"equals_string": "voxel_mask", "ifabsent": "string(voxel_mask)"}
        },
    )
    x: Optional[np.uint32] = Field(None, description="""Voxel x-coordinate.""")
    y: Optional[np.uint32] = Field(None, description="""Voxel y-coordinate.""")
    z: Optional[np.uint32] = Field(None, description="""Voxel z-coordinate.""")
    weight: Optional[np.float32] = Field(None, description="""Weight of the voxel.""")
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

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    children: Optional[List[OpticalChannel]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "OpticalChannel"}]}}
    )
    name: str = Field(...)


class OpticalChannel(NWBContainer):
    """
    An optical channel used to record from an imaging plane.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    name: str = Field(...)
    description: str = Field(..., description="""Description or other notes about the channel.""")
    emission_lambda: np.float32 = Field(
        ..., description="""Emission wavelength for channel, in nm."""
    )


class MotionCorrection(NWBDataInterface):
    """
    An image stack where all frames are shifted (registered) to a common coordinate system, to account for movement and drift between frames. Note: each frame at each point in time is assumed to be 2-D (has only x & y dimensions).
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    children: Optional[List[CorrectedImageStack]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "CorrectedImageStack"}]}}
    )
    name: str = Field(...)


class CorrectedImageStack(NWBDataInterface):
    """
    Reuslts from motion correction of an image stack.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    name: str = Field(...)
    corrected: ImageSeries = Field(
        ..., description="""Image stack with frames shifted to the common coordinates."""
    )
    xy_translation: TimeSeries = Field(
        ...,
        description="""Stores the x,y delta necessary to align each frame to the common coordinates, for example, to align each frame to a reference image.""",
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
TwoPhotonSeries.model_rebuild()
RoiResponseSeries.model_rebuild()
DfOverF.model_rebuild()
Fluorescence.model_rebuild()
ImageSegmentation.model_rebuild()
PlaneSegmentation.model_rebuild()
PlaneSegmentationImageMask.model_rebuild()
PlaneSegmentationPixelMask.model_rebuild()
PlaneSegmentationVoxelMask.model_rebuild()
ImagingPlane.model_rebuild()
OpticalChannel.model_rebuild()
MotionCorrection.model_rebuild()
CorrectedImageStack.model_rebuild()
