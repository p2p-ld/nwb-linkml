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
    Container
)

from .hdmf_experimental_resources_include import (
    HERDObjectKeys,
    HERDObjects,
    HERDEntities,
    HERDKeys,
    HERDFiles,
    HERDEntityKeys
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


class HERD(Container):
    """
    HDMF External Resources Data Structure. A set of six tables for tracking external resource references in a file or across multiple files.
    """
    keys: HERDKeys = Field(<built-in method keys of dict object at 0x10ab5b600>, description="""A table for storing user terms that are used to refer to external resources.""")
    files: HERDFiles = Field(..., description="""A table for storing object ids of files used in external resources.""")
    entities: HERDEntities = Field(..., description="""A table for mapping user terms (i.e., keys) to resource entities.""")
    objects: HERDObjects = Field(..., description="""A table for identifying which objects in a file contain references to external resources.""")
    object_keys: HERDObjectKeys = Field(..., description="""A table for identifying which objects use which keys.""")
    entity_keys: HERDEntityKeys = Field(..., description="""A table for identifying which keys use which entity.""")
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
HERD.update_forward_refs()
