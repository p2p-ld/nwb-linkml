from __future__ import annotations

import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator, model_validator


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=False,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )
    pass


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


class ParentizeMixin(BaseModel):

    @model_validator(mode="after")
    def parentize(self):
        """Set the parent attribute for all our fields they have one"""
        for field_name in self.model_fields:
            if field_name == "parent":
                continue
            field = getattr(self, field_name)
            if not isinstance(field, list):
                field = [field]
            for item in field:
                if hasattr(item, "parent"):
                    item.parent = self

        return self


linkml_meta = LinkMLMeta(
    {
        "default_prefix": "nwb_schema_language",
        "default_range": "string",
        "description": "Translation of the nwb-schema-language to LinkML",
        "id": "https://w3id.org/p2p_ld/nwb-schema-language",
        "imports": ["linkml:types"],
        "license": "GNU GPL v3.0",
        "name": "nwb-schema-language",
        "prefixes": {
            "linkml": {"prefix_prefix": "linkml", "prefix_reference": "https://w3id.org/linkml/"},
            "nwb_schema_language": {
                "prefix_prefix": "nwb_schema_language",
                "prefix_reference": "https://w3id.org/p2p_ld/nwb-schema-language/",
            },
            "schema": {"prefix_prefix": "schema", "prefix_reference": "http://schema.org/"},
        },
        "see_also": ["https://p2p_ld.github.io/nwb-schema-language"],
        "settings": {
            "email": {"setting_key": "email", "setting_value": "\\S+@\\S+{\\.\\w}+"},
            "protected_string": {
                "setting_key": "protected_string",
                "setting_value": "^[A-Za-z_][A-Za-z0-9_]*$",
            },
        },
        "source_file": "/Users/jonny/git/p2p-ld/nwb-linkml/nwb_schema_language/src/nwb_schema_language/schema/nwb_schema_language.yaml",
        "title": "nwb-schema-language",
    }
)


class ReftypeOptions(str, Enum):
    # Reference to another group or dataset of the given target_type
    ref = "ref"
    # Reference to another group or dataset of the given target_type
    reference = "reference"
    # Reference to another group or dataset of the given target_type
    object = "object"
    # Reference to a region (i.e. subset) of another dataset of the given target_type
    region = "region"


class QuantityEnum(str, Enum):
    # Zero or more instances, equivalent to zero_or_many
    ASTERISK = "*"
    # Zero or one instances, equivalent to zero_or_one
    QUESTION_MARK = "?"
    # One or more instances, equivalent to one_or_many
    PLUS_SIGN = "+"
    # Zero or more instances, equivalent to *
    zero_or_many = "zero_or_many"
    # One or more instances, equivalent to +
    one_or_many = "one_or_many"
    # Zero or one instances, equivalent to ?
    zero_or_one = "zero_or_one"


class FlatDtype(str, Enum):
    # single precision floating point (32 bit)
    float = "float"
    # single precision floating point (32 bit)
    float32 = "float32"
    # double precision floating point (64 bit)
    double = "double"
    # double precision floating point (64 bit)
    float64 = "float64"
    # signed 64 bit integer
    long = "long"
    # signed 64 bit integer
    int64 = "int64"
    # signed 32 bit integer
    int = "int"
    # signed 32 bit integer
    int32 = "int32"
    # signed 16 bit integer
    int16 = "int16"
    # signed 16 bit integer
    short = "short"
    # signed 8 bit integer
    int8 = "int8"
    # unsigned 32 bit integer
    uint = "uint"
    # unsigned 32 bit integer
    uint32 = "uint32"
    # unsigned 16 bit integer
    uint16 = "uint16"
    # unsigned 8 bit integer
    uint8 = "uint8"
    # unsigned 64 bit integer
    uint64 = "uint64"
    # any numeric type (i.e., any int, uint, float)
    numeric = "numeric"
    # 8-bit Unicode
    text = "text"
    # 8-bit Unicode
    utf = "utf"
    # 8-bit Unicode
    utf8 = "utf8"
    # 8-bit Unicode
    utf_8 = "utf-8"
    # ASCII text
    ascii = "ascii"
    # 8 bit integer with valid values 0 or 1
    bool = "bool"
    # ISO 8601 datetime string
    isodatetime = "isodatetime"


