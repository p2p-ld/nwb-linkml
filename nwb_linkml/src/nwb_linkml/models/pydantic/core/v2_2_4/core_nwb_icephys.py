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


from .core_nwb_base import (
    TimeSeriesStartingTime,
    NWBContainer,
    TimeSeries,
    TimeSeriesSync,
)

from ...hdmf_common.v1_1_3.hdmf_common_table import (
    DynamicTable,
    VectorIndex,
    VectorData,
)


metamodel_version = "None"
version = "2.2.4"


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


class PatchClampSeries(TimeSeries):
    """
    An abstract base class for patch-clamp data - stimulus or response, current or voltage.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    stimulus_description: Optional[str] = Field(
        None, description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[int] = Field(
        None,
        description="""Sweep number, allows to group different PatchClampSeries together.""",
    )
    data: str = Field(..., description="""Recorded voltage or current.""")
    gain: Optional[float] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
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


class PatchClampSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage or current.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["data"] = Field("data")
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    array: Optional[NDArray[Shape["* num_times"], float]] = Field(None)


class CurrentClampSeries(PatchClampSeries):
    """
    Voltage data from an intracellular current-clamp recording. A corresponding CurrentClampStimulusSeries (stored separately as a stimulus) is used to store the current injected.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    data: str = Field(..., description="""Recorded voltage.""")
    bias_current: Optional[float] = Field(
        None, description="""Bias current, in amps."""
    )
    bridge_balance: Optional[float] = Field(
        None, description="""Bridge balance, in ohms."""
    )
    capacitance_compensation: Optional[float] = Field(
        None, description="""Capacitance compensation, in farads."""
    )
    stimulus_description: Optional[str] = Field(
        None, description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[int] = Field(
        None,
        description="""Sweep number, allows to group different PatchClampSeries together.""",
    )
    gain: Optional[float] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
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


class CurrentClampSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["data"] = Field("data")
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. which is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    value: Any = Field(...)


class IZeroClampSeries(CurrentClampSeries):
    """
    Voltage data from an intracellular recording when all current and amplifier settings are off (i.e., CurrentClampSeries fields will be zero). There is no CurrentClampStimulusSeries associated with an IZero series because the amplifier is disconnected and no stimulus can reach the cell.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    bias_current: float = Field(
        ..., description="""Bias current, in amps, fixed to 0.0."""
    )
    bridge_balance: float = Field(
        ..., description="""Bridge balance, in ohms, fixed to 0.0."""
    )
    capacitance_compensation: float = Field(
        ..., description="""Capacitance compensation, in farads, fixed to 0.0."""
    )
    data: str = Field(..., description="""Recorded voltage.""")
    stimulus_description: Optional[str] = Field(
        None, description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[int] = Field(
        None,
        description="""Sweep number, allows to group different PatchClampSeries together.""",
    )
    gain: Optional[float] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
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


class CurrentClampStimulusSeries(PatchClampSeries):
    """
    Stimulus current applied during current clamp recording.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    data: str = Field(..., description="""Stimulus current applied.""")
    stimulus_description: Optional[str] = Field(
        None, description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[int] = Field(
        None,
        description="""Sweep number, allows to group different PatchClampSeries together.""",
    )
    gain: Optional[float] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
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


class CurrentClampStimulusSeriesData(ConfiguredBaseModel):
    """
    Stimulus current applied.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["data"] = Field("data")
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. which is fixed to 'amperes'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    value: Any = Field(...)


class VoltageClampSeries(PatchClampSeries):
    """
    Current data from an intracellular voltage-clamp recording. A corresponding VoltageClampStimulusSeries (stored separately as a stimulus) is used to store the voltage injected.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    data: str = Field(..., description="""Recorded current.""")
    capacitance_fast: Optional[str] = Field(
        None, description="""Fast capacitance, in farads."""
    )
    capacitance_slow: Optional[str] = Field(
        None, description="""Slow capacitance, in farads."""
    )
    resistance_comp_bandwidth: Optional[str] = Field(
        None, description="""Resistance compensation bandwidth, in hertz."""
    )
    resistance_comp_correction: Optional[str] = Field(
        None, description="""Resistance compensation correction, in percent."""
    )
    resistance_comp_prediction: Optional[str] = Field(
        None, description="""Resistance compensation prediction, in percent."""
    )
    whole_cell_capacitance_comp: Optional[str] = Field(
        None, description="""Whole cell capacitance compensation, in farads."""
    )
    whole_cell_series_resistance_comp: Optional[str] = Field(
        None, description="""Whole cell series resistance compensation, in ohms."""
    )
    stimulus_description: Optional[str] = Field(
        None, description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[int] = Field(
        None,
        description="""Sweep number, allows to group different PatchClampSeries together.""",
    )
    gain: Optional[float] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
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


class VoltageClampSeriesData(ConfiguredBaseModel):
    """
    Recorded current.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["data"] = Field("data")
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. which is fixed to 'amperes'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    value: Any = Field(...)


class VoltageClampSeriesCapacitanceFast(ConfiguredBaseModel):
    """
    Fast capacitance, in farads.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["capacitance_fast"] = Field("capacitance_fast")
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for capacitance_fast, which is fixed to 'farads'.""",
    )
    value: float = Field(...)


class VoltageClampSeriesCapacitanceSlow(ConfiguredBaseModel):
    """
    Slow capacitance, in farads.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["capacitance_slow"] = Field("capacitance_slow")
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for capacitance_fast, which is fixed to 'farads'.""",
    )
    value: float = Field(...)


class VoltageClampSeriesResistanceCompBandwidth(ConfiguredBaseModel):
    """
    Resistance compensation bandwidth, in hertz.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["resistance_comp_bandwidth"] = Field("resistance_comp_bandwidth")
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for resistance_comp_bandwidth, which is fixed to 'hertz'.""",
    )
    value: float = Field(...)


class VoltageClampSeriesResistanceCompCorrection(ConfiguredBaseModel):
    """
    Resistance compensation correction, in percent.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["resistance_comp_correction"] = Field("resistance_comp_correction")
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for resistance_comp_correction, which is fixed to 'percent'.""",
    )
    value: float = Field(...)


class VoltageClampSeriesResistanceCompPrediction(ConfiguredBaseModel):
    """
    Resistance compensation prediction, in percent.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["resistance_comp_prediction"] = Field("resistance_comp_prediction")
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for resistance_comp_prediction, which is fixed to 'percent'.""",
    )
    value: float = Field(...)


class VoltageClampSeriesWholeCellCapacitanceComp(ConfiguredBaseModel):
    """
    Whole cell capacitance compensation, in farads.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["whole_cell_capacitance_comp"] = Field("whole_cell_capacitance_comp")
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for whole_cell_capacitance_comp, which is fixed to 'farads'.""",
    )
    value: float = Field(...)


class VoltageClampSeriesWholeCellSeriesResistanceComp(ConfiguredBaseModel):
    """
    Whole cell series resistance compensation, in ohms.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["whole_cell_series_resistance_comp"] = Field(
        "whole_cell_series_resistance_comp"
    )
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for whole_cell_series_resistance_comp, which is fixed to 'ohms'.""",
    )
    value: float = Field(...)


class VoltageClampStimulusSeries(PatchClampSeries):
    """
    Stimulus voltage applied during a voltage clamp recording.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    data: str = Field(..., description="""Stimulus voltage applied.""")
    stimulus_description: Optional[str] = Field(
        None, description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[int] = Field(
        None,
        description="""Sweep number, allows to group different PatchClampSeries together.""",
    )
    gain: Optional[float] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
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


class VoltageClampStimulusSeriesData(ConfiguredBaseModel):
    """
    Stimulus voltage applied.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["data"] = Field("data")
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. which is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    value: Any = Field(...)


class IntracellularElectrode(NWBContainer):
    """
    An intracellular electrode and its metadata.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    description: str = Field(
        ...,
        description="""Description of electrode (e.g.,  whole-cell, sharp, etc.).""",
    )
    filtering: Optional[str] = Field(
        None, description="""Electrode specific filtering."""
    )
    initial_access_resistance: Optional[str] = Field(
        None, description="""Initial access resistance."""
    )
    location: Optional[str] = Field(
        None,
        description="""Location of the electrode. Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""",
    )
    resistance: Optional[str] = Field(
        None, description="""Electrode resistance, in ohms."""
    )
    seal: Optional[str] = Field(
        None, description="""Information about seal used for recording."""
    )
    slice: Optional[str] = Field(
        None, description="""Information about slice used for recording."""
    )


class SweepTable(DynamicTable):
    """
    The table which groups different PatchClampSeries together.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    sweep_number: Optional[List[int] | int] = Field(
        default_factory=list,
        description="""Sweep number of the PatchClampSeries in that row.""",
    )
    series: Optional[List[str] | str] = Field(
        default_factory=list,
        description="""The PatchClampSeries with the sweep number in that row.""",
    )
    series_index: str = Field(..., description="""Index for series.""")
    colnames: Optional[str] = Field(
        None,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of what is in this dynamic table."""
    )
    id: NDArray[Shape["* num_rows"], int] = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
    )
    vector_data: Optional[List[str] | str] = Field(
        default_factory=list, description="""Vector columns of this dynamic table."""
    )
    vector_index: Optional[List[str] | str] = Field(
        default_factory=list,
        description="""Indices for the vector columns of this dynamic table.""",
    )


class SweepTableSeriesIndex(VectorIndex):
    """
    Index for series.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["series_index"] = Field("series_index")
    target: Optional[str] = Field(
        None,
        description="""Reference to the target dataset that this index applies to.""",
    )
    array: Optional[NDArray[Shape["* num_rows"], Any]] = Field(None)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
PatchClampSeries.model_rebuild()
PatchClampSeriesData.model_rebuild()
CurrentClampSeries.model_rebuild()
CurrentClampSeriesData.model_rebuild()
IZeroClampSeries.model_rebuild()
CurrentClampStimulusSeries.model_rebuild()
CurrentClampStimulusSeriesData.model_rebuild()
VoltageClampSeries.model_rebuild()
VoltageClampSeriesData.model_rebuild()
VoltageClampSeriesCapacitanceFast.model_rebuild()
VoltageClampSeriesCapacitanceSlow.model_rebuild()
VoltageClampSeriesResistanceCompBandwidth.model_rebuild()
VoltageClampSeriesResistanceCompCorrection.model_rebuild()
VoltageClampSeriesResistanceCompPrediction.model_rebuild()
VoltageClampSeriesWholeCellCapacitanceComp.model_rebuild()
VoltageClampSeriesWholeCellSeriesResistanceComp.model_rebuild()
VoltageClampStimulusSeries.model_rebuild()
VoltageClampStimulusSeriesData.model_rebuild()
IntracellularElectrode.model_rebuild()
SweepTable.model_rebuild()
SweepTableSeriesIndex.model_rebuild()
