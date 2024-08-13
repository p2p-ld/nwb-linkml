from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
import numpy as np
from ...hdmf_common.v1_5_0.hdmf_common_base import Container
from numpydantic import NDArray, Shape

metamodel_version = "None"
version = "1.5.0"


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
            "namespace": {"tag": "namespace", "value": "hdmf-common"},
        },
        "default_prefix": "hdmf-common.sparse/",
        "id": "hdmf-common.sparse",
        "imports": ["hdmf-common.base", "hdmf-common.nwb.language"],
        "name": "hdmf-common.sparse",
    }
)


class CSRMatrix(Container):
    """
    A compressed sparse row matrix. Data are stored in the standard CSR format, where column indices for row i are stored in indices[indptr[i]:indptr[i+1]] and their corresponding values are stored in data[indptr[i]:indptr[i+1]].
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "hdmf-common.sparse", "tree_root": True}
    )

    name: str = Field(...)
    shape: List[int] = Field(
        ..., description="""The shape (number of rows, number of columns) of this sparse matrix."""
    )
    indices: NDArray[Shape["* number_of_non_zero_values"], int] = Field(
        ...,
        description="""The column indices.""",
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "number_of_non_zero_values"}]}}
        },
    )
    indptr: NDArray[Shape["* number_of_rows_in_the_matrix_1"], int] = Field(
        ...,
        description="""The row index pointer.""",
        json_schema_extra={
            "linkml_meta": {"array": {"dimensions": [{"alias": "number_of_rows_in_the_matrix_1"}]}}
        },
    )
    data: CSRMatrixData = Field(..., description="""The non-zero values in the matrix.""")


class CSRMatrixData(ConfiguredBaseModel):
    """
    The non-zero values in the matrix.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-common.sparse"})

    name: Literal["data"] = Field(
        "data",
        json_schema_extra={"linkml_meta": {"equals_string": "data", "ifabsent": "string(data)"}},
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
CSRMatrix.model_rebuild()
CSRMatrixData.model_rebuild()