class Namespace(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/p2p_ld/nwb-schema-language",
            "slot_usage": {"name": {"name": "name", "required": True}},
        }
    )

    doc: str = Field(
        ...,
        description="""Description of corresponding object.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "doc",
                "domain_of": [
                    "Namespace",
                    "Schema",
                    "Group",
                    "Attribute",
                    "Link",
                    "Dataset",
                    "CompoundDtype",
                ],
            }
        },
    )
    name: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "Namespace",
                    "Group",
                    "Attribute",
                    "Link",
                    "Dataset",
                    "CompoundDtype",
                ],
                "structured_pattern": {"interpolated": True, "syntax": "{protected_string}"},
            }
        },
    )
    full_name: Optional[str] = Field(
        None,
        description="""Optional string with extended full name for the namespace.""",
        json_schema_extra={"linkml_meta": {"alias": "full_name", "domain_of": ["Namespace"]}},
    )
    version: str = Field(
        ..., json_schema_extra={"linkml_meta": {"alias": "version", "domain_of": ["Namespace"]}}
    )
    date: Optional[datetime] = Field(
        None,
        description="""Date that a namespace was last modified or released""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "date",
                "domain_of": ["Namespace"],
                "examples": [{"value": "2017-04-25 17:14:13"}],
                "slot_uri": "schema:dateModified",
            }
        },
    )
    author: List[str] | str = Field(
        ...,
        description="""List of strings with the names of the authors of the namespace.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "author",
                "domain_of": ["Namespace"],
                "slot_uri": "schema:author",
            }
        },
    )
    contact: List[str] | str = Field(
        ...,
        description="""List of strings with the contact information for the authors. Ordering of the contacts should match the ordering of the authors.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "contact",
                "domain_of": ["Namespace"],
                "slot_uri": "schema:email",
                "structured_pattern": {"interpolated": True, "syntax": "{email}"},
            }
        },
    )
    schema_: Optional[List[Schema]] = Field(
        None,
        alias="schema",
        description="""List of the schema to be included in this namespace.""",
        json_schema_extra={"linkml_meta": {"alias": "schema_", "domain_of": ["Namespace"]}},
    )


class Namespaces(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://w3id.org/p2p_ld/nwb-schema-language"}
    )

    namespaces: Optional[List[Namespace]] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "namespaces", "domain_of": ["Namespaces"]}},
    )


