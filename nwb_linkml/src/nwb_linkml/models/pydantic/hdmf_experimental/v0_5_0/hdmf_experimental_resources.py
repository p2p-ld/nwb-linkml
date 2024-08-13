from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
import numpy as np
from ...hdmf_common.v1_8_0.hdmf_common_base import Container, Data
from numpydantic import NDArray, Shape

metamodel_version = "None"
version = "0.5.0"


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

    def __getitem__(self, val: Union[int, slice]) -> Any:
        """Try and get a value from value or "data" if we have it"""
        if hasattr(self, "value") and self.value is not None:
            return self.value[val]
        elif hasattr(self, "data") and self.data is not None:
            return self.data[val]
        else:
            raise KeyError("No value or data field to index from")


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


NUMPYDANTIC_VERSION = "1.2.1"
linkml_meta = LinkMLMeta(
    {
        "annotations": {
            "is_namespace": {"tag": "is_namespace", "value": False},
            "namespace": {"tag": "namespace", "value": "hdmf-experimental"},
        },
        "default_prefix": "hdmf-experimental.resources/",
        "id": "hdmf-experimental.resources",
        "imports": ["../../hdmf_common/v1_8_0/namespace", "hdmf-experimental.nwb.language"],
        "name": "hdmf-experimental.resources",
    }
)


class HERD(Container):
    """
    HDMF External Resources Data Structure. A set of six tables for tracking external resource references in a file or across multiple files.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "hdmf-experimental.resources", "tree_root": True}
    )

    name: str = Field(...)
    keys: HERDKeys = Field(
        ...,
        description="""A table for storing user terms that are used to refer to external resources.""",
    )
    files: HERDFiles = Field(
        ..., description="""A table for storing object ids of files used in external resources."""
    )
    entities: HERDEntities = Field(
        ..., description="""A table for mapping user terms (i.e., keys) to resource entities."""
    )
    objects: HERDObjects = Field(
        ...,
        description="""A table for identifying which objects in a file contain references to external resources.""",
    )
    object_keys: HERDObjectKeys = Field(
        ..., description="""A table for identifying which objects use which keys."""
    )
    entity_keys: HERDEntityKeys = Field(
        ..., description="""A table for identifying which keys use which entity."""
    )


class HERDKeys(Data):
    """
    A table for storing user terms that are used to refer to external resources.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-experimental.resources"})

    name: Literal["keys"] = Field(
        "keys",
        json_schema_extra={"linkml_meta": {"equals_string": "keys", "ifabsent": "string(keys)"}},
    )
    key: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The user term that maps to one or more resources in the `resources` table, e.g., \"human\".""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )


class HERDFiles(Data):
    """
    A table for storing object ids of files used in external resources.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-experimental.resources"})

    name: Literal["files"] = Field(
        "files",
        json_schema_extra={"linkml_meta": {"equals_string": "files", "ifabsent": "string(files)"}},
    )
    file_object_id: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The object id (UUID) of a file that contains objects that refers to external resources.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )


class HERDEntities(Data):
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
    entity_id: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The compact uniform resource identifier (CURIE) of the entity, in the form [prefix]:[unique local identifier], e.g., 'NCBI_TAXON:9606'.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    entity_uri: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The URI for the entity this reference applies to. This can be an empty string. e.g., https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=info&id=9606""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )


class HERDObjects(Data):
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
    files_idx: NDArray[Shape["*"], int] = Field(
        ...,
        description="""The row index to the file in the `files` table containing the object.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    object_id: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The object id (UUID) of the object.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    object_type: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The data type of the object.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    relative_path: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The relative path from the data object with the `object_id` to the dataset or attribute with the value(s) that is associated with an external resource. This can be an empty string if the object is a dataset that contains the value(s) that is associated with an external resource.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    field: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The field within the compound data type using an external resource. This is used only if the dataset or attribute is a compound data type; otherwise this should be an empty string.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )


class HERDObjectKeys(Data):
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
    objects_idx: NDArray[Shape["*"], int] = Field(
        ...,
        description="""The row index to the object in the `objects` table that holds the key""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    keys_idx: NDArray[Shape["*"], int] = Field(
        ...,
        description="""The row index to the key in the `keys` table.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )


class HERDEntityKeys(Data):
    """
    A table for identifying which keys use which entity.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "hdmf-experimental.resources"})

    name: Literal["entity_keys"] = Field(
        "entity_keys",
        json_schema_extra={
            "linkml_meta": {"equals_string": "entity_keys", "ifabsent": "string(entity_keys)"}
        },
    )
    entities_idx: NDArray[Shape["*"], int] = Field(
        ...,
        description="""The row index to the entity in the `entities` table.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    keys_idx: NDArray[Shape["*"], int] = Field(
        ...,
        description="""The row index to the key in the `keys` table.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
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
