from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
import numpy as np
from ...hdmf_common.v1_5_0.hdmf_common_sparse import CSRMatrix, CSRMatrixData
from ...hdmf_common.v1_5_0.hdmf_common_base import Data, Container, SimpleMultiContainer
from ...hdmf_common.v1_5_0.hdmf_common_table import (
    VectorData,
    VectorIndex,
    ElementIdentifiers,
    DynamicTableRegion,
    DynamicTable,
    AlignedDynamicTable,
)

metamodel_version = "None"
version = "0.1.0"


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


linkml_meta = LinkMLMeta(
    {
        "annotations": {
            "is_namespace": {"tag": "is_namespace", "value": False},
            "namespace": {"tag": "namespace", "value": "hdmf-experimental"},
        },
        "default_prefix": "hdmf-experimental.resources/",
        "id": "hdmf-experimental.resources",
        "imports": ["../../hdmf_common/v1_5_0/namespace", "hdmf-experimental.nwb.language"],
        "name": "hdmf-experimental.resources",
    }
)


class ExternalResources(Container):
    """
    A set of four tables for tracking external resource references in a file. NOTE: this data type is in beta testing and is subject to change in a later version.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "hdmf-experimental.resources", "tree_root": True}
    )

    name: str = Field(...)
    keys: ExternalResourcesKeys = Field(
        ...,
        description="""A table for storing user terms that are used to refer to external resources.""",
    )
    entities: ExternalResourcesEntities = Field(
        ..., description="""A table for mapping user terms (i.e., keys) to resource entities."""
    )
    resources: ExternalResourcesResources = Field(
        ..., description="""A table for mapping user terms (i.e., keys) to resource entities."""
    )
    objects: ExternalResourcesObjects = Field(
        ...,
        description="""A table for identifying which objects in a file contain references to external resources.""",
    )
    object_keys: ExternalResourcesObjectKeys = Field(
        ..., description="""A table for identifying which objects use which keys."""
    )


class ExternalResourcesKeys(Data):
    """
    A table for storing user terms that are used to refer to external resources.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-experimental.resources"})

    name: Literal["keys"] = Field(
        "keys",
        json_schema_extra={"linkml_meta": {"equals_string": "keys", "ifabsent": "string(keys)"}},
    )
    key: str = Field(
        ...,
        description="""The user term that maps to one or more resources in the 'resources' table.""",
    )


class ExternalResourcesEntities(Data):
    """
    A table for mapping user terms (i.e., keys) to resource entities.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-experimental.resources"})

    name: Literal["entities"] = Field(
        "entities",
        json_schema_extra={
            "linkml_meta": {"equals_string": "entities", "ifabsent": "string(entities)"}
        },
    )
    keys_idx: np.uint64 = Field(..., description="""The index to the key in the 'keys' table.""")
    resources_idx: np.uint64 = Field(..., description="""The index into the 'resources' table""")
    entity_id: str = Field(..., description="""The unique identifier entity.""")
    entity_uri: str = Field(
        ...,
        description="""The URI for the entity this reference applies to. This can be an empty string.""",
    )


class ExternalResourcesResources(Data):
    """
    A table for mapping user terms (i.e., keys) to resource entities.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-experimental.resources"})

    name: Literal["resources"] = Field(
        "resources",
        json_schema_extra={
            "linkml_meta": {"equals_string": "resources", "ifabsent": "string(resources)"}
        },
    )
    resource: str = Field(..., description="""The name of the resource.""")
    resource_uri: str = Field(
        ..., description="""The URI for the resource. This can be an empty string."""
    )


class ExternalResourcesObjects(Data):
    """
    A table for identifying which objects in a file contain references to external resources.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-experimental.resources"})

    name: Literal["objects"] = Field(
        "objects",
        json_schema_extra={
            "linkml_meta": {"equals_string": "objects", "ifabsent": "string(objects)"}
        },
    )
    object_id: str = Field(..., description="""The UUID for the object.""")
    field: str = Field(
        ...,
        description="""The field of the object. This can be an empty string if the object is a dataset and the field is the dataset values.""",
    )


class ExternalResourcesObjectKeys(Data):
    """
    A table for identifying which objects use which keys.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-experimental.resources"})

    name: Literal["object_keys"] = Field(
        "object_keys",
        json_schema_extra={
            "linkml_meta": {"equals_string": "object_keys", "ifabsent": "string(object_keys)"}
        },
    )
    objects_idx: np.uint64 = Field(
        ..., description="""The index to the 'objects' table for the object that holds the key."""
    )
    keys_idx: np.uint64 = Field(..., description="""The index to the 'keys' table for the key.""")


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ExternalResources.model_rebuild()
ExternalResourcesKeys.model_rebuild()
ExternalResourcesEntities.model_rebuild()
ExternalResourcesResources.model_rebuild()
ExternalResourcesObjects.model_rebuild()
ExternalResourcesObjectKeys.model_rebuild()
