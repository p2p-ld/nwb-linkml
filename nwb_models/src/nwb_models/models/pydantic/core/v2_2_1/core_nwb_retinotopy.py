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

from ...core.v2_2_1.core_nwb_base import NWBData, NWBDataInterface
from ...core.v2_2_1.core_nwb_image import GrayscaleImage


metamodel_version = "None"
version = "2.2.1"


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
        "default_prefix": "core.nwb.retinotopy/",
        "id": "core.nwb.retinotopy",
        "imports": ["core.nwb.base", "core.nwb.image", "core.nwb.language"],
        "name": "core.nwb.retinotopy",
    }
)


class RetinotopyMap(NWBData):
    """
    Abstract two-dimensional map of responses. Array structure: [num_rows][num_columns]
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.retinotopy", "tree_root": True}
    )

    name: str = Field(...)
    dimension: List[int] = Field(
        ...,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: List[float] = Field(..., description="""Size of viewing area, in meters.""")
    value: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}, {"alias": "num_cols"}]}}
        },
    )


class AxisMap(RetinotopyMap):
    """
    Abstract two-dimensional map of responses to stimuli along a single response axis (e.g. eccentricity)
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.retinotopy", "tree_root": True}
    )

    name: str = Field(...)
    unit: str = Field(..., description="""Unit that axis data is stored in (e.g., degrees).""")
    value: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}, {"alias": "num_cols"}]}}
        },
    )
    dimension: List[int] = Field(
        ...,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: List[float] = Field(..., description="""Size of viewing area, in meters.""")


class RetinotopyImage(GrayscaleImage):
    """
    Gray-scale image related to retinotopic mapping. Array structure: [num_rows][num_columns]
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.retinotopy", "tree_root": True}
    )

    name: str = Field(...)
    bits_per_pixel: int = Field(
        ...,
        description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value.""",
    )
    dimension: List[int] = Field(
        ...,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: List[float] = Field(..., description="""Size of viewing area, in meters.""")
    format: str = Field(..., description="""Format of image. Right now only 'raw' is supported.""")
    value: Optional[NDArray[Shape["* x, * y"], float | int]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "x"}, {"alias": "y"}]}}
        },
    )
    resolution: Optional[float] = Field(
        None, description="""Pixel resolution of the image, in pixels per centimeter."""
    )
    description: Optional[str] = Field(None, description="""Description of the image.""")


class ImagingRetinotopy(NWBDataInterface):
    """
    Intrinsic signal optical imaging or widefield imaging for measuring retinotopy. Stores orthogonal maps (e.g., altitude/azimuth; radius/theta) of responses to specific stimuli and a combined polarity map from which to identify visual areas. NOTE: for data consistency, all images and arrays are stored in the format [row][column] and [row, col], which equates to [y][x]. Field of view and dimension arrays may appear backward (i.e., y before x).
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.retinotopy", "tree_root": True}
    )

    name: str = Field(
        "ImagingRetinotopy",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(ImagingRetinotopy)"}},
    )
    axis_1_phase_map: Named[AxisMap] = Field(
        ...,
        description="""Phase response to stimulus on the first measured axis.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    axis_1_power_map: Optional[Named[AxisMap]] = Field(
        None,
        description="""Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    axis_2_phase_map: Named[AxisMap] = Field(
        ...,
        description="""Phase response to stimulus on the second measured axis.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    axis_2_power_map: Optional[Named[AxisMap]] = Field(
        None,
        description="""Power response to stimulus on the second measured axis.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    sign_map: Named[RetinotopyMap] = Field(
        ...,
        description="""Sine of the angle between the direction of the gradient in axis_1 and axis_2.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    axis_descriptions: NDArray[Shape["2 num_axes"], str] = Field(
        ...,
        description="""Two-element array describing the contents of the two response axis fields. Description should be something like ['altitude', 'azimuth'] or '['radius', 'theta'].""",
        json_schema_extra={
            "linkml_meta": {
                "array": {"dimensions": [{"alias": "num_axes", "exact_cardinality": 2}]}
            }
        },
    )
    focal_depth_image: ImagingRetinotopyFocalDepthImage = Field(
        ...,
        description="""Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].""",
    )
    vasculature_image: Named[RetinotopyImage] = Field(
        ...,
        description="""Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )


class ImagingRetinotopyFocalDepthImage(RetinotopyImage):
    """
    Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.retinotopy"})

    name: Literal["focal_depth_image"] = Field(
        "focal_depth_image",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "focal_depth_image",
                "ifabsent": "string(focal_depth_image)",
            }
        },
    )
    focal_depth: float = Field(..., description="""Focal depth offset, in meters.""")
    bits_per_pixel: int = Field(
        ...,
        description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value.""",
    )
    dimension: List[int] = Field(
        ...,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: List[float] = Field(..., description="""Size of viewing area, in meters.""")
    format: str = Field(..., description="""Format of image. Right now only 'raw' is supported.""")
    value: Optional[NDArray[Shape["* x, * y"], float | int]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "x"}, {"alias": "y"}]}}
        },
    )
    resolution: Optional[float] = Field(
        None, description="""Pixel resolution of the image, in pixels per centimeter."""
    )
    description: Optional[str] = Field(None, description="""Description of the image.""")


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
RetinotopyMap.model_rebuild()
AxisMap.model_rebuild()
RetinotopyImage.model_rebuild()
ImagingRetinotopy.model_rebuild()
ImagingRetinotopyFocalDepthImage.model_rebuild()
