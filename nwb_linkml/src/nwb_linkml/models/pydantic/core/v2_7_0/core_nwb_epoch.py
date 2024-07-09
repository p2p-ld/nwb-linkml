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


from ...hdmf_common.v1_8_0.hdmf_common_table import (
    VectorIndex,
    DynamicTable,
    VectorData,
)

from .core_nwb_base import TimeSeriesReferenceVectorData, TimeSeries


metamodel_version = "None"
version = "2.7.0"


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


class TimeIntervals(DynamicTable):
    """
    A container for aggregating epoch data and the TimeSeries that each epoch applies to.
    """

    name: str = Field(...)
    start_time: Optional[List[float] | float] = Field(
        default_factory=list, description="""Start time of epoch, in seconds."""
    )
    stop_time: Optional[List[float] | float] = Field(
        default_factory=list, description="""Stop time of epoch, in seconds."""
    )
    tags: Optional[List[str] | str] = Field(
        default_factory=list,
        description="""User-defined tags that identify or categorize events.""",
    )
    tags_index: Optional[str] = Field(None, description="""Index for tags.""")
    timeseries: Optional[str] = Field(None, description="""An index into a TimeSeries object.""")
    timeseries_index: Optional[str] = Field(None, description="""Index for timeseries.""")
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
        default_factory=list,
        description="""Vector columns, including index columns, of this dynamic table.""",
    )


class TimeIntervalsTagsIndex(VectorIndex):
    """
    Index for tags.
    """

    name: Literal["tags_index"] = Field("tags_index")
    target: Optional[str] = Field(
        None,
        description="""Reference to the target dataset that this index applies to.""",
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


class TimeIntervalsTimeseries(TimeSeriesReferenceVectorData):
    """
    An index into a TimeSeries object.
    """

    name: Literal["timeseries"] = Field("timeseries")
    idx_start: int = Field(
        ...,
        description="""Start index into the TimeSeries 'data' and 'timestamp' datasets of the referenced TimeSeries. The first dimension of those arrays is always time.""",
    )
    count: int = Field(
        ...,
        description="""Number of data samples available in this time series, during this epoch""",
    )
    timeseries: str = Field(..., description="""The TimeSeries that this index applies to""")
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


class TimeIntervalsTimeseriesIndex(VectorIndex):
    """
    Index for timeseries.
    """

    name: Literal["timeseries_index"] = Field("timeseries_index")
    target: Optional[str] = Field(
        None,
        description="""Reference to the target dataset that this index applies to.""",
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
