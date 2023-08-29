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


from .core_nwb_retinotopy_include import (
    ImagingRetinotopyAxisDescriptions,
    ImagingRetinotopyFocalDepthImage,
    ImagingRetinotopyAxis2PowerMap,
    ImagingRetinotopyVasculatureImage,
    ImagingRetinotopyAxis2PhaseMap,
    ImagingRetinotopyAxis1PhaseMap,
    ImagingRetinotopyAxis1PowerMap,
    ImagingRetinotopySignMap
)

from .core_nwb_base import (
    NWBDataInterface
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


class ImagingRetinotopy(NWBDataInterface):
    """
    Intrinsic signal optical imaging or widefield imaging for measuring retinotopy. Stores orthogonal maps (e.g., altitude/azimuth; radius/theta) of responses to specific stimuli and a combined polarity map from which to identify visual areas. This group does not store the raw responses imaged during retinotopic mapping or the stimuli presented, but rather the resulting phase and power maps after applying a Fourier transform on the averaged responses. Note: for data consistency, all images and arrays are stored in the format [row][column] and [row, col], which equates to [y][x]. Field of view and dimension arrays may appear backward (i.e., y before x).
    """
    axis_1_phase_map: ImagingRetinotopyAxis1PhaseMap = Field(..., description="""Phase response to stimulus on the first measured axis.""")
    axis_1_power_map: Optional[ImagingRetinotopyAxis1PowerMap] = Field(None, description="""Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.""")
    axis_2_phase_map: ImagingRetinotopyAxis2PhaseMap = Field(..., description="""Phase response to stimulus on the second measured axis.""")
    axis_2_power_map: Optional[ImagingRetinotopyAxis2PowerMap] = Field(None, description="""Power response on the second measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.""")
    axis_descriptions: ImagingRetinotopyAxisDescriptions = Field(..., description="""Two-element array describing the contents of the two response axis fields. Description should be something like ['altitude', 'azimuth'] or '['radius', 'theta'].""")
    focal_depth_image: Optional[ImagingRetinotopyFocalDepthImage] = Field(None, description="""Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].""")
    sign_map: Optional[ImagingRetinotopySignMap] = Field(None, description="""Sine of the angle between the direction of the gradient in axis_1 and axis_2.""")
    vasculature_image: ImagingRetinotopyVasculatureImage = Field(..., description="""Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]""")
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
ImagingRetinotopy.update_forward_refs()
