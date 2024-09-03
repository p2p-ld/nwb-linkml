from __future__ import annotations

import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

from ...core.v2_2_0.core_nwb_base import (
    Image,
    Images,
    NWBContainer,
    NWBData,
    NWBDataInterface,
    ProcessingModule,
    TimeSeries,
    TimeSeriesData,
    TimeSeriesStartingTime,
    TimeSeriesSync,
)
from ...core.v2_2_0.core_nwb_behavior import (
    BehavioralEpochs,
    BehavioralEvents,
    BehavioralTimeSeries,
    CompassDirection,
    EyeTracking,
    Position,
    PupilTracking,
    SpatialSeries,
    SpatialSeriesData,
)
from ...core.v2_2_0.core_nwb_device import Device
from ...core.v2_2_0.core_nwb_ecephys import (
    ClusterWaveforms,
    Clustering,
    ElectricalSeries,
    ElectrodeGroup,
    ElectrodeGroupPosition,
    EventDetection,
    EventWaveform,
    FeatureExtraction,
    FilteredEphys,
    LFP,
    SpikeEventSeries,
)
from ...core.v2_2_0.core_nwb_epoch import TimeIntervals, TimeIntervalsTimeseries
from ...core.v2_2_0.core_nwb_file import (
    ExtracellularEphysElectrodes,
    GeneralExtracellularEphys,
    GeneralIntracellularEphys,
    GeneralSourceScript,
    NWBFile,
    NWBFileGeneral,
    NWBFileIntervals,
    NWBFileStimulus,
    Subject,
)
from ...core.v2_2_0.core_nwb_icephys import (
    CurrentClampSeries,
    CurrentClampSeriesData,
    CurrentClampStimulusSeries,
    CurrentClampStimulusSeriesData,
    IZeroClampSeries,
    IntracellularElectrode,
    PatchClampSeries,
    PatchClampSeriesData,
    SweepTable,
    VoltageClampSeries,
    VoltageClampSeriesCapacitanceFast,
    VoltageClampSeriesCapacitanceSlow,
    VoltageClampSeriesData,
    VoltageClampSeriesResistanceCompBandwidth,
    VoltageClampSeriesResistanceCompCorrection,
    VoltageClampSeriesResistanceCompPrediction,
    VoltageClampSeriesWholeCellCapacitanceComp,
    VoltageClampSeriesWholeCellSeriesResistanceComp,
    VoltageClampStimulusSeries,
    VoltageClampStimulusSeriesData,
)
from ...core.v2_2_0.core_nwb_image import (
    GrayscaleImage,
    ImageMaskSeries,
    ImageSeries,
    ImageSeriesExternalFile,
    IndexSeries,
    OpticalSeries,
    RGBAImage,
    RGBImage,
)
from ...core.v2_2_0.core_nwb_misc import (
    AbstractFeatureSeries,
    AbstractFeatureSeriesData,
    AnnotationSeries,
    DecompositionSeries,
    DecompositionSeriesBands,
    DecompositionSeriesData,
    IntervalSeries,
    Units,
    UnitsSpikeTimes,
)
from ...core.v2_2_0.core_nwb_ogen import OptogeneticSeries, OptogeneticStimulusSite
from ...core.v2_2_0.core_nwb_ophys import (
    DfOverF,
    Fluorescence,
    ImageSegmentation,
    ImagingPlane,
    ImagingPlaneGridSpacing,
    ImagingPlaneManifold,
    ImagingPlaneOriginCoords,
    MotionCorrection,
    OpticalChannel,
    RoiResponseSeries,
    TwoPhotonSeries,
)
from ...core.v2_2_0.core_nwb_retinotopy import (
    AxisMap,
    ImagingRetinotopy,
    ImagingRetinotopyFocalDepthImage,
    RetinotopyImage,
    RetinotopyMap,
)
from ...hdmf_common.v1_1_0.hdmf_common_sparse import (
    CSRMatrix,
    CSRMatrixData,
    CSRMatrixIndices,
    CSRMatrixIndptr,
)
from ...hdmf_common.v1_1_0.hdmf_common_table import (
    Container,
    Data,
    DynamicTable,
    DynamicTableRegion,
    ElementIdentifiers,
    Index,
    VectorData,
    VectorIndex,
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

    @field_validator("*", mode="wrap")
    @classmethod
    def coerce_value(cls, v: Any, handler) -> Any:
        """Try to rescue instantiation by using the value field"""
        try:
            return handler(v)
        except Exception as e1:
            try:
                if hasattr(v, "value"):
                    return handler(v.value)
                else:
                    return handler(v["value"])
            except Exception as e2:
                raise e2 from e1


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
            "../../hdmf_common/v1_1_0/namespace",
        ],
        "name": "core",
    }
)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
