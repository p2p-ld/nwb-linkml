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


from .core_nwb_icephys_include import (
    IntracellularResponsesTableResponse,
    ExperimentalConditionsTableRepetitionsIndex,
    SimultaneousRecordingsTableRecordingsIndex,
    CurrentClampStimulusSeriesData,
    VoltageClampSeriesWholeCellSeriesResistanceComp,
    VoltageClampStimulusSeriesData,
    VoltageClampSeriesCapacitanceSlow,
    SimultaneousRecordingsTableRecordings,
    VoltageClampSeriesResistanceCompPrediction,
    SequentialRecordingsTableSimultaneousRecordings,
    VoltageClampSeriesCapacitanceFast,
    IntracellularStimuliTableStimulus,
    RepetitionsTableSequentialRecordingsIndex,
    VoltageClampSeriesResistanceCompBandwidth,
    VoltageClampSeriesData,
    SequentialRecordingsTableSimultaneousRecordingsIndex,
    ExperimentalConditionsTableRepetitions,
    RepetitionsTableSequentialRecordings,
    VoltageClampSeriesWholeCellCapacitanceComp,
    CurrentClampSeriesData,
    VoltageClampSeriesResistanceCompCorrection,
    SweepTableSeriesIndex
)

from .core_nwb_base import (
    NWBContainer,
    TimeSeries
)

