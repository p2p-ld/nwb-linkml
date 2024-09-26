from __future__ import annotations

import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union

import numpy as np
from numpydantic import NDArray, Shape
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

from ...hdmf_common.v1_7_0.hdmf_common_base import Container, Data


metamodel_version = "None"
version = "0.4.0"


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

    @field_validator("*", mode="wrap")
    @classmethod
    def coerce_value(cls, v: Any, handler, info) -> Any:
        """Try to rescue instantiation by using the value field"""
        try:
            return handler(v)
        except Exception as e1:
            try:
                return handler(v.value)
            except AttributeError:
                try:
                    return handler(v["value"])
                except (IndexError, KeyError, TypeError):
                    raise ValueError(
                        f"coerce_value: Could not use the value field of {type(v)} "
                        f"to construct {cls.__name__}.{info.field_name}, "
                        f"expected type: {cls.model_fields[info.field_name].annotation}\n"
                        f"inner error: {str(e1)}"
                    ) from e1

    @field_validator("*", mode="wrap")
    @classmethod
    def cast_with_value(cls, v: Any, handler, info) -> Any:
        """Try to rescue instantiation by casting into the model's value fiel"""
        try:
            return handler(v)
        except Exception as e1:
            try:
                return handler({"value": v})
            except Exception as e2:
                raise ValueError(
                    f"cast_with_value: Could not cast {type(v)} as value field for "
                    f"{cls.__name__}.{info.field_name},"
                    f" expected_type: {cls.model_fields[info.field_name].annotation}\n"
                    f"inner error: {str(e1)}"
                ) from e1

    @field_validator("*", mode="before")
    @classmethod
    def coerce_subclass(cls, v: Any, info) -> Any:
        """Recast parent classes into child classes"""
        if isinstance(v, BaseModel):
            annotation = cls.model_fields[info.field_name].annotation
            while hasattr(annotation, "__args__"):
                annotation = annotation.__args__[0]
            try:
                if issubclass(annotation, type(v)) and annotation is not type(v):
                    v = annotation(**{**v.__dict__, **v.__pydantic_extra__})
            except TypeError:
                # fine, annotation is a non-class type like a TypeVar
                pass
        return v


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
        "imports": ["../../hdmf_common/v1_7_0/namespace", "hdmf-experimental.nwb.language"],
        "name": "hdmf-experimental.resources",
    }
)


class ExternalResources(Container):
    """
    A set of five tables for tracking external resource references in a file. NOTE: this data type is experimental and is subject to change in a later version.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "hdmf-experimental.resources", "tree_root": True}
    )

    name: str = Field(...)
    keys: ExternalResourcesKeys = Field(
        ...,
        description="""A table for storing user terms that are used to refer to external resources.""",
    )
    files: ExternalResourcesFiles = Field(
        ..., description="""A table for storing object ids of files used in external resources."""
    )
    entities: ExternalResourcesEntities = Field(
        ..., description="""A table for mapping user terms (i.e., keys) to resource entities."""
    )
    objects: ExternalResourcesObjects = Field(
        ...,
        description="""A table for identifying which objects in a file contain references to external resources.""",
    )
    object_keys: ExternalResourcesObjectKeys = Field(
        ..., description="""A table for identifying which objects use which keys."""
    )
    entity_keys: ExternalResourcesEntityKeys = Field(
        ..., description="""A table for identifying which keys use which entity."""
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
    key: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The user term that maps to one or more resources in the `resources` table, e.g., \"human\".""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )


class ExternalResourcesFiles(Data):
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


class ExternalResourcesEntityKeys(Data):
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
ExternalResources.model_rebuild()
ExternalResourcesKeys.model_rebuild()
ExternalResourcesFiles.model_rebuild()
ExternalResourcesEntities.model_rebuild()
ExternalResourcesObjects.model_rebuild()
ExternalResourcesObjectKeys.model_rebuild()
ExternalResourcesEntityKeys.model_rebuild()
