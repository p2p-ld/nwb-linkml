from __future__ import annotations

import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any, ClassVar, Dict, List, Literal, Optional, Type, TypeVar, Union

import numpy as np
from numpydantic import NDArray, Shape
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    RootModel,
    ValidationInfo,
    field_validator,
    model_validator,
)

from ...core.v2_2_5.core_nwb_base import (
    NWBContainer,
    NWBDataInterface,
    TimeSeries,
    TimeSeriesStartingTime,
    TimeSeriesSync,
)
from ...core.v2_2_5.core_nwb_device import Device
from ...core.v2_2_5.core_nwb_image import ImageSeries, ImageSeriesData, ImageSeriesExternalFile
from ...hdmf_common.v1_1_3.hdmf_common_table import (
    DynamicTable,
    DynamicTableRegion,
    ElementIdentifiers,
    VectorData,
    VectorIndex,
)


metamodel_version = "None"
version = "2.2.5"


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

    def __getitem__(self, val: Union[int, slice, str]) -> Any:
        """Try and get a value from value or "data" if we have it"""
        if hasattr(self, "value") and self.value is not None:
            return self.value[val]
        elif hasattr(self, "data") and self.data is not None:
            return self.data[val]
        else:
            raise KeyError("No value or data field to index from")

    @field_validator("*", mode="wrap")
    @classmethod
    def coerce_value(cls, v: Any, handler, info) -> Any:
        """Try to rescue instantiation by using the value field"""
        try:
            return handler(v)
        except Exception as e1:
            try:
                return handler(v.value)
            except AttributeError:
                try:
                    return handler(v["value"])
                except (IndexError, KeyError, TypeError):
                    raise e1

    @field_validator("*", mode="wrap")
    @classmethod
    def cast_with_value(cls, v: Any, handler, info) -> Any:
        """Try to rescue instantiation by casting into the model's value field"""
        try:
            return handler(v)
        except Exception as e1:
            try:
                return handler({"value": v})
            except Exception:
                raise e1

    @field_validator("*", mode="before")
    @classmethod
    def coerce_subclass(cls, v: Any, info) -> Any:
        """Recast parent classes into child classes"""
        if isinstance(v, BaseModel):
            annotation = cls.model_fields[info.field_name].annotation
            while hasattr(annotation, "__args__"):
                annotation = annotation.__args__[0]
            try:
                if issubclass(annotation, type(v)) and annotation is not type(v):
                    if v.__pydantic_extra__:
                        v = annotation(**{**v.__dict__, **v.__pydantic_extra__})
                    else:
                        v = annotation(**v.__dict__)
            except TypeError:
                # fine, annotation is a non-class type like a TypeVar
                pass
        return v

    @model_validator(mode="before")
    @classmethod
    def gather_extra_to_value(cls, v: Any) -> Any:
        """
        For classes that don't allow extra fields and have a value slot,
        pack those extra kwargs into ``value``
        """
        if (
            cls.model_config["extra"] == "forbid"
            and "value" in cls.model_fields
            and isinstance(v, dict)
        ):
            extras = {key: val for key, val in v.items() if key not in cls.model_fields}
            if extras:
                for k in extras:
                    del v[k]
                if "value" in v:
                    v["value"].update(extras)
                else:
                    v["value"] = extras
        return v


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
    assert isinstance(item, (BaseModel, dict)), f"{item} was not a BaseModel or a dict!"
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
            "../../hdmf_common/v1_1_3/namespace",
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
    pmt_gain: Optional[float] = Field(None, description="""Photomultiplier gain.""")
    scan_line_rate: Optional[float] = Field(
        None,
        description="""Lines imaged per second. This is also stored in /general/optophysiology but is kept here as it is useful information for analysis, and so good to be stored w/ the actual data.""",
    )
    field_of_view: Optional[
        Union[
            NDArray[Shape["2 width_height"], float], NDArray[Shape["3 width_height_depth"], float]
        ]
    ] = Field(None, description="""Width, height and depth of image, or imaged area, in meters.""")
    imaging_plane: Union[ImagingPlane, str] = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"source_type": {"tag": "source_type", "value": "link"}},
                "any_of": [{"range": "ImagingPlane"}, {"range": "string"}],
            }
        },
    )
    data: Optional[ImageSeriesData] = Field(
        None, description="""Binary data representing images across frames."""
    )
    dimension: Optional[NDArray[Shape["* rank"], int]] = Field(
        None,
        description="""Number of pixels on x, y, (and z) axes.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "rank"}]}}},
    )
    external_file: Optional[ImageSeriesExternalFile] = Field(
        None,
        description="""Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.""",
    )
    format: Optional[str] = Field(
        "raw",
        description="""Format of image. If this is 'external', then the attribute 'external_file' contains the path information to the image files. If this is 'raw', then the raw (single-channel) binary data is stored in the 'data' dataset. If this attribute is not present, then the default format='raw' case is assumed.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(raw)"}},
    )
    description: Optional[str] = Field(
        "no description",
        description="""Description of the time series.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(no description)"}},
    )
    comments: Optional[str] = Field(
        "no comments",
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(no comments)"}},
    )
    starting_time: Optional[TimeSeriesStartingTime] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[NDArray[Shape["* num_times"], float]] = Field(
        None,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
    )
    control: Optional[NDArray[Shape["* num_times"], int]] = Field(
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
    data: RoiResponseSeriesData = Field(..., description="""Signals from ROIs.""")
    rois: Named[DynamicTableRegion] = Field(
        ...,
        description="""DynamicTableRegion referencing into an ROITable containing information on the ROIs stored in this timeseries.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    description: Optional[str] = Field(
        "no description",
        description="""Description of the time series.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(no description)"}},
    )
    comments: Optional[str] = Field(
        "no comments",
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(no comments)"}},
    )
    starting_time: Optional[TimeSeriesStartingTime] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[NDArray[Shape["* num_times"], float]] = Field(
        None,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
    )
    control: Optional[NDArray[Shape["* num_times"], int]] = Field(
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


class RoiResponseSeriesData(ConfiguredBaseModel):
    """
    Signals from ROIs.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.ophys"})

    name: Literal["data"] = Field(
        "data",
        json_schema_extra={"linkml_meta": {"equals_string": "data", "ifabsent": "string(data)"}},
    )
    conversion: Optional[float] = Field(
        1.0,
        description="""Scalar to multiply each element in data to convert it to the specified 'unit'. If the data are stored in acquisition system units or other units that require a conversion to be interpretable, multiply the data by 'conversion' to convert the data to the specified 'unit'. e.g. if the data acquisition system stores values in this object as signed 16-bit integers (int16 range -32,768 to 32,767) that correspond to a 5V range (-2.5V to 2.5V), and the data acquisition system gain is 8000X, then the 'conversion' multiplier to get from raw data acquisition values to recorded volts is 2.5/32768/8000 = 9.5367e-9.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "float(1.0)"}},
    )
    resolution: Optional[float] = Field(
        -1.0,
        description="""Smallest meaningful difference between values in data, stored in the specified by unit, e.g., the change in value of the least significant bit, or a larger number if signal noise is known to be present. If unknown, use -1.0.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "float(-1.0)"}},
    )
    unit: str = Field(
        ...,
        description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    value: Optional[
        Union[
            NDArray[Shape["* num_times"], float | int],
            NDArray[Shape["* num_times, * num_rois"], float | int],
        ]
    ] = Field(None)


class DfOverF(NWBDataInterface):
    """
    dF/F information about a region of interest (ROI). Storage hierarchy of dF/F should be the same as for segmentation (i.e., same names for ROIs and for image planes).
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    name: str = Field("DfOverF", json_schema_extra={"linkml_meta": {"ifabsent": "string(DfOverF)"}})
    value: Optional[Dict[str, RoiResponseSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "RoiResponseSeries"}]}}
    )


class Fluorescence(NWBDataInterface):
    """
    Fluorescence information about a region of interest (ROI). Storage hierarchy of fluorescence should be the same as for segmentation (ie, same names for ROIs and for image planes).
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    name: str = Field(
        "Fluorescence", json_schema_extra={"linkml_meta": {"ifabsent": "string(Fluorescence)"}}
    )
    value: Optional[Dict[str, RoiResponseSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "RoiResponseSeries"}]}}
    )


