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


from .core_nwb_file import (
    LabMetaData,
    ScratchData,
    Subject
)

from .core_nwb_misc import (
    Units
)

from .core_nwb_base import (
    TimeSeries,
    Images,
    NWBContainer,
    NWBDataInterface,
    ProcessingModule
)

from .core_nwb_icephys import (
    RepetitionsTable,
    ExperimentalConditionsTable,
    IntracellularElectrode,
    SimultaneousRecordingsTable,
    SweepTable,
    SequentialRecordingsTable,
    IntracellularRecordingsTable
)

from .core_nwb_epoch import (
    TimeIntervals
)

from .core_nwb_ogen import (
    OptogeneticStimulusSite
)

from .core_nwb_device import (
    Device
)

from .core_nwb_ecephys import (
    ElectrodeGroup
)

from .hdmf_common_table import (
    DynamicTable
)

from .core_nwb_ophys import (
    ImagingPlane
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


class NWBFileFileCreateDate(ConfiguredBaseModel):
    """
    A record of the date the file was created and of subsequent modifications. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted strings: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds. The file can be created after the experiment was run, so this may differ from the experiment start time. Each modification to the nwb file adds a new entry to the array.
    """
    file_create_date: List[date] = Field(default_factory=list, description="""A record of the date the file was created and of subsequent modifications. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted strings: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds. The file can be created after the experiment was run, so this may differ from the experiment start time. Each modification to the nwb file adds a new entry to the array.""")
    

class NWBFileAcquisition(ConfiguredBaseModel):
    """
    Data streams recorded from the system, including ephys, ophys, tracking, etc. This group should be read-only after the experiment is completed and timestamps are corrected to a common timebase. The data stored here may be links to raw data stored in external NWB files. This will allow keeping bulky raw data out of the file while preserving the option of keeping some/all in the file. Acquired data includes tracking and experimental data streams (i.e., everything measured from the system). If bulky data is stored in the /acquisition group, the data can exist in a separate NWB file that is linked to by the file being used for processing and analysis.
    """
    NWBDataInterface: Optional[List[NWBDataInterface]] = Field(default_factory=list, description="""Acquired, raw data.""")
    DynamicTable: Optional[List[DynamicTable]] = Field(default_factory=list, description="""Tabular data that is relevant to acquisition""")
    

class NWBFileAnalysis(ConfiguredBaseModel):
    """
    Lab-specific and custom scientific analysis of data. There is no defined format for the content of this group - the format is up to the individual user/lab. To facilitate sharing analysis data between labs, the contents here should be stored in standard types (e.g., neurodata_types) and appropriately documented. The file can store lab-specific and custom data analysis without restriction on its form or schema, reducing data formatting restrictions on end users. Such data should be placed in the analysis group. The analysis data should be documented so that it could be shared with other labs.
    """
    NWBContainer: Optional[List[NWBContainer]] = Field(default_factory=list, description="""Custom analysis results.""")
    DynamicTable: Optional[List[DynamicTable]] = Field(default_factory=list, description="""Tabular data that is relevant to data stored in analysis""")
    

class NWBFileScratch(ConfiguredBaseModel):
    """
    A place to store one-off analysis results. Data placed here is not intended for sharing. By placing data here, users acknowledge that there is no guarantee that their data meets any standard.
    """
    ScratchData: Optional[List[ScratchData]] = Field(default_factory=list, description="""Any one-off datasets""")
    NWBContainer: Optional[List[NWBContainer]] = Field(default_factory=list, description="""Any one-off containers""")
    DynamicTable: Optional[List[DynamicTable]] = Field(default_factory=list, description="""Any one-off tables""")
    

class NWBFileProcessing(ConfiguredBaseModel):
    """
    The home for ProcessingModules. These modules perform intermediate analysis of data that is necessary to perform before scientific analysis. Examples include spike clustering, extracting position from tracking data, stitching together image slices. ProcessingModules can be large and express many data sets from relatively complex analysis (e.g., spike detection and clustering) or small, representing extraction of position information from tracking video, or even binary lick/no-lick decisions. Common software tools (e.g., klustakwik, MClust) are expected to read/write data here.  'Processing' refers to intermediate analysis of the acquired data to make it more amenable to scientific analysis.
    """
    ProcessingModule: Optional[List[ProcessingModule]] = Field(default_factory=list, description="""Intermediate analysis of acquired data.""")
    

class NWBFileStimulus(ConfiguredBaseModel):
    """
    Data pushed into the system (eg, video stimulus, sound, voltage, etc) and secondary representations of that data (eg, measurements of something used as a stimulus). This group should be made read-only after experiment complete and timestamps are corrected to common timebase. Stores both presented stimuli and stimulus templates, the latter in case the same stimulus is presented multiple times, or is pulled from an external stimulus library. Stimuli are here defined as any signal that is pushed into the system as part of the experiment (eg, sound, video, voltage, etc). Many different experiments can use the same stimuli, and stimuli can be re-used during an experiment. The stimulus group is organized so that one version of template stimuli can be stored and these be used multiple times. These templates can exist in the present file or can be linked to a remote library file.
    """
    presentation: NWBFileStimulusPresentation = Field(..., description="""Stimuli presented during the experiment.""")
    templates: NWBFileStimulusTemplates = Field(..., description="""Template stimuli. Timestamps in templates are based on stimulus design and are relative to the beginning of the stimulus. When templates are used, the stimulus instances must convert presentation times to the experiment`s time reference frame.""")
    

class NWBFileStimulusPresentation(ConfiguredBaseModel):
    """
    Stimuli presented during the experiment.
    """
    TimeSeries: Optional[List[TimeSeries]] = Field(default_factory=list, description="""TimeSeries objects containing data of presented stimuli.""")
    

class NWBFileStimulusTemplates(ConfiguredBaseModel):
    """
    Template stimuli. Timestamps in templates are based on stimulus design and are relative to the beginning of the stimulus. When templates are used, the stimulus instances must convert presentation times to the experiment`s time reference frame.
    """
    TimeSeries: Optional[List[TimeSeries]] = Field(default_factory=list, description="""TimeSeries objects containing template data of presented stimuli.""")
    Images: Optional[List[Images]] = Field(default_factory=list, description="""Images objects containing images of presented stimuli.""")
    

class NWBFileGeneral(ConfiguredBaseModel):
    """
    Experimental metadata, including protocol, notes and description of hardware device(s).  The metadata stored in this section should be used to describe the experiment. Metadata necessary for interpreting the data is stored with the data. General experimental metadata, including animal strain, experimental protocols, experimenter, devices, etc, are stored under 'general'. Core metadata (e.g., that required to interpret data fields) is stored with the data itself, and implicitly defined by the file specification (e.g., time is in seconds). The strategy used here for storing non-core metadata is to use free-form text fields, such as would appear in sentences or paragraphs from a Methods section. Metadata fields are text to enable them to be more general, for example to represent ranges instead of numerical values. Machine-readable metadata is stored as attributes to these free-form datasets. All entries in the below table are to be included when data is present. Unused groups (e.g., intracellular_ephys in an optophysiology experiment) should not be created unless there is data to store within them.
    """
    data_collection: Optional[str] = Field(None, description="""Notes about data collection and analysis.""")
    experiment_description: Optional[str] = Field(None, description="""General description of the experiment.""")
    experimenter: Optional[NWBFileGeneralExperimenter] = Field(None, description="""Name of person(s) who performed the experiment. Can also specify roles of different people involved.""")
    institution: Optional[str] = Field(None, description="""Institution(s) where experiment was performed.""")
    keywords: Optional[NWBFileGeneralKeywords] = Field(None, description="""Terms to search over.""")
    lab: Optional[str] = Field(None, description="""Laboratory where experiment was performed.""")
    notes: Optional[str] = Field(None, description="""Notes about the experiment.""")
    pharmacology: Optional[str] = Field(None, description="""Description of drugs used, including how and when they were administered. Anesthesia(s), painkiller(s), etc., plus dosage, concentration, etc.""")
    protocol: Optional[str] = Field(None, description="""Experimental protocol, if applicable. e.g., include IACUC protocol number.""")
    related_publications: Optional[NWBFileGeneralRelatedPublications] = Field(None, description="""Publication information. PMID, DOI, URL, etc.""")
    session_id: Optional[str] = Field(None, description="""Lab-specific ID for the session.""")
    slices: Optional[str] = Field(None, description="""Description of slices, including information about preparation thickness, orientation, temperature, and bath solution.""")
    source_script: Optional[NWBFileGeneralSourceScript] = Field(None, description="""Script file or link to public source code used to create this NWB file.""")
    stimulus: Optional[str] = Field(None, description="""Notes about stimuli, such as how and where they were presented.""")
    surgery: Optional[str] = Field(None, description="""Narrative description about surgery/surgeries, including date(s) and who performed surgery.""")
    virus: Optional[str] = Field(None, description="""Information about virus(es) used in experiments, including virus ID, source, date made, injection location, volume, etc.""")
    LabMetaData: Optional[List[LabMetaData]] = Field(default_factory=list, description="""Place-holder than can be extended so that lab-specific meta-data can be placed in /general.""")
    devices: Optional[NWBFileGeneralDevices] = Field(None, description="""Description of hardware devices used during experiment, e.g., monitors, ADC boards, microscopes, etc.""")
    subject: Optional[NWBFileGeneralSubject] = Field(None, description="""Information about the animal or person from which the data was measured.""")
    extracellular_ephys: Optional[NWBFileGeneralExtracellularEphys] = Field(None, description="""Metadata related to extracellular electrophysiology.""")
    intracellular_ephys: Optional[NWBFileGeneralIntracellularEphys] = Field(None, description="""Metadata related to intracellular electrophysiology.""")
    optogenetics: Optional[NWBFileGeneralOptogenetics] = Field(None, description="""Metadata describing optogenetic stimuluation.""")
    optophysiology: Optional[NWBFileGeneralOptophysiology] = Field(None, description="""Metadata related to optophysiology.""")
    

class NWBFileGeneralExperimenter(ConfiguredBaseModel):
    """
    Name of person(s) who performed the experiment. Can also specify roles of different people involved.
    """
    experimenter: Optional[List[str]] = Field(default_factory=list, description="""Name of person(s) who performed the experiment. Can also specify roles of different people involved.""")
    

class NWBFileGeneralKeywords(ConfiguredBaseModel):
    """
    Terms to search over.
    """
    keywords: Optional[List[str]] = Field(default_factory=list, description="""Terms to search over.""")
    

class NWBFileGeneralRelatedPublications(ConfiguredBaseModel):
    """
    Publication information. PMID, DOI, URL, etc.
    """
    related_publications: Optional[List[str]] = Field(default_factory=list, description="""Publication information. PMID, DOI, URL, etc.""")
    

class NWBFileGeneralSourceScript(ConfiguredBaseModel):
    """
    Script file or link to public source code used to create this NWB file.
    """
    file_name: Optional[str] = Field(None, description="""Name of script file.""")
    

class NWBFileGeneralDevices(ConfiguredBaseModel):
    """
    Description of hardware devices used during experiment, e.g., monitors, ADC boards, microscopes, etc.
    """
    Device: Optional[List[Device]] = Field(default_factory=list, description="""Data acquisition devices.""")
    

class NWBFileGeneralSubject(Subject):
    """
    Information about the animal or person from which the data was measured.
    """
    age: Optional[SubjectAge] = Field(None, description="""Age of subject. Can be supplied instead of 'date_of_birth'.""")
    date_of_birth: Optional[date] = Field(None, description="""Date of birth of subject. Can be supplied instead of 'age'.""")
    description: Optional[str] = Field(None, description="""Description of subject and where subject came from (e.g., breeder, if animal).""")
    genotype: Optional[str] = Field(None, description="""Genetic strain. If absent, assume Wild Type (WT).""")
    sex: Optional[str] = Field(None, description="""Gender of subject.""")
    species: Optional[str] = Field(None, description="""Species of subject.""")
    strain: Optional[str] = Field(None, description="""Strain of subject.""")
    subject_id: Optional[str] = Field(None, description="""ID of animal/person used/participating in experiment (lab convention).""")
    weight: Optional[str] = Field(None, description="""Weight at time of experiment, at time of surgery and at other important times.""")
    

class NWBFileGeneralExtracellularEphys(ConfiguredBaseModel):
    """
    Metadata related to extracellular electrophysiology.
    """
    ElectrodeGroup: Optional[List[ElectrodeGroup]] = Field(default_factory=list, description="""Physical group of electrodes.""")
    electrodes: Optional[NWBFileGeneralExtracellularEphysElectrodes] = Field(None, description="""A table of all electrodes (i.e. channels) used for recording.""")
    

class NWBFileGeneralExtracellularEphysElectrodes(DynamicTable):
    """
    A table of all electrodes (i.e. channels) used for recording.
    """
    x: Optional[List[float]] = Field(default_factory=list, description="""x coordinate of the channel location in the brain (+x is posterior).""")
    y: Optional[List[float]] = Field(default_factory=list, description="""y coordinate of the channel location in the brain (+y is inferior).""")
    z: Optional[List[float]] = Field(default_factory=list, description="""z coordinate of the channel location in the brain (+z is right).""")
    imp: Optional[List[float]] = Field(default_factory=list, description="""Impedance of the channel, in ohms.""")
    location: Optional[List[str]] = Field(default_factory=list, description="""Location of the electrode (channel). Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""")
    filtering: Optional[List[str]] = Field(default_factory=list, description="""Description of hardware filtering, including the filter name and frequency cutoffs.""")
    group: Optional[List[ElectrodeGroup]] = Field(default_factory=list, description="""Reference to the ElectrodeGroup this electrode is a part of.""")
    group_name: Optional[List[str]] = Field(default_factory=list, description="""Name of the ElectrodeGroup this electrode is a part of.""")
    rel_x: Optional[List[float]] = Field(default_factory=list, description="""x coordinate in electrode group""")
    rel_y: Optional[List[float]] = Field(default_factory=list, description="""y coordinate in electrode group""")
    rel_z: Optional[List[float]] = Field(default_factory=list, description="""z coordinate in electrode group""")
    reference: Optional[List[str]] = Field(default_factory=list, description="""Description of the reference electrode and/or reference scheme used for this electrode, e.g., \"stainless steel skull screw\" or \"online common average referencing\".""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class NWBFileGeneralIntracellularEphys(ConfiguredBaseModel):
    """
    Metadata related to intracellular electrophysiology.
    """
    filtering: Optional[str] = Field(None, description="""[DEPRECATED] Use IntracellularElectrode.filtering instead. Description of filtering used. Includes filtering type and parameters, frequency fall-off, etc. If this changes between TimeSeries, filter description should be stored as a text attribute for each TimeSeries.""")
    IntracellularElectrode: Optional[List[IntracellularElectrode]] = Field(default_factory=list, description="""An intracellular electrode.""")
    sweep_table: Optional[NWBFileGeneralIntracellularEphysSweepTable] = Field(None, description="""[DEPRECATED] Table used to group different PatchClampSeries. SweepTable is being replaced by IntracellularRecordingsTable and SimultaneousRecordingsTable tables. Additional SequentialRecordingsTable, RepetitionsTable and ExperimentalConditions tables provide enhanced support for experiment metadata.""")
    intracellular_recordings: Optional[NWBFileGeneralIntracellularEphysIntracellularRecordings] = Field(None, description="""A table to group together a stimulus and response from a single electrode and a single simultaneous recording. Each row in the table represents a single recording consisting typically of a stimulus and a corresponding response. In some cases, however, only a stimulus or a response are recorded as as part of an experiment. In this case both, the stimulus and response will point to the same TimeSeries while the idx_start and count of the invalid column will be set to -1, thus, indicating that no values have been recorded for the stimulus or response, respectively. Note, a recording MUST contain at least a stimulus or a response. Typically the stimulus and response are PatchClampSeries. However, the use of AD/DA channels that are not associated to an electrode is also common in intracellular electrophysiology, in which case other TimeSeries may be used.""")
    simultaneous_recordings: Optional[NWBFileGeneralIntracellularEphysSimultaneousRecordings] = Field(None, description="""A table for grouping different intracellular recordings from the IntracellularRecordingsTable table together that were recorded simultaneously from different electrodes""")
    sequential_recordings: Optional[NWBFileGeneralIntracellularEphysSequentialRecordings] = Field(None, description="""A table for grouping different sequential recordings from the SimultaneousRecordingsTable table together. This is typically used to group together sequential recordings where the a sequence of stimuli of the same type with varying parameters have been presented in a sequence.""")
    repetitions: Optional[NWBFileGeneralIntracellularEphysRepetitions] = Field(None, description="""A table for grouping different sequential intracellular recordings together. With each SequentialRecording typically representing a particular type of stimulus, the RepetitionsTable table is typically used to group sets of stimuli applied in sequence.""")
    experimental_conditions: Optional[NWBFileGeneralIntracellularEphysExperimentalConditions] = Field(None, description="""A table for grouping different intracellular recording repetitions together that belong to the same experimental experimental_conditions.""")
    

class NWBFileGeneralIntracellularEphysSweepTable(SweepTable):
    """
    [DEPRECATED] Table used to group different PatchClampSeries. SweepTable is being replaced by IntracellularRecordingsTable and SimultaneousRecordingsTable tables. Additional SequentialRecordingsTable, RepetitionsTable and ExperimentalConditions tables provide enhanced support for experiment metadata.
    """
    sweep_number: Optional[List[int]] = Field(default_factory=list, description="""Sweep number of the PatchClampSeries in that row.""")
    series: Optional[List[PatchClampSeries]] = Field(default_factory=list, description="""The PatchClampSeries with the sweep number in that row.""")
    series_index: SweepTableSeriesIndex = Field(..., description="""Index for series.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class NWBFileGeneralIntracellularEphysIntracellularRecordings(IntracellularRecordingsTable):
    """
    A table to group together a stimulus and response from a single electrode and a single simultaneous recording. Each row in the table represents a single recording consisting typically of a stimulus and a corresponding response. In some cases, however, only a stimulus or a response are recorded as as part of an experiment. In this case both, the stimulus and response will point to the same TimeSeries while the idx_start and count of the invalid column will be set to -1, thus, indicating that no values have been recorded for the stimulus or response, respectively. Note, a recording MUST contain at least a stimulus or a response. Typically the stimulus and response are PatchClampSeries. However, the use of AD/DA channels that are not associated to an electrode is also common in intracellular electrophysiology, in which case other TimeSeries may be used.
    """
    description: Optional[str] = Field(None, description="""Description of the contents of this table. Inherited from AlignedDynamicTable and overwritten here to fix the value of the attribute.""")
    electrodes: IntracellularRecordingsTableElectrodes = Field(..., description="""Table for storing intracellular electrode related metadata.""")
    stimuli: IntracellularRecordingsTableStimuli = Field(..., description="""Table for storing intracellular stimulus related metadata.""")
    responses: IntracellularRecordingsTableResponses = Field(..., description="""Table for storing intracellular response related metadata.""")
    categories: Optional[str] = Field(None, description="""The names of the categories in this AlignedDynamicTable. Each category is represented by one DynamicTable stored in the parent group. This attribute should be used to specify an order of categories and the category names must match the names of the corresponding DynamicTable in the group.""")
    DynamicTable: Optional[List[DynamicTable]] = Field(default_factory=list, description="""A DynamicTable representing a particular category for columns in the AlignedDynamicTable parent container. The table MUST be aligned with (i.e., have the same number of rows) as all other DynamicTables stored in the AlignedDynamicTable parent container. The name of the category is given by the name of the DynamicTable and its description by the description attribute of the DynamicTable.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class NWBFileGeneralIntracellularEphysSimultaneousRecordings(SimultaneousRecordingsTable):
    """
    A table for grouping different intracellular recordings from the IntracellularRecordingsTable table together that were recorded simultaneously from different electrodes
    """
    recordings: SimultaneousRecordingsTableRecordings = Field(..., description="""A reference to one or more rows in the IntracellularRecordingsTable table.""")
    recordings_index: SimultaneousRecordingsTableRecordingsIndex = Field(..., description="""Index dataset for the recordings column.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class NWBFileGeneralIntracellularEphysSequentialRecordings(SequentialRecordingsTable):
    """
    A table for grouping different sequential recordings from the SimultaneousRecordingsTable table together. This is typically used to group together sequential recordings where the a sequence of stimuli of the same type with varying parameters have been presented in a sequence.
    """
    simultaneous_recordings: SequentialRecordingsTableSimultaneousRecordings = Field(..., description="""A reference to one or more rows in the SimultaneousRecordingsTable table.""")
    simultaneous_recordings_index: SequentialRecordingsTableSimultaneousRecordingsIndex = Field(..., description="""Index dataset for the simultaneous_recordings column.""")
    stimulus_type: Optional[List[str]] = Field(default_factory=list, description="""The type of stimulus used for the sequential recording.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class NWBFileGeneralIntracellularEphysRepetitions(RepetitionsTable):
    """
    A table for grouping different sequential intracellular recordings together. With each SequentialRecording typically representing a particular type of stimulus, the RepetitionsTable table is typically used to group sets of stimuli applied in sequence.
    """
    sequential_recordings: RepetitionsTableSequentialRecordings = Field(..., description="""A reference to one or more rows in the SequentialRecordingsTable table.""")
    sequential_recordings_index: RepetitionsTableSequentialRecordingsIndex = Field(..., description="""Index dataset for the sequential_recordings column.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class NWBFileGeneralIntracellularEphysExperimentalConditions(ExperimentalConditionsTable):
    """
    A table for grouping different intracellular recording repetitions together that belong to the same experimental experimental_conditions.
    """
    repetitions: ExperimentalConditionsTableRepetitions = Field(..., description="""A reference to one or more rows in the RepetitionsTable table.""")
    repetitions_index: ExperimentalConditionsTableRepetitionsIndex = Field(..., description="""Index dataset for the repetitions column.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class NWBFileGeneralOptogenetics(ConfiguredBaseModel):
    """
    Metadata describing optogenetic stimuluation.
    """
    OptogeneticStimulusSite: Optional[List[OptogeneticStimulusSite]] = Field(default_factory=list, description="""An optogenetic stimulation site.""")
    

class NWBFileGeneralOptophysiology(ConfiguredBaseModel):
    """
    Metadata related to optophysiology.
    """
    ImagingPlane: Optional[List[ImagingPlane]] = Field(default_factory=list, description="""An imaging plane.""")
    

class NWBFileIntervals(ConfiguredBaseModel):
    """
    Experimental intervals, whether that be logically distinct sub-experiments having a particular scientific goal, trials (see trials subgroup) during an experiment, or epochs (see epochs subgroup) deriving from analysis of data.
    """
    epochs: Optional[NWBFileIntervalsEpochs] = Field(None, description="""Divisions in time marking experimental stages or sub-divisions of a single recording session.""")
    trials: Optional[NWBFileIntervalsTrials] = Field(None, description="""Repeated experimental events that have a logical grouping.""")
    invalid_times: Optional[NWBFileIntervalsInvalidTimes] = Field(None, description="""Time intervals that should be removed from analysis.""")
    TimeIntervals: Optional[List[TimeIntervals]] = Field(default_factory=list, description="""Optional additional table(s) for describing other experimental time intervals.""")
    

class NWBFileIntervalsEpochs(TimeIntervals):
    """
    Divisions in time marking experimental stages or sub-divisions of a single recording session.
    """
    start_time: Optional[List[float]] = Field(default_factory=list, description="""Start time of epoch, in seconds.""")
    stop_time: Optional[List[float]] = Field(default_factory=list, description="""Stop time of epoch, in seconds.""")
    tags: Optional[List[str]] = Field(default_factory=list, description="""User-defined tags that identify or categorize events.""")
    tags_index: Optional[TimeIntervalsTagsIndex] = Field(None, description="""Index for tags.""")
    timeseries: Optional[TimeIntervalsTimeseries] = Field(None, description="""An index into a TimeSeries object.""")
    timeseries_index: Optional[TimeIntervalsTimeseriesIndex] = Field(None, description="""Index for timeseries.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class NWBFileIntervalsTrials(TimeIntervals):
    """
    Repeated experimental events that have a logical grouping.
    """
    start_time: Optional[List[float]] = Field(default_factory=list, description="""Start time of epoch, in seconds.""")
    stop_time: Optional[List[float]] = Field(default_factory=list, description="""Stop time of epoch, in seconds.""")
    tags: Optional[List[str]] = Field(default_factory=list, description="""User-defined tags that identify or categorize events.""")
    tags_index: Optional[TimeIntervalsTagsIndex] = Field(None, description="""Index for tags.""")
    timeseries: Optional[TimeIntervalsTimeseries] = Field(None, description="""An index into a TimeSeries object.""")
    timeseries_index: Optional[TimeIntervalsTimeseriesIndex] = Field(None, description="""Index for timeseries.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class NWBFileIntervalsInvalidTimes(TimeIntervals):
    """
    Time intervals that should be removed from analysis.
    """
    start_time: Optional[List[float]] = Field(default_factory=list, description="""Start time of epoch, in seconds.""")
    stop_time: Optional[List[float]] = Field(default_factory=list, description="""Stop time of epoch, in seconds.""")
    tags: Optional[List[str]] = Field(default_factory=list, description="""User-defined tags that identify or categorize events.""")
    tags_index: Optional[TimeIntervalsTagsIndex] = Field(None, description="""Index for tags.""")
    timeseries: Optional[TimeIntervalsTimeseries] = Field(None, description="""An index into a TimeSeries object.""")
    timeseries_index: Optional[TimeIntervalsTimeseriesIndex] = Field(None, description="""Index for timeseries.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class NWBFileUnits(Units):
    """
    Data about sorted spike units.
    """
    spike_times_index: Optional[UnitsSpikeTimesIndex] = Field(None, description="""Index into the spike_times dataset.""")
    spike_times: Optional[UnitsSpikeTimes] = Field(None, description="""Spike times for each unit in seconds.""")
    obs_intervals_index: Optional[UnitsObsIntervalsIndex] = Field(None, description="""Index into the obs_intervals dataset.""")
    obs_intervals: Optional[UnitsObsIntervals] = Field(None, description="""Observation intervals for each unit.""")
    electrodes_index: Optional[UnitsElectrodesIndex] = Field(None, description="""Index into electrodes.""")
    electrodes: Optional[UnitsElectrodes] = Field(None, description="""Electrode that each spike unit came from, specified using a DynamicTableRegion.""")
    electrode_group: Optional[List[ElectrodeGroup]] = Field(default_factory=list, description="""Electrode group that each spike unit came from.""")
    waveform_mean: Optional[UnitsWaveformMean] = Field(None, description="""Spike waveform mean for each spike unit.""")
    waveform_sd: Optional[UnitsWaveformSd] = Field(None, description="""Spike waveform standard deviation for each spike unit.""")
    waveforms: Optional[UnitsWaveforms] = Field(None, description="""Individual waveforms for each spike on each electrode. This is a doubly indexed column. The 'waveforms_index' column indexes which waveforms in this column belong to the same spike event for a given unit, where each waveform was recorded from a different electrode. The 'waveforms_index_index' column indexes the 'waveforms_index' column to indicate which spike events belong to a given unit. For example, if the 'waveforms_index_index' column has values [2, 5, 6], then the first 2 elements of the 'waveforms_index' column correspond to the 2 spike events of the first unit, the next 3 elements of the 'waveforms_index' column correspond to the 3 spike events of the second unit, and the next 1 element of the 'waveforms_index' column corresponds to the 1 spike event of the third unit. If the 'waveforms_index' column has values [3, 6, 8, 10, 12, 13], then the first 3 elements of the 'waveforms' column contain the 3 spike waveforms that were recorded from 3 different electrodes for the first spike time of the first unit. See https://nwb-schema.readthedocs.io/en/stable/format_description.html#doubly-ragged-arrays for a graphical representation of this example. When there is only one electrode for each unit (i.e., each spike time is associated with a single waveform), then the 'waveforms_index' column will have values 1, 2, ..., N, where N is the number of spike events. The number of electrodes for each spike event should be the same within a given unit. The 'electrodes' column should be used to indicate which electrodes are associated with each unit, and the order of the waveforms within a given unit x spike event should be in the same order as the electrodes referenced in the 'electrodes' column of this table. The number of samples for each waveform must be the same.""")
    waveforms_index: Optional[UnitsWaveformsIndex] = Field(None, description="""Index into the waveforms dataset. One value for every spike event. See 'waveforms' for more detail.""")
    waveforms_index_index: Optional[UnitsWaveformsIndexIndex] = Field(None, description="""Index into the waveforms_index dataset. One value for every unit (row in the table). See 'waveforms' for more detail.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class SubjectAge(ConfiguredBaseModel):
    """
    Age of subject. Can be supplied instead of 'date_of_birth'.
    """
    reference: Optional[str] = Field(None, description="""Age is with reference to this event. Can be 'birth' or 'gestational'. If reference is omitted, 'birth' is implied.""")
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
NWBFileFileCreateDate.update_forward_refs()
NWBFileAcquisition.update_forward_refs()
NWBFileAnalysis.update_forward_refs()
NWBFileScratch.update_forward_refs()
NWBFileProcessing.update_forward_refs()
NWBFileStimulus.update_forward_refs()
NWBFileStimulusPresentation.update_forward_refs()
NWBFileStimulusTemplates.update_forward_refs()
NWBFileGeneral.update_forward_refs()
NWBFileGeneralExperimenter.update_forward_refs()
NWBFileGeneralKeywords.update_forward_refs()
NWBFileGeneralRelatedPublications.update_forward_refs()
NWBFileGeneralSourceScript.update_forward_refs()
NWBFileGeneralDevices.update_forward_refs()
NWBFileGeneralSubject.update_forward_refs()
NWBFileGeneralExtracellularEphys.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodes.update_forward_refs()
NWBFileGeneralIntracellularEphys.update_forward_refs()
NWBFileGeneralIntracellularEphysSweepTable.update_forward_refs()
NWBFileGeneralIntracellularEphysIntracellularRecordings.update_forward_refs()
NWBFileGeneralIntracellularEphysSimultaneousRecordings.update_forward_refs()
NWBFileGeneralIntracellularEphysSequentialRecordings.update_forward_refs()
NWBFileGeneralIntracellularEphysRepetitions.update_forward_refs()
NWBFileGeneralIntracellularEphysExperimentalConditions.update_forward_refs()
NWBFileGeneralOptogenetics.update_forward_refs()
NWBFileGeneralOptophysiology.update_forward_refs()
NWBFileIntervals.update_forward_refs()
NWBFileIntervalsEpochs.update_forward_refs()
NWBFileIntervalsTrials.update_forward_refs()
NWBFileIntervalsInvalidTimes.update_forward_refs()
NWBFileUnits.update_forward_refs()
SubjectAge.update_forward_refs()
