from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union, ClassVar
from pydantic import BaseModel as BaseModel, Field
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


from ...hdmf_common.v1_5_0.hdmf_common_base import Container


metamodel_version = "None"
version = "0.1.0"


class ConfiguredBaseModel(
    BaseModel,
    validate_assignment=True,
    validate_default=True,
    extra="forbid",
    arbitrary_types_allowed=True,
    use_enum_values=True,
):
    hdf5_path: Optional[str] = Field(
        None, description="The absolute path that this object is stored in an NWB file"
    )


class LinkML_Meta(BaseModel):
    """Extra LinkML Metadata stored as a class attribute"""

    tree_root: bool = False


class ExternalResources(Container):
    """
    A set of four tables for tracking external resource references in a file. NOTE: this data type is in beta testing and is subject to change in a later version.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    keys: List[Any] = Field(
        default_factory=list,
        description="""A table for storing user terms that are used to refer to external resources.""",
    )
    entities: List[Any] = Field(
        default_factory=list,
        description="""A table for mapping user terms (i.e., keys) to resource entities.""",
    )
    resources: List[Any] = Field(
        default_factory=list,
        description="""A table for mapping user terms (i.e., keys) to resource entities.""",
    )
    objects: List[Any] = Field(
        default_factory=list,
        description="""A table for identifying which objects in a file contain references to external resources.""",
    )
    object_keys: List[Any] = Field(
        default_factory=list,
        description="""A table for identifying which objects use which keys.""",
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ExternalResources.model_rebuild()
