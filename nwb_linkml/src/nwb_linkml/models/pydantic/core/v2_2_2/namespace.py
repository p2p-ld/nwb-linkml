from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union, ClassVar
from pydantic import BaseModel as BaseModel, Field
from nptyping import (
    Shape,
    Float,
    Float32,
    Double,
    Float64,
    LongLong,
    Int64,
    Int,
    Int32,
    Int16,
    Short,
    Int8,
    UInt,
    UInt32,
    UInt16,
    UInt8,
    UInt64,
    Number,
    String,
    Unicode,
    Unicode,
    Unicode,
    String,
    Bool,
    Datetime64,
)
from nwb_linkml.types import NDArray
import sys

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


from ...hdmf_common.v1_1_3.hdmf_common_sparse import CSRMatrix

from ...hdmf_common.v1_1_3.hdmf_common_table import (
    Data,
    Index,
    VectorData,
    VectorIndex,
    ElementIdentifiers,
    DynamicTableRegion,
    Container,
    DynamicTable,
)

from .core_nwb_retinotopy import ImagingRetinotopy

from .core_nwb_base import (
    NWBData,
    Image,
    NWBContainer,
    NWBDataInterface,
    TimeSeries,
    ProcessingModule,
    Images,
)

from .core_nwb_ophys import (
    TwoPhotonSeries,
    RoiResponseSeries,
    DfOverF,
    Fluorescence,
    ImageSegmentation,
    ImagingPlane,
    MotionCorrection,
)

from .core_nwb_device import Device

from .core_nwb_image import (
    GrayscaleImage,
    RGBImage,
    RGBAImage,
    ImageSeries,
    ImageMaskSeries,
    OpticalSeries,
    IndexSeries,
)

from .core_nwb_ogen import OptogeneticSeries, OptogeneticStimulusSite

from .core_nwb_icephys import (
    PatchClampSeries,
    CurrentClampSeries,
    IZeroClampSeries,
    CurrentClampStimulusSeries,
    VoltageClampSeries,
    VoltageClampStimulusSeries,
    IntracellularElectrode,
    SweepTable,
)

from .core_nwb_ecephys import (
    ElectricalSeries,
    SpikeEventSeries,
    FeatureExtraction,
    EventDetection,
    EventWaveform,
    FilteredEphys,
    LFP,
    ElectrodeGroup,
    ClusterWaveforms,
    Clustering,
)

from .core_nwb_behavior import (
    SpatialSeries,
    BehavioralEpochs,
    BehavioralEvents,
    BehavioralTimeSeries,
    PupilTracking,
    EyeTracking,
    CompassDirection,
    Position,
)

from .core_nwb_misc import (
    AbstractFeatureSeries,
    AnnotationSeries,
    IntervalSeries,
    DecompositionSeries,
    Units,
)

from .core_nwb_file import NWBFile

from .core_nwb_epoch import TimeIntervals


metamodel_version = "None"
version = "2.2.2"


class ConfiguredBaseModel(
    BaseModel,
    validate_assignment=True,
    validate_default=True,
    extra="forbid",
    arbitrary_types_allowed=True,
    use_enum_values=True,
):
    hdf5_path: Optional[str] = Field(
        None, description="The absolute path that this object is stored in an NWB file"
    )


class LinkML_Meta(BaseModel):
    """Extra LinkML Metadata stored as a class attribute"""

    tree_root: bool = False


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
