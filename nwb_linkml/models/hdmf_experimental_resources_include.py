from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, Field
from nptyping import NDArray, Shape, Float, Float32, Double, Float64, LongLong, Int64, Int, Int32, Int16, Short, Int8, UInt, UInt32, UInt16, UInt8, UInt64, Number, String, Unicode, Unicode, Unicode, String, Bool, Datetime64
import sys
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


from .hdmf_common_base import (
    Data
)


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


class HERDKeys(Data):
    """
    A table for storing user terms that are used to refer to external resources.
    """
    keys: List[Any] = Field(default_factory=list, description="""A table for storing user terms that are used to refer to external resources.""")
    

class HERDFiles(Data):
    """
    A table for storing object ids of files used in external resources.
    """
    files: List[Any] = Field(default_factory=list, description="""A table for storing object ids of files used in external resources.""")
    

class HERDEntities(Data):
    """
    A table for mapping user terms (i.e., keys) to resource entities.
    """
    entities: List[Any] = Field(default_factory=list, description="""A table for mapping user terms (i.e., keys) to resource entities.""")
    

class HERDObjects(Data):
    """
    A table for identifying which objects in a file contain references to external resources.
    """
    objects: List[Any] = Field(default_factory=list, description="""A table for identifying which objects in a file contain references to external resources.""")
    

class HERDObjectKeys(Data):
    """
    A table for identifying which objects use which keys.
    """
    object_keys: List[Any] = Field(default_factory=list, description="""A table for identifying which objects use which keys.""")
    

class HERDEntityKeys(Data):
    """
    A table for identifying which keys use which entity.
    """
    entity_keys: List[Any] = Field(default_factory=list, description="""A table for identifying which keys use which entity.""")
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
HERDKeys.update_forward_refs()
HERDFiles.update_forward_refs()
HERDEntities.update_forward_refs()
HERDObjects.update_forward_refs()
HERDObjectKeys.update_forward_refs()
HERDEntityKeys.update_forward_refs()
