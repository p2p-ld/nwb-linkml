from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
import numpy as np
from ...core.v2_2_4.core_nwb_base import (
    TimeSeries,
    TimeSeriesStartingTime,
    TimeSeriesSync,
    NWBContainer,
)
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union, Annotated, Type, TypeVar
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator,
    ValidationInfo,
    BeforeValidator,
)
from numpydantic import NDArray, Shape
from ...hdmf_common.v1_1_3.hdmf_common_table import DynamicTable, VectorIndex, VectorData

metamodel_version = "None"
version = "2.2.4"


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
    assert isinstance(item, (BaseModel, dict))
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
        "default_prefix": "core.nwb.icephys/",
        "id": "core.nwb.icephys",
        "imports": [
            "core.nwb.base",
            "core.nwb.device",
            "../../hdmf_common/v1_1_3/namespace",
            "core.nwb.language",
        ],
        "name": "core.nwb.icephys",
    }
)


class PatchClampSeries(TimeSeries):
    """
    An abstract base class for patch-clamp data - stimulus or response, current or voltage.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    stimulus_description: Optional[str] = Field(
        None, description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[np.uint32] = Field(
        None, description="""Sweep number, allows to group different PatchClampSeries together."""
    )
    data: PatchClampSeriesData = Field(..., description="""Recorded voltage or current.""")
    gain: Optional[np.float32] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
    )
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(
        None,
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
    )
    starting_time: Optional[TimeSeriesStartingTime] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[NDArray[Shape["* num_times"], np.float64]] = Field(
        None,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
    )
    control: Optional[NDArray[Shape["* num_times"], np.uint8]] = Field(
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


class PatchClampSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage or current.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["data"] = Field(
        "data",
        json_schema_extra={"linkml_meta": {"equals_string": "data", "ifabsent": "string(data)"}},
    )
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    array: Optional[NDArray[Shape["* num_times"], np.number]] = Field(
        None, json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}}
    )


class CurrentClampSeries(PatchClampSeries):
    """
    Voltage data from an intracellular current-clamp recording. A corresponding CurrentClampStimulusSeries (stored separately as a stimulus) is used to store the current injected.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    data: CurrentClampSeriesData = Field(..., description="""Recorded voltage.""")
    bias_current: Optional[np.float32] = Field(None, description="""Bias current, in amps.""")
    bridge_balance: Optional[np.float32] = Field(None, description="""Bridge balance, in ohms.""")
    capacitance_compensation: Optional[np.float32] = Field(
        None, description="""Capacitance compensation, in farads."""
    )
    stimulus_description: Optional[str] = Field(
        None, description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[np.uint32] = Field(
        None, description="""Sweep number, allows to group different PatchClampSeries together."""
    )
    gain: Optional[np.float32] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
    )
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(
        None,
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
    )
    starting_time: Optional[TimeSeriesStartingTime] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[NDArray[Shape["* num_times"], np.float64]] = Field(
        None,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
    )
    control: Optional[NDArray[Shape["* num_times"], np.uint8]] = Field(
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


class CurrentClampSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["data"] = Field(
        "data",
        json_schema_extra={"linkml_meta": {"equals_string": "data", "ifabsent": "string(data)"}},
    )
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. which is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    value: Any = Field(...)


class IZeroClampSeries(CurrentClampSeries):
    """
    Voltage data from an intracellular recording when all current and amplifier settings are off (i.e., CurrentClampSeries fields will be zero). There is no CurrentClampStimulusSeries associated with an IZero series because the amplifier is disconnected and no stimulus can reach the cell.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    bias_current: np.float32 = Field(..., description="""Bias current, in amps, fixed to 0.0.""")
    bridge_balance: np.float32 = Field(
        ..., description="""Bridge balance, in ohms, fixed to 0.0."""
    )
    capacitance_compensation: np.float32 = Field(
        ..., description="""Capacitance compensation, in farads, fixed to 0.0."""
    )
    data: CurrentClampSeriesData = Field(..., description="""Recorded voltage.""")
    stimulus_description: Optional[str] = Field(
        None, description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[np.uint32] = Field(
        None, description="""Sweep number, allows to group different PatchClampSeries together."""
    )
    gain: Optional[np.float32] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
    )
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(
        None,
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
    )
    starting_time: Optional[TimeSeriesStartingTime] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[NDArray[Shape["* num_times"], np.float64]] = Field(
        None,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
    )
    control: Optional[NDArray[Shape["* num_times"], np.uint8]] = Field(
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


class CurrentClampStimulusSeries(PatchClampSeries):
    """
    Stimulus current applied during current clamp recording.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    data: CurrentClampStimulusSeriesData = Field(..., description="""Stimulus current applied.""")
    stimulus_description: Optional[str] = Field(
        None, description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[np.uint32] = Field(
        None, description="""Sweep number, allows to group different PatchClampSeries together."""
    )
    gain: Optional[np.float32] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
    )
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(
        None,
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
    )
    starting_time: Optional[TimeSeriesStartingTime] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[NDArray[Shape["* num_times"], np.float64]] = Field(
        None,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
    )
    control: Optional[NDArray[Shape["* num_times"], np.uint8]] = Field(
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


class CurrentClampStimulusSeriesData(ConfiguredBaseModel):
    """
    Stimulus current applied.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["data"] = Field(
        "data",
        json_schema_extra={"linkml_meta": {"equals_string": "data", "ifabsent": "string(data)"}},
    )
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. which is fixed to 'amperes'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    value: Any = Field(...)


class VoltageClampSeries(PatchClampSeries):
    """
    Current data from an intracellular voltage-clamp recording. A corresponding VoltageClampStimulusSeries (stored separately as a stimulus) is used to store the voltage injected.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    data: VoltageClampSeriesData = Field(..., description="""Recorded current.""")
    capacitance_fast: Optional[VoltageClampSeriesCapacitanceFast] = Field(
        None, description="""Fast capacitance, in farads."""
    )
    capacitance_slow: Optional[VoltageClampSeriesCapacitanceSlow] = Field(
        None, description="""Slow capacitance, in farads."""
    )
    resistance_comp_bandwidth: Optional[VoltageClampSeriesResistanceCompBandwidth] = Field(
        None, description="""Resistance compensation bandwidth, in hertz."""
    )
    resistance_comp_correction: Optional[VoltageClampSeriesResistanceCompCorrection] = Field(
        None, description="""Resistance compensation correction, in percent."""
    )
    resistance_comp_prediction: Optional[VoltageClampSeriesResistanceCompPrediction] = Field(
        None, description="""Resistance compensation prediction, in percent."""
    )
    whole_cell_capacitance_comp: Optional[VoltageClampSeriesWholeCellCapacitanceComp] = Field(
        None, description="""Whole cell capacitance compensation, in farads."""
    )
    whole_cell_series_resistance_comp: Optional[VoltageClampSeriesWholeCellSeriesResistanceComp] = (
        Field(None, description="""Whole cell series resistance compensation, in ohms.""")
    )
    stimulus_description: Optional[str] = Field(
        None, description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[np.uint32] = Field(
        None, description="""Sweep number, allows to group different PatchClampSeries together."""
    )
    gain: Optional[np.float32] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
    )
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(
        None,
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
    )
    starting_time: Optional[TimeSeriesStartingTime] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[NDArray[Shape["* num_times"], np.float64]] = Field(
        None,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
    )
    control: Optional[NDArray[Shape["* num_times"], np.uint8]] = Field(
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


class VoltageClampSeriesData(ConfiguredBaseModel):
    """
    Recorded current.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["data"] = Field(
        "data",
        json_schema_extra={"linkml_meta": {"equals_string": "data", "ifabsent": "string(data)"}},
    )
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. which is fixed to 'amperes'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    value: Any = Field(...)


class VoltageClampSeriesCapacitanceFast(ConfiguredBaseModel):
    """
    Fast capacitance, in farads.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["capacitance_fast"] = Field(
        "capacitance_fast",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "capacitance_fast",
                "ifabsent": "string(capacitance_fast)",
            }
        },
    )
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for capacitance_fast, which is fixed to 'farads'.""",
    )
    value: np.float32 = Field(...)


class VoltageClampSeriesCapacitanceSlow(ConfiguredBaseModel):
    """
    Slow capacitance, in farads.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["capacitance_slow"] = Field(
        "capacitance_slow",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "capacitance_slow",
                "ifabsent": "string(capacitance_slow)",
            }
        },
    )
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for capacitance_fast, which is fixed to 'farads'.""",
    )
    value: np.float32 = Field(...)


class VoltageClampSeriesResistanceCompBandwidth(ConfiguredBaseModel):
    """
    Resistance compensation bandwidth, in hertz.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["resistance_comp_bandwidth"] = Field(
        "resistance_comp_bandwidth",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "resistance_comp_bandwidth",
                "ifabsent": "string(resistance_comp_bandwidth)",
            }
        },
    )
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for resistance_comp_bandwidth, which is fixed to 'hertz'.""",
    )
    value: np.float32 = Field(...)


class VoltageClampSeriesResistanceCompCorrection(ConfiguredBaseModel):
    """
    Resistance compensation correction, in percent.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["resistance_comp_correction"] = Field(
        "resistance_comp_correction",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "resistance_comp_correction",
                "ifabsent": "string(resistance_comp_correction)",
            }
        },
    )
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for resistance_comp_correction, which is fixed to 'percent'.""",
    )
    value: np.float32 = Field(...)


class VoltageClampSeriesResistanceCompPrediction(ConfiguredBaseModel):
    """
    Resistance compensation prediction, in percent.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["resistance_comp_prediction"] = Field(
        "resistance_comp_prediction",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "resistance_comp_prediction",
                "ifabsent": "string(resistance_comp_prediction)",
            }
        },
    )
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for resistance_comp_prediction, which is fixed to 'percent'.""",
    )
    value: np.float32 = Field(...)


class VoltageClampSeriesWholeCellCapacitanceComp(ConfiguredBaseModel):
    """
    Whole cell capacitance compensation, in farads.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["whole_cell_capacitance_comp"] = Field(
        "whole_cell_capacitance_comp",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "whole_cell_capacitance_comp",
                "ifabsent": "string(whole_cell_capacitance_comp)",
            }
        },
    )
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for whole_cell_capacitance_comp, which is fixed to 'farads'.""",
    )
    value: np.float32 = Field(...)


class VoltageClampSeriesWholeCellSeriesResistanceComp(ConfiguredBaseModel):
    """
    Whole cell series resistance compensation, in ohms.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["whole_cell_series_resistance_comp"] = Field(
        "whole_cell_series_resistance_comp",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "whole_cell_series_resistance_comp",
                "ifabsent": "string(whole_cell_series_resistance_comp)",
            }
        },
    )
    unit: Optional[str] = Field(
        None,
        description="""Unit of measurement for whole_cell_series_resistance_comp, which is fixed to 'ohms'.""",
    )
    value: np.float32 = Field(...)


