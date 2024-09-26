from __future__ import annotations

import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union

import numpy as np
from numpydantic import NDArray, Shape
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator, model_validator

from ...core.v2_6_0_alpha.core_nwb_base import (
    NWBDataInterface,
    TimeSeries,
    TimeSeriesStartingTime,
    TimeSeriesSync,
)
from ...core.v2_6_0_alpha.core_nwb_misc import IntervalSeries


metamodel_version = "None"
version = "2.6.0-alpha"


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
linkml_meta = LinkMLMeta(
    {
        "annotations": {
            "is_namespace": {"tag": "is_namespace", "value": False},
            "namespace": {"tag": "namespace", "value": "core"},
        },
        "default_prefix": "core.nwb.behavior/",
        "id": "core.nwb.behavior",
        "imports": ["core.nwb.base", "core.nwb.misc", "core.nwb.language"],
        "name": "core.nwb.behavior",
    }
)


class SpatialSeries(TimeSeries):
    """
    Direction, e.g., of gaze or travel, or position. The TimeSeries::data field is a 2D array storing position or direction relative to some reference frame. Array structure: [num measurements] [num dimensions]. Each SpatialSeries has a text dataset reference_frame that indicates the zero-position, or the zero-axes for direction. For example, if representing gaze direction, 'straight-ahead' might be a specific pixel on the monitor, or some other point in space. For position data, the 0,0 point might be the top-left corner of an enclosure, as viewed from the tracking camera. The unit of data will indicate how to interpret SpatialSeries values.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    name: str = Field(...)
    data: SpatialSeriesData = Field(
        ...,
        description="""1-D or 2-D array storing position or direction relative to some reference frame.""",
    )
    reference_frame: Optional[str] = Field(
        None, description="""Description defining what exactly 'straight-ahead' means."""
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


class SpatialSeriesData(ConfiguredBaseModel):
    """
    1-D or 2-D array storing position or direction relative to some reference frame.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.behavior"})

    name: Literal["data"] = Field(
        "data",
        json_schema_extra={"linkml_meta": {"equals_string": "data", "ifabsent": "string(data)"}},
    )
    continuity: Optional[str] = Field(
        None,
        description="""Optionally describe the continuity of the data. Can be \"continuous\", \"instantaneous\", or \"step\". For example, a voltage trace would be \"continuous\", because samples are recorded from a continuous process. An array of lick times would be \"instantaneous\", because the data represents distinct moments in time. Times of image presentations would be \"step\" because the picture remains the same until the next timepoint. This field is optional, but is useful in providing information about the underlying data. It may inform the way this data is interpreted, the way it is visualized, and what analysis methods are applicable.""",
    )
    conversion: Optional[float] = Field(
        1.0,
        description="""Scalar to multiply each element in data to convert it to the specified 'unit'. If the data are stored in acquisition system units or other units that require a conversion to be interpretable, multiply the data by 'conversion' to convert the data to the specified 'unit'. e.g. if the data acquisition system stores values in this object as signed 16-bit integers (int16 range -32,768 to 32,767) that correspond to a 5V range (-2.5V to 2.5V), and the data acquisition system gain is 8000X, then the 'conversion' multiplier to get from raw data acquisition values to recorded volts is 2.5/32768/8000 = 9.5367e-9.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "float(1.0)"}},
    )
    offset: Optional[float] = Field(
        None,
        description="""Scalar to add to the data after scaling by 'conversion' to finalize its coercion to the specified 'unit'. Two common examples of this include (a) data stored in an unsigned type that requires a shift after scaling to re-center the data, and (b) specialized recording devices that naturally cause a scalar offset with respect to the true units.""",
    )
    resolution: Optional[float] = Field(
        -1.0,
        description="""Smallest meaningful difference between values in data, stored in the specified by unit, e.g., the change in value of the least significant bit, or a larger number if signal noise is known to be present. If unknown, use -1.0.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "float(-1.0)"}},
    )
    unit: Optional[str] = Field(
        "meters",
        description="""Base unit of measurement for working with the data. The default value is 'meters'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(meters)"}},
    )
    value: Optional[
        Union[
            NDArray[Shape["* num_times"], float | int],
            NDArray[Shape["* num_times, 1 x"], float | int],
            NDArray[Shape["* num_times, 2 x_y"], float | int],
            NDArray[Shape["* num_times, 3 x_y_z"], float | int],
        ]
    ] = Field(None)


class BehavioralEpochs(NWBDataInterface):
    """
    TimeSeries for storing behavioral epochs.  The objective of this and the other two Behavioral interfaces (e.g. BehavioralEvents and BehavioralTimeSeries) is to provide generic hooks for software tools/scripts. This allows a tool/script to take the output one specific interface (e.g., UnitTimes) and plot that data relative to another data modality (e.g., behavioral events) without having to define all possible modalities in advance. Declaring one of these interfaces means that one or more TimeSeries of the specified type is published. These TimeSeries should reside in a group having the same name as the interface. For example, if a BehavioralTimeSeries interface is declared, the module will have one or more TimeSeries defined in the module sub-group 'BehavioralTimeSeries'. BehavioralEpochs should use IntervalSeries. BehavioralEvents is used for irregular events. BehavioralTimeSeries is for continuous data.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    name: str = Field(
        "BehavioralEpochs",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(BehavioralEpochs)"}},
    )
    value: Optional[Dict[str, IntervalSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "IntervalSeries"}]}}
    )


