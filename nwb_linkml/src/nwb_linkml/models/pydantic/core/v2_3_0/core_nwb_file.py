from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
from typing import Any, ClassVar, List, Literal, Dict, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator
import numpy as np
from ...core.v2_3_0.core_nwb_misc import (
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
from ...core.v2_3_0.core_nwb_ecephys import (
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
from ...core.v2_3_0.core_nwb_device import Device
from ...core.v2_3_0.core_nwb_base import (
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
from ...hdmf_common.v1_5_0.hdmf_common_sparse import CSRMatrix, CSRMatrixData
from ...hdmf_common.v1_5_0.hdmf_common_base import Data, Container, SimpleMultiContainer
from ...hdmf_common.v1_5_0.hdmf_common_table import (
    VectorData,
    VectorIndex,
    ElementIdentifiers,
    DynamicTableRegion,
    DynamicTable,
    AlignedDynamicTable,
)
from ...core.v2_3_0.core_nwb_epoch import TimeIntervals, TimeIntervalsTimeseries
from ...core.v2_3_0.core_nwb_ophys import (
    TwoPhotonSeries,
    RoiResponseSeries,
    DfOverF,
    Fluorescence,
    ImageSegmentation,
    PlaneSegmentation,
    PlaneSegmentationImageMask,
    PlaneSegmentationPixelMask,
    PlaneSegmentationVoxelMask,
    ImagingPlane,
    OpticalChannel,
    MotionCorrection,
    CorrectedImageStack,
)
from ...core.v2_3_0.core_nwb_image import (
    GrayscaleImage,
    RGBImage,
    RGBAImage,
    ImageSeries,
    ImageSeriesExternalFile,
    ImageMaskSeries,
    OpticalSeries,
    IndexSeries,
)
from ...core.v2_3_0.core_nwb_ogen import OptogeneticSeries, OptogeneticStimulusSite
from ...core.v2_3_0.core_nwb_icephys import (
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
from numpydantic import NDArray, Shape

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
    hdf5_path: Optional[str] = Field(None, description="The absolute path that this object is stored in an NWB file")
    object_id: Optional[str] = Field(None, description="Unique UUID for each object")


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


NUMPYDANTIC_VERSION = "1.2.1"

ModelType = TypeVar("ModelType", bound=Type[BaseModel])


def _get_name(item: BaseModel | dict, info: ValidationInfo):
    assert isinstance(item, (BaseModel, dict))
    name = info.field_name
    if isinstance(item, BaseModel):
        item.name = name
    else:
        item["name"] = name
    return item


Named = Annotated[ModelType, BeforeValidator(_get_name)]
linkml_meta = LinkMLMeta(
    {
        "annotations": {
            "is_namespace": {"tag": "is_namespace", "value": False},
            "namespace": {"tag": "namespace", "value": "core"},
        },
        "default_prefix": "core.nwb.file/",
        "id": "core.nwb.file",
        "imports": [
            "core.nwb.base",
            "../../hdmf_common/v1_5_0/namespace",
            "core.nwb.device",
            "core.nwb.ecephys",
            "core.nwb.icephys",
            "core.nwb.ogen",
            "core.nwb.ophys",
            "core.nwb.epoch",
            "core.nwb.misc",
            "core.nwb.language",
        ],
        "name": "core.nwb.file",
    }
)


class ScratchData(NWBData):
    """
    Any one-off datasets
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.file", "tree_root": True})

    name: str = Field(...)
    notes: Optional[str] = Field(None, description="""Any notes the user has about the dataset being stored""")


class NWBFile(NWBContainer):
    """
    An NWB:N file storing cellular-based neurophysiology data from a single experimental session.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.file", "tree_root": True})

    name: Literal["root"] = Field(
        "root", json_schema_extra={"linkml_meta": {"equals_string": "root", "ifabsent": "string(root)"}}
    )
    nwb_version: Optional[str] = Field(
        None,
        description="""File version string. Use semantic versioning, e.g. 1.2.1. This will be the name of the format with trailing major, minor and patch numbers.""",
    )
    file_create_date: NDArray[Shape["* num_modifications"], np.datetime64] = Field(
        ...,
        description="""A record of the date the file was created and of subsequent modifications. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted strings: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds. The file can be created after the experiment was run, so this may differ from the experiment start time. Each modification to the nwb file adds a new entry to the array.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_modifications"}]}}},
    )
    identifier: str = Field(
        ...,
        description="""A unique text identifier for the file. For example, concatenated lab name, file creation date/time and experimentalist, or a hash of these and/or other values. The goal is that the string should be unique to all other files.""",
    )
    session_description: str = Field(
        ..., description="""A description of the experimental session and data in the file."""
    )
    session_start_time: np.datetime64 = Field(
        ...,
        description="""Date and time of the experiment/session start. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted string: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds.""",
    )
    timestamps_reference_time: np.datetime64 = Field(
        ...,
        description="""Date and time corresponding to time zero of all timestamps. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted string: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds. All times stored in the file use this time as reference (i.e., time zero).""",
    )
    acquisition: Optional[List[Union[DynamicTable, NWBDataInterface]]] = Field(
        None,
        description="""Data streams recorded from the system, including ephys, ophys, tracking, etc. This group should be read-only after the experiment is completed and timestamps are corrected to a common timebase. The data stored here may be links to raw data stored in external NWB files. This will allow keeping bulky raw data out of the file while preserving the option of keeping some/all in the file. Acquired data includes tracking and experimental data streams (i.e., everything measured from the system). If bulky data is stored in the /acquisition group, the data can exist in a separate NWB file that is linked to by the file being used for processing and analysis.""",
        json_schema_extra={"linkml_meta": {"any_of": [{"range": "NWBDataInterface"}, {"range": "DynamicTable"}]}},
    )
    analysis: Optional[List[Union[DynamicTable, NWBContainer]]] = Field(
        None,
        description="""Lab-specific and custom scientific analysis of data. There is no defined format for the content of this group - the format is up to the individual user/lab. To facilitate sharing analysis data between labs, the contents here should be stored in standard types (e.g., neurodata_types) and appropriately documented. The file can store lab-specific and custom data analysis without restriction on its form or schema, reducing data formatting restrictions on end users. Such data should be placed in the analysis group. The analysis data should be documented so that it could be shared with other labs.""",
        json_schema_extra={"linkml_meta": {"any_of": [{"range": "NWBContainer"}, {"range": "DynamicTable"}]}},
    )
    scratch: Optional[List[Union[DynamicTable, NWBContainer]]] = Field(
        None,
        description="""A place to store one-off analysis results. Data placed here is not intended for sharing. By placing data here, users acknowledge that there is no guarantee that their data meets any standard.""",
        json_schema_extra={"linkml_meta": {"any_of": [{"range": "NWBContainer"}, {"range": "DynamicTable"}]}},
    )
    processing: Optional[List[ProcessingModule]] = Field(
        None,
        description="""The home for ProcessingModules. These modules perform intermediate analysis of data that is necessary to perform before scientific analysis. Examples include spike clustering, extracting position from tracking data, stitching together image slices. ProcessingModules can be large and express many data sets from relatively complex analysis (e.g., spike detection and clustering) or small, representing extraction of position information from tracking video, or even binary lick/no-lick decisions. Common software tools (e.g., klustakwik, MClust) are expected to read/write data here.  'Processing' refers to intermediate analysis of the acquired data to make it more amenable to scientific analysis.""",
        json_schema_extra={"linkml_meta": {"any_of": [{"range": "ProcessingModule"}]}},
    )
    stimulus: NWBFileStimulus = Field(
        ...,
        description="""Data pushed into the system (eg, video stimulus, sound, voltage, etc) and secondary representations of that data (eg, measurements of something used as a stimulus). This group should be made read-only after experiment complete and timestamps are corrected to common timebase. Stores both presented stimuli and stimulus templates, the latter in case the same stimulus is presented multiple times, or is pulled from an external stimulus library. Stimuli are here defined as any signal that is pushed into the system as part of the experiment (eg, sound, video, voltage, etc). Many different experiments can use the same stimuli, and stimuli can be re-used during an experiment. The stimulus group is organized so that one version of template stimuli can be stored and these be used multiple times. These templates can exist in the present file or can be linked to a remote library file.""",
    )
    general: NWBFileGeneral = Field(
        ...,
        description="""Experimental metadata, including protocol, notes and description of hardware device(s).  The metadata stored in this section should be used to describe the experiment. Metadata necessary for interpreting the data is stored with the data. General experimental metadata, including animal strain, experimental protocols, experimenter, devices, etc, are stored under 'general'. Core metadata (e.g., that required to interpret data fields) is stored with the data itself, and implicitly defined by the file specification (e.g., time is in seconds). The strategy used here for storing non-core metadata is to use free-form text fields, such as would appear in sentences or paragraphs from a Methods section. Metadata fields are text to enable them to be more general, for example to represent ranges instead of numerical values. Machine-readable metadata is stored as attributes to these free-form datasets. All entries in the below table are to be included when data is present. Unused groups (e.g., intracellular_ephys in an optophysiology experiment) should not be created unless there is data to store within them.""",
    )
    intervals: Optional[List[TimeIntervals]] = Field(
        None,
        description="""Experimental intervals, whether that be logically distinct sub-experiments having a particular scientific goal, trials (see trials subgroup) during an experiment, or epochs (see epochs subgroup) deriving from analysis of data.""",
        json_schema_extra={
            "linkml_meta": {
                "any_of": [
                    {"range": "TimeIntervals"},
                    {"range": "TimeIntervals"},
                    {"range": "TimeIntervals"},
                    {"range": "TimeIntervals"},
                ]
            }
        },
    )
    units: Optional[Units] = Field(None, description="""Data about sorted spike units.""")


class NWBFileStimulus(ConfiguredBaseModel):
    """
    Data pushed into the system (eg, video stimulus, sound, voltage, etc) and secondary representations of that data (eg, measurements of something used as a stimulus). This group should be made read-only after experiment complete and timestamps are corrected to common timebase. Stores both presented stimuli and stimulus templates, the latter in case the same stimulus is presented multiple times, or is pulled from an external stimulus library. Stimuli are here defined as any signal that is pushed into the system as part of the experiment (eg, sound, video, voltage, etc). Many different experiments can use the same stimuli, and stimuli can be re-used during an experiment. The stimulus group is organized so that one version of template stimuli can be stored and these be used multiple times. These templates can exist in the present file or can be linked to a remote library file.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.file"})

    name: Literal["stimulus"] = Field(
        "stimulus", json_schema_extra={"linkml_meta": {"equals_string": "stimulus", "ifabsent": "string(stimulus)"}}
    )
    presentation: Optional[List[TimeSeries]] = Field(
        None,
        description="""Stimuli presented during the experiment.""",
        json_schema_extra={"linkml_meta": {"any_of": [{"range": "TimeSeries"}]}},
    )
    templates: Optional[List[TimeSeries]] = Field(
        None,
        description="""Template stimuli. Timestamps in templates are based on stimulus design and are relative to the beginning of the stimulus. When templates are used, the stimulus instances must convert presentation times to the experiment`s time reference frame.""",
        json_schema_extra={"linkml_meta": {"any_of": [{"range": "TimeSeries"}]}},
    )


class NWBFileGeneral(ConfiguredBaseModel):
    """
    Experimental metadata, including protocol, notes and description of hardware device(s).  The metadata stored in this section should be used to describe the experiment. Metadata necessary for interpreting the data is stored with the data. General experimental metadata, including animal strain, experimental protocols, experimenter, devices, etc, are stored under 'general'. Core metadata (e.g., that required to interpret data fields) is stored with the data itself, and implicitly defined by the file specification (e.g., time is in seconds). The strategy used here for storing non-core metadata is to use free-form text fields, such as would appear in sentences or paragraphs from a Methods section. Metadata fields are text to enable them to be more general, for example to represent ranges instead of numerical values. Machine-readable metadata is stored as attributes to these free-form datasets. All entries in the below table are to be included when data is present. Unused groups (e.g., intracellular_ephys in an optophysiology experiment) should not be created unless there is data to store within them.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.file"})

    name: Literal["general"] = Field(
        "general", json_schema_extra={"linkml_meta": {"equals_string": "general", "ifabsent": "string(general)"}}
    )
    data_collection: Optional[str] = Field(None, description="""Notes about data collection and analysis.""")
    experiment_description: Optional[str] = Field(None, description="""General description of the experiment.""")
    experimenter: Optional[NDArray[Shape["* num_experimenters"], str]] = Field(
        None,
        description="""Name of person(s) who performed the experiment. Can also specify roles of different people involved.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_experimenters"}]}}},
    )
    institution: Optional[str] = Field(None, description="""Institution(s) where experiment was performed.""")
    keywords: Optional[NDArray[Shape["* num_keywords"], str]] = Field(
        None,
        description="""Terms to search over.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_keywords"}]}}},
    )
    lab: Optional[str] = Field(None, description="""Laboratory where experiment was performed.""")
    notes: Optional[str] = Field(None, description="""Notes about the experiment.""")
    pharmacology: Optional[str] = Field(
        None,
        description="""Description of drugs used, including how and when they were administered. Anesthesia(s), painkiller(s), etc., plus dosage, concentration, etc.""",
    )
    protocol: Optional[str] = Field(
        None, description="""Experimental protocol, if applicable. e.g., include IACUC protocol number."""
    )
    related_publications: Optional[NDArray[Shape["* num_publications"], str]] = Field(
        None,
        description="""Publication information. PMID, DOI, URL, etc.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_publications"}]}}},
    )
    session_id: Optional[str] = Field(None, description="""Lab-specific ID for the session.""")
    slices: Optional[str] = Field(
        None,
        description="""Description of slices, including information about preparation thickness, orientation, temperature, and bath solution.""",
    )
    source_script: Optional[NWBFileGeneralSourceScript] = Field(
        None, description="""Script file or link to public source code used to create this NWB file."""
    )
    stimulus: Optional[str] = Field(
        None, description="""Notes about stimuli, such as how and where they were presented."""
    )
    surgery: Optional[str] = Field(
        None,
        description="""Narrative description about surgery/surgeries, including date(s) and who performed surgery.""",
    )
    virus: Optional[str] = Field(
        None,
        description="""Information about virus(es) used in experiments, including virus ID, source, date made, injection location, volume, etc.""",
    )
    lab_meta_data: Optional[List[LabMetaData]] = Field(
        None,
        description="""Place-holder than can be extended so that lab-specific meta-data can be placed in /general.""",
    )
    devices: Optional[List[Device]] = Field(
        None,
        description="""Description of hardware devices used during experiment, e.g., monitors, ADC boards, microscopes, etc.""",
        json_schema_extra={"linkml_meta": {"any_of": [{"range": "Device"}]}},
    )
    subject: Optional[Subject] = Field(
        None, description="""Information about the animal or person from which the data was measured."""
    )
    extracellular_ephys: Optional[NWBFileGeneralExtracellularEphys] = Field(
        None, description="""Metadata related to extracellular electrophysiology."""
    )
    intracellular_ephys: Optional[NWBFileGeneralIntracellularEphys] = Field(
        None, description="""Metadata related to intracellular electrophysiology."""
    )
    optogenetics: Optional[List[OptogeneticStimulusSite]] = Field(
        None,
        description="""Metadata describing optogenetic stimuluation.""",
        json_schema_extra={"linkml_meta": {"any_of": [{"range": "OptogeneticStimulusSite"}]}},
    )
    optophysiology: Optional[List[ImagingPlane]] = Field(
        None,
        description="""Metadata related to optophysiology.""",
        json_schema_extra={"linkml_meta": {"any_of": [{"range": "ImagingPlane"}]}},
    )


class NWBFileGeneralSourceScript(ConfiguredBaseModel):
    """
    Script file or link to public source code used to create this NWB file.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.file"})

    name: Literal["source_script"] = Field(
        "source_script",
        json_schema_extra={"linkml_meta": {"equals_string": "source_script", "ifabsent": "string(source_script)"}},
    )
    file_name: Optional[str] = Field(None, description="""Name of script file.""")
    value: str = Field(...)


class NWBFileGeneralExtracellularEphys(ConfiguredBaseModel):
    """
    Metadata related to extracellular electrophysiology.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.file"})

    name: Literal["extracellular_ephys"] = Field(
        "extracellular_ephys",
        json_schema_extra={
            "linkml_meta": {"equals_string": "extracellular_ephys", "ifabsent": "string(extracellular_ephys)"}
        },
    )
    electrode_group: Optional[List[ElectrodeGroup]] = Field(None, description="""Physical group of electrodes.""")
    electrodes: Optional[NWBFileGeneralExtracellularEphysElectrodes] = Field(
        None, description="""A table of all electrodes (i.e. channels) used for recording."""
    )


class NWBFileGeneralExtracellularEphysElectrodes(DynamicTable):
    """
    A table of all electrodes (i.e. channels) used for recording.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.file"})

    name: Literal["electrodes"] = Field(
        "electrodes",
        json_schema_extra={"linkml_meta": {"equals_string": "electrodes", "ifabsent": "string(electrodes)"}},
    )
    x: NDArray[Any, np.float32] = Field(
        ...,
        description="""x coordinate of the channel location in the brain (+x is posterior).""",
        json_schema_extra={
            "linkml_meta": {"array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}}
        },
    )
    y: NDArray[Any, np.float32] = Field(
        ...,
        description="""y coordinate of the channel location in the brain (+y is inferior).""",
        json_schema_extra={
            "linkml_meta": {"array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}}
        },
    )
    z: NDArray[Any, np.float32] = Field(
        ...,
        description="""z coordinate of the channel location in the brain (+z is right).""",
        json_schema_extra={
            "linkml_meta": {"array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}}
        },
    )
    imp: NDArray[Any, np.float32] = Field(
        ...,
        description="""Impedance of the channel, in ohms.""",
        json_schema_extra={
            "linkml_meta": {"array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}}
        },
    )
    location: NDArray[Any, str] = Field(
        ...,
        description="""Location of the electrode (channel). Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""",
        json_schema_extra={
            "linkml_meta": {"array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}}
        },
    )
    filtering: NDArray[Any, np.float32] = Field(
        ...,
        description="""Description of hardware filtering, including the filter name and frequency cutoffs.""",
        json_schema_extra={
            "linkml_meta": {"array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}}
        },
    )
    group: List[ElectrodeGroup] = Field(
        ..., description="""Reference to the ElectrodeGroup this electrode is a part of."""
    )
    group_name: NDArray[Any, str] = Field(
        ...,
        description="""Name of the ElectrodeGroup this electrode is a part of.""",
        json_schema_extra={
            "linkml_meta": {"array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}}
        },
    )
    rel_x: Optional[NDArray[Any, np.float32]] = Field(
        None,
        description="""x coordinate in electrode group""",
        json_schema_extra={
            "linkml_meta": {"array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}}
        },
    )
    rel_y: Optional[NDArray[Any, np.float32]] = Field(
        None,
        description="""y coordinate in electrode group""",
        json_schema_extra={
            "linkml_meta": {"array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}}
        },
    )
    rel_z: Optional[NDArray[Any, np.float32]] = Field(
        None,
        description="""z coordinate in electrode group""",
        json_schema_extra={
            "linkml_meta": {"array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}}
        },
    )
    reference: Optional[NDArray[Any, str]] = Field(
        None,
        description="""Description of the reference used for this electrode.""",
        json_schema_extra={
            "linkml_meta": {"array": {"maximum_number_dimensions": False, "minimum_number_dimensions": 1}}
        },
    )
    colnames: Optional[str] = Field(
        None,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: NDArray[Shape["* num_rows"], int] = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )
    vector_data: Optional[List[VectorData]] = Field(
        None, description="""Vector columns, including index columns, of this dynamic table."""
    )


class NWBFileGeneralIntracellularEphys(ConfiguredBaseModel):
    """
    Metadata related to intracellular electrophysiology.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.file"})

    name: Literal["intracellular_ephys"] = Field(
        "intracellular_ephys",
        json_schema_extra={
            "linkml_meta": {"equals_string": "intracellular_ephys", "ifabsent": "string(intracellular_ephys)"}
        },
    )
    filtering: Optional[str] = Field(
        None,
        description="""Description of filtering used. Includes filtering type and parameters, frequency fall-off, etc. If this changes between TimeSeries, filter description should be stored as a text attribute for each TimeSeries.""",
    )
    intracellular_electrode: Optional[List[IntracellularElectrode]] = Field(
        None, description="""An intracellular electrode."""
    )
    sweep_table: Optional[SweepTable] = Field(
        None, description="""The table which groups different PatchClampSeries together."""
    )


class LabMetaData(NWBContainer):
    """
    Lab-specific meta-data.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.file", "tree_root": True})

    name: str = Field(...)


class Subject(NWBContainer):
    """
    Information about the animal or person from which the data was measured.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({"from_schema": "core.nwb.file", "tree_root": True})

    name: str = Field(...)
    age: Optional[str] = Field(None, description="""Age of subject. Can be supplied instead of 'date_of_birth'.""")
    date_of_birth: Optional[np.datetime64] = Field(
        None, description="""Date of birth of subject. Can be supplied instead of 'age'."""
    )
    description: Optional[str] = Field(
        None, description="""Description of subject and where subject came from (e.g., breeder, if animal)."""
    )
    genotype: Optional[str] = Field(None, description="""Genetic strain. If absent, assume Wild Type (WT).""")
    sex: Optional[str] = Field(None, description="""Gender of subject.""")
    species: Optional[str] = Field(None, description="""Species of subject.""")
    strain: Optional[str] = Field(None, description="""Strain of subject.""")
    subject_id: Optional[str] = Field(
        None, description="""ID of animal/person used/participating in experiment (lab convention)."""
    )
    weight: Optional[str] = Field(
        None, description="""Weight at time of experiment, at time of surgery and at other important times."""
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ScratchData.model_rebuild()
NWBFile.model_rebuild()
NWBFileStimulus.model_rebuild()
NWBFileGeneral.model_rebuild()
NWBFileGeneralSourceScript.model_rebuild()
NWBFileGeneralExtracellularEphys.model_rebuild()
NWBFileGeneralExtracellularEphysElectrodes.model_rebuild()
NWBFileGeneralIntracellularEphys.model_rebuild()
LabMetaData.model_rebuild()
Subject.model_rebuild()
