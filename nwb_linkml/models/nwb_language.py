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


class Arraylike(ConfiguredBaseModel):
    """
    Container for arraylike information held in the dims, shape, and dtype properties.this is a special case to be interpreted by downstream i/o. this class has no slotsand is abstract by default.- Each slot within a subclass indicates a possible dimension.- Only dimensions that are present in all the dimension specifiers in the  original schema are required.- Shape requirements are indicated using max/min cardinalities on the slot.
    """
    None
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
Arraylike.update_forward_refs()