class Schema(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/p2p_ld/nwb-schema-language",
            "rules": [
                {
                    "description": "If namespace is absent, source is required",
                    "postconditions": {
                        "slot_conditions": {"source": {"name": "source", "required": True}}
                    },
                    "preconditions": {
                        "slot_conditions": {
                            "namespace": {"name": "namespace", "value_presence": "ABSENT"}
                        }
                    },
                },
                {
                    "description": "If source is absent, namespace is required.",
                    "postconditions": {
                        "slot_conditions": {"namespace": {"name": "namespace", "required": True}}
                    },
                    "preconditions": {
                        "slot_conditions": {
                            "source": {"name": "source", "value_presence": "ABSENT"}
                        }
                    },
                },
                {
                    "description": "If namespace is present, source is cannot be",
                    "postconditions": {
                        "slot_conditions": {
                            "source": {"name": "source", "value_presence": "ABSENT"}
                        }
                    },
                    "preconditions": {
                        "slot_conditions": {
                            "namespace": {"name": "namespace", "value_presence": "PRESENT"}
                        }
                    },
                },
                {
                    "description": "If source is present, namespace cannot be.",
                    "postconditions": {
                        "slot_conditions": {
                            "namespace": {"name": "namespace", "value_presence": "ABSENT"}
                        }
                    },
                    "preconditions": {
                        "slot_conditions": {
                            "source": {"name": "source", "value_presence": "PRESENT"}
                        }
                    },
                },
            ],
        }
    )

    source: Optional[str] = Field(
        None,
        description="""describes the name of the YAML (or JSON) file with the schema specification. The schema files should be located in the same folder as the namespace file.""",
        json_schema_extra={"linkml_meta": {"alias": "source", "domain_of": ["Schema"]}},
    )
    namespace: Optional[str] = Field(
        None,
        description="""describes a named reference to another namespace. In contrast to source, this is a reference by name to a known namespace (i.e., the namespace is resolved during the build and must point to an already existing namespace). This mechanism is used to allow, e.g., extension of a core namespace (here the NWB core namespace) without requiring hard paths to the files describing the core namespace. Either source or namespace must be specified, but not both.""",
        json_schema_extra={"linkml_meta": {"alias": "namespace", "domain_of": ["Schema"]}},
    )
    title: Optional[str] = Field(
        None,
        description="""a descriptive title for a file for documentation purposes.""",
        json_schema_extra={"linkml_meta": {"alias": "title", "domain_of": ["Schema"]}},
    )
    neurodata_types: Optional[List[Union[Dataset, Group]]] = Field(
        None,
        description="""an optional list of strings indicating which data types should be included from the given specification source or namespace. The default is null indicating that all data types should be included.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "neurodata_types",
                "any_of": [{"range": "Dataset"}, {"range": "Group"}],
                "domain_of": ["Schema"],
            }
        },
    )
    doc: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "doc",
                "domain_of": [
                    "Namespace",
                    "Schema",
                    "Group",
                    "Attribute",
                    "Link",
                    "Dataset",
                    "CompoundDtype",
                ],
            }
        },
    )


class Group(ConfiguredBaseModel, ParentizeMixin):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://w3id.org/p2p_ld/nwb-schema-language"}
    )

    neurodata_type_def: Optional[str] = Field(
        None,
        description="""Used alongside neurodata_type_inc to indicate inheritance, naming, and mixins""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "neurodata_type_def",
                "domain_of": ["Group", "Dataset"],
                "structured_pattern": {"interpolated": True, "syntax": "{protected_string}"},
            }
        },
    )
    neurodata_type_inc: Optional[str] = Field(
        None,
        description="""Used alongside neurodata_type_def to indicate inheritance, naming, and mixins""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "neurodata_type_inc",
                "domain_of": ["Group", "Dataset"],
                "structured_pattern": {"interpolated": True, "syntax": "{protected_string}"},
            }
        },
    )
    name: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "Namespace",
                    "Group",
                    "Attribute",
                    "Link",
                    "Dataset",
                    "CompoundDtype",
                ],
                "structured_pattern": {"interpolated": True, "syntax": "{protected_string}"},
            }
        },
    )
    default_name: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "default_name",
                "domain_of": ["Group", "Dataset"],
                "structured_pattern": {"interpolated": True, "syntax": "{protected_string}"},
            }
        },
    )
    doc: str = Field(
        ...,
        description="""Description of corresponding object.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "doc",
                "domain_of": [
                    "Namespace",
                    "Schema",
                    "Group",
                    "Attribute",
                    "Link",
                    "Dataset",
                    "CompoundDtype",
                ],
            }
        },
    )
    quantity: Optional[Union[QuantityEnum, int]] = Field(
        "1",
        json_schema_extra={
            "linkml_meta": {
                "alias": "quantity",
                "any_of": [{"minimum_value": 1, "range": "integer"}, {"range": "QuantityEnum"}],
                "domain_of": ["Group", "Link", "Dataset"],
                "ifabsent": "int(1)",
                "todos": [
                    "logic to check that the corresponding class can only be "
                    "implemented quantity times."
                ],
            }
        },
    )
    linkable: Optional[bool] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "linkable", "domain_of": ["Group", "Dataset"]}},
    )
    attributes: Optional[List[Attribute]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"alias": "attributes", "domain_of": ["Group", "Dataset"]}
        },
    )
    datasets: Optional[List[Dataset]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"alias": "datasets", "domain_of": ["Group", "Datasets"]}
        },
    )
    groups: Optional[List[Group]] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "groups", "domain_of": ["Group", "Groups"]}},
    )
    links: Optional[List[Link]] = Field(
        None, json_schema_extra={"linkml_meta": {"alias": "links", "domain_of": ["Group"]}}
    )
    parent: Optional[Group] = Field(
        None,
        exclude=True,
        description="""The parent group that contains this dataset or group""",
        json_schema_extra={
            "linkml_meta": {"alias": "parent", "domain_of": ["Group", "Attribute", "Dataset"]}
        },
    )


