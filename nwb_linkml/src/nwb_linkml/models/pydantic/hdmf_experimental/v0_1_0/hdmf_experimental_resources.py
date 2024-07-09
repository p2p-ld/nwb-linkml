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


from ...hdmf_common.v1_5_0.hdmf_common_base import Data, Container


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


class ExternalResources(Container):
    """
    A set of four tables for tracking external resource references in a file. NOTE: this data type is in beta testing and is subject to change in a later version.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    keys: str = Field(
        ...,
        description="""A table for storing user terms that are used to refer to external resources.""",
    )
    entities: str = Field(
        ...,
        description="""A table for mapping user terms (i.e., keys) to resource entities.""",
    )
    resources: str = Field(
        ...,
        description="""A table for mapping user terms (i.e., keys) to resource entities.""",
    )
    objects: str = Field(
        ...,
        description="""A table for identifying which objects in a file contain references to external resources.""",
    )
    object_keys: str = Field(
        ..., description="""A table for identifying which objects use which keys."""
    )


class ExternalResourcesKeys(Data):
    """
    A table for storing user terms that are used to refer to external resources.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["keys"] = Field("keys")
    key: str = Field(
        ...,
        description="""The user term that maps to one or more resources in the 'resources' table.""",
    )


class ExternalResourcesEntities(Data):
    """
    A table for mapping user terms (i.e., keys) to resource entities.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["entities"] = Field("entities")
    keys_idx: int = Field(
        ..., description="""The index to the key in the 'keys' table."""
    )
    resources_idx: int = Field(
        ..., description="""The index into the 'resources' table"""
    )
    entity_id: str = Field(..., description="""The unique identifier entity.""")
    entity_uri: str = Field(
        ...,
        description="""The URI for the entity this reference applies to. This can be an empty string.""",
    )


class ExternalResourcesResources(Data):
    """
    A table for mapping user terms (i.e., keys) to resource entities.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["resources"] = Field("resources")
    resource: str = Field(..., description="""The name of the resource.""")
    resource_uri: str = Field(
        ..., description="""The URI for the resource. This can be an empty string."""
    )


class ExternalResourcesObjects(Data):
    """
    A table for identifying which objects in a file contain references to external resources.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["objects"] = Field("objects")
    object_id: str = Field(..., description="""The UUID for the object.""")
    field: str = Field(
        ...,
        description="""The field of the object. This can be an empty string if the object is a dataset and the field is the dataset values.""",
    )


class ExternalResourcesObjectKeys(Data):
    """
    A table for identifying which objects use which keys.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["object_keys"] = Field("object_keys")
    objects_idx: int = Field(
        ...,
        description="""The index to the 'objects' table for the object that holds the key.""",
    )
    keys_idx: int = Field(
        ..., description="""The index to the 'keys' table for the key."""
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ExternalResources.model_rebuild()
ExternalResourcesKeys.model_rebuild()
ExternalResourcesEntities.model_rebuild()
ExternalResourcesResources.model_rebuild()
ExternalResourcesObjects.model_rebuild()
ExternalResourcesObjectKeys.model_rebuild()
