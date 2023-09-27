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
version = "1.1.2"

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




class CSRMatrix(ConfiguredBaseModel):
    """
    a compressed sparse row matrix
    """
    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(tree_root=True), frozen=True)
    name: str = Field(...)
    shape: Optional[int] = Field(None, description="""the shape of this sparse matrix""")
    indices: CSRMatrixIndices = Field(..., description="""column indices""")
    indptr: CSRMatrixIndptr = Field(..., description="""index pointer""")
    data: CSRMatrixData = Field(..., description="""values in the matrix""")
    

class CSRMatrixIndices(ConfiguredBaseModel):
    """
    column indices
    """
    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["indices"] = Field("indices")
    

class CSRMatrixIndptr(ConfiguredBaseModel):
    """
    index pointer
    """
    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["indptr"] = Field("indptr")
    

class CSRMatrixData(ConfiguredBaseModel):
    """
    values in the matrix
    """
    linkml_meta: ClassVar[LinkML_Meta] = Field(LinkML_Meta(), frozen=True)
    name: Literal["data"] = Field("data")
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
CSRMatrix.model_rebuild()
CSRMatrixIndices.model_rebuild()
CSRMatrixIndptr.model_rebuild()
CSRMatrixData.model_rebuild()
    