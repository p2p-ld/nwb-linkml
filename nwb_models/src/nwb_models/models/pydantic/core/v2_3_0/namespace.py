from __future__ import annotations

import re
import sys
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator, model_validator

from ...core.v2_3_0.core_nwb_base import (
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
from ...core.v2_3_0.core_nwb_behavior import (
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
from ...core.v2_3_0.core_nwb_device import Device
from ...core.v2_3_0.core_nwb_ecephys import (
    ClusterWaveforms,
    Clustering,
    ElectricalSeries,
    ElectricalSeriesData,
    ElectrodeGroup,
    ElectrodeGroupPosition,
    EventDetection,
    EventWaveform,
    FeatureExtraction,
    FilteredEphys,
    LFP,
    SpikeEventSeries,
    SpikeEventSeriesData,
)
from ...core.v2_3_0.core_nwb_epoch import TimeIntervals, TimeIntervalsTimeseries
from ...core.v2_3_0.core_nwb_file import (
    ExtracellularEphysElectrodes,
    GeneralExtracellularEphys,
    GeneralIntracellularEphys,
    GeneralSourceScript,
    LabMetaData,
    NWBFile,
    NWBFileGeneral,
    NWBFileIntervals,
    NWBFileStimulus,
    ScratchData,
    Subject,
)
from ...core.v2_3_0.core_nwb_icephys import (
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
from ...core.v2_3_0.core_nwb_image import (
    GrayscaleImage,
    ImageMaskSeries,
    ImageSeries,
    ImageSeriesData,
    ImageSeriesExternalFile,
    IndexSeries,
    IndexSeriesData,
    OpticalSeries,
    OpticalSeriesData,
    RGBAImage,
    RGBImage,
)
from ...core.v2_3_0.core_nwb_misc import (
    AbstractFeatureSeries,
    AbstractFeatureSeriesData,
    AnnotationSeries,
    AnnotationSeriesData,
    DecompositionSeries,
    DecompositionSeriesBands,
    DecompositionSeriesData,
    IntervalSeries,
    IntervalSeriesData,
    Units,
    UnitsSpikeTimes,
    UnitsWaveformMean,
    UnitsWaveformSd,
    UnitsWaveforms,
)
from ...core.v2_3_0.core_nwb_ogen import (
    OptogeneticSeries,
    OptogeneticSeriesData,
    OptogeneticStimulusSite,
)
from ...core.v2_3_0.core_nwb_ophys import (
    CorrectedImageStack,
    DfOverF,
    Fluorescence,
    ImageSegmentation,
    ImagingPlane,
    ImagingPlaneGridSpacing,
    ImagingPlaneManifold,
    ImagingPlaneOriginCoords,
    MotionCorrection,
    OpticalChannel,
    PlaneSegmentation,
    PlaneSegmentationPixelMask,
    PlaneSegmentationVoxelMask,
    RoiResponseSeries,
    RoiResponseSeriesData,
    TwoPhotonSeries,
)
from ...core.v2_3_0.core_nwb_retinotopy import (
    ImagingRetinotopy,
    ImagingRetinotopyAxis1PhaseMap,
    ImagingRetinotopyAxis1PowerMap,
    ImagingRetinotopyAxis2PhaseMap,
    ImagingRetinotopyAxis2PowerMap,
    ImagingRetinotopyFocalDepthImage,
    ImagingRetinotopySignMap,
    ImagingRetinotopyVasculatureImage,
)
from ...hdmf_common.v1_5_0.hdmf_common_base import Container, Data, SimpleMultiContainer
from ...hdmf_common.v1_5_0.hdmf_common_sparse import CSRMatrix
from ...hdmf_common.v1_5_0.hdmf_common_table import (
    AlignedDynamicTable,
    DynamicTable,
    DynamicTableRegion,
    ElementIdentifiers,
    VectorData,
    VectorIndex,
)
from ...hdmf_experimental.v0_1_0.hdmf_experimental_experimental import EnumData
from ...hdmf_experimental.v0_1_0.hdmf_experimental_resources import (
    ExternalResources,
    ExternalResourcesEntities,
    ExternalResourcesKeys,
    ExternalResourcesObjectKeys,
    ExternalResourcesObjects,
    ExternalResourcesResources,
)


metamodel_version = "None"
version = "2.3.0"


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

    def __getitem__(self, val: Union[int, slice, str]) -> Any:
        """Try and get a value from value or "data" if we have it"""
        if hasattr(self, "value") and self.value is not None:
            return self.value[val]
        elif hasattr(self, "data") and self.data is not None:
            return self.data[val]
        else:
            raise KeyError("No value or data field to index from")

    @field_validator("*", mode="wrap")
    @classmethod
    def coerce_value(cls, v: Any, handler, info) -> Any:
        """Try to rescue instantiation by using the value field"""
        try:
            return handler(v)
        except Exception as e1:
            try:
                return handler(v.value)
            except AttributeError:
                try:
                    return handler(v["value"])
                except (IndexError, KeyError, TypeError):
                    raise e1

    @field_validator("*", mode="wrap")
    @classmethod
    def cast_with_value(cls, v: Any, handler, info) -> Any:
        """Try to rescue instantiation by casting into the model's value fiel"""
        try:
            return handler(v)
        except Exception as e1:
            try:
                return handler({"value": v})
            except Exception:
                raise e1

    @field_validator("*", mode="before")
    @classmethod
    def coerce_subclass(cls, v: Any, info) -> Any:
        """Recast parent classes into child classes"""
        if isinstance(v, BaseModel):
            annotation = cls.model_fields[info.field_name].annotation
            while hasattr(annotation, "__args__"):
                annotation = annotation.__args__[0]
            try:
                if issubclass(annotation, type(v)) and annotation is not type(v):
                    if v.__pydantic_extra__:
                        v = annotation(**{**v.__dict__, **v.__pydantic_extra__})
                    else:
                        v = annotation(**v.__dict__)
            except TypeError:
                # fine, annotation is a non-class type like a TypeVar
                pass
        return v

    @model_validator(mode="before")
    @classmethod
    def gather_extra_to_value(cls, v: Any, handler) -> Any:
        """
        For classes that don't allow extra fields and have a value slot,
        pack those extra kwargs into ``value``
        """
        if (
            cls.model_config["extra"] == "forbid"
            and "value" in cls.model_fields
            and isinstance(v, dict)
        ):
            extras = {key: val for key, val in v.items() if key not in cls.model_fields}
            if extras:
                for k in extras:
                    del v[k]
                if "value" in v:
                    v["value"].update(extras)
                else:
                    v["value"] = extras
        return v


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
            "../../hdmf_common/v1_5_0/namespace",
            "../../hdmf_experimental/v0_1_0/namespace",
        ],
        "name": "core",
    }
)


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
