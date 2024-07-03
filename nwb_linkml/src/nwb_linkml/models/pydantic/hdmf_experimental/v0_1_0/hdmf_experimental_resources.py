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


from ...hdmf_common.v1_5_0.hdmf_common_base import Container

metamodel_version = "None"
version = "0.1.0"


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


class ExternalResources(Container):
    """
    A set of four tables for tracking external resource references in a file. NOTE: this data type is in beta testing and is subject to change in a later version.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    keys: NDArray[Shape["* num_rows"], Any] = Field(
        ...,
        description="""A table for storing user terms that are used to refer to external resources.""",
    )
    entities: NDArray[Shape["* num_rows"], Any] = Field(
        ...,
        description="""A table for mapping user terms (i.e., keys) to resource entities.""",
    )
    resources: NDArray[Shape["* num_rows"], Any] = Field(
        ...,
        description="""A table for mapping user terms (i.e., keys) to resource entities.""",
    )
    objects: NDArray[Shape["* num_rows"], Any] = Field(
        ...,
        description="""A table for identifying which objects in a file contain references to external resources.""",
    )
    object_keys: NDArray[Shape["* num_rows"], Any] = Field(
        ..., description="""A table for identifying which objects use which keys."""
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ExternalResources.model_rebuild()
