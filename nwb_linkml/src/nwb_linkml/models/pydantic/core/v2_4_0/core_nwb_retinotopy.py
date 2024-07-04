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


from .core_nwb_base import NWBDataInterface


metamodel_version = "None"
version = "2.4.0"


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


class ImagingRetinotopy(NWBDataInterface):
    """
    Intrinsic signal optical imaging or widefield imaging for measuring retinotopy. Stores orthogonal maps (e.g., altitude/azimuth; radius/theta) of responses to specific stimuli and a combined polarity map from which to identify visual areas. This group does not store the raw responses imaged during retinotopic mapping or the stimuli presented, but rather the resulting phase and power maps after applying a Fourier transform on the averaged responses. Note: for data consistency, all images and arrays are stored in the format [row][column] and [row, col], which equates to [y][x]. Field of view and dimension arrays may appear backward (i.e., y before x).
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field("ImagingRetinotopy")
    axis_1_phase_map: str = Field(
        ..., description="""Phase response to stimulus on the first measured axis."""
    )
    axis_1_power_map: Optional[str] = Field(
        None,
        description="""Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.""",
    )
    axis_2_phase_map: str = Field(
        ..., description="""Phase response to stimulus on the second measured axis."""
    )
    axis_2_power_map: Optional[str] = Field(
        None,
        description="""Power response on the second measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.""",
    )
    axis_descriptions: NDArray[Shape["2 axis_1, axis_2"], str] = Field(
        ...,
        description="""Two-element array describing the contents of the two response axis fields. Description should be something like ['altitude', 'azimuth'] or '['radius', 'theta'].""",
    )
    focal_depth_image: Optional[str] = Field(
        None,
        description="""Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].""",
    )
    sign_map: Optional[str] = Field(
        None,
        description="""Sine of the angle between the direction of the gradient in axis_1 and axis_2.""",
    )
    vasculature_image: str = Field(
        ...,
        description="""Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]""",
    )


class ImagingRetinotopyAxis1PhaseMap(ConfiguredBaseModel):
    """
    Phase response to stimulus on the first measured axis.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["axis_1_phase_map"] = Field("axis_1_phase_map")
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(
        None, description="""Size of viewing area, in meters."""
    )
    unit: Optional[str] = Field(
        None, description="""Unit that axis data is stored in (e.g., degrees)."""
    )
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(None)


class ImagingRetinotopyAxis1PowerMap(ConfiguredBaseModel):
    """
    Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["axis_1_power_map"] = Field("axis_1_power_map")
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(
        None, description="""Size of viewing area, in meters."""
    )
    unit: Optional[str] = Field(
        None, description="""Unit that axis data is stored in (e.g., degrees)."""
    )
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(None)


class ImagingRetinotopyAxis2PhaseMap(ConfiguredBaseModel):
    """
    Phase response to stimulus on the second measured axis.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["axis_2_phase_map"] = Field("axis_2_phase_map")
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(
        None, description="""Size of viewing area, in meters."""
    )
    unit: Optional[str] = Field(
        None, description="""Unit that axis data is stored in (e.g., degrees)."""
    )
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(None)


class ImagingRetinotopyAxis2PowerMap(ConfiguredBaseModel):
    """
    Power response on the second measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["axis_2_power_map"] = Field("axis_2_power_map")
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(
        None, description="""Size of viewing area, in meters."""
    )
    unit: Optional[str] = Field(
        None, description="""Unit that axis data is stored in (e.g., degrees)."""
    )
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(None)


class ImagingRetinotopyFocalDepthImage(ConfiguredBaseModel):
    """
    Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["focal_depth_image"] = Field("focal_depth_image")
    bits_per_pixel: Optional[int] = Field(
        None,
        description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value.""",
    )
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(
        None, description="""Size of viewing area, in meters."""
    )
    focal_depth: Optional[float] = Field(
        None, description="""Focal depth offset, in meters."""
    )
    format: Optional[str] = Field(
        None, description="""Format of image. Right now only 'raw' is supported."""
    )
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], int]] = Field(None)


class ImagingRetinotopySignMap(ConfiguredBaseModel):
    """
    Sine of the angle between the direction of the gradient in axis_1 and axis_2.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["sign_map"] = Field("sign_map")
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(
        None, description="""Size of viewing area, in meters."""
    )
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(None)


class ImagingRetinotopyVasculatureImage(ConfiguredBaseModel):
    """
    Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["vasculature_image"] = Field("vasculature_image")
    bits_per_pixel: Optional[int] = Field(
        None,
        description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value""",
    )
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(
        None, description="""Size of viewing area, in meters."""
    )
    format: Optional[str] = Field(
        None, description="""Format of image. Right now only 'raw' is supported."""
    )
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], int]] = Field(None)


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
