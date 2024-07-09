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
    TimeSeriesStartingTime,
    NWBDataInterface,
    TimeSeriesSync,
)

from .core_nwb_misc import IntervalSeries


metamodel_version = "None"
version = "2.2.1"


class ConfiguredBaseModel(BaseModel):
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


class SpatialSeries(TimeSeries):
    """
    Direction, e.g., of gaze or travel, or position. The TimeSeries::data field is a 2D array storing position or direction relative to some reference frame. Array structure: [num measurements] [num dimensions]. Each SpatialSeries has a text dataset reference_frame that indicates the zero-position, or the zero-axes for direction. For example, if representing gaze direction, 'straight-ahead' might be a specific pixel on the monitor, or some other point in space. For position data, the 0,0 point might be the top-left corner of an enclosure, as viewed from the tracking camera. The unit of data will indicate how to interpret SpatialSeries values.
    """

    name: str = Field(...)
    data: str = Field(
        ...,
        description="""1-D or 2-D array storing position or direction relative to some reference frame.""",
    )
    reference_frame: Optional[str] = Field(
        None,
        description="""Description defining what exactly 'straight-ahead' means.""",
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


class SpatialSeriesData(ConfiguredBaseModel):
    """
    1-D or 2-D array storing position or direction relative to some reference frame.
    """

    name: Literal["data"] = Field("data")
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. The default value is 'meters'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    array: Optional[
        Union[
            NDArray[Shape["* num_times"], float],
            NDArray[Shape["* num_times, * num_features"], float],
        ]
    ] = Field(None)


class BehavioralEpochs(NWBDataInterface):
    """
    TimeSeries for storing behavioral epochs.  The objective of this and the other two Behavioral interfaces (e.g. BehavioralEvents and BehavioralTimeSeries) is to provide generic hooks for software tools/scripts. This allows a tool/script to take the output one specific interface (e.g., UnitTimes) and plot that data relative to another data modality (e.g., behavioral events) without having to define all possible modalities in advance. Declaring one of these interfaces means that one or more TimeSeries of the specified type is published. These TimeSeries should reside in a group having the same name as the interface. For example, if a BehavioralTimeSeries interface is declared, the module will have one or more TimeSeries defined in the module sub-group 'BehavioralTimeSeries'. BehavioralEpochs should use IntervalSeries. BehavioralEvents is used for irregular events. BehavioralTimeSeries is for continuous data.
    """

    children: Optional[List[IntervalSeries] | IntervalSeries] = Field(
        default_factory=dict
    )
    name: str = Field(...)


class BehavioralEvents(NWBDataInterface):
    """
    TimeSeries for storing behavioral events. See description of <a href=\"#BehavioralEpochs\">BehavioralEpochs</a> for more details.
    """

    children: Optional[List[TimeSeries] | TimeSeries] = Field(default_factory=dict)
    name: str = Field(...)


class BehavioralTimeSeries(NWBDataInterface):
    """
    TimeSeries for storing Behavoioral time series data. See description of <a href=\"#BehavioralEpochs\">BehavioralEpochs</a> for more details.
    """

    children: Optional[List[TimeSeries] | TimeSeries] = Field(default_factory=dict)
    name: str = Field(...)


class PupilTracking(NWBDataInterface):
    """
    Eye-tracking data, representing pupil size.
    """

    children: Optional[List[TimeSeries] | TimeSeries] = Field(default_factory=dict)
    name: str = Field(...)


class EyeTracking(NWBDataInterface):
    """
    Eye-tracking data, representing direction of gaze.
    """

    children: Optional[List[SpatialSeries] | SpatialSeries] = Field(
        default_factory=dict
    )
    name: str = Field(...)


class CompassDirection(NWBDataInterface):
    """
    With a CompassDirection interface, a module publishes a SpatialSeries object representing a floating point value for theta. The SpatialSeries::reference_frame field should indicate what direction corresponds to 0 and which is the direction of rotation (this should be clockwise). The si_unit for the SpatialSeries should be radians or degrees.
    """

    children: Optional[List[SpatialSeries] | SpatialSeries] = Field(
        default_factory=dict
    )
    name: str = Field(...)


class Position(NWBDataInterface):
    """
    Position data, whether along the x, x/y or x/y/z axis.
    """

    children: Optional[List[SpatialSeries] | SpatialSeries] = Field(
        default_factory=dict
    )
    name: str = Field(...)
