from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import (
    Dict,
    Optional,
    Any,
    Union,
    ClassVar,
    Annotated,
    TypeVar,
    List,
    TYPE_CHECKING,
)
from pydantic import BaseModel as BaseModel, Field
from pydantic import ConfigDict, BeforeValidator

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
if TYPE_CHECKING:
    import numpy as np


from ...hdmf_common.v1_1_0.hdmf_common_sparse import (
    CSRMatrix,
    CSRMatrixIndices,
    CSRMatrixIndptr,
    CSRMatrixData,
)

from ...hdmf_common.v1_1_0.hdmf_common_table import (
    Data,
    Index,
    VectorData,
    VectorIndex,
    ElementIdentifiers,
    DynamicTableRegion,
    Container,
    DynamicTable,
)

from .core_nwb_retinotopy import (
    RetinotopyMap,
    AxisMap,
    RetinotopyImage,
    ImagingRetinotopy,
    ImagingRetinotopyAxis1PhaseMap,
    ImagingRetinotopyAxis1PowerMap,
    ImagingRetinotopyAxis2PhaseMap,
    ImagingRetinotopyAxis2PowerMap,
    ImagingRetinotopySignMap,
    ImagingRetinotopyFocalDepthImage,
    ImagingRetinotopyVasculatureImage,
)

from .core_nwb_image import (
    GrayscaleImage,
    RGBImage,
    RGBAImage,
    ImageSeries,
    ImageSeriesExternalFile,
    ImageMaskSeries,
    OpticalSeries,
    IndexSeries,
)

from .core_nwb_base import (
    NWBData,
    Image,
    NWBContainer,
    NWBDataInterface,
    TimeSeries,
    TimeSeriesData,
    TimeSeriesStartingTime,
    TimeSeriesSync,
    ProcessingModule,
    Images,
)

from .core_nwb_ophys import (
    TwoPhotonSeries,
    RoiResponseSeries,
    RoiResponseSeriesRois,
    DfOverF,
    Fluorescence,
    ImageSegmentation,
    ImagingPlane,
    ImagingPlaneManifold,
    ImagingPlaneOriginCoords,
    ImagingPlaneGridSpacing,
    OpticalChannel,
    MotionCorrection,
)

from .core_nwb_device import Device

from .core_nwb_ogen import OptogeneticSeries, OptogeneticStimulusSite

from .core_nwb_icephys import (
    PatchClampSeries,
    PatchClampSeriesData,
    CurrentClampSeries,
    CurrentClampSeriesData,
    IZeroClampSeries,
    CurrentClampStimulusSeries,
    CurrentClampStimulusSeriesData,
    VoltageClampSeries,
    VoltageClampSeriesData,
    VoltageClampSeriesCapacitanceFast,
    VoltageClampSeriesCapacitanceSlow,
    VoltageClampSeriesResistanceCompBandwidth,
    VoltageClampSeriesResistanceCompCorrection,
    VoltageClampSeriesResistanceCompPrediction,
    VoltageClampSeriesWholeCellCapacitanceComp,
    VoltageClampSeriesWholeCellSeriesResistanceComp,
    VoltageClampStimulusSeries,
    VoltageClampStimulusSeriesData,
    IntracellularElectrode,
    SweepTable,
    SweepTableSeriesIndex,
)

from .core_nwb_ecephys import (
    ElectricalSeries,
    ElectricalSeriesElectrodes,
    SpikeEventSeries,
    FeatureExtraction,
    FeatureExtractionElectrodes,
    EventDetection,
    EventWaveform,
    FilteredEphys,
    LFP,
    ElectrodeGroup,
    ElectrodeGroupPosition,
    ClusterWaveforms,
    Clustering,
)

from .core_nwb_behavior import (
    SpatialSeries,
    SpatialSeriesData,
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
    AbstractFeatureSeriesData,
    AnnotationSeries,
    IntervalSeries,
    DecompositionSeries,
    DecompositionSeriesData,
    DecompositionSeriesBands,
    Units,
    UnitsSpikeTimesIndex,
    UnitsSpikeTimes,
    UnitsObsIntervalsIndex,
    UnitsElectrodesIndex,
    UnitsElectrodes,
)

from .core_nwb_file import (
    NWBFile,
    NWBFileStimulus,
    NWBFileGeneral,
    NWBFileGeneralSourceScript,
    Subject,
    NWBFileGeneralExtracellularEphys,
    NWBFileGeneralExtracellularEphysElectrodes,
    NWBFileGeneralIntracellularEphys,
)

from .core_nwb_epoch import (
    TimeIntervals,
    TimeIntervalsTagsIndex,
    TimeIntervalsTimeseries,
    TimeIntervalsTimeseriesIndex,
)


metamodel_version = "None"
version = "2.2.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="allow",
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )
    hdf5_path: Optional[str] = Field(
        None, description="The absolute path that this object is stored in an NWB file"
    )

    object_id: Optional[str] = Field(None, description="Unique UUID for each object")

    def __getitem__(self, i: slice | int) -> "np.ndarray":
        if hasattr(self, "array"):
            return self.array[i]
        else:
            return super().__getitem__(i)

    def __setitem__(self, i: slice | int, value: Any):
        if hasattr(self, "array"):
            self.array[i] = value
        else:
            super().__setitem__(i, value)


class LinkML_Meta(BaseModel):
    """Extra LinkML Metadata stored as a class attribute"""

    tree_root: bool = False


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
