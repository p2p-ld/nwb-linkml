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
    DynamicTableRegion,
    VectorData,
    VectorIndex
)

from .nwb_language import (
    Arraylike
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


class AbstractFeatureSeriesData(ConfiguredBaseModel):
    """
    Values of each feature at each time.
    """
    name: str = Field("data", const=True)
    unit: Optional[str] = Field(None, description="""Since there can be different units for different features, store the units in 'feature_units'. The default value for this attribute is \"see 'feature_units'\".""")
    array: Optional[Union[
        NDArray[Shape["* num_times"], Number],
        NDArray[Shape["* num_times, * num_features"], Number]
    ]] = Field(None)
    

class AbstractFeatureSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    num_features: Optional[float] = Field(None)
    

class DecompositionSeriesData(ConfiguredBaseModel):
    """
    Data decomposed into frequency bands.
    """
    name: str = Field("data", const=True)
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""")
    array: Optional[NDArray[Shape["* num_times, * num_channels, * num_bands"], Number]] = Field(None)
    

class DecompositionSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    num_channels: float = Field(...)
    num_bands: float = Field(...)
    

class DecompositionSeriesSourceChannels(DynamicTableRegion):
    """
    DynamicTableRegion pointer to the channels that this decomposition series was generated from.
    """
    name: str = Field("source_channels", const=True)
    table: Optional[DynamicTable] = Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class UnitsSpikeTimesIndex(VectorIndex):
    """
    Index into the spike_times dataset.
    """
    name: str = Field("spike_times_index", const=True)
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class UnitsSpikeTimes(VectorData):
    """
    Spike times for each unit in seconds.
    """
    name: str = Field("spike_times", const=True)
    resolution: Optional[float] = Field(None, description="""The smallest possible difference between two spike times. Usually 1 divided by the acquisition sampling rate from which spike times were extracted, but could be larger if the acquisition time series was downsampled or smaller if the acquisition time series was smoothed/interpolated and it is possible for the spike time to be between samples.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class UnitsObsIntervalsIndex(VectorIndex):
    """
    Index into the obs_intervals dataset.
    """
    name: str = Field("obs_intervals_index", const=True)
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class UnitsObsIntervals(VectorData):
    """
    Observation intervals for each unit.
    """
    name: str = Field("obs_intervals", const=True)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class UnitsElectrodesIndex(VectorIndex):
    """
    Index into electrodes.
    """
    name: str = Field("electrodes_index", const=True)
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class UnitsElectrodes(DynamicTableRegion):
    """
    Electrode that each spike unit came from, specified using a DynamicTableRegion.
    """
    name: str = Field("electrodes", const=True)
    table: Optional[DynamicTable] = Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class UnitsWaveformMean(VectorData):
    """
    Spike waveform mean for each spike unit.
    """
    name: str = Field("waveform_mean", const=True)
    sampling_rate: Optional[float] = Field(None, description="""Sampling rate, in hertz.""")
    unit: Optional[str] = Field(None, description="""Unit of measurement. This value is fixed to 'volts'.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class UnitsWaveformSd(VectorData):
    """
    Spike waveform standard deviation for each spike unit.
    """
    name: str = Field("waveform_sd", const=True)
    sampling_rate: Optional[float] = Field(None, description="""Sampling rate, in hertz.""")
    unit: Optional[str] = Field(None, description="""Unit of measurement. This value is fixed to 'volts'.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class UnitsWaveforms(VectorData):
    """
    Individual waveforms for each spike on each electrode. This is a doubly indexed column. The 'waveforms_index' column indexes which waveforms in this column belong to the same spike event for a given unit, where each waveform was recorded from a different electrode. The 'waveforms_index_index' column indexes the 'waveforms_index' column to indicate which spike events belong to a given unit. For example, if the 'waveforms_index_index' column has values [2, 5, 6], then the first 2 elements of the 'waveforms_index' column correspond to the 2 spike events of the first unit, the next 3 elements of the 'waveforms_index' column correspond to the 3 spike events of the second unit, and the next 1 element of the 'waveforms_index' column corresponds to the 1 spike event of the third unit. If the 'waveforms_index' column has values [3, 6, 8, 10, 12, 13], then the first 3 elements of the 'waveforms' column contain the 3 spike waveforms that were recorded from 3 different electrodes for the first spike time of the first unit. See https://nwb-schema.readthedocs.io/en/stable/format_description.html#doubly-ragged-arrays for a graphical representation of this example. When there is only one electrode for each unit (i.e., each spike time is associated with a single waveform), then the 'waveforms_index' column will have values 1, 2, ..., N, where N is the number of spike events. The number of electrodes for each spike event should be the same within a given unit. The 'electrodes' column should be used to indicate which electrodes are associated with each unit, and the order of the waveforms within a given unit x spike event should be in the same order as the electrodes referenced in the 'electrodes' column of this table. The number of samples for each waveform must be the same.
    """
    name: str = Field("waveforms", const=True)
    sampling_rate: Optional[float] = Field(None, description="""Sampling rate, in hertz.""")
    unit: Optional[str] = Field(None, description="""Unit of measurement. This value is fixed to 'volts'.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class UnitsWaveformsIndex(VectorIndex):
    """
    Index into the waveforms dataset. One value for every spike event. See 'waveforms' for more detail.
    """
    name: str = Field("waveforms_index", const=True)
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class UnitsWaveformsIndexIndex(VectorIndex):
    """
    Index into the waveforms_index dataset. One value for every unit (row in the table). See 'waveforms' for more detail.
    """
    name: str = Field("waveforms_index_index", const=True)
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
AbstractFeatureSeriesData.model_rebuild()
AbstractFeatureSeriesDataArray.model_rebuild()
DecompositionSeriesData.model_rebuild()
DecompositionSeriesDataArray.model_rebuild()
DecompositionSeriesSourceChannels.model_rebuild()
UnitsSpikeTimesIndex.model_rebuild()
UnitsSpikeTimes.model_rebuild()
UnitsObsIntervalsIndex.model_rebuild()
UnitsObsIntervals.model_rebuild()
UnitsElectrodesIndex.model_rebuild()
UnitsElectrodes.model_rebuild()
UnitsWaveformMean.model_rebuild()
UnitsWaveformSd.model_rebuild()
UnitsWaveforms.model_rebuild()
UnitsWaveformsIndex.model_rebuild()
UnitsWaveformsIndexIndex.model_rebuild()
    