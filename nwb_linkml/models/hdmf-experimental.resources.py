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
    
    

class Arraylike(ConfiguredBaseModel):
    """
    Container for arraylike information held in the dims, shape, and dtype properties.this is a special case to be interpreted by downstream i/o. this class has no slotsand is abstract by default.- Each slot within a subclass indicates a possible dimension.- Only dimensions that are present in all the dimension specifiers in the  original schema are required.- Shape requirements are indicated using max/min cardinalities on the slot.
    """
    None
    

class HERDKeysArray(Arraylike):
    
    num_rows: Any = Field(...)
    

class HERDFilesArray(Arraylike):
    
    num_rows: Any = Field(...)
    

class HERDEntitiesArray(Arraylike):
    
    num_rows: Any = Field(...)
    

class HERDObjectsArray(Arraylike):
    
    num_rows: Any = Field(...)
    

class HERDObjectKeysArray(Arraylike):
    
    num_rows: Any = Field(...)
    

class HERDEntityKeysArray(Arraylike):
    
    num_rows: Any = Field(...)
    

class Data(ConfiguredBaseModel):
    """
    An abstract data type for a dataset.
    """
    None
    

class HERDKeys(Data):
    """
    A table for storing user terms that are used to refer to external resources.
    """
    array: Optional[HERDKeysArray] = Field(None)
    

class HERDFiles(Data):
    """
    A table for storing object ids of files used in external resources.
    """
    array: Optional[HERDFilesArray] = Field(None)
    

class HERDEntities(Data):
    """
    A table for mapping user terms (i.e., keys) to resource entities.
    """
    array: Optional[HERDEntitiesArray] = Field(None)
    

class HERDObjects(Data):
    """
    A table for identifying which objects in a file contain references to external resources.
    """
    array: Optional[HERDObjectsArray] = Field(None)
    

class HERDObjectKeys(Data):
    """
    A table for identifying which objects use which keys.
    """
    array: Optional[HERDObjectKeysArray] = Field(None)
    

class HERDEntityKeys(Data):
    """
    A table for identifying which keys use which entity.
    """
    array: Optional[HERDEntityKeysArray] = Field(None)
    

class Container(ConfiguredBaseModel):
    """
    An abstract data type for a group storing collections of data and metadata. Base type for all data and metadata containers.
    """
    None
    

class HERD(Container):
    """
    HDMF External Resources Data Structure. A set of six tables for tracking external resource references in a file or across multiple files.
    """
    keys: HERDKeys = Field(<built-in method keys of dict object at 0x10ad57dc0>, description="""A table for storing user terms that are used to refer to external resources.""")
    files: HERDFiles = Field(..., description="""A table for storing object ids of files used in external resources.""")
    entities: HERDEntities = Field(..., description="""A table for mapping user terms (i.e., keys) to resource entities.""")
    objects: HERDObjects = Field(..., description="""A table for identifying which objects in a file contain references to external resources.""")
    object_keys: HERDObjectKeys = Field(..., description="""A table for identifying which objects use which keys.""")
    entity_keys: HERDEntityKeys = Field(..., description="""A table for identifying which keys use which entity.""")
    

class SimpleMultiContainer(Container):
    """
    A simple Container for holding onto multiple containers.
    """
    Data: Optional[List[Data]] = Field(default_factory=list, description="""Data objects held within this SimpleMultiContainer.""")
    Container: Optional[List[Container]] = Field(default_factory=list, description="""Container objects held within this SimpleMultiContainer.""")
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
Arraylike.update_forward_refs()
HERDKeysArray.update_forward_refs()
HERDFilesArray.update_forward_refs()
HERDEntitiesArray.update_forward_refs()
HERDObjectsArray.update_forward_refs()
HERDObjectKeysArray.update_forward_refs()
HERDEntityKeysArray.update_forward_refs()
Data.update_forward_refs()
HERDKeys.update_forward_refs()
HERDFiles.update_forward_refs()
HERDEntities.update_forward_refs()
HERDObjects.update_forward_refs()
HERDObjectKeys.update_forward_refs()
HERDEntityKeys.update_forward_refs()
Container.update_forward_refs()
HERD.update_forward_refs()
SimpleMultiContainer.update_forward_refs()
