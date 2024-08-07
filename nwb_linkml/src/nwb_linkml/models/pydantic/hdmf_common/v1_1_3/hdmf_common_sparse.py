from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
import numpy as np

metamodel_version = "None"
version = "1.1.3"


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
            "is_namespace": {"tag": "is_namespace", "value": False},
            "namespace": {"tag": "namespace", "value": "hdmf-common"},
        },
        "default_prefix": "hdmf-common.sparse/",
        "id": "hdmf-common.sparse",
        "imports": ["hdmf-common.nwb.language"],
        "name": "hdmf-common.sparse",
    }
)


class CSRMatrix(ConfiguredBaseModel):
    """
    a compressed sparse row matrix
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "hdmf-common.sparse", "tree_root": True}
    )

    name: str = Field(...)
    shape: Optional[int] = Field(None, description="""the shape of this sparse matrix""")
    indices: CSRMatrixIndices = Field(..., description="""column indices""")
    indptr: CSRMatrixIndptr = Field(..., description="""index pointer""")
    data: CSRMatrixData = Field(..., description="""values in the matrix""")


class CSRMatrixIndices(ConfiguredBaseModel):
    """
    column indices
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-common.sparse"})

    name: Literal["indices"] = Field(
        "indices",
        json_schema_extra={
            "linkml_meta": {"equals_string": "indices", "ifabsent": "string(indices)"}
        },
    )


class CSRMatrixIndptr(ConfiguredBaseModel):
    """
    index pointer
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-common.sparse"})

    name: Literal["indptr"] = Field(
        "indptr",
        json_schema_extra={
            "linkml_meta": {"equals_string": "indptr", "ifabsent": "string(indptr)"}
        },
    )


class CSRMatrixData(ConfiguredBaseModel):
    """
    values in the matrix
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-common.sparse"})

    name: Literal["data"] = Field(
        "data",
        json_schema_extra={"linkml_meta": {"equals_string": "data", "ifabsent": "string(data)"}},
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
CSRMatrix.model_rebuild()
CSRMatrixIndices.model_rebuild()
CSRMatrixIndptr.model_rebuild()
CSRMatrixData.model_rebuild()
