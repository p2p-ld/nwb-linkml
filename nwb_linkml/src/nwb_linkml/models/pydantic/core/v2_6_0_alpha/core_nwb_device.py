from __future__ import annotations

import sys
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Optional,
)

from pydantic import BaseModel as BaseModel
from pydantic import ConfigDict, Field

if sys.version_info >= (3, 8):
    pass
else:
    pass
if TYPE_CHECKING:
    import numpy as np


from .core_nwb_base import NWBContainer

metamodel_version = "None"
version = "2.6.0-alpha"


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


class Device(NWBContainer):
    """
    Metadata about a data acquisition device, e.g., recording system, electrode, microscope.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    description: Optional[str] = Field(
        None,
        description="""Description of the device (e.g., model, firmware version, processing software version, etc.) as free-form text.""",
    )
    manufacturer: Optional[str] = Field(
        None, description="""The name of the manufacturer of the device."""
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Device.model_rebuild()