class BehavioralEvents(NWBDataInterface):
    """
    TimeSeries for storing behavioral events. See description of <a href=\"#BehavioralEpochs\">BehavioralEpochs</a> for more details.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    name: str = Field(
        "BehavioralEvents",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(BehavioralEvents)"}},
    )
    value: Optional[Dict[str, TimeSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "TimeSeries"}]}}
    )


class BehavioralTimeSeries(NWBDataInterface):
    """
    TimeSeries for storing Behavoioral time series data. See description of <a href=\"#BehavioralEpochs\">BehavioralEpochs</a> for more details.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    name: str = Field(
        "BehavioralTimeSeries",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(BehavioralTimeSeries)"}},
    )
    value: Optional[Dict[str, TimeSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "TimeSeries"}]}}
    )


class PupilTracking(NWBDataInterface):
    """
    Eye-tracking data, representing pupil size.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    name: str = Field(
        "PupilTracking", json_schema_extra={"linkml_meta": {"ifabsent": "string(PupilTracking)"}}
    )
    value: Optional[Dict[str, TimeSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "TimeSeries"}]}}
    )


class EyeTracking(NWBDataInterface):
    """
    Eye-tracking data, representing direction of gaze.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    name: str = Field(
        "EyeTracking", json_schema_extra={"linkml_meta": {"ifabsent": "string(EyeTracking)"}}
    )
    value: Optional[Dict[str, SpatialSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "SpatialSeries"}]}}
    )


class CompassDirection(NWBDataInterface):
    """
    With a CompassDirection interface, a module publishes a SpatialSeries object representing a floating point value for theta. The SpatialSeries::reference_frame field should indicate what direction corresponds to 0 and which is the direction of rotation (this should be clockwise). The si_unit for the SpatialSeries should be radians or degrees.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    name: str = Field(
        "CompassDirection",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(CompassDirection)"}},
    )
    value: Optional[Dict[str, SpatialSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "SpatialSeries"}]}}
    )


class Position(NWBDataInterface):
    """
    Position data, whether along the x, x/y or x/y/z axis.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    name: str = Field(
        "Position", json_schema_extra={"linkml_meta": {"ifabsent": "string(Position)"}}
    )
    value: Optional[Dict[str, SpatialSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "SpatialSeries"}]}}
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
SpatialSeries.model_rebuild()
SpatialSeriesData.model_rebuild()
BehavioralEpochs.model_rebuild()
BehavioralEvents.model_rebuild()
BehavioralTimeSeries.model_rebuild()
PupilTracking.model_rebuild()
EyeTracking.model_rebuild()
CompassDirection.model_rebuild()
Position.model_rebuild()
