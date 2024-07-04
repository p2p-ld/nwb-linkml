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


from ...hdmf_common.v1_8_0.hdmf_common_base import Container, Data


metamodel_version = "None"
version = "0.5.0"


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


class HERD(Container):
    """
    HDMF External Resources Data Structure. A set of six tables for tracking external resource references in a file or across multiple files.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    keys: str = Field(
        ...,
        description="""A table for storing user terms that are used to refer to external resources.""",
    )
    files: str = Field(
        ...,
        description="""A table for storing object ids of files used in external resources.""",
    )
    entities: str = Field(
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
    entity_keys: str = Field(
        ..., description="""A table for identifying which keys use which entity."""
    )


class HERDKeys(Data):
    """
    A table for storing user terms that are used to refer to external resources.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["keys"] = Field("keys")
    key: str = Field(
        ...,
        description="""The user term that maps to one or more resources in the `resources` table, e.g., \"human\".""",
    )


class HERDFiles(Data):
    """
    A table for storing object ids of files used in external resources.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["files"] = Field("files")
    file_object_id: str = Field(
        ...,
        description="""The object id (UUID) of a file that contains objects that refers to external resources.""",
    )


class HERDEntities(Data):
    """
    A table for mapping user terms (i.e., keys) to resource entities.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["entities"] = Field("entities")
    entity_id: str = Field(
        ...,
        description="""The compact uniform resource identifier (CURIE) of the entity, in the form [prefix]:[unique local identifier], e.g., 'NCBI_TAXON:9606'.""",
    )
    entity_uri: str = Field(
        ...,
        description="""The URI for the entity this reference applies to. This can be an empty string. e.g., https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=info&id=9606""",
    )


class HERDObjects(Data):
    """
    A table for identifying which objects in a file contain references to external resources.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["objects"] = Field("objects")
    files_idx: int = Field(
        ...,
        description="""The row index to the file in the `files` table containing the object.""",
    )
    object_id: str = Field(..., description="""The object id (UUID) of the object.""")
    object_type: str = Field(..., description="""The data type of the object.""")
    relative_path: str = Field(
        ...,
        description="""The relative path from the data object with the `object_id` to the dataset or attribute with the value(s) that is associated with an external resource. This can be an empty string if the object is a dataset that contains the value(s) that is associated with an external resource.""",
    )
    field: str = Field(
        ...,
        description="""The field within the compound data type using an external resource. This is used only if the dataset or attribute is a compound data type; otherwise this should be an empty string.""",
    )


class HERDObjectKeys(Data):
    """
    A table for identifying which objects use which keys.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["object_keys"] = Field("object_keys")
    objects_idx: int = Field(
        ...,
        description="""The row index to the object in the `objects` table that holds the key""",
    )
    keys_idx: int = Field(
        ..., description="""The row index to the key in the `keys` table."""
    )


class HERDEntityKeys(Data):
    """
    A table for identifying which keys use which entity.
    """

    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["entity_keys"] = Field("entity_keys")
    entities_idx: int = Field(
        ..., description="""The row index to the entity in the `entities` table."""
    )
    keys_idx: int = Field(
        ..., description="""The row index to the key in the `keys` table."""
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
HERD.model_rebuild()
HERDKeys.model_rebuild()
HERDFiles.model_rebuild()
HERDEntities.model_rebuild()
HERDObjects.model_rebuild()
HERDObjectKeys.model_rebuild()
HERDEntityKeys.model_rebuild()
