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
if TYPE_CHECKING:
    import numpy as np


metamodel_version = "None"
version = "1.8.0"


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


class LinkML_Meta(BaseModel):
    """Extra LinkML Metadata stored as a class attribute"""

    tree_root: bool = False


class Data(ConfiguredBaseModel):
    """
    An abstract data type for a dataset.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)


class Container(ConfiguredBaseModel):
    """
    An abstract data type for a group storing collections of data and metadata. Base type for all data and metadata containers.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)


class SimpleMultiContainer(Container):
    """
    A simple Container for holding onto multiple containers.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    children: Optional[List[Container] | Container] = Field(default_factory=dict)
    name: str = Field(...)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Data.model_rebuild()
Container.model_rebuild()
SimpleMultiContainer.model_rebuild()