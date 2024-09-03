from __future__ import annotations

import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

from ...hdmf_common.v1_5_1.hdmf_common_base import Container, Data, SimpleMultiContainer
from ...hdmf_common.v1_5_1.hdmf_common_sparse import CSRMatrix, CSRMatrixData
from ...hdmf_common.v1_5_1.hdmf_common_table import (
    AlignedDynamicTable,
    DynamicTable,
    DynamicTableRegion,
    ElementIdentifiers,
    VectorData,
    VectorIndex,
)
from ...hdmf_experimental.v0_2_0.hdmf_experimental_experimental import EnumData
from ...hdmf_experimental.v0_2_0.hdmf_experimental_resources import (
    ExternalResources,
    ExternalResourcesEntities,
    ExternalResourcesKeys,
    ExternalResourcesObjectKeys,
    ExternalResourcesObjects,
    ExternalResourcesResources,
)


metamodel_version = "None"
version = "0.2.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="allow",
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

    @field_validator("*", mode="wrap")
    @classmethod
    def coerce_value(cls, v: Any, handler) -> Any:
        """Try to rescue instantiation by using the value field"""
        try:
            return handler(v)
        except Exception as e1:
            try:
                if hasattr(v, "value"):
                    return handler(v.value)
                else:
                    return handler(v["value"])
            except Exception as e2:
                raise e2 from e1


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


linkml_meta = LinkMLMeta(
    {
        "annotations": {
            "is_namespace": {"tag": "is_namespace", "value": True},
            "namespace": {"tag": "namespace", "value": "hdmf-experimental"},
        },
        "default_prefix": "hdmf-experimental/",
        "description": (
            "Experimental data structures provided by HDMF. These are not "
            "guaranteed to be available in the future."
        ),
        "id": "hdmf-experimental",
        "imports": [
            "hdmf-experimental.experimental",
            "hdmf-experimental.resources",
            "hdmf-experimental.nwb.language",
        ],
        "name": "hdmf-experimental",
    }
)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
