from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union, ClassVar
from pydantic import BaseModel as BaseModel, Field
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


from ...hdmf_common.v1_1_2.hdmf_common_table import VectorData, DynamicTable, VectorIndex


metamodel_version = "None"
version = "2.2.1"


class ConfiguredBaseModel(
    BaseModel,
    validate_assignment=True,
    validate_default=True,
    extra="forbid",
    arbitrary_types_allowed=True,
    use_enum_values=True,
):
    hdf5_path: Optional[str] = Field(
        None, description="The absolute path that this object is stored in an NWB file"
    )


class LinkML_Meta(BaseModel):
    """Extra LinkML Metadata stored as a class attribute"""

    tree_root: bool = False


class TimeIntervals(DynamicTable):
    """
    A container for aggregating epoch data and the TimeSeries that each epoch applies to.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    start_time: Optional[List[float]] = Field(
        default_factory=list, description="""Start time of epoch, in seconds."""
    )
    stop_time: Optional[List[float]] = Field(
        default_factory=list, description="""Stop time of epoch, in seconds."""
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="""User-defined tags that identify or categorize events.""",
    )
    tags_index: Optional[TimeIntervalsTagsIndex] = Field(None, description="""Index for tags.""")
    timeseries: Optional[List[Any]] = Field(
        default_factory=list, description="""An index into a TimeSeries object."""
    )
    timeseries_index: Optional[TimeIntervalsTimeseriesIndex] = Field(
        None, description="""Index for timeseries."""
    )
    colnames: Optional[str] = Field(
        None,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: Optional[str] = Field(
        None, description="""Description of what is in this dynamic table."""
    )
    id: List[int] = Field(
        default_factory=list,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
    )
    vector_data: Optional[List[VectorData]] = Field(
        default_factory=list, description="""Vector columns of this dynamic table."""
    )
    vector_index: Optional[List[VectorIndex]] = Field(
        default_factory=list,
        description="""Indices for the vector columns of this dynamic table.""",
    )


class TimeIntervalsTagsIndex(VectorIndex):
    """
    Index for tags.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["tags_index"] = Field("tags_index")
    target: Optional[VectorData] = Field(
        None, description="""Reference to the target dataset that this index applies to."""
    )


class TimeIntervalsTimeseriesIndex(VectorIndex):
    """
    Index for timeseries.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["timeseries_index"] = Field("timeseries_index")
    target: Optional[VectorData] = Field(
        None, description="""Reference to the target dataset that this index applies to."""
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
TimeIntervals.model_rebuild()
TimeIntervalsTagsIndex.model_rebuild()
TimeIntervalsTimeseriesIndex.model_rebuild()
