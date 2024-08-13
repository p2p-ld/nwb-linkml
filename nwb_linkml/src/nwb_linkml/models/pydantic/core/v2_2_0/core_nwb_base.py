from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
import numpy as np
from numpydantic import NDArray, Shape
from ...hdmf_common.v1_1_0.hdmf_common_table import Data, Container, DynamicTable

metamodel_version = "None"
version = "2.2.0"


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
linkml_meta = LinkMLMeta(
    {
        "annotations": {
            "is_namespace": {"tag": "is_namespace", "value": False},
            "namespace": {"tag": "namespace", "value": "core"},
        },
        "default_prefix": "core.nwb.base/",
        "id": "core.nwb.base",
        "imports": ["../../hdmf_common/v1_1_0/namespace", "core.nwb.language"],
        "name": "core.nwb.base",
    }
)


class NWBData(Data):
    """
    An abstract data type for a dataset.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.base", "tree_root": True}
    )

    name: str = Field(...)


class Image(NWBData):
    """
    An abstract data type for an image. Shape can be 2-D (x, y), or 3-D where the third dimension can have three or four elements, e.g. (x, y, (r, g, b)) or (x, y, (r, g, b, a)).
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.base", "tree_root": True}
    )

    name: str = Field(...)
    resolution: Optional[float] = Field(
        None, description="""Pixel resolution of the image, in pixels per centimeter."""
    )
    description: Optional[str] = Field(None, description="""Description of the image.""")
    value: Optional[
        Union[
            NDArray[Shape["* x, * y"], float],
            NDArray[Shape["* x, * y, 3 r_g_b"], float],
            NDArray[Shape["* x, * y, 4 r_g_b_a"], float],
        ]
    ] = Field(None)


class NWBContainer(Container):
    """
    An abstract data type for a generic container storing collections of data and metadata. Base type for all data and metadata containers.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.base", "tree_root": True}
    )

    name: str = Field(...)


class NWBDataInterface(NWBContainer):
    """
    An abstract data type for a generic container storing collections of data, as opposed to metadata.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.base", "tree_root": True}
    )

    name: str = Field(...)


class TimeSeries(NWBDataInterface):
    """
    General purpose time series.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.base", "tree_root": True}
    )

    name: str = Field(...)
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
    data: TimeSeriesData = Field(
        ...,
        description="""Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension should always represent time. This can also be used to store binary data (e.g., image frames). This can also be a link to data stored in an external file.""",
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


class TimeSeriesData(ConfiguredBaseModel):
    """
    Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension should always represent time. This can also be used to store binary data (e.g., image frames). This can also be a link to data stored in an external file.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.base"})

    name: Literal["data"] = Field(
        "data",
        json_schema_extra={"linkml_meta": {"equals_string": "data", "ifabsent": "string(data)"}},
    )
    conversion: Optional[float] = Field(
        1.0,
        description="""Scalar to multiply each element in data to convert it to the specified 'unit'. If the data are stored in acquisition system units or other units that require a conversion to be interpretable, multiply the data by 'conversion' to convert the data to the specified 'unit'. e.g. if the data acquisition system stores values in this object as signed 16-bit integers (int16 range -32,768 to 32,767) that correspond to a 5V range (-2.5V to 2.5V), and the data acquisition system gain is 8000X, then the 'conversion' multiplier to get from raw data acquisition values to recorded volts is 2.5/32768/8000 = 9.5367e-9.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "float(1.0)"}},
    )
    resolution: Optional[float] = Field(
        -1.0,
        description="""Smallest meaningful difference between values in data, stored in the specified by unit, e.g., the change in value of the least significant bit, or a larger number if signal noise is known to be present. If unknown, use -1.0.""",
        json_schema_extra={"linkml_meta": {"ifabsent": "float(-1.0)"}},
    )
    unit: str = Field(
        ...,
        description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""",
    )
    value: Optional[
        Union[
            NDArray[Shape["* num_times"], Any],
            NDArray[Shape["* num_times, * num_dim2"], Any],
            NDArray[Shape["* num_times, * num_dim2, * num_dim3"], Any],
            NDArray[Shape["* num_times, * num_dim2, * num_dim3, * num_dim4"], Any],
        ]
    ] = Field(None)


class TimeSeriesStartingTime(ConfiguredBaseModel):
    """
    Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.base"})

    name: Literal["starting_time"] = Field(
        "starting_time",
        json_schema_extra={
            "linkml_meta": {"equals_string": "starting_time", "ifabsent": "string(starting_time)"}
        },
    )
    rate: float = Field(..., description="""Sampling rate, in Hz.""")
    unit: Literal["seconds"] = Field(
        "seconds",
        description="""Unit of measurement for time, which is fixed to 'seconds'.""",
        json_schema_extra={
            "linkml_meta": {"equals_string": "seconds", "ifabsent": "string(seconds)"}
        },
    )
    value: float = Field(...)


class TimeSeriesSync(ConfiguredBaseModel):
    """
    Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.base"})

    name: Literal["sync"] = Field(
        "sync",
        json_schema_extra={"linkml_meta": {"equals_string": "sync", "ifabsent": "string(sync)"}},
    )


class ProcessingModule(NWBContainer):
    """
    A collection of processed data.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.base", "tree_root": True}
    )

    value: Optional[List[Union[DynamicTable, NWBDataInterface]]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"any_of": [{"range": "NWBDataInterface"}, {"range": "DynamicTable"}]}
        },
    )
    name: str = Field(...)


class Images(NWBDataInterface):
    """
    A collection of images.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.base", "tree_root": True}
    )

    name: str = Field("Images", json_schema_extra={"linkml_meta": {"ifabsent": "string(Images)"}})
    description: str = Field(..., description="""Description of this collection of images.""")
    image: List[Image] = Field(..., description="""Images stored in this collection.""")


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
