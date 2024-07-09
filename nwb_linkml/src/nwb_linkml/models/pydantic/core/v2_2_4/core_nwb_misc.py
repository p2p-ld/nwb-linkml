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


from ...hdmf_common.v1_1_3.hdmf_common_table import (
    VectorIndex,
    VectorData,
    DynamicTable,
    DynamicTableRegion,
)

from .core_nwb_base import TimeSeriesStartingTime, TimeSeriesSync, TimeSeries

from .core_nwb_ecephys import ElectrodeGroup


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


class AbstractFeatureSeries(TimeSeries):
    """
    Abstract features, such as quantitative descriptions of sensory stimuli. The TimeSeries::data field is a 2D array, storing those features (e.g., for visual grating stimulus this might be orientation, spatial frequency and contrast). Null stimuli (eg, uniform gray) can be marked as being an independent feature (eg, 1.0 for gray, 0.0 for actual stimulus) or by storing NaNs for feature values, or through use of the TimeSeries::control fields. A set of features is considered to persist until the next set of features is defined. The final set of features stored should be the null set. This is useful when storing the raw stimulus is impractical.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    data: str = Field(..., description="""Values of each feature at each time.""")
    feature_units: Optional[NDArray[Shape["* num_features"], str]] = Field(
        None, description="""Units of each feature."""
    )
    features: NDArray[Shape["* num_features"], str] = Field(
        ...,
        description="""Description of the features represented in TimeSeries::data.""",
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


class AbstractFeatureSeriesData(ConfiguredBaseModel):
    """
    Values of each feature at each time.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["data"] = Field("data")
    unit: Optional[str] = Field(
        None,
        description="""Since there can be different units for different features, store the units in 'feature_units'. The default value for this attribute is \"see 'feature_units'\".""",
    )
    array: Optional[
        Union[
            NDArray[Shape["* num_times"], float],
            NDArray[Shape["* num_times, * num_features"], float],
        ]
    ] = Field(None)