from .hdmf_common_table import (
    AlignedDynamicTable,
    DynamicTable
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


class PatchClampSeries(TimeSeries):
    """
    An abstract base class for patch-clamp data - stimulus or response, current or voltage.
    """
    name: str = Field(...)
    stimulus_description: Optional[string] = Field(None, description="""Protocol/stimulus name for this patch-clamp dataset.""")
    sweep_number: Optional[integer] = Field(None, description="""Sweep number, allows to group different PatchClampSeries together.""")
    data: List[float] = Field(default_factory=list, description="""Recorded voltage or current.""")
    gain: Optional[float] = Field(None, description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""")
    description: Optional[string] = Field(None, description="""Description of the time series.""")
    comments: Optional[string] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[List[double]] = Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[List[integer]] = Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[List[string]] = Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class CurrentClampSeries(PatchClampSeries):
    """
    Voltage data from an intracellular current-clamp recording. A corresponding CurrentClampStimulusSeries (stored separately as a stimulus) is used to store the current injected.
    """
    name: str = Field(...)
    data: CurrentClampSeriesData = Field(..., description="""Recorded voltage.""")
    bias_current: Optional[float] = Field(None, description="""Bias current, in amps.""")
    bridge_balance: Optional[float] = Field(None, description="""Bridge balance, in ohms.""")
    capacitance_compensation: Optional[float] = Field(None, description="""Capacitance compensation, in farads.""")
    stimulus_description: Optional[string] = Field(None, description="""Protocol/stimulus name for this patch-clamp dataset.""")
    sweep_number: Optional[integer] = Field(None, description="""Sweep number, allows to group different PatchClampSeries together.""")
    gain: Optional[float] = Field(None, description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""")
    description: Optional[string] = Field(None, description="""Description of the time series.""")
    comments: Optional[string] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[List[double]] = Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[List[integer]] = Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[List[string]] = Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class IZeroClampSeries(CurrentClampSeries):
    """
    Voltage data from an intracellular recording when all current and amplifier settings are off (i.e., CurrentClampSeries fields will be zero). There is no CurrentClampStimulusSeries associated with an IZero series because the amplifier is disconnected and no stimulus can reach the cell.
    """
    name: str = Field(...)
    stimulus_description: Optional[string] = Field(None, description="""An IZeroClampSeries has no stimulus, so this attribute is automatically set to \"N/A\"""")
    bias_current: float = Field(..., description="""Bias current, in amps, fixed to 0.0.""")
    bridge_balance: float = Field(..., description="""Bridge balance, in ohms, fixed to 0.0.""")
    capacitance_compensation: float = Field(..., description="""Capacitance compensation, in farads, fixed to 0.0.""")
    data: CurrentClampSeriesData = Field(..., description="""Recorded voltage.""")
    sweep_number: Optional[integer] = Field(None, description="""Sweep number, allows to group different PatchClampSeries together.""")
    gain: Optional[float] = Field(None, description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""")
    description: Optional[string] = Field(None, description="""Description of the time series.""")
    comments: Optional[string] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[List[double]] = Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[List[integer]] = Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[List[string]] = Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class CurrentClampStimulusSeries(PatchClampSeries):
    """
    Stimulus current applied during current clamp recording.
    """
    name: str = Field(...)
    data: CurrentClampStimulusSeriesData = Field(..., description="""Stimulus current applied.""")
    stimulus_description: Optional[string] = Field(None, description="""Protocol/stimulus name for this patch-clamp dataset.""")
    sweep_number: Optional[integer] = Field(None, description="""Sweep number, allows to group different PatchClampSeries together.""")
    gain: Optional[float] = Field(None, description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""")
    description: Optional[string] = Field(None, description="""Description of the time series.""")
    comments: Optional[string] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[List[double]] = Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[List[integer]] = Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[List[string]] = Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class VoltageClampSeries(PatchClampSeries):
    """
    Current data from an intracellular voltage-clamp recording. A corresponding VoltageClampStimulusSeries (stored separately as a stimulus) is used to store the voltage injected.
    """
    name: str = Field(...)
    data: VoltageClampSeriesData = Field(..., description="""Recorded current.""")
    capacitance_fast: Optional[VoltageClampSeriesCapacitanceFast] = Field(None, description="""Fast capacitance, in farads.""")
    capacitance_slow: Optional[VoltageClampSeriesCapacitanceSlow] = Field(None, description="""Slow capacitance, in farads.""")
    resistance_comp_bandwidth: Optional[VoltageClampSeriesResistanceCompBandwidth] = Field(None, description="""Resistance compensation bandwidth, in hertz.""")
    resistance_comp_correction: Optional[VoltageClampSeriesResistanceCompCorrection] = Field(None, description="""Resistance compensation correction, in percent.""")
    resistance_comp_prediction: Optional[VoltageClampSeriesResistanceCompPrediction] = Field(None, description="""Resistance compensation prediction, in percent.""")
    whole_cell_capacitance_comp: Optional[VoltageClampSeriesWholeCellCapacitanceComp] = Field(None, description="""Whole cell capacitance compensation, in farads.""")
    whole_cell_series_resistance_comp: Optional[VoltageClampSeriesWholeCellSeriesResistanceComp] = Field(None, description="""Whole cell series resistance compensation, in ohms.""")
    stimulus_description: Optional[string] = Field(None, description="""Protocol/stimulus name for this patch-clamp dataset.""")
    sweep_number: Optional[integer] = Field(None, description="""Sweep number, allows to group different PatchClampSeries together.""")
    gain: Optional[float] = Field(None, description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""")
    description: Optional[string] = Field(None, description="""Description of the time series.""")
    comments: Optional[string] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[List[double]] = Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[List[integer]] = Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[List[string]] = Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class VoltageClampStimulusSeries(PatchClampSeries):
    """
    Stimulus voltage applied during a voltage clamp recording.
    """
    name: str = Field(...)
    data: VoltageClampStimulusSeriesData = Field(..., description="""Stimulus voltage applied.""")
    stimulus_description: Optional[string] = Field(None, description="""Protocol/stimulus name for this patch-clamp dataset.""")
    sweep_number: Optional[integer] = Field(None, description="""Sweep number, allows to group different PatchClampSeries together.""")
    gain: Optional[float] = Field(None, description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""")
    description: Optional[string] = Field(None, description="""Description of the time series.""")
    comments: Optional[string] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[List[double]] = Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[List[integer]] = Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[List[string]] = Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class IntracellularElectrode(NWBContainer):
    """
    An intracellular electrode and its metadata.
    """
    name: str = Field(...)
    cell_id: Optional[string] = Field(None, description="""unique ID of the cell""")
    description: string = Field(..., description="""Description of electrode (e.g.,  whole-cell, sharp, etc.).""")
    filtering: Optional[string] = Field(None, description="""Electrode specific filtering.""")
    initial_access_resistance: Optional[string] = Field(None, description="""Initial access resistance.""")
    location: Optional[string] = Field(None, description="""Location of the electrode. Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""")
    resistance: Optional[string] = Field(None, description="""Electrode resistance, in ohms.""")
    seal: Optional[string] = Field(None, description="""Information about seal used for recording.""")
    slice: Optional[string] = Field(None, description="""Information about slice used for recording.""")
    

class SweepTable(DynamicTable):
    """
    [DEPRECATED] Table used to group different PatchClampSeries. SweepTable is being replaced by IntracellularRecordingsTable and SimultaneousRecordingsTable tables. Additional SequentialRecordingsTable, RepetitionsTable, and ExperimentalConditions tables provide enhanced support for experiment metadata.
    """
    name: str = Field(...)
    sweep_number: Optional[List[integer]] = Field(default_factory=list, description="""Sweep number of the PatchClampSeries in that row.""")
    series: Optional[List[PatchClampSeries]] = Field(default_factory=list, description="""The PatchClampSeries with the sweep number in that row.""")
    series_index: SweepTableSeriesIndex = Field(..., description="""Index for series.""")
    colnames: Optional[string] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[string] = Field(None, description="""Description of what is in this dynamic table.""")
    id: List[integer] = Field(default_factory=list, description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularElectrodesTable(DynamicTable):
    """
    Table for storing intracellular electrode related metadata.
    """
    name: str = Field(...)
    description: Optional[string] = Field(None, description="""Description of what is in this dynamic table.""")
    electrode: Optional[List[IntracellularElectrode]] = Field(default_factory=list, description="""Column for storing the reference to the intracellular electrode.""")
    colnames: Optional[string] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: List[integer] = Field(default_factory=list, description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularStimuliTable(DynamicTable):
    """
    Table for storing intracellular stimulus related metadata.
    """
    name: str = Field(...)
    description: Optional[string] = Field(None, description="""Description of what is in this dynamic table.""")
    stimulus: IntracellularStimuliTableStimulus = Field(..., description="""Column storing the reference to the recorded stimulus for the recording (rows).""")
    colnames: Optional[string] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: List[integer] = Field(default_factory=list, description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularResponsesTable(DynamicTable):
    """
    Table for storing intracellular response related metadata.
    """
    name: str = Field(...)
    description: Optional[string] = Field(None, description="""Description of what is in this dynamic table.""")
    response: IntracellularResponsesTableResponse = Field(..., description="""Column storing the reference to the recorded response for the recording (rows)""")
    colnames: Optional[string] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: List[integer] = Field(default_factory=list, description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularRecordingsTable(AlignedDynamicTable):
    """
    A table to group together a stimulus and response from a single electrode and a single simultaneous recording. Each row in the table represents a single recording consisting typically of a stimulus and a corresponding response. In some cases, however, only a stimulus or a response is recorded as part of an experiment. In this case, both the stimulus and response will point to the same TimeSeries while the idx_start and count of the invalid column will be set to -1, thus, indicating that no values have been recorded for the stimulus or response, respectively. Note, a recording MUST contain at least a stimulus or a response. Typically the stimulus and response are PatchClampSeries. However, the use of AD/DA channels that are not associated to an electrode is also common in intracellular electrophysiology, in which case other TimeSeries may be used.
    """
    name: str = Field("intracellular_recordings", const=True)
    description: Optional[string] = Field(None, description="""Description of the contents of this table. Inherited from AlignedDynamicTable and overwritten here to fix the value of the attribute.""")
    electrodes: IntracellularElectrodesTable = Field(..., description="""Table for storing intracellular electrode related metadata.""")
    stimuli: IntracellularStimuliTable = Field(..., description="""Table for storing intracellular stimulus related metadata.""")
    responses: IntracellularResponsesTable = Field(..., description="""Table for storing intracellular response related metadata.""")
    categories: Optional[string] = Field(None, description="""The names of the categories in this AlignedDynamicTable. Each category is represented by one DynamicTable stored in the parent group. This attribute should be used to specify an order of categories and the category names must match the names of the corresponding DynamicTable in the group.""")
    dynamic_table: Optional[List[DynamicTable]] = Field(default_factory=list, description="""A DynamicTable representing a particular category for columns in the AlignedDynamicTable parent container. The table MUST be aligned with (i.e., have the same number of rows) as all other DynamicTables stored in the AlignedDynamicTable parent container. The name of the category is given by the name of the DynamicTable and its description by the description attribute of the DynamicTable.""")
    colnames: Optional[string] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: List[integer] = Field(default_factory=list, description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class SimultaneousRecordingsTable(DynamicTable):
    """
    A table for grouping different intracellular recordings from the IntracellularRecordingsTable table together that were recorded simultaneously from different electrodes.
    """
    name: str = Field("simultaneous_recordings", const=True)
    recordings: SimultaneousRecordingsTableRecordings = Field(..., description="""A reference to one or more rows in the IntracellularRecordingsTable table.""")
    recordings_index: SimultaneousRecordingsTableRecordingsIndex = Field(..., description="""Index dataset for the recordings column.""")
    colnames: Optional[string] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[string] = Field(None, description="""Description of what is in this dynamic table.""")
    id: List[integer] = Field(default_factory=list, description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class SequentialRecordingsTable(DynamicTable):
    """
    A table for grouping different sequential recordings from the SimultaneousRecordingsTable table together. This is typically used to group together sequential recordings where a sequence of stimuli of the same type with varying parameters have been presented in a sequence.
    """
    name: str = Field("sequential_recordings", const=True)
    simultaneous_recordings: SequentialRecordingsTableSimultaneousRecordings = Field(..., description="""A reference to one or more rows in the SimultaneousRecordingsTable table.""")
    simultaneous_recordings_index: SequentialRecordingsTableSimultaneousRecordingsIndex = Field(..., description="""Index dataset for the simultaneous_recordings column.""")
    stimulus_type: Optional[List[string]] = Field(default_factory=list, description="""The type of stimulus used for the sequential recording.""")
    colnames: Optional[string] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[string] = Field(None, description="""Description of what is in this dynamic table.""")
    id: List[integer] = Field(default_factory=list, description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class RepetitionsTable(DynamicTable):
    """
    A table for grouping different sequential intracellular recordings together. With each SequentialRecording typically representing a particular type of stimulus, the RepetitionsTable table is typically used to group sets of stimuli applied in sequence.
    """
    name: str = Field("repetitions", const=True)
    sequential_recordings: RepetitionsTableSequentialRecordings = Field(..., description="""A reference to one or more rows in the SequentialRecordingsTable table.""")
    sequential_recordings_index: RepetitionsTableSequentialRecordingsIndex = Field(..., description="""Index dataset for the sequential_recordings column.""")
    colnames: Optional[string] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[string] = Field(None, description="""Description of what is in this dynamic table.""")
    id: List[integer] = Field(default_factory=list, description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class ExperimentalConditionsTable(DynamicTable):
    """
    A table for grouping different intracellular recording repetitions together that belong to the same experimental condition.
    """
    name: str = Field("experimental_conditions", const=True)
    repetitions: ExperimentalConditionsTableRepetitions = Field(..., description="""A reference to one or more rows in the RepetitionsTable table.""")
    repetitions_index: ExperimentalConditionsTableRepetitionsIndex = Field(..., description="""Index dataset for the repetitions column.""")
    colnames: Optional[string] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[string] = Field(None, description="""Description of what is in this dynamic table.""")
    id: List[integer] = Field(default_factory=list, description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
PatchClampSeries.model_rebuild()
CurrentClampSeries.model_rebuild()
IZeroClampSeries.model_rebuild()
CurrentClampStimulusSeries.model_rebuild()
VoltageClampSeries.model_rebuild()
VoltageClampStimulusSeries.model_rebuild()
IntracellularElectrode.model_rebuild()
SweepTable.model_rebuild()
IntracellularElectrodesTable.model_rebuild()
IntracellularStimuliTable.model_rebuild()
IntracellularResponsesTable.model_rebuild()
IntracellularRecordingsTable.model_rebuild()
SimultaneousRecordingsTable.model_rebuild()
SequentialRecordingsTable.model_rebuild()
RepetitionsTable.model_rebuild()
ExperimentalConditionsTable.model_rebuild()
    