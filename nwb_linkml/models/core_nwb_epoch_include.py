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
    TimeSeriesReferenceVectorData
)

from .hdmf_common_table import (
    VectorIndex
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


class TimeIntervalsTagsIndex(VectorIndex):
    """
    Index for tags.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class TimeIntervalsTimeseries(TimeSeriesReferenceVectorData):
    """
    An index into a TimeSeries object.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class TimeIntervalsTimeseriesIndex(VectorIndex):
    """
    Index for timeseries.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
TimeIntervalsTagsIndex.update_forward_refs()
TimeIntervalsTimeseries.update_forward_refs()
TimeIntervalsTimeseriesIndex.update_forward_refs()
