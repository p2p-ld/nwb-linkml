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


from ...hdmf_common.v1_5_0.hdmf_common_table import DynamicTableRegion, DynamicTable

from .core_nwb_base import (
    NWBContainer,
    TimeSeriesStartingTime,
    NWBDataInterface,
    TimeSeries,
    TimeSeriesSync,
)


metamodel_version = "None"
version = "2.5.0"


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


class ElectricalSeries(TimeSeries):
    """
    A time series of acquired voltage data from extracellular recordings. The data field is an int or float array storing data in volts. The first dimension should always represent time. The second dimension, if present, should represent channels.
    """

    name: str = Field(...)
    filtering: Optional[str] = Field(
        None,
        description="""Filtering applied to all channels of the data. For example, if this ElectricalSeries represents high-pass-filtered data (also known as AP Band), then this value could be \"High-pass 4-pole Bessel filter at 500 Hz\". If this ElectricalSeries represents low-pass-filtered LFP data and the type of filter is unknown, then this value could be \"Low-pass filter at 300 Hz\". If a non-standard filter type is used, provide as much detail about the filter properties as possible.""",
    )
    data: Union[
        NDArray[Shape["* num_times"], float],
        NDArray[Shape["* num_times, * num_channels"], float],
        NDArray[Shape["* num_times, * num_channels, * num_samples"], float],
    ] = Field(..., description="""Recorded voltage data.""")
    electrodes: str = Field(
        ...,
        description="""DynamicTableRegion pointer to the electrodes that this time series was generated from.""",
    )
    channel_conversion: Optional[NDArray[Shape["* num_channels"], float]] = Field(
        None,
        description="""Channel-specific conversion factor. Multiply the data in the 'data' dataset by these values along the channel axis (as indicated by axis attribute) AND by the global conversion factor in the 'conversion' attribute of 'data' to get the data values in Volts, i.e, data in Volts = data * data.conversion * channel_conversion. This approach allows for both global and per-channel data conversion factors needed to support the storage of electrical recordings as native values generated by data acquisition systems. If this dataset is not present, then there is no channel-specific conversion factor, i.e. it is 1 for all channels.""",
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


class ElectricalSeriesElectrodes(DynamicTableRegion):
    """
    DynamicTableRegion pointer to the electrodes that this time series was generated from.
    """

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


class SpikeEventSeries(ElectricalSeries):
    """
    Stores snapshots/snippets of recorded spike events (i.e., threshold crossings). This may also be raw data, as reported by ephys hardware. If so, the TimeSeries::description field should describe how events were detected. All SpikeEventSeries should reside in a module (under EventWaveform interface) even if the spikes were reported and stored by hardware. All events span the same recording channels and store snapshots of equal duration. TimeSeries::data array structure: [num events] [num channels] [num samples] (or [num events] [num samples] for single electrode).
    """

    name: str = Field(...)
    data: Union[
        NDArray[Shape["* num_events, * num_channels, * num_samples"], float],
        NDArray[Shape["* num_events, * num_samples"], float],
    ] = Field(..., description="""Spike waveforms.""")
    timestamps: NDArray[Shape["* num_times"], float] = Field(
        ...,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time. Timestamps are required for the events. Unlike for TimeSeries, timestamps are required for SpikeEventSeries and are thus re-specified here.""",
    )
    filtering: Optional[str] = Field(
        None,
        description="""Filtering applied to all channels of the data. For example, if this ElectricalSeries represents high-pass-filtered data (also known as AP Band), then this value could be \"High-pass 4-pole Bessel filter at 500 Hz\". If this ElectricalSeries represents low-pass-filtered LFP data and the type of filter is unknown, then this value could be \"Low-pass filter at 300 Hz\". If a non-standard filter type is used, provide as much detail about the filter properties as possible.""",
    )
    electrodes: str = Field(
        ...,
        description="""DynamicTableRegion pointer to the electrodes that this time series was generated from.""",
    )
    channel_conversion: Optional[NDArray[Shape["* num_channels"], float]] = Field(
        None,
        description="""Channel-specific conversion factor. Multiply the data in the 'data' dataset by these values along the channel axis (as indicated by axis attribute) AND by the global conversion factor in the 'conversion' attribute of 'data' to get the data values in Volts, i.e, data in Volts = data * data.conversion * channel_conversion. This approach allows for both global and per-channel data conversion factors needed to support the storage of electrical recordings as native values generated by data acquisition systems. If this dataset is not present, then there is no channel-specific conversion factor, i.e. it is 1 for all channels.""",
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


class FeatureExtraction(NWBDataInterface):
    """
    Features, such as PC1 and PC2, that are extracted from signals stored in a SpikeEventSeries or other source.
    """

    name: str = Field("FeatureExtraction")
    description: NDArray[Shape["* num_features"], str] = Field(
        ...,
        description="""Description of features (eg, ''PC1'') for each of the extracted features.""",
    )
    features: NDArray[Shape["* num_events, * num_channels, * num_features"], float] = (
        Field(
            ...,
            description="""Multi-dimensional array of features extracted from each event.""",
        )
    )
    times: NDArray[Shape["* num_events"], float] = Field(
        ...,
        description="""Times of events that features correspond to (can be a link).""",
    )
    electrodes: str = Field(
        ...,
        description="""DynamicTableRegion pointer to the electrodes that this time series was generated from.""",
    )


class FeatureExtractionElectrodes(DynamicTableRegion):
    """
    DynamicTableRegion pointer to the electrodes that this time series was generated from.
    """

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


class EventDetection(NWBDataInterface):
    """
    Detected spike events from voltage trace(s).
    """

    name: str = Field("EventDetection")
    detection_method: str = Field(
        ...,
        description="""Description of how events were detected, such as voltage threshold, or dV/dT threshold, as well as relevant values.""",
    )
    source_idx: NDArray[Shape["* num_events"], int] = Field(
        ...,
        description="""Indices (zero-based) into source ElectricalSeries::data array corresponding to time of event. ''description'' should define what is meant by time of event (e.g., .25 ms before action potential peak, zero-crossing time, etc). The index points to each event from the raw data.""",
    )
    times: NDArray[Shape["* num_events"], float] = Field(
        ..., description="""Timestamps of events, in seconds."""
    )


class EventWaveform(NWBDataInterface):
    """
    Represents either the waveforms of detected events, as extracted from a raw data trace in /acquisition, or the event waveforms that were stored during experiment acquisition.
    """

    children: Optional[List[SpikeEventSeries] | SpikeEventSeries] = Field(
        default_factory=dict
    )
    name: str = Field(...)


class FilteredEphys(NWBDataInterface):
    """
    Electrophysiology data from one or more channels that has been subjected to filtering. Examples of filtered data include Theta and Gamma (LFP has its own interface). FilteredEphys modules publish an ElectricalSeries for each filtered channel or set of channels. The name of each ElectricalSeries is arbitrary but should be informative. The source of the filtered data, whether this is from analysis of another time series or as acquired by hardware, should be noted in each's TimeSeries::description field. There is no assumed 1::1 correspondence between filtered ephys signals and electrodes, as a single signal can apply to many nearby electrodes, and one electrode may have different filtered (e.g., theta and/or gamma) signals represented. Filter properties should be noted in the ElectricalSeries 'filtering' attribute.
    """

    children: Optional[List[ElectricalSeries] | ElectricalSeries] = Field(
        default_factory=dict
    )
    name: str = Field(...)


class LFP(NWBDataInterface):
    """
    LFP data from one or more channels. The electrode map in each published ElectricalSeries will identify which channels are providing LFP data. Filter properties should be noted in the ElectricalSeries 'filtering' attribute.
    """

    children: Optional[List[ElectricalSeries] | ElectricalSeries] = Field(
        default_factory=dict
    )
    name: str = Field(...)


class ElectrodeGroup(NWBContainer):
    """
    A physical grouping of electrodes, e.g. a shank of an array.
    """

    name: str = Field(...)
    description: Optional[str] = Field(
        None, description="""Description of this electrode group."""
    )
    location: Optional[str] = Field(
        None,
        description="""Location of electrode group. Specify the area, layer, comments on estimation of area/layer, etc. Use standard atlas names for anatomical regions when possible.""",
    )
    position: Optional[str] = Field(
        None, description="""stereotaxic or common framework coordinates"""
    )


class ElectrodeGroupPosition(ConfiguredBaseModel):
    """
    stereotaxic or common framework coordinates
    """

    name: Literal["position"] = Field("position")
    x: Optional[float] = Field(None, description="""x coordinate""")
    y: Optional[float] = Field(None, description="""y coordinate""")
    z: Optional[float] = Field(None, description="""z coordinate""")


class ClusterWaveforms(NWBDataInterface):
    """
    DEPRECATED The mean waveform shape, including standard deviation, of the different clusters. Ideally, the waveform analysis should be performed on data that is only high-pass filtered. This is a separate module because it is expected to require updating. For example, IMEC probes may require different storage requirements to store/display mean waveforms, requiring a new interface or an extension of this one.
    """

    name: str = Field("ClusterWaveforms")
    waveform_filtering: str = Field(
        ..., description="""Filtering applied to data before generating mean/sd"""
    )
    waveform_mean: NDArray[Shape["* num_clusters, * num_samples"], float] = Field(
        ...,
        description="""The mean waveform for each cluster, using the same indices for each wave as cluster numbers in the associated Clustering module (i.e, cluster 3 is in array slot [3]). Waveforms corresponding to gaps in cluster sequence should be empty (e.g., zero- filled)""",
    )
    waveform_sd: NDArray[Shape["* num_clusters, * num_samples"], float] = Field(
        ...,
        description="""Stdev of waveforms for each cluster, using the same indices as in mean""",
    )


class Clustering(NWBDataInterface):
    """
    DEPRECATED Clustered spike data, whether from automatic clustering tools (e.g., klustakwik) or as a result of manual sorting.
    """

    name: str = Field("Clustering")
    description: str = Field(
        ...,
        description="""Description of clusters or clustering, (e.g. cluster 0 is noise, clusters curated using Klusters, etc)""",
    )
    num: NDArray[Shape["* num_events"], int] = Field(
        ..., description="""Cluster number of each event"""
    )
    peak_over_rms: NDArray[Shape["* num_clusters"], float] = Field(
        ...,
        description="""Maximum ratio of waveform peak to RMS on any channel in the cluster (provides a basic clustering metric).""",
    )
    times: NDArray[Shape["* num_events"], float] = Field(
        ...,
        description="""Times of clustered events, in seconds. This may be a link to times field in associated FeatureExtraction module.""",
    )
