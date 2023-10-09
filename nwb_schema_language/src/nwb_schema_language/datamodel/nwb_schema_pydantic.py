from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, Field
import sys
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


metamodel_version = "None"
version = "None"

class ConfiguredBaseModel(BaseModel,
                validate_assignment = True,
                validate_default = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


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
    
    doc: str = Field(..., description="""Description of corresponding object.""")
    name: str = Field(...)
    full_name: Optional[str] = Field(None, description="""Optional string with extended full name for the namespace.""")
    version: str = Field(...)
    date: Optional[datetime ] = Field(None, description="""Date that a namespace was last modified or released""")
    author: List[str] = Field(default_factory=list, description="""List of strings with the names of the authors of the namespace.""")
    contact: List[str] = Field(default_factory=list, description="""List of strings with the contact information for the authors. Ordering of the contacts should match the ordering of the authors.""")
    schema_: Optional[List[Schema]] = Field(alias="schema", default_factory=list, description="""List of the schema to be included in this namespace.""")
    

class Namespaces(ConfiguredBaseModel):
    
    namespaces: Optional[List[Namespace]] = Field(default_factory=list)
    

class Schema(ConfiguredBaseModel):
    
    source: Optional[str] = Field(None, description="""describes the name of the YAML (or JSON) file with the schema specification. The schema files should be located in the same folder as the namespace file.""")
    namespace: Optional[str] = Field(None, description="""describes a named reference to another namespace. In contrast to source, this is a reference by name to a known namespace (i.e., the namespace is resolved during the build and must point to an already existing namespace). This mechanism is used to allow, e.g., extension of a core namespace (here the NWB core namespace) without requiring hard paths to the files describing the core namespace. Either source or namespace must be specified, but not both.""")
    title: Optional[str] = Field(None, description="""a descriptive title for a file for documentation purposes.""")
    neurodata_types: Optional[List[Union[Dataset, Group]]] = Field(default_factory=list, description="""an optional list of strings indicating which data types should be included from the given specification source or namespace. The default is null indicating that all data types should be included.""")
    doc: Optional[str] = Field(None)
    

class Group(ConfiguredBaseModel):
    
    neurodata_type_def: Optional[str] = Field(None, description="""Used alongside neurodata_type_inc to indicate inheritance, naming, and mixins""")
    neurodata_type_inc: Optional[str] = Field(None, description="""Used alongside neurodata_type_def to indicate inheritance, naming, and mixins""")
    name: Optional[str] = Field(None)
    default_name: Optional[str] = Field(None)
    doc: str = Field(..., description="""Description of corresponding object.""")
    quantity: Optional[Union[QuantityEnum, int]] = Field(1)
    linkable: Optional[bool] = Field(None)
    attributes: Optional[List[Attribute]] = Field(default_factory=list)
    datasets: Optional[List[Dataset]] = Field(default_factory=list)
    groups: Optional[List[Group]] = Field(default_factory=list)
    links: Optional[List[Link]] = Field(default_factory=list)
    

class Groups(ConfiguredBaseModel):
    
    groups: Optional[List[Group]] = Field(default_factory=list)
    

class Link(ConfiguredBaseModel):
    
    name: Optional[str] = Field(None)
    doc: str = Field(..., description="""Description of corresponding object.""")
    target_type: str = Field(..., description="""Describes the neurodata_type of the target that the reference points to""")
    quantity: Optional[Union[QuantityEnum, int]] = Field(1)
    

class Datasets(ConfiguredBaseModel):
    
    datasets: Optional[List[Dataset]] = Field(default_factory=list)
    

class ReferenceDtype(ConfiguredBaseModel):
    
    target_type: str = Field(..., description="""Describes the neurodata_type of the target that the reference points to""")
    reftype: Optional[ReftypeOptions] = Field(None, description="""describes the kind of reference""")
    

class CompoundDtype(ConfiguredBaseModel):
    
    name: str = Field(...)
    doc: str = Field(..., description="""Description of corresponding object.""")
    dtype: Union[FlatDtype, ReferenceDtype] = Field(...)
    

class DtypeMixin(ConfiguredBaseModel):
    
    dtype: Optional[Union[List[CompoundDtype], FlatDtype, ReferenceDtype]] = Field(default_factory=list)
    

class Attribute(DtypeMixin):
    
    name: str = Field(...)
    dims: Optional[List[Union[Any, str]]] = Field(default_factory=list)
    shape: Optional[List[Union[Any, int, str]]] = Field(default_factory=list)
    value: Optional[Any] = Field(None, description="""Optional constant, fixed value for the attribute.""")
    default_value: Optional[Any] = Field(None, description="""Optional default value for variable-valued attributes.""")
    doc: str = Field(..., description="""Description of corresponding object.""")
    required: Optional[bool] = Field(True, description="""Optional boolean key describing whether the attribute is required. Default value is True.""")
    dtype: Optional[Union[List[CompoundDtype], FlatDtype, ReferenceDtype]] = Field(default_factory=list)
    

class Dataset(DtypeMixin):
    
    neurodata_type_def: Optional[str] = Field(None, description="""Used alongside neurodata_type_inc to indicate inheritance, naming, and mixins""")
    neurodata_type_inc: Optional[str] = Field(None, description="""Used alongside neurodata_type_def to indicate inheritance, naming, and mixins""")
    name: Optional[str] = Field(None)
    default_name: Optional[str] = Field(None)
    dims: Optional[List[Union[Any, str]]] = Field(default_factory=list)
    shape: Optional[List[Union[Any, int, str]]] = Field(default_factory=list)
    value: Optional[Any] = Field(None, description="""Optional constant, fixed value for the attribute.""")
    default_value: Optional[Any] = Field(None, description="""Optional default value for variable-valued attributes.""")
    doc: str = Field(..., description="""Description of corresponding object.""")
    quantity: Optional[Union[QuantityEnum, int]] = Field(1)
    linkable: Optional[bool] = Field(None)
    attributes: Optional[List[Attribute]] = Field(default_factory=list)
    dtype: Optional[Union[List[CompoundDtype], FlatDtype, ReferenceDtype]] = Field(default_factory=list)
    


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
    
