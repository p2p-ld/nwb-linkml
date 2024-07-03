from __future__ import annotations

import sys
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Optional,
)

from nptyping import (
    Shape,
)
from pydantic import BaseModel as BaseModel
from pydantic import ConfigDict, Field

from nwb_linkml.types import NDArray

if sys.version_info >= (3, 8):
    pass
else:
    pass
if TYPE_CHECKING:
    import numpy as np


from .hdmf_common_base import Container

metamodel_version = "None"
version = "1.5.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="allow",
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )
    hdf5_path: Optional[str] = Field(
        None, description="The absolute path that this object is stored in an NWB file"
    )

    object_id: Optional[str] = Field(None, description="Unique UUID for each object")

    def __getitem__(self, i: slice | int) -> np.ndarray:
        if hasattr(self, "array"):
            return self.array[i]
        else:
            return super().__getitem__(i)

    def __setitem__(self, i: slice | int, value: Any):
        if hasattr(self, "array"):
            self.array[i] = value
        else:
            super().__setitem__(i, value)


class LinkML_Meta(BaseModel):
    """Extra LinkML Metadata stored as a class attribute"""

    tree_root: bool = False


class CSRMatrix(Container):
    """
    A compressed sparse row matrix. Data are stored in the standard CSR format, where column indices for row i are stored in indices[indptr[i]:indptr[i+1]] and their corresponding values are stored in data[indptr[i]:indptr[i+1]].
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    shape: Optional[int] = Field(
        None,
        description="""The shape (number of rows, number of columns) of this sparse matrix.""",
    )
    indices: NDArray[Shape["* number of non-zero values"], int] = Field(
        ..., description="""The column indices."""
    )
    indptr: NDArray[Shape["* number of rows in the matrix + 1"], int] = Field(
        ..., description="""The row index pointer."""
    )
    data: NDArray[Shape["* number of non-zero values"], Any] = Field(
        ..., description="""The non-zero values in the matrix."""
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
CSRMatrix.model_rebuild()
