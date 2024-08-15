from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
import numpy as np
from ...hdmf_common.v1_1_3.hdmf_common_sparse import (
    CSRMatrix,
    CSRMatrixIndices,
    CSRMatrixIndptr,
    CSRMatrixData,
)
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
from ...core.v2_2_2.core_nwb_retinotopy import (
    ImagingRetinotopy,
    ImagingRetinotopyAxis1PhaseMap,
    ImagingRetinotopyAxis1PowerMap,
    ImagingRetinotopyAxis2PhaseMap,
    ImagingRetinotopyAxis2PowerMap,
    ImagingRetinotopyFocalDepthImage,
    ImagingRetinotopySignMap,
    ImagingRetinotopyVasculatureImage,
)
from ...core.v2_2_2.core_nwb_base import (
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
from ...core.v2_2_2.core_nwb_ophys import (
    TwoPhotonSeries,
    RoiResponseSeries,
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
from ...core.v2_2_2.core_nwb_device import Device
from ...core.v2_2_2.core_nwb_image import (
    GrayscaleImage,
    RGBImage,
    RGBAImage,
    ImageSeries,
    ImageSeriesExternalFile,
    ImageMaskSeries,
    OpticalSeries,
    IndexSeries,
)
from ...core.v2_2_2.core_nwb_ogen import OptogeneticSeries, OptogeneticStimulusSite
from ...core.v2_2_2.core_nwb_icephys import (
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
)
from ...core.v2_2_2.core_nwb_ecephys import (
    ElectricalSeries,
    SpikeEventSeries,
    FeatureExtraction,
    EventDetection,
    EventWaveform,
    FilteredEphys,
    LFP,
    ElectrodeGroup,
    ElectrodeGroupPosition,
    ClusterWaveforms,
    Clustering,
)
from ...core.v2_2_2.core_nwb_behavior import (
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
from ...core.v2_2_2.core_nwb_misc import (
    AbstractFeatureSeries,
    AbstractFeatureSeriesData,
    AnnotationSeries,
    IntervalSeries,
    DecompositionSeries,
    DecompositionSeriesData,
    DecompositionSeriesBands,
    Units,
    UnitsSpikeTimes,
)
from ...core.v2_2_2.core_nwb_file import (
    NWBFile,
    NWBFileStimulus,
    NWBFileGeneral,
    GeneralSourceScript,
    Subject,
    GeneralExtracellularEphys,
    ExtracellularEphysElectrodes,
    GeneralIntracellularEphys,
    NWBFileIntervals,
)
from ...core.v2_2_2.core_nwb_epoch import TimeIntervals, TimeIntervalsTimeseries

metamodel_version = "None"
version = "2.2.2"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )
    hdf5_path: Optional[str] = Field(
        None, description="The absolute path that this object is stored in an NWB file"
    )
    object_id: Optional[str] = Field(None, description="Unique UUID for each object")

    def __getitem__(self, val: Union[int, slice]) -> Any:
        """Try and get a value from value or "data" if we have it"""
        if hasattr(self, "value") and self.value is not None:
            return self.value[val]
        elif hasattr(self, "data") and self.data is not None:
            return self.data[val]
        else:
            raise KeyError("No value or data field to index from")


class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key: str):
        return getattr(self.root, key)

    def __getitem__(self, key: str):
        return self.root[key]

    def __setitem__(self, key: str, value):
        self.root[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta(
    {
        "annotations": {
            "is_namespace": {"tag": "is_namespace", "value": True},
            "namespace": {"tag": "namespace", "value": "core"},
        },
        "default_prefix": "core/",
        "description": "NWB namespace",
        "id": "core",
        "imports": [
            "core.nwb.base",
            "core.nwb.device",
            "core.nwb.epoch",
            "core.nwb.image",
            "core.nwb.file",
            "core.nwb.misc",
            "core.nwb.behavior",
            "core.nwb.ecephys",
            "core.nwb.icephys",
            "core.nwb.ogen",
            "core.nwb.ophys",
            "core.nwb.retinotopy",
            "core.nwb.language",
            "../../hdmf_common/v1_1_3/namespace",
        ],
        "name": "core",
    }
)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