class VoltageClampStimulusSeries(PatchClampSeries):
    """
    Stimulus voltage applied during a voltage clamp recording.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    data: VoltageClampStimulusSeriesData = Field(..., description="""Stimulus voltage applied.""")
    stimulus_description: Optional[str] = Field(
        None, description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[np.uint32] = Field(
        None, description="""Sweep number, allows to group different PatchClampSeries together."""
    )
    gain: Optional[np.float32] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
    )
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(
        None,
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
    )
    starting_time: Optional[TimeSeriesStartingTime] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[NDArray[Shape["* num_times"], np.float64]] = Field(
        None,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
    )
    control: Optional[NDArray[Shape["* num_times"], np.uint8]] = Field(
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


class VoltageClampStimulusSeriesData(ConfiguredBaseModel):
    """
    Stimulus voltage applied.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["data"] = Field(
        "data",
        json_schema_extra={"linkml_meta": {"equals_string": "data", "ifabsent": "string(data)"}},
    )
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. which is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    value: Any = Field(...)


class IntracellularElectrode(NWBContainer):
    """
    An intracellular electrode and its metadata.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    description: str = Field(
        ..., description="""Description of electrode (e.g.,  whole-cell, sharp, etc.)."""
    )
    filtering: Optional[str] = Field(None, description="""Electrode specific filtering.""")
    initial_access_resistance: Optional[str] = Field(
        None, description="""Initial access resistance."""
    )
    location: Optional[str] = Field(
        None,
        description="""Location of the electrode. Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""",
    )
    resistance: Optional[str] = Field(None, description="""Electrode resistance, in ohms.""")
    seal: Optional[str] = Field(None, description="""Information about seal used for recording.""")
    slice: Optional[str] = Field(
        None, description="""Information about slice used for recording."""
    )


class SweepTable(DynamicTable):
    """
    The table which groups different PatchClampSeries together.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    sweep_number: NDArray[Any, np.uint32] = Field(
        ...,
        description="""Sweep number of the PatchClampSeries in that row.""",
        json_schema_extra={
            "linkml_meta": {
                "array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}
            }
        },
    )
    series: List[PatchClampSeries] = Field(
        ..., description="""The PatchClampSeries with the sweep number in that row."""
    )
    series_index: Named[VectorIndex] = Field(
        ...,
        description="""Index for series.""",
        json_schema_extra={
            "linkml_meta": {"annotations": {"named": {"tag": "named", "value": True}}}
        },
    )
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
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )
    vector_data: Optional[List[VectorData]] = Field(
        None, description="""Vector columns of this dynamic table."""
    )
    vector_index: Optional[List[VectorIndex]] = Field(
        None, description="""Indices for the vector columns of this dynamic table."""
    )


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
