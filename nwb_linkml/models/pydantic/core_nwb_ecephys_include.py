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


from .nwb_language import (
    Arraylike
)

from .hdmf_common_table import (
    DynamicTableRegion
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


class ElectricalSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage data.
    """
    name: str = Field("data", const=True)
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. This value is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion', followed by 'channel_conversion' (if present), and then add 'offset'.""")
    array: Optional[Union[
        NDArray[Shape["* num_times"], Number],
        NDArray[Shape["* num_times, * num_channels"], Number],
        NDArray[Shape["* num_times, * num_channels, * num_samples"], Number]
    ]] = Field(None)
    

class ElectricalSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    num_channels: Optional[float] = Field(None)
    num_samples: Optional[float] = Field(None)
    

class ElectricalSeriesElectrodes(DynamicTableRegion):
    """
    DynamicTableRegion pointer to the electrodes that this time series was generated from.
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
    

class SpikeEventSeriesData(ConfiguredBaseModel):
    """
    Spike waveforms.
    """
    name: str = Field("data", const=True)
    unit: Optional[str] = Field(None, description="""Unit of measurement for waveforms, which is fixed to 'volts'.""")
    array: Optional[Union[
        NDArray[Shape["* num_events, * num_samples"], Number],
        NDArray[Shape["* num_events, * num_samples, * num_channels"], Number]
    ]] = Field(None)
    

class SpikeEventSeriesDataArray(Arraylike):
    
    num_events: float = Field(...)
    num_samples: float = Field(...)
    num_channels: Optional[float] = Field(None)
    

class FeatureExtractionFeatures(ConfiguredBaseModel):
    """
    Multi-dimensional array of features extracted from each event.
    """
    name: str = Field("features", const=True)
    array: Optional[NDArray[Shape["* num_events, * num_channels, * num_features"], Float32]] = Field(None)
    

class FeatureExtractionFeaturesArray(Arraylike):
    
    num_events: float = Field(...)
    num_channels: float = Field(...)
    num_features: float = Field(...)
    

class FeatureExtractionElectrodes(DynamicTableRegion):
    """
    DynamicTableRegion pointer to the electrodes that this time series was generated from.
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
    

class ClusterWaveformsWaveformMean(ConfiguredBaseModel):
    """
    The mean waveform for each cluster, using the same indices for each wave as cluster numbers in the associated Clustering module (i.e, cluster 3 is in array slot [3]). Waveforms corresponding to gaps in cluster sequence should be empty (e.g., zero- filled)
    """
    name: str = Field("waveform_mean", const=True)
    array: Optional[NDArray[Shape["* num_clusters, * num_samples"], Float32]] = Field(None)
    

class ClusterWaveformsWaveformMeanArray(Arraylike):
    
    num_clusters: float = Field(...)
    num_samples: float = Field(...)
    

class ClusterWaveformsWaveformSd(ConfiguredBaseModel):
    """
    Stdev of waveforms for each cluster, using the same indices as in mean
    """
    name: str = Field("waveform_sd", const=True)
    array: Optional[NDArray[Shape["* num_clusters, * num_samples"], Float32]] = Field(None)
    

class ClusterWaveformsWaveformSdArray(Arraylike):
    
    num_clusters: float = Field(...)
    num_samples: float = Field(...)
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ElectricalSeriesData.model_rebuild()
ElectricalSeriesDataArray.model_rebuild()
ElectricalSeriesElectrodes.model_rebuild()
SpikeEventSeriesData.model_rebuild()
SpikeEventSeriesDataArray.model_rebuild()
FeatureExtractionFeatures.model_rebuild()
FeatureExtractionFeaturesArray.model_rebuild()
FeatureExtractionElectrodes.model_rebuild()
ClusterWaveformsWaveformMean.model_rebuild()
ClusterWaveformsWaveformMeanArray.model_rebuild()
ClusterWaveformsWaveformSd.model_rebuild()
ClusterWaveformsWaveformSdArray.model_rebuild()
    