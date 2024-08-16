from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
import numpy as np
from ...core.v2_5_0.core_nwb_base import TimeSeries, TimeSeriesStartingTime, TimeSeriesSync
from ...core.v2_5_0.core_nwb_ecephys import ElectrodeGroup
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
from ...hdmf_common.v1_5_0.hdmf_common_table import (
    DynamicTableRegion,
    DynamicTable,
    VectorData,
    VectorIndex,
)
from numpydantic import NDArray, Shape

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
        "default_prefix": "core.nwb.misc/",
        "id": "core.nwb.misc",
        "imports": [
            "core.nwb.base",
            "../../hdmf_common/v1_5_0/namespace",
            "core.nwb.ecephys",
            "core.nwb.language",
        ],
        "name": "core.nwb.misc",
    }
)


class AbstractFeatureSeries(TimeSeries):
    """
    Abstract features, such as quantitative descriptions of sensory stimuli. The TimeSeries::data field is a 2D array, storing those features (e.g., for visual grating stimulus this might be orientation, spatial frequency and contrast). Null stimuli (eg, uniform gray) can be marked as being an independent feature (eg, 1.0 for gray, 0.0 for actual stimulus) or by storing NaNs for feature values, or through use of the TimeSeries::control fields. A set of features is considered to persist until the next set of features is defined. The final set of features stored should be the null set. This is useful when storing the raw stimulus is impractical.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.misc", "tree_root": True}
    )

    name: str = Field(...)
    data: AbstractFeatureSeriesData = Field(
        ..., description="""Values of each feature at each time."""
    )
    feature_units: Optional[NDArray[Shape["* num_features"], str]] = Field(
        None,
        description="""Units of each feature.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_features"}]}}},
    )
    features: NDArray[Shape["* num_features"], str] = Field(
        ...,
        description="""Description of the features represented in TimeSeries::data.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_features"}]}}},
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


class AbstractFeatureSeriesData(ConfiguredBaseModel):
    """
    Values of each feature at each time.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.misc"})

    name: Literal["data"] = Field(
        "data",
        json_schema_extra={"linkml_meta": {"equals_string": "data", "ifabsent": "string(data)"}},
    )
    unit: Optional[str] = Field(
        "see 'feature_units'",
        description="""Since there can be different units for different features, store the units in 'feature_units'. The default value for this attribute is \"see 'feature_units'\".""",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(see 'feature_units')"}},
    )
    value: Optional[
        Union[
            NDArray[Shape["* num_times"], float],
            NDArray[Shape["* num_times, * num_features"], float],
        ]
    ] = Field(None)


class AnnotationSeries(TimeSeries):
    """
    Stores user annotations made during an experiment. The data[] field stores a text array, and timestamps are stored for each annotation (ie, interval=1). This is largely an alias to a standard TimeSeries storing a text array but that is identifiable as storing annotations in a machine-readable way.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.misc", "tree_root": True}
    )

    name: str = Field(...)
    data: NDArray[Shape["* num_times"], str] = Field(
        ...,
        description="""Annotations made during an experiment.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
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


class IntervalSeries(TimeSeries):
    """
    Stores intervals of data. The timestamps field stores the beginning and end of intervals. The data field stores whether the interval just started (>0 value) or ended (<0 value). Different interval types can be represented in the same series by using multiple key values (eg, 1 for feature A, 2 for feature B, 3 for feature C, etc). The field data stores an 8-bit integer. This is largely an alias of a standard TimeSeries but that is identifiable as representing time intervals in a machine-readable way.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.misc", "tree_root": True}
    )

    name: str = Field(...)
    data: NDArray[Shape["* num_times"], int] = Field(
        ...,
        description="""Use values >0 if interval started, <0 if interval ended.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_times"}]}}},
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


class DecompositionSeries(TimeSeries):
    """
    Spectral analysis of a time series, e.g. of an LFP or a speech signal.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.misc", "tree_root": True}
    )

    name: str = Field(...)
    data: DecompositionSeriesData = Field(
        ..., description="""Data decomposed into frequency bands."""
    )
    metric: str = Field(..., description="""The metric used, e.g. phase, amplitude, power.""")
    source_channels: Named[Optional[DynamicTableRegion]] = Field(
        None,
        description="""DynamicTableRegion pointer to the channels that this decomposition series was generated from.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    bands: DecompositionSeriesBands = Field(
        ...,
        description="""Table for describing the bands that this series was generated from. There should be one row in this table for each band.""",
    )
    source_timeseries: Optional[Union[TimeSeries, str]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "annotations": {"source_type": {"tag": "source_type", "value": "link"}},
                "any_of": [{"range": "TimeSeries"}, {"range": "string"}],
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


class DecompositionSeriesData(ConfiguredBaseModel):
    """
    Data decomposed into frequency bands.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.misc"})

    name: Literal["data"] = Field(
        "data",
        json_schema_extra={"linkml_meta": {"equals_string": "data", "ifabsent": "string(data)"}},
    )
    unit: str = Field(
        "no unit",
        description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "string(no unit)"}},
    )
    value: Optional[NDArray[Shape["* num_times, * num_channels, * num_bands"], float]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "array": {
                    "dimensions": [
                        {"alias": "num_times"},
                        {"alias": "num_channels"},
                        {"alias": "num_bands"},
                    ]
                }
            }
        },
    )


class DecompositionSeriesBands(DynamicTable):
    """
    Table for describing the bands that this series was generated from. There should be one row in this table for each band.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.misc"})

    name: Literal["bands"] = Field(
        "bands",
        json_schema_extra={"linkml_meta": {"equals_string": "bands", "ifabsent": "string(bands)"}},
    )
    band_name: VectorData[NDArray[Any, str]] = Field(
        ...,
        description="""Name of the band, e.g. theta.""",
        json_schema_extra={
            "linkml_meta": {
                "array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}
            }
        },
    )
    band_limits: VectorData[NDArray[Shape["* num_bands, 2 low_high"], float]] = Field(
        ...,
        description="""Low and high limit of each band in Hz. If it is a Gaussian filter, use 2 SD on either side of the center.""",
        json_schema_extra={
            "linkml_meta": {
                "array": {
                    "dimensions": [
                        {"alias": "num_bands"},
                        {"alias": "low_high", "exact_cardinality": 2},
                    ]
                }
            }
        },
    )
    band_mean: VectorData[NDArray[Shape["* num_bands"], float]] = Field(
        ...,
        description="""The mean Gaussian filters, in Hz.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_bands"}]}}},
    )
    band_stdev: VectorData[NDArray[Shape["* num_bands"], float]] = Field(
        ...,
        description="""The standard deviation of Gaussian filters, in Hz.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_bands"}]}}},
    )
    colnames: List[str] = Field(
        ...,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: str = Field(..., description="""Description of what is in this dynamic table.""")
    id: VectorData[NDArray[Shape["* num_rows"], int]] = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )
    vector_data: Optional[List[VectorData]] = Field(
        None, description="""Vector columns, including index columns, of this dynamic table."""
    )


class Units(DynamicTable):
    """
    Data about spiking units. Event times of observed units (e.g. cell, synapse, etc.) should be concatenated and stored in spike_times.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.misc", "tree_root": True}
    )

    name: str = Field("Units", json_schema_extra={"linkml_meta": {"ifabsent": "string(Units)"}})
    spike_times_index: Named[Optional[VectorIndex]] = Field(
        None,
        description="""Index into the spike_times dataset.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    spike_times: Optional[UnitsSpikeTimes] = Field(
        None, description="""Spike times for each unit."""
    )
    obs_intervals_index: Named[Optional[VectorIndex]] = Field(
        None,
        description="""Index into the obs_intervals dataset.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    obs_intervals: VectorData[Optional[NDArray[Shape["* num_intervals, 2 start_end"], float]]] = (
        Field(
            None,
            description="""Observation intervals for each unit.""",
            json_schema_extra={
                "linkml_meta": {
                    "array": {
                        "dimensions": [
                            {"alias": "num_intervals"},
                            {"alias": "start_end", "exact_cardinality": 2},
                        ]
                    }
                }
            },
        )
    )
    electrodes_index: Named[Optional[VectorIndex]] = Field(
        None,
        description="""Index into electrodes.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    electrodes: Named[Optional[DynamicTableRegion]] = Field(
        None,
        description="""Electrode that each spike unit came from, specified using a DynamicTableRegion.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    electrode_group: Optional[List[ElectrodeGroup]] = Field(
        None, description="""Electrode group that each spike unit came from."""
    )
    waveform_mean: VectorData[
        Optional[
            Union[
                NDArray[Shape["* num_units, * num_samples"], float],
                NDArray[Shape["* num_units, * num_samples, * num_electrodes"], float],
            ]
        ]
    ] = Field(None, description="""Spike waveform mean for each spike unit.""")
    waveform_sd: VectorData[
        Optional[
            Union[
                NDArray[Shape["* num_units, * num_samples"], float],
                NDArray[Shape["* num_units, * num_samples, * num_electrodes"], float],
            ]
        ]
    ] = Field(None, description="""Spike waveform standard deviation for each spike unit.""")
    waveforms: VectorData[Optional[NDArray[Shape["* num_waveforms, * num_samples"], float]]] = (
        Field(
            None,
            description="""Individual waveforms for each spike on each electrode. This is a doubly indexed column. The 'waveforms_index' column indexes which waveforms in this column belong to the same spike event for a given unit, where each waveform was recorded from a different electrode. The 'waveforms_index_index' column indexes the 'waveforms_index' column to indicate which spike events belong to a given unit. For example, if the 'waveforms_index_index' column has values [2, 5, 6], then the first 2 elements of the 'waveforms_index' column correspond to the 2 spike events of the first unit, the next 3 elements of the 'waveforms_index' column correspond to the 3 spike events of the second unit, and the next 1 element of the 'waveforms_index' column corresponds to the 1 spike event of the third unit. If the 'waveforms_index' column has values [3, 6, 8, 10, 12, 13], then the first 3 elements of the 'waveforms' column contain the 3 spike waveforms that were recorded from 3 different electrodes for the first spike time of the first unit. See https://nwb-schema.readthedocs.io/en/stable/format_description.html#doubly-ragged-arrays for a graphical representation of this example. When there is only one electrode for each unit (i.e., each spike time is associated with a single waveform), then the 'waveforms_index' column will have values 1, 2, ..., N, where N is the number of spike events. The number of electrodes for each spike event should be the same within a given unit. The 'electrodes' column should be used to indicate which electrodes are associated with each unit, and the order of the waveforms within a given unit x spike event should be in the same order as the electrodes referenced in the 'electrodes' column of this table. The number of samples for each waveform must be the same.""",
            json_schema_extra={
                "linkml_meta": {
                    "array": {"dimensions": [{"alias": "num_waveforms"}, {"alias": "num_samples"}]}
                }
            },
        )
    )
    waveforms_index: Named[Optional[VectorIndex]] = Field(
        None,
        description="""Index into the waveforms dataset. One value for every spike event. See 'waveforms' for more detail.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    waveforms_index_index: Named[Optional[VectorIndex]] = Field(
        None,
        description="""Index into the waveforms_index dataset. One value for every unit (row in the table). See 'waveforms' for more detail.""",
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
    id: VectorData[NDArray[Shape["* num_rows"], int]] = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )
    vector_data: Optional[List[VectorData]] = Field(
        None, description="""Vector columns, including index columns, of this dynamic table."""
    )


class UnitsSpikeTimes(VectorData):
    """
    Spike times for each unit.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.misc"})

    name: Literal["spike_times"] = Field(
        "spike_times",
        json_schema_extra={
            "linkml_meta": {"equals_string": "spike_times", "ifabsent": "string(spike_times)"}
        },
    )
    resolution: Optional[float] = Field(
        None,
        description="""The smallest possible difference between two spike times. Usually 1 divided by the acquisition sampling rate from which spike times were extracted, but could be larger if the acquisition time series was downsampled or smaller if the acquisition time series was smoothed/interpolated and it is possible for the spike time to be between samples.""",
    )
    description: str = Field(..., description="""Description of what these vectors represent.""")
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
AbstractFeatureSeries.model_rebuild()
AbstractFeatureSeriesData.model_rebuild()
AnnotationSeries.model_rebuild()
IntervalSeries.model_rebuild()
DecompositionSeries.model_rebuild()
DecompositionSeriesData.model_rebuild()
DecompositionSeriesBands.model_rebuild()
Units.model_rebuild()
UnitsSpikeTimes.model_rebuild()
