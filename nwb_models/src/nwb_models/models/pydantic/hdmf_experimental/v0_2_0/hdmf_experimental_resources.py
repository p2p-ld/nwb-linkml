from __future__ import annotations

import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union

import numpy as np
from numpydantic import NDArray, Shape
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator, model_validator

from ...hdmf_common.v1_5_1.hdmf_common_base import Container, Data


metamodel_version = "None"
version = "0.2.0"


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

    def __getitem__(self, val: Union[int, slice, str]) -> Any:
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
                    raise e1

    @field_validator("*", mode="wrap")
    @classmethod
    def cast_with_value(cls, v: Any, handler, info) -> Any:
        """Try to rescue instantiation by casting into the model's value field"""
        try:
            return handler(v)
        except Exception as e1:
            try:
                return handler({"value": v})
            except Exception:
                raise e1

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
                    if v.__pydantic_extra__:
                        v = annotation(**{**v.__dict__, **v.__pydantic_extra__})
                    else:
                        v = annotation(**v.__dict__)
            except TypeError:
                # fine, annotation is a non-class type like a TypeVar
                pass
        return v

    @model_validator(mode="before")
    @classmethod
    def gather_extra_to_value(cls, v: Any) -> Any:
        """
        For classes that don't allow extra fields and have a value slot,
        pack those extra kwargs into ``value``
        """
        if (
            cls.model_config["extra"] == "forbid"
            and "value" in cls.model_fields
            and isinstance(v, dict)
        ):
            extras = {key: val for key, val in v.items() if key not in cls.model_fields}
            if extras:
                for k in extras:
                    del v[k]
                if "value" in v:
                    v["value"].update(extras)
                else:
                    v["value"] = extras
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
        "imports": ["../../hdmf_common/v1_5_1/namespace", "hdmf-experimental.nwb.language"],
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
    key: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The user term that maps to one or more resources in the 'resources' table.""",
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
    keys_idx: NDArray[Shape["*"], int] = Field(
        ...,
        description="""The index to the key in the 'keys' table.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    resources_idx: NDArray[Shape["*"], int] = Field(
        ...,
        description="""The index into the 'resources' table""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    entity_id: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The unique identifier entity.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    entity_uri: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The URI for the entity this reference applies to. This can be an empty string.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
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
    resource: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The name of the resource.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    resource_uri: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The URI for the resource. This can be an empty string.""",
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
    object_id: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The UUID for the object.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    relative_path: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The relative path from the container with the object_id to the dataset or attribute with the value(s) that is associated with an external resource. This can be an empty string if the container is a dataset which contains the value(s) that is associated with an external resource.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    field: NDArray[Shape["*"], str] = Field(
        ...,
        description="""The field of the compound data type using an external resource. This is used only if the dataset or attribute is a compound data type; otherwise this should be an empty string.""",
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
        description="""The index to the 'objects' table for the object that holds the key.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )
    keys_idx: NDArray[Shape["*"], int] = Field(
        ...,
        description="""The index to the 'keys' table for the key.""",
        json_schema_extra={"linkml_meta": {"array": {"exact_number_dimensions": 1}}},
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ExternalResources.model_rebuild()
ExternalResourcesKeys.model_rebuild()
ExternalResourcesEntities.model_rebuild()
ExternalResourcesResources.model_rebuild()
ExternalResourcesObjects.model_rebuild()
ExternalResourcesObjectKeys.model_rebuild()