class Groups(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://w3id.org/p2p_ld/nwb-schema-language"}
    )

    groups: Optional[List[Group]] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "groups", "domain_of": ["Group", "Groups"]}},
    )


class Link(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://w3id.org/p2p_ld/nwb-schema-language"}
    )

    name: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "Namespace",
                    "Group",
                    "Attribute",
                    "Link",
                    "Dataset",
                    "CompoundDtype",
                ],
                "structured_pattern": {"interpolated": True, "syntax": "{protected_string}"},
            }
        },
    )
    doc: str = Field(
        ...,
        description="""Description of corresponding object.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "doc",
                "domain_of": [
                    "Namespace",
                    "Schema",
                    "Group",
                    "Attribute",
                    "Link",
                    "Dataset",
                    "CompoundDtype",
                ],
            }
        },
    )
    target_type: str = Field(
        ...,
        description="""Describes the neurodata_type of the target that the reference points to""",
        json_schema_extra={
            "linkml_meta": {"alias": "target_type", "domain_of": ["Link", "ReferenceDtype"]}
        },
    )
    quantity: Optional[Union[QuantityEnum, int]] = Field(
        "1",
        json_schema_extra={
            "linkml_meta": {
                "alias": "quantity",
                "any_of": [{"minimum_value": 1, "range": "integer"}, {"range": "QuantityEnum"}],
                "domain_of": ["Group", "Link", "Dataset"],
                "ifabsent": "int(1)",
                "todos": [
                    "logic to check that the corresponding class can only be "
                    "implemented quantity times."
                ],
            }
        },
    )


class Datasets(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://w3id.org/p2p_ld/nwb-schema-language"}
    )

    datasets: Optional[List[Dataset]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"alias": "datasets", "domain_of": ["Group", "Datasets"]}
        },
    )


class ReferenceDtype(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://w3id.org/p2p_ld/nwb-schema-language"}
    )

    target_type: str = Field(
        ...,
        description="""Describes the neurodata_type of the target that the reference points to""",
        json_schema_extra={
            "linkml_meta": {"alias": "target_type", "domain_of": ["Link", "ReferenceDtype"]}
        },
    )
    reftype: Optional[ReftypeOptions] = Field(
        None,
        description="""describes the kind of reference""",
        json_schema_extra={"linkml_meta": {"alias": "reftype", "domain_of": ["ReferenceDtype"]}},
    )


class CompoundDtype(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/p2p_ld/nwb-schema-language",
            "slot_usage": {
                "dtype": {
                    "any_of": [{"range": "ReferenceDtype"}, {"range": "FlatDtype"}],
                    "multivalued": False,
                    "name": "dtype",
                    "required": True,
                },
                "name": {"name": "name", "required": True},
            },
        }
    )

    name: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "Namespace",
                    "Group",
                    "Attribute",
                    "Link",
                    "Dataset",
                    "CompoundDtype",
                ],
                "structured_pattern": {"interpolated": True, "syntax": "{protected_string}"},
            }
        },
    )
    doc: str = Field(
        ...,
        description="""Description of corresponding object.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "doc",
                "domain_of": [
                    "Namespace",
                    "Schema",
                    "Group",
                    "Attribute",
                    "Link",
                    "Dataset",
                    "CompoundDtype",
                ],
            }
        },
    )
    dtype: Union[FlatDtype, ReferenceDtype] = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "dtype",
                "any_of": [{"range": "ReferenceDtype"}, {"range": "FlatDtype"}],
                "domain_of": ["CompoundDtype", "DtypeMixin"],
            }
        },
    )


class DtypeMixin(ConfiguredBaseModel):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/p2p_ld/nwb-schema-language",
            "mixin": True,
            "rules": [
                {
                    "postconditions": {
                        "slot_conditions": {"dtype": {"multivalued": False, "name": "dtype"}}
                    },
                    "preconditions": {
                        "slot_conditions": {"dtype": {"name": "dtype", "range": "FlatDtype"}}
                    },
                }
            ],
        }
    )

    dtype: Optional[Union[List[CompoundDtype], FlatDtype, ReferenceDtype]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "dtype",
                "any_of": [
                    {"range": "FlatDtype"},
                    {"range": "CompoundDtype"},
                    {"range": "ReferenceDtype"},
                ],
                "domain_of": ["CompoundDtype", "DtypeMixin"],
            }
        },
    )


