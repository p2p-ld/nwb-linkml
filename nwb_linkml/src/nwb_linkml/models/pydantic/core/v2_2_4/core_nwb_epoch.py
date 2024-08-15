from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
import numpy as np
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union, Annotated, Type, TypeVar
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator,
    ValidationInfo,
    BeforeValidator,
)
from ...hdmf_common.v1_1_3.hdmf_common_table import DynamicTable, VectorIndex, VectorData
from ...core.v2_2_4.core_nwb_base import TimeSeries
from numpydantic import NDArray, Shape

metamodel_version = "None"
version = "2.2.4"


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

ModelType = TypeVar("ModelType", bound=Type[BaseModel])


def _get_name(item: ModelType | dict, info: ValidationInfo) -> Union[ModelType, dict]:
    """Get the name of the slot that refers to this object"""
    assert isinstance(item, (BaseModel, dict)), f"{item} was not a BaseModel or a dict!"
    name = info.field_name
    if isinstance(item, BaseModel):
        item.name = name
    else:
        item["name"] = name
    return item


Named = Annotated[ModelType, BeforeValidator(_get_name)]
linkml_meta = LinkMLMeta(
    {
        "annotations": {
            "is_namespace": {"tag": "is_namespace", "value": False},
            "namespace": {"tag": "namespace", "value": "core"},
        },
        "default_prefix": "core.nwb.epoch/",
        "id": "core.nwb.epoch",
        "imports": ["../../hdmf_common/v1_1_3/namespace", "core.nwb.base", "core.nwb.language"],
        "name": "core.nwb.epoch",
    }
)


class TimeIntervals(DynamicTable):
    """
    A container for aggregating epoch data and the TimeSeries that each epoch applies to.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "core.nwb.epoch", "tree_root": True}
    )

    name: str = Field(...)
    start_time: VectorData[NDArray[Any, float]] = Field(
        ...,
        description="""Start time of epoch, in seconds.""",
        json_schema_extra={
            "linkml_meta": {
                "array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}
            }
        },
    )
    stop_time: VectorData[NDArray[Any, float]] = Field(
        ...,
        description="""Stop time of epoch, in seconds.""",
        json_schema_extra={
            "linkml_meta": {
                "array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}
            }
        },
    )
    tags: VectorData[Optional[NDArray[Any, str]]] = Field(
        None,
        description="""User-defined tags that identify or categorize events.""",
        json_schema_extra={
            "linkml_meta": {
                "array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}
            }
        },
    )
    tags_index: Named[Optional[VectorIndex]] = Field(
        None,
        description="""Index for tags.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    timeseries: Optional[TimeIntervalsTimeseries] = Field(
        None, description="""An index into a TimeSeries object."""
    )
    timeseries_index: Named[Optional[VectorIndex]] = Field(
        None,
        description="""Index for timeseries.""",
        json_schema_extra={
            "linkml_meta": {
                "annotations": {
                    "named": {"tag": "named", "value": True},
                    "source_type": {"tag": "source_type", "value": "neurodata_type_inc"},
                }
            }
        },
    )
    colnames: List[str] = Field(
        ...,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: str = Field(..., description="""Description of what is in this dynamic table.""")
    id: VectorData[NDArray[Shape["* num_rows"], int]] = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )
    vector_data: Optional[List[VectorData]] = Field(
        None, description="""Vector columns of this dynamic table."""
    )
    vector_index: Optional[List[VectorIndex]] = Field(
        None, description="""Indices for the vector columns of this dynamic table."""
    )


class TimeIntervalsTimeseries(VectorData):
    """
    An index into a TimeSeries object.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.epoch"})

    name: Literal["timeseries"] = Field(
        "timeseries",
        json_schema_extra={
            "linkml_meta": {"equals_string": "timeseries", "ifabsent": "string(timeseries)"}
        },
    )
    idx_start: Optional[NDArray[Shape["*"], int]] = Field(
        None,
        description="""Start index into the TimeSeries 'data' and 'timestamp' datasets of the referenced TimeSeries. The first dimension of those arrays is always time.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    count: Optional[NDArray[Shape["*"], int]] = Field(
        None,
        description="""Number of data samples available in this time series, during this epoch.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    timeseries: Optional[NDArray[Shape["*"], TimeSeries]] = Field(
        None,
        description="""the TimeSeries that this index applies to.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    description: str = Field(..., description="""Description of what these vectors represent.""")
    value: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
TimeIntervals.model_rebuild()
TimeIntervalsTimeseries.model_rebuild()
