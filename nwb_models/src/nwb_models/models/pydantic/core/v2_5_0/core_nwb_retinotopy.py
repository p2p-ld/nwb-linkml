from __future__ import annotations

import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union

import numpy as np
from numpydantic import NDArray, Shape
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

from ...core.v2_5_0.core_nwb_base import NWBDataInterface


metamodel_version = "None"
version = "2.5.0"


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

    def __getitem__(self, val: Union[int, slice]) -> Any:
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
        """Try to rescue instantiation by casting into the model's value fiel"""
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
linkml_meta = LinkMLMeta(
    {
        "annotations": {
            "is_namespace": {"tag": "is_namespace", "value": False},
            "namespace": {"tag": "namespace", "value": "core"},
        },
        "default_prefix": "core.nwb.retinotopy/",
        "id": "core.nwb.retinotopy",
        "imports": ["core.nwb.base", "core.nwb.language"],
        "name": "core.nwb.retinotopy",
    }
)


class ImagingRetinotopy(NWBDataInterface):
    """
    Intrinsic signal optical imaging or widefield imaging for measuring retinotopy. Stores orthogonal maps (e.g., altitude/azimuth; radius/theta) of responses to specific stimuli and a combined polarity map from which to identify visual areas. This group does not store the raw responses imaged during retinotopic mapping or the stimuli presented, but rather the resulting phase and power maps after applying a Fourier transform on the averaged responses. Note: for data consistency, all images and arrays are stored in the format [row][column] and [row, col], which equates to [y][x]. Field of view and dimension arrays may appear backward (i.e., y before x).
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.retinotopy", "tree_root": True}
    )

    name: str = Field(
        "ImagingRetinotopy",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(ImagingRetinotopy)"}},
    )
    axis_1_phase_map: ImagingRetinotopyAxis1PhaseMap = Field(
        ..., description="""Phase response to stimulus on the first measured axis."""
    )
    axis_1_power_map: Optional[ImagingRetinotopyAxis1PowerMap] = Field(
        None,
        description="""Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.""",
    )
    axis_2_phase_map: ImagingRetinotopyAxis2PhaseMap = Field(
        ..., description="""Phase response to stimulus on the second measured axis."""
    )
    axis_2_power_map: Optional[ImagingRetinotopyAxis2PowerMap] = Field(
        None,
        description="""Power response on the second measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.""",
    )
    axis_descriptions: NDArray[Shape["2 axis_1_axis_2"], str] = Field(
        ...,
        description="""Two-element array describing the contents of the two response axis fields. Description should be something like ['altitude', 'azimuth'] or '['radius', 'theta'].""",
        json_schema_extra={
            "linkml_meta": {
                "array": {"dimensions": [{"alias": "axis_1_axis_2", "exact_cardinality": 2}]}
            }
        },
    )
    focal_depth_image: Optional[ImagingRetinotopyFocalDepthImage] = Field(
        None,
        description="""Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].""",
    )
    sign_map: Optional[ImagingRetinotopySignMap] = Field(
        None,
        description="""Sine of the angle between the direction of the gradient in axis_1 and axis_2.""",
    )
    vasculature_image: ImagingRetinotopyVasculatureImage = Field(
        ...,
        description="""Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]""",
    )


class ImagingRetinotopyAxis1PhaseMap(ConfiguredBaseModel):
    """
    Phase response to stimulus on the first measured axis.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.retinotopy"})

    name: Literal["axis_1_phase_map"] = Field(
        "axis_1_phase_map",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "axis_1_phase_map",
                "ifabsent": "string(axis_1_phase_map)",
            }
        },
    )
    dimension: List[int] = Field(
        ...,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: List[float] = Field(..., description="""Size of viewing area, in meters.""")
    unit: str = Field(..., description="""Unit that axis data is stored in (e.g., degrees).""")
    value: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}, {"alias": "num_cols"}]}}
        },
    )


class ImagingRetinotopyAxis1PowerMap(ConfiguredBaseModel):
    """
    Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.retinotopy"})

    name: Literal["axis_1_power_map"] = Field(
        "axis_1_power_map",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "axis_1_power_map",
                "ifabsent": "string(axis_1_power_map)",
            }
        },
    )
    dimension: List[int] = Field(
        ...,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: List[float] = Field(..., description="""Size of viewing area, in meters.""")
    unit: str = Field(..., description="""Unit that axis data is stored in (e.g., degrees).""")
    value: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}, {"alias": "num_cols"}]}}
        },
    )


class ImagingRetinotopyAxis2PhaseMap(ConfiguredBaseModel):
    """
    Phase response to stimulus on the second measured axis.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.retinotopy"})

    name: Literal["axis_2_phase_map"] = Field(
        "axis_2_phase_map",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "axis_2_phase_map",
                "ifabsent": "string(axis_2_phase_map)",
            }
        },
    )
    dimension: List[int] = Field(
        ...,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: List[float] = Field(..., description="""Size of viewing area, in meters.""")
    unit: str = Field(..., description="""Unit that axis data is stored in (e.g., degrees).""")
    value: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}, {"alias": "num_cols"}]}}
        },
    )


class ImagingRetinotopyAxis2PowerMap(ConfiguredBaseModel):
    """
    Power response on the second measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.retinotopy"})

    name: Literal["axis_2_power_map"] = Field(
        "axis_2_power_map",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "axis_2_power_map",
                "ifabsent": "string(axis_2_power_map)",
            }
        },
    )
    dimension: List[int] = Field(
        ...,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: List[float] = Field(..., description="""Size of viewing area, in meters.""")
    unit: str = Field(..., description="""Unit that axis data is stored in (e.g., degrees).""")
    value: Optional[NDArray[Shape["* num_rows, * num_cols"], float]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}, {"alias": "num_cols"}]}}
        },
    )


class ImagingRetinotopyFocalDepthImage(ConfiguredBaseModel):
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
    bits_per_pixel: int = Field(
        ...,
        description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value.""",
    )
    dimension: List[int] = Field(
        ...,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: List[float] = Field(..., description="""Size of viewing area, in meters.""")
    focal_depth: float = Field(..., description="""Focal depth offset, in meters.""")
    format: str = Field(..., description="""Format of image. Right now only 'raw' is supported.""")
    value: Optional[NDArray[Shape["* num_rows, * num_cols"], int]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}, {"alias": "num_cols"}]}}
        },
    )


class ImagingRetinotopySignMap(ConfiguredBaseModel):
    """
    Sine of the angle between the direction of the gradient in axis_1 and axis_2.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.retinotopy"})

    name: Literal["sign_map"] = Field(
        "sign_map",
        json_schema_extra={
            "linkml_meta": {"equals_string": "sign_map", "ifabsent": "string(sign_map)"}
        },
    )
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


class ImagingRetinotopyVasculatureImage(ConfiguredBaseModel):
    """
    Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.retinotopy"})

    name: Literal["vasculature_image"] = Field(
        "vasculature_image",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "vasculature_image",
                "ifabsent": "string(vasculature_image)",
            }
        },
    )
    bits_per_pixel: int = Field(
        ...,
        description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value""",
    )
    dimension: List[int] = Field(
        ...,
        description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""",
    )
    field_of_view: List[float] = Field(..., description="""Size of viewing area, in meters.""")
    format: str = Field(..., description="""Format of image. Right now only 'raw' is supported.""")
    value: Optional[NDArray[Shape["* num_rows, * num_cols"], int]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}, {"alias": "num_cols"}]}}
        },
    )


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
