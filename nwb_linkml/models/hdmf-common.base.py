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

class WeakRefShimBaseModel(BaseModel):
   __slots__ = '__weakref__'

class ConfiguredBaseModel(WeakRefShimBaseModel,
                validate_assignment = True,
                validate_all = True,
                underscore_attrs_are_private = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


class FlatDType(str, Enum):
    
    
    float = "float"
    
    float32 = "float32"
    
    double = "double"
    
    float64 = "float64"
    
    long = "long"
    
    int64 = "int64"
    
    int = "int"
    
    int32 = "int32"
    
    int16 = "int16"
    
    short = "short"
    
    int8 = "int8"
    
    uint = "uint"
    
    uint32 = "uint32"
    
    uint16 = "uint16"
    
    uint8 = "uint8"
    
    uint64 = "uint64"
    
    numeric = "numeric"
    
    text = "text"
    
    utf = "utf"
    
    utf8 = "utf8"
    
    utf_8 = "utf_8"
    
    ascii = "ascii"
    
    bool = "bool"
    
    isodatetime = "isodatetime"
    
    

class Data(ConfiguredBaseModel):
    """
    An abstract data type for a dataset.
    """
    None
    

class Container(ConfiguredBaseModel):
    """
    An abstract data type for a group storing collections of data and metadata. Base type for all data and metadata containers.
    """
    None
    

class SimpleMultiContainer(Container):
    """
    A simple Container for holding onto multiple containers.
    """
    Data: Optional[List[Data]] = Field(default_factory=list, description="""Data objects held within this SimpleMultiContainer.""")
    Container: Optional[List[Container]] = Field(default_factory=list, description="""Container objects held within this SimpleMultiContainer.""")
    

class Arraylike(ConfiguredBaseModel):
    """
    Container for arraylike information held in the dims, shape, and dtype properties.this is a special case to be interpreted by downstream i/o. this class has no slotsand is abstract by default.- Each slot within a subclass indicates a possible dimension.- Only dimensions that are present in all the dimension specifiers in the  original schema are required.- Shape requirements are indicated using max/min cardinalities on the slot.
    """
    None
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
Data.update_forward_refs()
Container.update_forward_refs()
SimpleMultiContainer.update_forward_refs()
Arraylike.update_forward_refs()
