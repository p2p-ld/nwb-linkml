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


from .core_nwb_base import (
    TimeSeriesStartingTime,
    TimeSeries,
    TimeSeriesSync,
    NWBContainer
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


class OptogeneticSeries(TimeSeries):
    """
    An optogenetic stimulus.
    """
    name:str= Field(...)
    data:List[float]= Field(default_factory=list, description="""Applied power for optogenetic stimulus, in watts.""")
    description:Optional[str]= Field(None, description="""Description of the time series.""")
    comments:Optional[str]= Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time:Optional[TimeSeriesStartingTime]= Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps:Optional[List[float]]= Field(default_factory=list, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control:Optional[List[int]]= Field(default_factory=list, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description:Optional[List[str]]= Field(default_factory=list, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync:Optional[TimeSeriesSync]= Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class OptogeneticStimulusSite(NWBContainer):
    """
    A site of optogenetic stimulation.
    """
    name:str= Field(...)
    description:str= Field(..., description="""Description of stimulation site.""")
    excitation_lambda:float= Field(..., description="""Excitation wavelength, in nm.""")
    location:str= Field(..., description="""Location of the stimulation site. Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""")
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
# OptogeneticSeries.model_rebuild()
# OptogeneticStimulusSite.model_rebuild()
    