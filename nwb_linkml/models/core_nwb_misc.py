from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, Field
from nptyping import NDArray, Shape, Float, Float32, Double, Float64, LongLong, Int64, Int, Int32, Int16, Short, Int8, UInt, UInt32, UInt16, UInt8, UInt64, Number, String, Unicode, Unicode, Unicode, String, Bool, Datetime64
import sys
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


from .hdmf_common_table import (
    DynamicTable
)

from .core_nwb_misc_include import (
    UnitsElectrodes,
    UnitsElectrodesIndex,
    UnitsObsIntervalsIndex,
    UnitsSpikeTimes,
    UnitsSpikeTimesIndex,
    UnitsWaveformSd,
    UnitsWaveformMean,
    UnitsWaveforms,
    AbstractFeatureSeriesData,
    UnitsWaveformsIndexIndex,
    UnitsObsIntervals,
    UnitsWaveformsIndex,
    DecompositionSeriesData,
    DecompositionSeriesSourceChannels
)

from .core_nwb_base import (
    TimeSeries
)

from .core_nwb_ecephys import (
    ElectrodeGroup
)


metamodel_version = "None"
version = "None"

class ConfiguredBaseModel(BaseModel,
                validate_assignment = True,
                validate_default = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


class AbstractFeatureSeries(TimeSeries):
    """
    Abstract features, such as quantitative descriptions of sensory stimuli. The TimeSeries::data field is a 2D array, storing those features (e.g., for visual grating stimulus this might be orientation, spatial frequency and contrast). Null stimuli (eg, uniform gray) can be marked as being an independent feature (eg, 1.0 for gray, 0.0 for actual stimulus) or by storing NaNs for feature values, or through use of the TimeSeries::control fields. A set of features is considered to persist until the next set of features is defined. The final set of features stored should be the null set. This is useful when storing the raw stimulus is impractical.
    """
    name: str = Field(...)
    data: AbstractFeatureSeriesData = Field(..., description="""Values of each feature at each time.""")
    feature_units: Optional[List[str]] = Field(default_factory=list, description="""Units of each feature.""")
    features: List[str] = Field(default_factory=list, description="""Description of the features represented in TimeSeries::data.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[List[float]] = Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[List[int]] = Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[List[str]] = Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class AnnotationSeries(TimeSeries):
    """
    Stores user annotations made during an experiment. The data[] field stores a text array, and timestamps are stored for each annotation (ie, interval=1). This is largely an alias to a standard TimeSeries storing a text array but that is identifiable as storing annotations in a machine-readable way.
    """
    name: str = Field(...)
    data: List[str] = Field(default_factory=list, description="""Annotations made during an experiment.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[List[float]] = Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[List[int]] = Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[List[str]] = Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class IntervalSeries(TimeSeries):
    """
    Stores intervals of data. The timestamps field stores the beginning and end of intervals. The data field stores whether the interval just started (>0 value) or ended (<0 value). Different interval types can be represented in the same series by using multiple key values (eg, 1 for feature A, 2 for feature B, 3 for feature C, etc). The field data stores an 8-bit integer. This is largely an alias of a standard TimeSeries but that is identifiable as representing time intervals in a machine-readable way.
    """
    name: str = Field(...)
    data: List[int] = Field(default_factory=list, description="""Use values >0 if interval started, <0 if interval ended.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[List[float]] = Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[List[int]] = Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[List[str]] = Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class DecompositionSeries(TimeSeries):
    """
    Spectral analysis of a time series, e.g. of an LFP or a speech signal.
    """
    name: str = Field(...)
    data: DecompositionSeriesData = Field(..., description="""Data decomposed into frequency bands.""")
    metric: str = Field(..., description="""The metric used, e.g. phase, amplitude, power.""")
    source_channels: Optional[DecompositionSeriesSourceChannels] = Field(None, description="""DynamicTableRegion pointer to the channels that this decomposition series was generated from.""")
    bands: DynamicTable = Field(..., description="""Table for describing the bands that this series was generated from. There should be one row in this table for each band.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[List[float]] = Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[List[int]] = Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[List[str]] = Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class Units(DynamicTable):
    """
    Data about spiking units. Event times of observed units (e.g. cell, synapse, etc.) should be concatenated and stored in spike_times.
    """
    name: str = Field(...)
    spike_times_index: Optional[UnitsSpikeTimesIndex] = Field(None, description="""Index into the spike_times dataset.""")
    spike_times: Optional[UnitsSpikeTimes] = Field(None, description="""Spike times for each unit in seconds.""")
    obs_intervals_index: Optional[UnitsObsIntervalsIndex] = Field(None, description="""Index into the obs_intervals dataset.""")
    obs_intervals: Optional[UnitsObsIntervals] = Field(None, description="""Observation intervals for each unit.""")
    electrodes_index: Optional[UnitsElectrodesIndex] = Field(None, description="""Index into electrodes.""")
    electrodes: Optional[UnitsElectrodes] = Field(None, description="""Electrode that each spike unit came from, specified using a DynamicTableRegion.""")
    electrode_group: Optional[List[ElectrodeGroup]] = Field(default_factory=list, description="""Electrode group that each spike unit came from.""")
    waveform_mean: Optional[UnitsWaveformMean] = Field(None, description="""Spike waveform mean for each spike unit.""")
    waveform_sd: Optional[UnitsWaveformSd] = Field(None, description="""Spike waveform standard deviation for each spike unit.""")
    waveforms: Optional[UnitsWaveforms] = Field(None, description="""Individual waveforms for each spike on each electrode. This is a doubly indexed column. The 'waveforms_index' column indexes which waveforms in this column belong to the same spike event for a given unit, where each waveform was recorded from a different electrode. The 'waveforms_index_index' column indexes the 'waveforms_index' column to indicate which spike events belong to a given unit. For example, if the 'waveforms_index_index' column has values [2, 5, 6], then the first 2 elements of the 'waveforms_index' column correspond to the 2 spike events of the first unit, the next 3 elements of the 'waveforms_index' column correspond to the 3 spike events of the second unit, and the next 1 element of the 'waveforms_index' column corresponds to the 1 spike event of the third unit. If the 'waveforms_index' column has values [3, 6, 8, 10, 12, 13], then the first 3 elements of the 'waveforms' column contain the 3 spike waveforms that were recorded from 3 different electrodes for the first spike time of the first unit. See https://nwb-schema.readthedocs.io/en/stable/format_description.html#doubly-ragged-arrays for a graphical representation of this example. When there is only one electrode for each unit (i.e., each spike time is associated with a single waveform), then the 'waveforms_index' column will have values 1, 2, ..., N, where N is the number of spike events. The number of electrodes for each spike event should be the same within a given unit. The 'electrodes' column should be used to indicate which electrodes are associated with each unit, and the order of the waveforms within a given unit x spike event should be in the same order as the electrodes referenced in the 'electrodes' column of this table. The number of samples for each waveform must be the same.""")
    waveforms_index: Optional[UnitsWaveformsIndex] = Field(None, description="""Index into the waveforms dataset. One value for every spike event. See 'waveforms' for more detail.""")
    waveforms_index_index: Optional[UnitsWaveformsIndexIndex] = Field(None, description="""Index into the waveforms_index dataset. One value for every unit (row in the table). See 'waveforms' for more detail.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: List[int] = Field(default_factory=list, description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
AbstractFeatureSeries.model_rebuild()
AnnotationSeries.model_rebuild()
IntervalSeries.model_rebuild()
DecompositionSeries.model_rebuild()
Units.model_rebuild()
    