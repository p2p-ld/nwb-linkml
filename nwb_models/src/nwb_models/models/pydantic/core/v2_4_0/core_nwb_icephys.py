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

from ...core.v2_4_0.core_nwb_base import (
    NWBContainer,
    TimeSeries,
    TimeSeriesReferenceVectorData,
    TimeSeriesStartingTime,
    TimeSeriesSync,
)
from ...core.v2_4_0.core_nwb_device import Device
from ...hdmf_common.v1_5_0.hdmf_common_table import (
    AlignedDynamicTable,
    DynamicTable,
    DynamicTableRegion,
    ElementIdentifiers,
    VectorData,
    VectorIndex,
)


metamodel_version = "None"
version = "2.4.0"


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
        "default_prefix": "core.nwb.icephys/",
        "id": "core.nwb.icephys",
        "imports": [
            "core.nwb.base",
            "core.nwb.device",
            "../../hdmf_common/v1_5_0/namespace",
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
    stimulus_description: str = Field(
        ..., description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[int] = Field(
        None, description="""Sweep number, allows to group different PatchClampSeries together."""
    )
    data: PatchClampSeriesData = Field(..., description="""Recorded voltage or current.""")
    gain: Optional[float] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
    )
    electrode: Union[IntracellularElectrode, str] = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"source_type": {"tag": "source_type", "value": "link"}},
                "any_of": [{"range": "IntracellularElectrode"}, {"range": "string"}],
            }
        },
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


class PatchClampSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage or current.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

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
    resolution: Optional[float] = Field(
        -1.0,
        description="""Smallest meaningful difference between values in data, stored in the specified by unit, e.g., the change in value of the least significant bit, or a larger number if signal noise is known to be present. If unknown, use -1.0.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "float(-1.0)"}},
    )
    unit: str = Field(
        ...,
        description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    value: Optional[NDArray[Shape["* num_times"], float | int]] = Field(
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
    bias_current: Optional[float] = Field(None, description="""Bias current, in amps.""")
    bridge_balance: Optional[float] = Field(None, description="""Bridge balance, in ohms.""")
    capacitance_compensation: Optional[float] = Field(
        None, description="""Capacitance compensation, in farads."""
    )
    data: CurrentClampSeriesData = Field(..., description="""Recorded voltage.""")
    stimulus_description: str = Field(
        ..., description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[int] = Field(
        None, description="""Sweep number, allows to group different PatchClampSeries together."""
    )
    gain: Optional[float] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
    )
    electrode: Union[IntracellularElectrode, str] = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"source_type": {"tag": "source_type", "value": "link"}},
                "any_of": [{"range": "IntracellularElectrode"}, {"range": "string"}],
            }
        },
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


class CurrentClampSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

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
    resolution: Optional[float] = Field(
        -1.0,
        description="""Smallest meaningful difference between values in data, stored in the specified by unit, e.g., the change in value of the least significant bit, or a larger number if signal noise is known to be present. If unknown, use -1.0.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "float(-1.0)"}},
    )
    unit: Literal["volts"] = Field(
        "volts",
        description="""Base unit of measurement for working with the data. which is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
        json_schema_extra={"linkml_meta": {"equals_string": "volts", "ifabsent": "string(volts)"}},
    )
    value: Optional[NDArray[Shape["* num_times"], float | int]] = Field(
        None, json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}}
    )


class IZeroClampSeries(CurrentClampSeries):
    """
    Voltage data from an intracellular recording when all current and amplifier settings are off (i.e., CurrentClampSeries fields will be zero). There is no CurrentClampStimulusSeries associated with an IZero series because the amplifier is disconnected and no stimulus can reach the cell.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    stimulus_description: Literal["N/A"] = Field(
        "N/A",
        description="""An IZeroClampSeries has no stimulus, so this attribute is automatically set to \"N/A\"""",
        json_schema_extra={"linkml_meta": {"equals_string": "N/A", "ifabsent": "string(N/A)"}},
    )
    bias_current: float = Field(..., description="""Bias current, in amps, fixed to 0.0.""")
    bridge_balance: float = Field(..., description="""Bridge balance, in ohms, fixed to 0.0.""")
    capacitance_compensation: float = Field(
        ..., description="""Capacitance compensation, in farads, fixed to 0.0."""
    )
    data: CurrentClampSeriesData = Field(..., description="""Recorded voltage.""")
    sweep_number: Optional[int] = Field(
        None, description="""Sweep number, allows to group different PatchClampSeries together."""
    )
    gain: Optional[float] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
    )
    electrode: Union[IntracellularElectrode, str] = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"source_type": {"tag": "source_type", "value": "link"}},
                "any_of": [{"range": "IntracellularElectrode"}, {"range": "string"}],
            }
        },
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


