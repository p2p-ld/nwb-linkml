from __future__ import annotations

import sys
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Optional,
    Union,
)

from nptyping import (
    Shape,
)
from pydantic import BaseModel as BaseModel
from pydantic import ConfigDict, Field

from nwb_linkml.types import NDArray

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal
if TYPE_CHECKING:
    import numpy as np


from .core_nwb_base import NWBData, NWBDataInterface
from .core_nwb_image import GrayscaleImage

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

    def __getitem__(self, i: slice | int) -> np.ndarray:
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


class RetinotopyMap(NWBData):
    """
    Abstract two-dimensional map of responses. Array structure: [num_rows][num_columns]
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(None)


class AxisMap(RetinotopyMap):
    """
    Abstract two-dimensional map of responses to stimuli along a single response axis (e.g. eccentricity)
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    unit: Optional[str] = Field(
        None, description="""Unit that axis data is stored in (e.g., degrees)."""
    )
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(None)
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")


class RetinotopyImage(GrayscaleImage):
    """
    Gray-scale image related to retinotopic mapping. Array structure: [num_rows][num_columns]
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    bits_per_pixel: Optional[int] = Field(
        None,
        description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value.""",
    )
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    format: Optional[str] = Field(
        None, description="""Format of image. Right now only 'raw' is supported."""
    )
    resolution: Optional[float] = Field(
        None, description="""Pixel resolution of the image, in pixels per centimeter."""
    )
    description: Optional[str] = Field(None, description="""Description of the image.""")
    array: Optional[
        Union[
            NDArray[Shape["* x, * y"], float],
            NDArray[Shape["* x, * y, 3 r, g, b"], float],
            NDArray[Shape["* x, * y, 4 r, g, b, a"], float],
        ]
    ] = Field(None)


class ImagingRetinotopy(NWBDataInterface):
    """
    Intrinsic signal optical imaging or widefield imaging for measuring retinotopy. Stores orthogonal maps (e.g., altitude/azimuth; radius/theta) of responses to specific stimuli and a combined polarity map from which to identify visual areas. NOTE: for data consistency, all images and arrays are stored in the format [row][column] and [row, col], which equates to [y][x]. Field of view and dimension arrays may appear backward (i.e., y before x).
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
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
        None, description="""Power response to stimulus on the second measured axis."""
    )
    sign_map: str = Field(
        ...,
        description="""Sine of the angle between the direction of the gradient in axis_1 and axis_2.""",
    )
    axis_descriptions: NDArray[Shape["2 num_axes"], str] = Field(
        ...,
        description="""Two-element array describing the contents of the two response axis fields. Description should be something like ['altitude', 'azimuth'] or '['radius', 'theta'].""",
    )
    focal_depth_image: str = Field(
        ...,
        description="""Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].""",
    )
    vasculature_image: str = Field(
        ...,
        description="""Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]""",
    )


class ImagingRetinotopyAxis1PhaseMap(AxisMap):
    """
    Phase response to stimulus on the first measured axis.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["axis_1_phase_map"] = Field("axis_1_phase_map")
    unit: Optional[str] = Field(
        None, description="""Unit that axis data is stored in (e.g., degrees)."""
    )
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(None)
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")


class ImagingRetinotopyAxis1PowerMap(AxisMap):
    """
    Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["axis_1_power_map"] = Field("axis_1_power_map")
    unit: Optional[str] = Field(
        None, description="""Unit that axis data is stored in (e.g., degrees)."""
    )
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(None)
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")


class ImagingRetinotopyAxis2PhaseMap(AxisMap):
    """
    Phase response to stimulus on the second measured axis.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["axis_2_phase_map"] = Field("axis_2_phase_map")
    unit: Optional[str] = Field(
        None, description="""Unit that axis data is stored in (e.g., degrees)."""
    )
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(None)
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")


class ImagingRetinotopyAxis2PowerMap(AxisMap):
    """
    Power response to stimulus on the second measured axis.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["axis_2_power_map"] = Field("axis_2_power_map")
    unit: Optional[str] = Field(
        None, description="""Unit that axis data is stored in (e.g., degrees)."""
    )
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(None)
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")


class ImagingRetinotopySignMap(RetinotopyMap):
    """
    Sine of the angle between the direction of the gradient in axis_1 and axis_2.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["sign_map"] = Field("sign_map")
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    array: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(None)


class ImagingRetinotopyFocalDepthImage(RetinotopyImage):
    """
    Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["focal_depth_image"] = Field("focal_depth_image")
    focal_depth: Optional[float] = Field(None, description="""Focal depth offset, in meters.""")
    bits_per_pixel: Optional[int] = Field(
        None,
        description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value.""",
    )
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    format: Optional[str] = Field(
        None, description="""Format of image. Right now only 'raw' is supported."""
    )
    resolution: Optional[float] = Field(
        None, description="""Pixel resolution of the image, in pixels per centimeter."""
    )
    description: Optional[str] = Field(None, description="""Description of the image.""")
    array: Optional[
        Union[
            NDArray[Shape["* x, * y"], float],
            NDArray[Shape["* x, * y, 3 r, g, b"], float],
            NDArray[Shape["* x, * y, 4 r, g, b, a"], float],
        ]
    ] = Field(None)


class ImagingRetinotopyVasculatureImage(RetinotopyImage):
    """
    Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["vasculature_image"] = Field("vasculature_image")
    bits_per_pixel: Optional[int] = Field(
        None,
        description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value.""",
    )
    dimension: Optional[int] = Field(
        None,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    format: Optional[str] = Field(
        None, description="""Format of image. Right now only 'raw' is supported."""
    )
    resolution: Optional[float] = Field(
        None, description="""Pixel resolution of the image, in pixels per centimeter."""
    )
    description: Optional[str] = Field(None, description="""Description of the image.""")
    array: Optional[
        Union[
            NDArray[Shape["* x, * y"], float],
            NDArray[Shape["* x, * y, 3 r, g, b"], float],
            NDArray[Shape["* x, * y, 4 r, g, b, a"], float],
        ]
    ] = Field(None)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
RetinotopyMap.model_rebuild()
AxisMap.model_rebuild()
RetinotopyImage.model_rebuild()
ImagingRetinotopy.model_rebuild()
ImagingRetinotopyAxis1PhaseMap.model_rebuild()
ImagingRetinotopyAxis1PowerMap.model_rebuild()
ImagingRetinotopyAxis2PhaseMap.model_rebuild()
ImagingRetinotopyAxis2PowerMap.model_rebuild()
ImagingRetinotopySignMap.model_rebuild()
ImagingRetinotopyFocalDepthImage.model_rebuild()
ImagingRetinotopyVasculatureImage.model_rebuild()