class AnnotationSeries(TimeSeries):
    """
    Stores user annotations made during an experiment. The data[] field stores a text array, and timestamps are stored for each annotation (ie, interval=1). This is largely an alias to a standard TimeSeries storing a text array but that is identifiable as storing annotations in a machine-readable way.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    data: NDArray[Shape["* num_times"], str] = Field(
        ..., description="""Annotations made during an experiment."""
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


class IntervalSeries(TimeSeries):
    """
    Stores intervals of data. The timestamps field stores the beginning and end of intervals. The data field stores whether the interval just started (>0 value) or ended (<0 value). Different interval types can be represented in the same series by using multiple key values (eg, 1 for feature A, 2 for feature B, 3 for feature C, etc). The field data stores an 8-bit integer. This is largely an alias of a standard TimeSeries but that is identifiable as representing time intervals in a machine-readable way.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    data: NDArray[Shape["* num_times"], int] = Field(
        ..., description="""Use values >0 if interval started, <0 if interval ended."""
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


class DecompositionSeries(TimeSeries):
    """
    Spectral analysis of a time series, e.g. of an LFP or a speech signal.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    data: str = Field(..., description="""Data decomposed into frequency bands.""")
    metric: str = Field(
        ..., description="""The metric used, e.g. phase, amplitude, power."""
    )
    bands: str = Field(
        ...,
        description="""Table for describing the bands that this series was generated from. There should be one row in this table for each band.""",
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


class DecompositionSeriesData(ConfiguredBaseModel):
    """
    Data decomposed into frequency bands.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["data"] = Field("data")
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    array: Optional[
        NDArray[Shape["* num_times, * num_channels, * num_bands"], float]
    ] = Field(None)


class DecompositionSeriesBands(DynamicTable):
    """
    Table for describing the bands that this series was generated from. There should be one row in this table for each band.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["bands"] = Field("bands")
    band_name: Optional[List[str] | str] = Field(
        default_factory=list, description="""Name of the band, e.g. theta."""
    )
    band_limits: NDArray[Shape["* num_bands, 2 low_high"], float] = Field(
        ...,
        description="""Low and high limit of each band in Hz. If it is a Gaussian filter, use 2 SD on either side of the center.""",
    )
    band_mean: NDArray[Shape["* num_bands"], float] = Field(
        ..., description="""The mean Gaussian filters, in Hz."""
    )
    band_stdev: NDArray[Shape["* num_bands"], float] = Field(
        ..., description="""The standard deviation of Gaussian filters, in Hz."""
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
    )
    vector_data: Optional[List[str] | str] = Field(
        default_factory=list, description="""Vector columns of this dynamic table."""
    )
    vector_index: Optional[List[str] | str] = Field(
        default_factory=list,
        description="""Indices for the vector columns of this dynamic table.""",
    )


class Units(DynamicTable):
    """
    Data about spiking units. Event times of observed units (e.g. cell, synapse, etc.) should be concatenated and stored in spike_times.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field("Units")
    spike_times_index: Optional[str] = Field(
        None, description="""Index into the spike_times dataset."""
    )
    spike_times: Optional[str] = Field(
        None, description="""Spike times for each unit."""
    )
    obs_intervals_index: Optional[str] = Field(
        None, description="""Index into the obs_intervals dataset."""
    )
    obs_intervals: Optional[NDArray[Shape["* num_intervals, 2 start_end"], float]] = (
        Field(None, description="""Observation intervals for each unit.""")
    )
    electrodes_index: Optional[str] = Field(
        None, description="""Index into electrodes."""
    )
    electrodes: Optional[str] = Field(
        None,
        description="""Electrode that each spike unit came from, specified using a DynamicTableRegion.""",
    )
    electrode_group: Optional[List[str] | str] = Field(
        default_factory=list,
        description="""Electrode group that each spike unit came from.""",
    )
    waveform_mean: Optional[
        Union[
            NDArray[Shape["* num_units, * num_samples"], float],
            NDArray[Shape["* num_units, * num_samples, * num_electrodes"], float],
        ]
    ] = Field(None, description="""Spike waveform mean for each spike unit.""")
    waveform_sd: Optional[
        Union[
            NDArray[Shape["* num_units, * num_samples"], float],
            NDArray[Shape["* num_units, * num_samples, * num_electrodes"], float],
        ]
    ] = Field(
        None, description="""Spike waveform standard deviation for each spike unit."""
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
    )
    vector_data: Optional[List[str] | str] = Field(
        default_factory=list, description="""Vector columns of this dynamic table."""
    )
    vector_index: Optional[List[str] | str] = Field(
        default_factory=list,
        description="""Indices for the vector columns of this dynamic table.""",
    )


class UnitsSpikeTimesIndex(VectorIndex):
    """
    Index into the spike_times dataset.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["spike_times_index"] = Field("spike_times_index")
    target: Optional[str] = Field(
        None,
        description="""Reference to the target dataset that this index applies to.""",
    )
    array: Optional[NDArray[Shape["* num_rows"], Any]] = Field(None)


class UnitsSpikeTimes(VectorData):
    """
    Spike times for each unit.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["spike_times"] = Field("spike_times")
    resolution: Optional[float] = Field(
        None,
        description="""The smallest possible difference between two spike times. Usually 1 divided by the acquisition sampling rate from which spike times were extracted, but could be larger if the acquisition time series was downsampled or smaller if the acquisition time series was smoothed/interpolated and it is possible for the spike time to be between samples.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of what these vectors represent."""
    )
    array: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class UnitsObsIntervalsIndex(VectorIndex):
    """
    Index into the obs_intervals dataset.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["obs_intervals_index"] = Field("obs_intervals_index")
    target: Optional[str] = Field(
        None,
        description="""Reference to the target dataset that this index applies to.""",
    )
    array: Optional[NDArray[Shape["* num_rows"], Any]] = Field(None)


class UnitsElectrodesIndex(VectorIndex):
    """
    Index into electrodes.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["electrodes_index"] = Field("electrodes_index")
    target: Optional[str] = Field(
        None,
        description="""Reference to the target dataset that this index applies to.""",
    )
    array: Optional[NDArray[Shape["* num_rows"], Any]] = Field(None)


class UnitsElectrodes(DynamicTableRegion):
    """
    Electrode that each spike unit came from, specified using a DynamicTableRegion.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["electrodes"] = Field("electrodes")
    table: Optional[str] = Field(
        None,
        description="""Reference to the DynamicTable object that this region applies to.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of what this table region points to."""
    )
    array: Optional[
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
UnitsSpikeTimesIndex.model_rebuild()
UnitsSpikeTimes.model_rebuild()
UnitsObsIntervalsIndex.model_rebuild()
UnitsElectrodesIndex.model_rebuild()
UnitsElectrodes.model_rebuild()