class CurrentClampStimulusSeries(PatchClampSeries):
    """
    Stimulus current applied during current clamp recording.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    data: CurrentClampStimulusSeriesData = Field(..., description="""Stimulus current applied.""")
    stimulus_description: str = Field(
        ..., description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[int] = Field(
        None, description="""Sweep number, allows to group different PatchClampSeries together."""
    )
    gain: Optional[float] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
    )
    electrode: Union[IntracellularElectrode, str] = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"source_type": {"tag": "source_type", "value": "link"}},
                "any_of": [{"range": "IntracellularElectrode"}, {"range": "string"}],
            }
        },
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


class CurrentClampStimulusSeriesData(ConfiguredBaseModel):
    """
    Stimulus current applied.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

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
    resolution: Optional[float] = Field(
        -1.0,
        description="""Smallest meaningful difference between values in data, stored in the specified by unit, e.g., the change in value of the least significant bit, or a larger number if signal noise is known to be present. If unknown, use -1.0.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "float(-1.0)"}},
    )
    unit: Literal["amperes"] = Field(
        "amperes",
        description="""Base unit of measurement for working with the data. which is fixed to 'amperes'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
        json_schema_extra={
            "linkml_meta": {"equals_string": "amperes", "ifabsent": "string(amperes)"}
        },
    )
    value: Optional[NDArray[Shape["* num_times"], float | int]] = Field(
        None, json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}}
    )


class VoltageClampSeries(PatchClampSeries):
    """
    Current data from an intracellular voltage-clamp recording. A corresponding VoltageClampStimulusSeries (stored separately as a stimulus) is used to store the voltage injected.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    capacitance_fast: Optional[VoltageClampSeriesCapacitanceFast] = Field(
        None, description="""Fast capacitance, in farads."""
    )
    capacitance_slow: Optional[VoltageClampSeriesCapacitanceSlow] = Field(
        None, description="""Slow capacitance, in farads."""
    )
    data: VoltageClampSeriesData = Field(..., description="""Recorded current.""")
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
    stimulus_description: str = Field(
        ..., description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[int] = Field(
        None, description="""Sweep number, allows to group different PatchClampSeries together."""
    )
    gain: Optional[float] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
    )
    electrode: Union[IntracellularElectrode, str] = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"source_type": {"tag": "source_type", "value": "link"}},
                "any_of": [{"range": "IntracellularElectrode"}, {"range": "string"}],
            }
        },
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
    unit: Literal["farads"] = Field(
        "farads",
        description="""Unit of measurement for capacitance_fast, which is fixed to 'farads'.""",
        json_schema_extra={
            "linkml_meta": {"equals_string": "farads", "ifabsent": "string(farads)"}
        },
    )
    value: float = Field(...)


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
    unit: Literal["farads"] = Field(
        "farads",
        description="""Unit of measurement for capacitance_fast, which is fixed to 'farads'.""",
        json_schema_extra={
            "linkml_meta": {"equals_string": "farads", "ifabsent": "string(farads)"}
        },
    )
    value: float = Field(...)


class VoltageClampSeriesData(ConfiguredBaseModel):
    """
    Recorded current.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

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
    resolution: Optional[float] = Field(
        -1.0,
        description="""Smallest meaningful difference between values in data, stored in the specified by unit, e.g., the change in value of the least significant bit, or a larger number if signal noise is known to be present. If unknown, use -1.0.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "float(-1.0)"}},
    )
    unit: Literal["amperes"] = Field(
        "amperes",
        description="""Base unit of measurement for working with the data. which is fixed to 'amperes'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
        json_schema_extra={
            "linkml_meta": {"equals_string": "amperes", "ifabsent": "string(amperes)"}
        },
    )
    value: Optional[NDArray[Shape["* num_times"], float | int]] = Field(
        None, json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}}
    )


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
    unit: Literal["hertz"] = Field(
        "hertz",
        description="""Unit of measurement for resistance_comp_bandwidth, which is fixed to 'hertz'.""",
        json_schema_extra={"linkml_meta": {"equals_string": "hertz", "ifabsent": "string(hertz)"}},
    )
    value: float = Field(...)


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
    unit: Literal["percent"] = Field(
        "percent",
        description="""Unit of measurement for resistance_comp_correction, which is fixed to 'percent'.""",
        json_schema_extra={
            "linkml_meta": {"equals_string": "percent", "ifabsent": "string(percent)"}
        },
    )
    value: float = Field(...)


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
    unit: Literal["percent"] = Field(
        "percent",
        description="""Unit of measurement for resistance_comp_prediction, which is fixed to 'percent'.""",
        json_schema_extra={
            "linkml_meta": {"equals_string": "percent", "ifabsent": "string(percent)"}
        },
    )
    value: float = Field(...)


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
    unit: Literal["farads"] = Field(
        "farads",
        description="""Unit of measurement for whole_cell_capacitance_comp, which is fixed to 'farads'.""",
        json_schema_extra={
            "linkml_meta": {"equals_string": "farads", "ifabsent": "string(farads)"}
        },
    )
    value: float = Field(...)


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
    unit: Literal["ohms"] = Field(
        "ohms",
        description="""Unit of measurement for whole_cell_series_resistance_comp, which is fixed to 'ohms'.""",
        json_schema_extra={"linkml_meta": {"equals_string": "ohms", "ifabsent": "string(ohms)"}},
    )
    value: float = Field(...)