class Attribute(DtypeMixin):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {
            "from_schema": "https://w3id.org/p2p_ld/nwb-schema-language",
            "mixins": ["DtypeMixin"],
            "slot_usage": {
                "name": {"name": "name", "required": True},
                "parent": {"any_of": [{"range": "Group"}, {"range": "Dataset"}], "name": "parent"},
            },
        }
    )

    name: str = Field(
        ...,
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "Namespace",
                    "Group",
                    "Attribute",
                    "Link",
                    "Dataset",
                    "CompoundDtype",
                ],
                "structured_pattern": {"interpolated": True, "syntax": "{protected_string}"},
            }
        },
    )
    dims: Optional[List[Union[Any, str]]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "dims",
                "any_of": [{"range": "string"}, {"range": "AnyType"}],
                "domain_of": ["Attribute", "Dataset"],
                "todos": [
                    "Can't quite figure out how to allow an array of arrays - see "
                    "https://github.com/linkml/linkml/issues/895"
                ],
            }
        },
    )
    shape: Optional[List[Union[Any, int, str]]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "shape",
                "any_of": [
                    {"minimum_value": 1, "range": "integer"},
                    {"equals_string": "null", "range": "string"},
                    {"range": "AnyType"},
                ],
                "domain_of": ["Attribute", "Dataset"],
                "todos": [
                    "Can't quite figure out how to allow an array of arrays - see "
                    "https://github.com/linkml/linkml/issues/895"
                ],
            }
        },
    )
    value: Optional[Any] = Field(
        None,
        description="""Optional constant, fixed value for the attribute.""",
        json_schema_extra={
            "linkml_meta": {"alias": "value", "domain_of": ["Attribute", "Dataset"]}
        },
    )
    default_value: Optional[Any] = Field(
        None,
        description="""Optional default value for variable-valued attributes.""",
        json_schema_extra={
            "linkml_meta": {"alias": "default_value", "domain_of": ["Attribute", "Dataset"]}
        },
    )
    doc: str = Field(
        ...,
        description="""Description of corresponding object.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "doc",
                "domain_of": [
                    "Namespace",
                    "Schema",
                    "Group",
                    "Attribute",
                    "Link",
                    "Dataset",
                    "CompoundDtype",
                ],
            }
        },
    )
    required: Optional[bool] = Field(
        True,
        description="""Optional boolean key describing whether the attribute is required. Default value is True.""",
        json_schema_extra={
            "linkml_meta": {"alias": "required", "domain_of": ["Attribute"], "ifabsent": "true"}
        },
    )
    parent: Optional[Union[Dataset, Group]] = Field(
        None,
        exclude=True,
        description="""The parent group that contains this dataset or group""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "parent",
                "any_of": [{"range": "Group"}, {"range": "Dataset"}],
                "domain_of": ["Group", "Attribute", "Dataset"],
            }
        },
    )
    dtype: Optional[Union[List[CompoundDtype], FlatDtype, ReferenceDtype]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "dtype",
                "any_of": [
                    {"range": "FlatDtype"},
                    {"range": "CompoundDtype"},
                    {"range": "ReferenceDtype"},
                ],
                "domain_of": ["CompoundDtype", "DtypeMixin"],
            }
        },
    )