class ImageSegmentation(NWBDataInterface):
    """
    Stores pixels in an image that represent different regions of interest (ROIs) or masks. All segmentation for a given imaging plane is stored together, with storage for multiple imaging planes (masks) supported. Each ROI is stored in its own subgroup, with the ROI group containing both a 2D mask and a list of pixels that make up this mask. Segments can also be used for masking neuropil. If segmentation is allowed to change with time, a new imaging plane (or module) is required and ROI names should remain consistent between them.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    name: str = Field(
        "ImageSegmentation",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(ImageSegmentation)"}},
    )
    value: Optional[Dict[str, PlaneSegmentation]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "PlaneSegmentation"}]}}
    )


class PlaneSegmentation(DynamicTable):
    """
    Results from image segmentation of a specific imaging plane.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    name: str = Field(...)
    image_mask: Optional[
        VectorData[
            Union[
                NDArray[Shape["* num_roi, * num_x, * num_y"], Any],
                NDArray[Shape["* num_roi, * num_x, * num_y, * num_z"], Any],
            ]
        ]
    ] = Field(
        None,
        description="""ROI masks for each ROI. Each image mask is the size of the original imaging plane (or volume) and members of the ROI are finite non-zero.""",
    )
    pixel_mask: Optional[PlaneSegmentationPixelMask] = Field(
        None,
        description="""Pixel masks for each ROI: a list of indices and weights for the ROI. Pixel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation""",
    )
    pixel_mask_index: Optional[Named[VectorIndex]] = Field(
        None,
        description="""Index into pixel_mask.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    voxel_mask: Optional[PlaneSegmentationVoxelMask] = Field(
        None,
        description="""Voxel masks for each ROI: a list of indices and weights for the ROI. Voxel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation""",
    )
    voxel_mask_index: Optional[Named[VectorIndex]] = Field(
        None,
        description="""Index into voxel_mask.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    reference_images: Optional[Dict[str, ImageSeries]] = Field(
        None,
        description="""Image stacks that the segmentation masks apply to.""",
        json_schema_extra={"linkml_meta": {"any_of": [{"range": "ImageSeries"}]}},
    )
    imaging_plane: Union[ImagingPlane, str] = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"source_type": {"tag": "source_type", "value": "link"}},
                "any_of": [{"range": "ImagingPlane"}, {"range": "string"}],
            }
        },
    )
    colnames: List[str] = Field(
        ...,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: str = Field(..., description="""Description of what is in this dynamic table.""")
    id: ElementIdentifiers = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )


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
    x: Optional[NDArray[Shape["*"], int]] = Field(
        None,
        description="""Pixel x-coordinate.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    y: Optional[NDArray[Shape["*"], int]] = Field(
        None,
        description="""Pixel y-coordinate.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    weight: Optional[NDArray[Shape["*"], float]] = Field(
        None,
        description="""Weight of the pixel.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    description: str = Field(..., description="""Description of what these vectors represent.""")
    value: Optional[
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
    x: Optional[NDArray[Shape["*"], int]] = Field(
        None,
        description="""Voxel x-coordinate.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    y: Optional[NDArray[Shape["*"], int]] = Field(
        None,
        description="""Voxel y-coordinate.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    z: Optional[NDArray[Shape["*"], int]] = Field(
        None,
        description="""Voxel z-coordinate.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    weight: Optional[NDArray[Shape["*"], float]] = Field(
        None,
        description="""Weight of the voxel.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    description: str = Field(..., description="""Description of what these vectors represent.""")
    value: Optional[
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

    name: str = Field(...)
    description: Optional[str] = Field(None, description="""Description of the imaging plane.""")
    excitation_lambda: float = Field(..., description="""Excitation wavelength, in nm.""")
    imaging_rate: Optional[float] = Field(
        None,
        description="""Rate that images are acquired, in Hz. If the corresponding TimeSeries is present, the rate should be stored there instead.""",
    )
    indicator: str = Field(..., description="""Calcium indicator.""")
    location: str = Field(
        ...,
        description="""Location of the imaging plane. Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""",
    )
    manifold: Optional[ImagingPlaneManifold] = Field(
        None,
        description="""DEPRECATED Physical position of each pixel. 'xyz' represents the position of the pixel relative to the defined coordinate space. Deprecated in favor of origin_coords and grid_spacing.""",
    )
    origin_coords: Optional[ImagingPlaneOriginCoords] = Field(
        None,
        description="""Physical location of the first element of the imaging plane (0, 0) for 2-D data or (0, 0, 0) for 3-D data. See also reference_frame for what the physical location is relative to (e.g., bregma).""",
    )
    grid_spacing: Optional[ImagingPlaneGridSpacing] = Field(
        None,
        description="""Space between pixels in (x, y) or voxels in (x, y, z) directions, in the specified unit. Assumes imaging plane is a regular grid. See also reference_frame to interpret the grid.""",
    )
    reference_frame: Optional[str] = Field(
        None,
        description="""Describes reference frame of origin_coords and grid_spacing. For example, this can be a text description of the anatomical location and orientation of the grid defined by origin_coords and grid_spacing or the vectors needed to transform or rotate the grid to a common anatomical axis (e.g., AP/DV/ML). This field is necessary to interpret origin_coords and grid_spacing. If origin_coords and grid_spacing are not present, then this field is not required. For example, if the microscope takes 10 x 10 x 2 images, where the first value of the data matrix (index (0, 0, 0)) corresponds to (-1.2, -0.6, -2) mm relative to bregma, the spacing between pixels is 0.2 mm in x, 0.2 mm in y and 0.5 mm in z, and larger numbers in x means more anterior, larger numbers in y means more rightward, and larger numbers in z means more ventral, then enter the following -- origin_coords = (-1.2, -0.6, -2) grid_spacing = (0.2, 0.2, 0.5) reference_frame = \"Origin coordinates are relative to bregma. First dimension corresponds to anterior-posterior axis (larger index = more anterior). Second dimension corresponds to medial-lateral axis (larger index = more rightward). Third dimension corresponds to dorsal-ventral axis (larger index = more ventral).\"""",
    )
    optical_channel: Dict[str, OpticalChannel] = Field(
        ..., description="""An optical channel used to record from an imaging plane."""
    )
    device: Union[Device, str] = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"source_type": {"tag": "source_type", "value": "link"}},
                "any_of": [{"range": "Device"}, {"range": "string"}],
            }
        },
    )