class VoltageClampStimulusSeries(PatchClampSeries):
    """
    Stimulus voltage applied during a voltage clamp recording.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    data: VoltageClampStimulusSeriesData = Field(..., description="""Stimulus voltage applied.""")
    stimulus_description: str = Field(
        ..., description="""Protocol/stimulus name for this patch-clamp dataset."""
    )
    sweep_number: Optional[int] = Field(
        None, description="""Sweep number, allows to group different PatchClampSeries together."""
    )
    gain: Optional[float] = Field(
        None,
        description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""",
    )
    electrode: Union[IntracellularElectrode, str] = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"source_type": {"tag": "source_type", "value": "link"}},
                "any_of": [{"range": "IntracellularElectrode"}, {"range": "string"}],
            }
        },
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


class VoltageClampStimulusSeriesData(ConfiguredBaseModel):
    """
    Stimulus voltage applied.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

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
    resolution: Optional[float] = Field(
        -1.0,
        description="""Smallest meaningful difference between values in data, stored in the specified by unit, e.g., the change in value of the least significant bit, or a larger number if signal noise is known to be present. If unknown, use -1.0.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "float(-1.0)"}},
    )
    unit: Literal["volts"] = Field(
        "volts",
        description="""Base unit of measurement for working with the data. which is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
        json_schema_extra={"linkml_meta": {"equals_string": "volts", "ifabsent": "string(volts)"}},
    )
    value: Optional[NDArray[Shape["* num_times"], float | int]] = Field(
        None, json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}}
    )


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
    device: Union[Device, str] = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"source_type": {"tag": "source_type", "value": "link"}},
                "any_of": [{"range": "Device"}, {"range": "string"}],
            }
        },
    )


class SweepTable(DynamicTable):
    """
    [DEPRECATED] Table used to group different PatchClampSeries. SweepTable is being replaced by IntracellularRecordingsTable and SimultaneousRecordingsTable tables. Additional SequentialRecordingsTable, RepetitionsTable, and ExperimentalConditions tables provide enhanced support for experiment metadata.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    series: VectorData[NDArray[Any, PatchClampSeries]] = Field(
        ...,
        description="""The PatchClampSeries with the sweep number in that row.""",
        json_schema_extra={
            "linkml_meta": {
                "array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}
            }
        },
    )
    series_index: Named[VectorIndex] = Field(
        ...,
        description="""Index for series.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    sweep_number: VectorData[NDArray[Any, int]] = Field(
        ...,
        description="""Sweep number of the PatchClampSeries in that row.""",
        json_schema_extra={
            "linkml_meta": {
                "array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}
            }
        },
    )
    colnames: List[str] = Field(
        ...,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: str = Field(..., description="""Description of what is in this dynamic table.""")
    id: ElementIdentifiers = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )


class IntracellularElectrodesTable(DynamicTable):
    """
    Table for storing intracellular electrode related metadata.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    description: Literal["Table for storing intracellular electrode related metadata."] = Field(
        "Table for storing intracellular electrode related metadata.",
        description="""Description of what is in this dynamic table.""",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "Table for storing intracellular electrode related metadata.",
                "ifabsent": "string(Table for storing intracellular electrode related metadata.)",
            }
        },
    )
    electrode: VectorData[NDArray[Any, IntracellularElectrode]] = Field(
        ...,
        description="""Column for storing the reference to the intracellular electrode.""",
        json_schema_extra={
            "linkml_meta": {
                "array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}
            }
        },
    )
    colnames: List[str] = Field(
        ...,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    id: ElementIdentifiers = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )


class IntracellularStimuliTable(DynamicTable):
    """
    Table for storing intracellular stimulus related metadata.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    description: Literal["Table for storing intracellular stimulus related metadata."] = Field(
        "Table for storing intracellular stimulus related metadata.",
        description="""Description of what is in this dynamic table.""",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "Table for storing intracellular stimulus related metadata.",
                "ifabsent": "string(Table for storing intracellular stimulus related metadata.)",
            }
        },
    )
    stimulus: Named[TimeSeriesReferenceVectorData] = Field(
        ...,
        description="""Column storing the reference to the recorded stimulus for the recording (rows).""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    colnames: List[str] = Field(
        ...,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    id: ElementIdentifiers = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )


class IntracellularResponsesTable(DynamicTable):
    """
    Table for storing intracellular response related metadata.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: str = Field(...)
    description: Literal["Table for storing intracellular response related metadata."] = Field(
        "Table for storing intracellular response related metadata.",
        description="""Description of what is in this dynamic table.""",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "Table for storing intracellular response related metadata.",
                "ifabsent": "string(Table for storing intracellular response related metadata.)",
            }
        },
    )
    response: Named[TimeSeriesReferenceVectorData] = Field(
        ...,
        description="""Column storing the reference to the recorded response for the recording (rows)""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    colnames: List[str] = Field(
        ...,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    id: ElementIdentifiers = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )


