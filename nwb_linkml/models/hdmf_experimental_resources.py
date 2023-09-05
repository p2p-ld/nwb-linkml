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


metamodel_version = "None"
version = "None"

class ConfiguredBaseModel(BaseModel,
                validate_assignment = True,
                validate_default = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


class HERD(Container):
    """
    HDMF External Resources Data Structure. A set of six tables for tracking external resource references in a file or across multiple files.
    """
    name:str= Field(...)
    keys:List[Any]= Field(default_factory=list, description="""A table for storing user terms that are used to refer to external resources.""")
    files:List[Any]= Field(default_factory=list, description="""A table for storing object ids of files used in external resources.""")
    entities:List[Any]= Field(default_factory=list, description="""A table for mapping user terms (i.e., keys) to resource entities.""")
    objects:List[Any]= Field(default_factory=list, description="""A table for identifying which objects in a file contain references to external resources.""")
    object_keys:List[Any]= Field(default_factory=list, description="""A table for identifying which objects use which keys.""")
    entity_keys:List[Any]= Field(default_factory=list, description="""A table for identifying which keys use which entity.""")
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
HERD.model_rebuild()
    