class Dataset(ConfiguredBaseModel, ParentizeMixin):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "https://w3id.org/p2p_ld/nwb-schema-language", "mixins": ["DtypeMixin"]}
    )

    neurodata_type_def: Optional[str] = Field(
        None,
        description="""Used alongside neurodata_type_inc to indicate inheritance, naming, and mixins""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "neurodata_type_def",
                "domain_of": ["Group", "Dataset"],
                "structured_pattern": {"interpolated": True, "syntax": "{protected_string}"},
            }
        },
    )
    neurodata_type_inc: Optional[str] = Field(
        None,
        description="""Used alongside neurodata_type_def to indicate inheritance, naming, and mixins""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "neurodata_type_inc",
                "domain_of": ["Group", "Dataset"],
                "structured_pattern": {"interpolated": True, "syntax": "{protected_string}"},
            }
        },
    )
    name: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "name",
                "domain_of": [
                    "Namespace",
                    "Group",
                    "Attribute",
                    "Link",
                    "Dataset",
                    "CompoundDtype",
                ],
                "structured_pattern": {"interpolated": True, "syntax": "{protected_string}"},
            }
        },
    )
    default_name: Optional[str] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "default_name",
                "domain_of": ["Group", "Dataset"],
                "structured_pattern": {"interpolated": True, "syntax": "{protected_string}"},
            }
        },
    )
    dims: Optional[List[Union[Any, str]]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "dims",
                "any_of": [{"range": "string"}, {"range": "AnyType"}],
                "domain_of": ["Attribute", "Dataset"],
                "todos": [
                    "Can't quite figure out how to allow an array of arrays - see "
                    "https://github.com/linkml/linkml/issues/895"
                ],
            }
        },
    )
    shape: Optional[List[Union[Any, int, str]]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "shape",
                "any_of": [
                    {"minimum_value": 1, "range": "integer"},
                    {"equals_string": "null", "range": "string"},
                    {"range": "AnyType"},
                ],
                "domain_of": ["Attribute", "Dataset"],
                "todos": [
                    "Can't quite figure out how to allow an array of arrays - see "
                    "https://github.com/linkml/linkml/issues/895"
                ],
            }
        },
    )
    value: Optional[Any] = Field(
        None,
        description="""Optional constant, fixed value for the attribute.""",
        json_schema_extra={
            "linkml_meta": {"alias": "value", "domain_of": ["Attribute", "Dataset"]}
        },
    )
    default_value: Optional[Any] = Field(
        None,
        description="""Optional default value for variable-valued attributes.""",
        json_schema_extra={
            "linkml_meta": {"alias": "default_value", "domain_of": ["Attribute", "Dataset"]}
        },
    )
    doc: str = Field(
        ...,
        description="""Description of corresponding object.""",
        json_schema_extra={
            "linkml_meta": {
                "alias": "doc",
                "domain_of": [
                    "Namespace",
                    "Schema",
                    "Group",
                    "Attribute",
                    "Link",
                    "Dataset",
                    "CompoundDtype",
                ],
            }
        },
    )
    quantity: Optional[Union[QuantityEnum, int]] = Field(
        "1",
        json_schema_extra={
            "linkml_meta": {
                "alias": "quantity",
                "any_of": [{"minimum_value": 1, "range": "integer"}, {"range": "QuantityEnum"}],
                "domain_of": ["Group", "Link", "Dataset"],
                "ifabsent": "int(1)",
                "todos": [
                    "logic to check that the corresponding class can only be "
                    "implemented quantity times."
                ],
            }
        },
    )
    linkable: Optional[bool] = Field(
        None,
        json_schema_extra={"linkml_meta": {"alias": "linkable", "domain_of": ["Group", "Dataset"]}},
    )
    attributes: Optional[List[Attribute]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {"alias": "attributes", "domain_of": ["Group", "Dataset"]}
        },
    )
    parent: Optional[Group] = Field(
        None,
        exclude=True,
        description="""The parent group that contains this dataset or group""",
        json_schema_extra={
            "linkml_meta": {"alias": "parent", "domain_of": ["Group", "Attribute", "Dataset"]}
        },
    )
    dtype: Optional[Union[List[CompoundDtype], FlatDtype, ReferenceDtype]] = Field(
        None,
        json_schema_extra={
            "linkml_meta": {
                "alias": "dtype",
                "any_of": [
                    {"range": "FlatDtype"},
                    {"range": "CompoundDtype"},
                    {"range": "ReferenceDtype"},
                ],
                "domain_of": ["CompoundDtype", "DtypeMixin"],
            }
        },
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Namespace.model_rebuild()
Namespaces.model_rebuild()
Schema.model_rebuild()
Group.model_rebuild()
Groups.model_rebuild()
Link.model_rebuild()
Datasets.model_rebuild()
ReferenceDtype.model_rebuild()
CompoundDtype.model_rebuild()
DtypeMixin.model_rebuild()
Attribute.model_rebuild()
Dataset.model_rebuild()
