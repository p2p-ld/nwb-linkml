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


from .hdmf_common_base import Container


metamodel_version = "None"
version = "1.8.0"


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


class CSRMatrix(Container):
    """
    A compressed sparse row matrix. Data are stored in the standard CSR format, where column indices for row i are stored in indices[indptr[i]:indptr[i+1]] and their corresponding values are stored in data[indptr[i]:indptr[i+1]].
    """

    name: str = Field(...)
    shape: Optional[int] = Field(
        None,
        description="""The shape (number of rows, number of columns) of this sparse matrix.""",
    )
    indices: NDArray[Shape["* number_of_non_zero_values"], int] = Field(
        ..., description="""The column indices."""
    )
    indptr: NDArray[Shape["* number_of_rows_in_the_matrix_1"], int] = Field(
        ..., description="""The row index pointer."""
    )
    data: NDArray[Shape["* number_of_non_zero_values"], Any] = Field(
        ..., description="""The non-zero values in the matrix."""
    )
