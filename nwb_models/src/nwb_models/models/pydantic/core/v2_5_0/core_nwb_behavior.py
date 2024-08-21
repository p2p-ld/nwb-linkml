from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
import numpy as np
from numpydantic import NDArray, Shape
from ...core.v2_5_0.core_nwb_misc import IntervalSeries
from ...core.v2_5_0.core_nwb_base import (
    TimeSeries,
    TimeSeriesStartingTime,
    TimeSeriesSync,
    NWBDataInterface,
)

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
    unit: Optional[str] = Field(
        "meters",
        description="""Base unit of measurement for working with the data. The default value is 'meters'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(meters)"}},
    )
    value: Optional[
        Union[
            NDArray[Shape["* num_times"], float],
            NDArray[Shape["* num_times, 1 x"], float],
            NDArray[Shape["* num_times, 2 x_y"], float],
            NDArray[Shape["* num_times, 3 x_y_z"], float],
        ]
    ] = Field(None)


class BehavioralEpochs(NWBDataInterface):
    """
    TimeSeries for storing behavioral epochs.  The objective of this and the other two Behavioral interfaces (e.g. BehavioralEvents and BehavioralTimeSeries) is to provide generic hooks for software tools/scripts. This allows a tool/script to take the output one specific interface (e.g., UnitTimes) and plot that data relative to another data modality (e.g., behavioral events) without having to define all possible modalities in advance. Declaring one of these interfaces means that one or more TimeSeries of the specified type is published. These TimeSeries should reside in a group having the same name as the interface. For example, if a BehavioralTimeSeries interface is declared, the module will have one or more TimeSeries defined in the module sub-group 'BehavioralTimeSeries'. BehavioralEpochs should use IntervalSeries. BehavioralEvents is used for irregular events. BehavioralTimeSeries is for continuous data.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    value: Optional[List[IntervalSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "IntervalSeries"}]}}
    )
    name: str = Field(...)


class BehavioralEvents(NWBDataInterface):
    """
    TimeSeries for storing behavioral events. See description of <a href=\"#BehavioralEpochs\">BehavioralEpochs</a> for more details.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    value: Optional[List[TimeSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "TimeSeries"}]}}
    )
    name: str = Field(...)


class BehavioralTimeSeries(NWBDataInterface):
    """
    TimeSeries for storing Behavoioral time series data. See description of <a href=\"#BehavioralEpochs\">BehavioralEpochs</a> for more details.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    value: Optional[List[TimeSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "TimeSeries"}]}}
    )
    name: str = Field(...)


class PupilTracking(NWBDataInterface):
    """
    Eye-tracking data, representing pupil size.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    value: Optional[List[TimeSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "TimeSeries"}]}}
    )
    name: str = Field(...)


class EyeTracking(NWBDataInterface):
    """
    Eye-tracking data, representing direction of gaze.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    value: Optional[List[SpatialSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "SpatialSeries"}]}}
    )
    name: str = Field(...)


class CompassDirection(NWBDataInterface):
    """
    With a CompassDirection interface, a module publishes a SpatialSeries object representing a floating point value for theta. The SpatialSeries::reference_frame field should indicate what direction corresponds to 0 and which is the direction of rotation (this should be clockwise). The si_unit for the SpatialSeries should be radians or degrees.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    value: Optional[List[SpatialSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "SpatialSeries"}]}}
    )
    name: str = Field(...)


class Position(NWBDataInterface):
    """
    Position data, whether along the x, x/y or x/y/z axis.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.behavior", "tree_root": True}
    )

    value: Optional[List[SpatialSeries]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "SpatialSeries"}]}}
    )
    name: str = Field(...)


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
