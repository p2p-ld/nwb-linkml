from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, Field
from nptyping import Shape, Float, Float32, Double, Float64, LongLong, Int64, Int, Int32, Int16, Short, Int8, UInt, UInt32, UInt16, UInt8, UInt64, Number, String, Unicode, Unicode, Unicode, String, Bool, Datetime64
from nwb_linkml.types import NDArray
import sys
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


from .hdmf_experimental_resources import (
    ExternalResources
)

from ...hdmf_common.v1_5_0.hdmf_common_sparse import (
    CSRMatrix
)

from ...hdmf_common.v1_5_0.hdmf_common_base import (
    Data,
    Container,
    SimpleMultiContainer
)

from ...hdmf_common.v1_5_0.hdmf_common_table import (
    VectorData,
    VectorIndex,
    ElementIdentifiers,
    DynamicTableRegion,
    DynamicTable,
    AlignedDynamicTable
)

from .hdmf_experimental_experimental import (
    EnumData
)


metamodel_version = "None"
version = "0.1.0"

class ConfiguredBaseModel(BaseModel,
                validate_assignment = True,
                validate_default = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass



# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
    