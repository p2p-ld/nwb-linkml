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


from ...hdmf_common.v1_1_3.hdmf_common_table import Container, Data, DynamicTable


metamodel_version = "None"
version = "2.2.4"


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


class NWBData(Data):
    """
    An abstract data type for a dataset.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)


class Image(NWBData):
    """
    An abstract data type for an image. Shape can be 2-D (x, y), or 3-D where the third dimension can have three or four elements, e.g. (x, y, (r, g, b)) or (x, y, (r, g, b, a)).
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    resolution: Optional[float] = Field(
        None, description="""Pixel resolution of the image, in pixels per centimeter."""
    )
    description: Optional[str] = Field(None, description="""Description of the image.""")
    array: Optional[
        Union[
            NDArray[Shape["* x, * y"], Number],
            NDArray[Shape["* x, * y, 3 r_g_b"], Number],
            NDArray[Shape["* x, * y, 3 r_g_b, 4 r_g_b_a"], Number],
        ]
    ] = Field(None)


class NWBContainer(Container):
    """
    An abstract data type for a generic container storing collections of data and metadata. Base type for all data and metadata containers.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)


class NWBDataInterface(NWBContainer):
    """
    An abstract data type for a generic container storing collections of data, as opposed to metadata.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)


class TimeSeries(NWBDataInterface):
    """
    General purpose time series.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(
        None,
        description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""",
    )
    data: TimeSeriesData = Field(
        ...,
        description="""Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension should always represent time. This can also be used to store binary data (e.g., image frames). This can also be a link to data stored in an external file.""",
    )
    starting_time: Optional[TimeSeriesStartingTime] = Field(
        None,
        description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""",
    )
    timestamps: Optional[List[float]] = Field(
        default_factory=list,
        description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""",
    )
    control: Optional[List[int]] = Field(
        default_factory=list,
        description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""",
    )
    control_description: Optional[List[str]] = Field(
        default_factory=list,
        description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""",
    )
    sync: Optional[TimeSeriesSync] = Field(
        None,
        description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""",
    )


class TimeSeriesData(ConfiguredBaseModel):
    """
    Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension should always represent time. This can also be used to store binary data (e.g., image frames). This can also be a link to data stored in an external file.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["data"] = Field("data")
    conversion: Optional[float] = Field(
        None,
        description="""Scalar to multiply each element in data to convert it to the specified 'unit'. If the data are stored in acquisition system units or other units that require a conversion to be interpretable, multiply the data by 'conversion' to convert the data to the specified 'unit'. e.g. if the data acquisition system stores values in this object as signed 16-bit integers (int16 range -32,768 to 32,767) that correspond to a 5V range (-2.5V to 2.5V), and the data acquisition system gain is 8000X, then the 'conversion' multiplier to get from raw data acquisition values to recorded volts is 2.5/32768/8000 = 9.5367e-9.""",
    )
    resolution: Optional[float] = Field(
        None,
        description="""Smallest meaningful difference between values in data, stored in the specified by unit, e.g., the change in value of the least significant bit, or a larger number if signal noise is known to be present. If unknown, use -1.0.""",
    )
    unit: Optional[str] = Field(
        None,
        description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    array: Optional[
        Union[
            NDArray[Shape["* num_times"], Any],
            NDArray[Shape["* num_times, * num_DIM2"], Any],
            NDArray[Shape["* num_times, * num_DIM2, * num_DIM3"], Any],
            NDArray[Shape["* num_times, * num_DIM2, * num_DIM3, * num_DIM4"], Any],
        ]
    ] = Field(None)


class TimeSeriesStartingTime(ConfiguredBaseModel):
    """
    Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["starting_time"] = Field("starting_time")
    rate: Optional[float] = Field(None, description="""Sampling rate, in Hz.""")
    unit: Optional[str] = Field(
        None, description="""Unit of measurement for time, which is fixed to 'seconds'."""
    )
    value: float = Field(...)


class TimeSeriesSync(ConfiguredBaseModel):
    """
    Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["sync"] = Field("sync")


class ProcessingModule(NWBContainer):
    """
    A collection of processed data.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    children: Optional[Dict[str, Union[DynamicTable, NWBDataInterface]]] = Field(
        default_factory=dict
    )
    name: str = Field(...)


class Images(NWBDataInterface):
    """
    A collection of images.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    description: Optional[str] = Field(
        None, description="""Description of this collection of images."""
    )
    image: List[Image] = Field(
        default_factory=list, description="""Images stored in this collection."""
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
NWBData.model_rebuild()
Image.model_rebuild()
NWBContainer.model_rebuild()
NWBDataInterface.model_rebuild()
TimeSeries.model_rebuild()
TimeSeriesData.model_rebuild()
TimeSeriesStartingTime.model_rebuild()
TimeSeriesSync.model_rebuild()
ProcessingModule.model_rebuild()
Images.model_rebuild()