class ImagingPlaneManifold(ConfiguredBaseModel):
    """
    DEPRECATED Physical position of each pixel. 'xyz' represents the position of the pixel relative to the defined coordinate space. Deprecated in favor of origin_coords and grid_spacing.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.ophys"})

    name: Literal["manifold"] = Field(
        "manifold",
        json_schema_extra={
            "linkml_meta": {"equals_string": "manifold", "ifabsent": "string(manifold)"}
        },
    )
    conversion: Optional[float] = Field(
        1.0,
        description="""Scalar to multiply each element in data to convert it to the specified 'unit'. If the data are stored in acquisition system units or other units that require a conversion to be interpretable, multiply the data by 'conversion' to convert the data to the specified 'unit'. e.g. if the data acquisition system stores values in this object as pixels from x = -500 to 499, y = -500 to 499 that correspond to a 2 m x 2 m range, then the 'conversion' multiplier to get from raw data acquisition pixel units to meters is 2/1000.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "float(1.0)"}},
    )
    unit: Optional[str] = Field(
        "meters",
        description="""Base unit of measurement for working with the data. The default value is 'meters'.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(meters)"}},
    )
    value: Optional[
        Union[
            NDArray[Shape["* height, * width, 3 x_y_z"], float],
            NDArray[Shape["* height, * width, * depth, 3 x_y_z"], float],
        ]
    ] = Field(None)


class ImagingPlaneOriginCoords(ConfiguredBaseModel):
    """
    Physical location of the first element of the imaging plane (0, 0) for 2-D data or (0, 0, 0) for 3-D data. See also reference_frame for what the physical location is relative to (e.g., bregma).
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.ophys"})

    name: Literal["origin_coords"] = Field(
        "origin_coords",
        json_schema_extra={
            "linkml_meta": {"equals_string": "origin_coords", "ifabsent": "string(origin_coords)"}
        },
    )
    unit: str = Field(
        "meters",
        description="""Measurement units for origin_coords. The default value is 'meters'.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(meters)"}},
    )
    value: Optional[Union[NDArray[Shape["2 x_y"], float], NDArray[Shape["3 x_y_z"], float]]] = (
        Field(None)
    )


class ImagingPlaneGridSpacing(ConfiguredBaseModel):
    """
    Space between pixels in (x, y) or voxels in (x, y, z) directions, in the specified unit. Assumes imaging plane is a regular grid. See also reference_frame to interpret the grid.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.ophys"})

    name: Literal["grid_spacing"] = Field(
        "grid_spacing",
        json_schema_extra={
            "linkml_meta": {"equals_string": "grid_spacing", "ifabsent": "string(grid_spacing)"}
        },
    )
    unit: str = Field(
        "meters",
        description="""Measurement units for grid_spacing. The default value is 'meters'.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(meters)"}},
    )
    value: Optional[Union[NDArray[Shape["2 x_y"], float], NDArray[Shape["3 x_y_z"], float]]] = (
        Field(None)
    )


class OpticalChannel(NWBContainer):
    """
    An optical channel used to record from an imaging plane.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    name: str = Field(...)
    description: str = Field(..., description="""Description or other notes about the channel.""")
    emission_lambda: float = Field(..., description="""Emission wavelength for channel, in nm.""")


class MotionCorrection(NWBDataInterface):
    """
    An image stack where all frames are shifted (registered) to a common coordinate system, to account for movement and drift between frames. Note: each frame at each point in time is assumed to be 2-D (has only x & y dimensions).
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.ophys", "tree_root": True}
    )

    name: str = Field(
        "MotionCorrection",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(MotionCorrection)"}},
    )
    value: Optional[Dict[str, CorrectedImageStack]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "CorrectedImageStack"}]}}
    )


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
    original: Union[ImageSeries, str] = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"source_type": {"tag": "source_type", "value": "link"}},
                "any_of": [{"range": "ImageSeries"}, {"range": "string"}],
            }
        },
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
TwoPhotonSeries.model_rebuild()
RoiResponseSeries.model_rebuild()
RoiResponseSeriesData.model_rebuild()
DfOverF.model_rebuild()
Fluorescence.model_rebuild()
ImageSegmentation.model_rebuild()
PlaneSegmentation.model_rebuild()
PlaneSegmentationPixelMask.model_rebuild()
PlaneSegmentationVoxelMask.model_rebuild()
ImagingPlane.model_rebuild()
ImagingPlaneManifold.model_rebuild()
ImagingPlaneOriginCoords.model_rebuild()
ImagingPlaneGridSpacing.model_rebuild()
OpticalChannel.model_rebuild()
MotionCorrection.model_rebuild()
CorrectedImageStack.model_rebuild()
