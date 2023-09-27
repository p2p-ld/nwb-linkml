from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union, ClassVar
from pydantic import BaseModel as BaseModel, Field
from nptyping import Shape, Float, Float32, Double, Float64, LongLong, Int64, Int, Int32, Int16, Short, Int8, UInt, UInt32, UInt16, UInt8, UInt64, Number, String, Unicode, Unicode, Unicode, String, Bool, Datetime64
from nwb_linkml.types import NDArray
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
    hdf5_path: Optional[str] = Field(None, description="The absolute path that this object is stored in an NWB file")
    

class LinkML_Meta(BaseModel):
    """Extra LinkML Metadata stored as a class attribute"""
    tree_root: bool = False




class Arraylike(ConfiguredBaseModel):
    """
    Container for arraylike information held in the dims, shape, and dtype properties.this is a special case to be interpreted by downstream i/o. this class has no slotsand is abstract by default.- Each slot within a subclass indicates a possible dimension.- Only dimensions that are present in all the dimension specifiers in the  original schema are required.- Shape requirements are indicated using max/min cardinalities on the slot.
    """
    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Arraylike.model_rebuild()
    