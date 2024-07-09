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


metamodel_version = "None"
version = "1.5.0"


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


class Data(ConfiguredBaseModel):
    """
    An abstract data type for a dataset.
    """

    name: str = Field(...)


class Container(ConfiguredBaseModel):
    """
    An abstract data type for a group storing collections of data and metadata. Base type for all data and metadata containers.
    """

    name: str = Field(...)


class SimpleMultiContainer(Container):
    """
    A simple Container for holding onto multiple containers.
    """

    children: Optional[List[Container] | Container] = Field(default_factory=dict)
    name: str = Field(...)
