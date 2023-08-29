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


from .core_nwb_epoch_include import (
    TimeIntervalsTimeseriesIndex,
    TimeIntervalsTagsIndex,
    TimeIntervalsTimeseries
)

from .hdmf_common_table import (
    DynamicTable
)


metamodel_version = "None"
version = "None"

class WeakRefShimBaseModel(BaseModel):
   __slots__ = '__weakref__'

class ConfiguredBaseModel(WeakRefShimBaseModel,
                validate_assignment = True,
                validate_all = True,
                underscore_attrs_are_private = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


class TimeIntervals(DynamicTable):
    """
    A container for aggregating epoch data and the TimeSeries that each epoch applies to.
    """
    start_time: Optional[List[float]] = Field(default_factory=list, description="""Start time of epoch, in seconds.""")
    stop_time: Optional[List[float]] = Field(default_factory=list, description="""Stop time of epoch, in seconds.""")
    tags: Optional[List[str]] = Field(default_factory=list, description="""User-defined tags that identify or categorize events.""")
    tags_index: Optional[TimeIntervalsTagsIndex] = Field(None, description="""Index for tags.""")
    timeseries: Optional[TimeIntervalsTimeseries] = Field(None, description="""An index into a TimeSeries object.""")
    timeseries_index: Optional[TimeIntervalsTimeseriesIndex] = Field(None, description="""Index for timeseries.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
TimeIntervals.update_forward_refs()