class IntracellularRecordingsTable(AlignedDynamicTable):
    """
    A table to group together a stimulus and response from a single electrode and a single simultaneous recording. Each row in the table represents a single recording consisting typically of a stimulus and a corresponding response. In some cases, however, only a stimulus or a response is recorded as part of an experiment. In this case, both the stimulus and response will point to the same TimeSeries while the idx_start and count of the invalid column will be set to -1, thus, indicating that no values have been recorded for the stimulus or response, respectively. Note, a recording MUST contain at least a stimulus or a response. Typically the stimulus and response are PatchClampSeries. However, the use of AD/DA channels that are not associated to an electrode is also common in intracellular electrophysiology, in which case other TimeSeries may be used.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: Literal["intracellular_recordings"] = Field(
        "intracellular_recordings",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "intracellular_recordings",
                "ifabsent": "string(intracellular_recordings)",
            }
        },
    )
    description: Literal[
        "A table to group together a stimulus and response from a single electrode and a single"
        " simultaneous recording and for storing metadata about the intracellular recording."
    ] = Field(
        "A table to group together a stimulus and response from a single electrode and a single"
        " simultaneous recording and for storing metadata about the intracellular recording.",
        description="""Description of the contents of this table. Inherited from AlignedDynamicTable and overwritten here to fix the value of the attribute.""",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": (
                    "A table to group together a stimulus and response from a "
                    "single electrode and a single simultaneous recording and "
                    "for storing metadata about the intracellular recording."
                ),
                "ifabsent": (
                    "string(A table to group together a stimulus and response from a "
                    "single electrode and a single simultaneous recording and for "
                    "storing metadata about the intracellular recording.)"
                ),
            }
        },
    )
    electrodes: IntracellularElectrodesTable = Field(
        ..., description="""Table for storing intracellular electrode related metadata."""
    )
    responses: IntracellularResponsesTable = Field(
        ..., description="""Table for storing intracellular response related metadata."""
    )
    stimuli: IntracellularStimuliTable = Field(
        ..., description="""Table for storing intracellular stimulus related metadata."""
    )
    categories: List[str] = Field(
        ...,
        description="""The names of the categories in this AlignedDynamicTable. Each category is represented by one DynamicTable stored in the parent group. This attribute should be used to specify an order of categories and the category names must match the names of the corresponding DynamicTable in the group.""",
    )
    value: Optional[Dict[str, DynamicTable]] = Field(
        None, json_schema_extra={"linkml_meta": {"any_of": [{"range": "DynamicTable"}]}}
    )
    colnames: List[str] = Field(
        ...,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    id: ElementIdentifiers = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )


class SimultaneousRecordingsTable(DynamicTable):
    """
    A table for grouping different intracellular recordings from the IntracellularRecordingsTable table together that were recorded simultaneously from different electrodes.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: Literal["simultaneous_recordings"] = Field(
        "simultaneous_recordings",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "simultaneous_recordings",
                "ifabsent": "string(simultaneous_recordings)",
            }
        },
    )
    recordings: SimultaneousRecordingsTableRecordings = Field(
        ...,
        description="""A reference to one or more rows in the IntracellularRecordingsTable table.""",
    )
    recordings_index: Named[VectorIndex] = Field(
        ...,
        description="""Index dataset for the recordings column.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    colnames: List[str] = Field(
        ...,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: str = Field(..., description="""Description of what is in this dynamic table.""")
    id: ElementIdentifiers = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )


class SimultaneousRecordingsTableRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the IntracellularRecordingsTable table.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["recordings"] = Field(
        "recordings",
        json_schema_extra={
            "linkml_meta": {"equals_string": "recordings", "ifabsent": "string(recordings)"}
        },
    )
    table: IntracellularRecordingsTable = Field(
        ...,
        description="""Reference to the IntracellularRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""",
    )
    description: str = Field(
        ..., description="""Description of what this table region points to."""
    )
    value: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class SequentialRecordingsTable(DynamicTable):
    """
    A table for grouping different sequential recordings from the SimultaneousRecordingsTable table together. This is typically used to group together sequential recordings where a sequence of stimuli of the same type with varying parameters have been presented in a sequence.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: Literal["sequential_recordings"] = Field(
        "sequential_recordings",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "sequential_recordings",
                "ifabsent": "string(sequential_recordings)",
            }
        },
    )
    simultaneous_recordings: SequentialRecordingsTableSimultaneousRecordings = Field(
        ...,
        description="""A reference to one or more rows in the SimultaneousRecordingsTable table.""",
    )
    simultaneous_recordings_index: Named[VectorIndex] = Field(
        ...,
        description="""Index dataset for the simultaneous_recordings column.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    stimulus_type: VectorData[NDArray[Any, str]] = Field(
        ...,
        description="""The type of stimulus used for the sequential recording.""",
        json_schema_extra={
            "linkml_meta": {
                "array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}
            }
        },
    )
    colnames: List[str] = Field(
        ...,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: str = Field(..., description="""Description of what is in this dynamic table.""")
    id: ElementIdentifiers = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )


class SequentialRecordingsTableSimultaneousRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the SimultaneousRecordingsTable table.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["simultaneous_recordings"] = Field(
        "simultaneous_recordings",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "simultaneous_recordings",
                "ifabsent": "string(simultaneous_recordings)",
            }
        },
    )
    table: SimultaneousRecordingsTable = Field(
        ...,
        description="""Reference to the SimultaneousRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""",
    )
    description: str = Field(
        ..., description="""Description of what this table region points to."""
    )
    value: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class RepetitionsTable(DynamicTable):
    """
    A table for grouping different sequential intracellular recordings together. With each SequentialRecording typically representing a particular type of stimulus, the RepetitionsTable table is typically used to group sets of stimuli applied in sequence.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: Literal["repetitions"] = Field(
        "repetitions",
        json_schema_extra={
            "linkml_meta": {"equals_string": "repetitions", "ifabsent": "string(repetitions)"}
        },
    )
    sequential_recordings: RepetitionsTableSequentialRecordings = Field(
        ...,
        description="""A reference to one or more rows in the SequentialRecordingsTable table.""",
    )
    sequential_recordings_index: Named[VectorIndex] = Field(
        ...,
        description="""Index dataset for the sequential_recordings column.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    colnames: List[str] = Field(
        ...,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: str = Field(..., description="""Description of what is in this dynamic table.""")
    id: ElementIdentifiers = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )


class RepetitionsTableSequentialRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the SequentialRecordingsTable table.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["sequential_recordings"] = Field(
        "sequential_recordings",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "sequential_recordings",
                "ifabsent": "string(sequential_recordings)",
            }
        },
    )
    table: SequentialRecordingsTable = Field(
        ...,
        description="""Reference to the SequentialRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""",
    )
    description: str = Field(
        ..., description="""Description of what this table region points to."""
    )
    value: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class ExperimentalConditionsTable(DynamicTable):
    """
    A table for grouping different intracellular recording repetitions together that belong to the same experimental condition.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.icephys", "tree_root": True}
    )

    name: Literal["experimental_conditions"] = Field(
        "experimental_conditions",
        json_schema_extra={
            "linkml_meta": {
                "equals_string": "experimental_conditions",
                "ifabsent": "string(experimental_conditions)",
            }
        },
    )
    repetitions: ExperimentalConditionsTableRepetitions = Field(
        ..., description="""A reference to one or more rows in the RepetitionsTable table."""
    )
    repetitions_index: Named[VectorIndex] = Field(
        ...,
        description="""Index dataset for the repetitions column.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    colnames: List[str] = Field(
        ...,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: str = Field(..., description="""Description of what is in this dynamic table.""")
    id: ElementIdentifiers = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )


class ExperimentalConditionsTableRepetitions(DynamicTableRegion):
    """
    A reference to one or more rows in the RepetitionsTable table.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.icephys"})

    name: Literal["repetitions"] = Field(
        "repetitions",
        json_schema_extra={
            "linkml_meta": {"equals_string": "repetitions", "ifabsent": "string(repetitions)"}
        },
    )
    table: RepetitionsTable = Field(
        ...,
        description="""Reference to the RepetitionsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""",
    )
    description: str = Field(
        ..., description="""Description of what this table region points to."""
    )
    value: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


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
VoltageClampSeriesCapacitanceFast.model_rebuild()
VoltageClampSeriesCapacitanceSlow.model_rebuild()
VoltageClampSeriesData.model_rebuild()
VoltageClampSeriesResistanceCompBandwidth.model_rebuild()
VoltageClampSeriesResistanceCompCorrection.model_rebuild()
VoltageClampSeriesResistanceCompPrediction.model_rebuild()
VoltageClampSeriesWholeCellCapacitanceComp.model_rebuild()
VoltageClampSeriesWholeCellSeriesResistanceComp.model_rebuild()
VoltageClampStimulusSeries.model_rebuild()
VoltageClampStimulusSeriesData.model_rebuild()
IntracellularElectrode.model_rebuild()
SweepTable.model_rebuild()
IntracellularElectrodesTable.model_rebuild()
IntracellularStimuliTable.model_rebuild()
IntracellularResponsesTable.model_rebuild()
IntracellularRecordingsTable.model_rebuild()
SimultaneousRecordingsTable.model_rebuild()
SimultaneousRecordingsTableRecordings.model_rebuild()
SequentialRecordingsTable.model_rebuild()
SequentialRecordingsTableSimultaneousRecordings.model_rebuild()
RepetitionsTable.model_rebuild()
RepetitionsTableSequentialRecordings.model_rebuild()
ExperimentalConditionsTable.model_rebuild()
ExperimentalConditionsTableRepetitions.model_rebuild()
