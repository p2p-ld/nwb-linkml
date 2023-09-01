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


from .core_nwb_base import (
    TimeSeries,
    Images
)

from .core_nwb_icephys import (
    ExperimentalConditionsTable,
    SweepTable,
    IntracellularElectrode,
    SequentialRecordingsTable,
    RepetitionsTable,
    SimultaneousRecordingsTable,
    IntracellularRecordingsTable
)

from .core_nwb_ogen import (
    OptogeneticStimulusSite
)

from .core_nwb_epoch import (
    TimeIntervals
)

from .core_nwb_file import (
    LabMetaData,
    Subject
)

from .hdmf_common_table import (
    DynamicTable
)

from .core_nwb_device import (
    Device
)

from .core_nwb_ecephys import (
    ElectrodeGroup
)

from .core_nwb_ophys import (
    ImagingPlane
)


metamodel_version = "None"
version = "None"

class ConfiguredBaseModel(BaseModel,
                validate_assignment = True,
                validate_default = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


class NWBFileStimulus(ConfiguredBaseModel):
    """
    Data pushed into the system (eg, video stimulus, sound, voltage, etc) and secondary representations of that data (eg, measurements of something used as a stimulus). This group should be made read-only after experiment complete and timestamps are corrected to common timebase. Stores both presented stimuli and stimulus templates, the latter in case the same stimulus is presented multiple times, or is pulled from an external stimulus library. Stimuli are here defined as any signal that is pushed into the system as part of the experiment (eg, sound, video, voltage, etc). Many different experiments can use the same stimuli, and stimuli can be re-used during an experiment. The stimulus group is organized so that one version of template stimuli can be stored and these be used multiple times. These templates can exist in the present file or can be linked to a remote library file.
    """
    name: str = Field("stimulus", const=True)
    presentation: Optional[List[TimeSeries]] = Field(default_factory=list, description="""Stimuli presented during the experiment.""")
    templates: Optional[List[Union[Images, TimeSeries]]] = Field(default_factory=list, description="""Template stimuli. Timestamps in templates are based on stimulus design and are relative to the beginning of the stimulus. When templates are used, the stimulus instances must convert presentation times to the experiment`s time reference frame.""")
    

class NWBFileGeneral(ConfiguredBaseModel):
    """
    Experimental metadata, including protocol, notes and description of hardware device(s).  The metadata stored in this section should be used to describe the experiment. Metadata necessary for interpreting the data is stored with the data. General experimental metadata, including animal strain, experimental protocols, experimenter, devices, etc, are stored under 'general'. Core metadata (e.g., that required to interpret data fields) is stored with the data itself, and implicitly defined by the file specification (e.g., time is in seconds). The strategy used here for storing non-core metadata is to use free-form text fields, such as would appear in sentences or paragraphs from a Methods section. Metadata fields are text to enable them to be more general, for example to represent ranges instead of numerical values. Machine-readable metadata is stored as attributes to these free-form datasets. All entries in the below table are to be included when data is present. Unused groups (e.g., intracellular_ephys in an optophysiology experiment) should not be created unless there is data to store within them.
    """
    name: str = Field("general", const=True)
    data_collection: Optional[str] = Field(None, description="""Notes about data collection and analysis.""")
    experiment_description: Optional[str] = Field(None, description="""General description of the experiment.""")
    experimenter: Optional[List[str]] = Field(default_factory=list, description="""Name of person(s) who performed the experiment. Can also specify roles of different people involved.""")
    institution: Optional[str] = Field(None, description="""Institution(s) where experiment was performed.""")
    keywords: Optional[List[str]] = Field(default_factory=list, description="""Terms to search over.""")
    lab: Optional[str] = Field(None, description="""Laboratory where experiment was performed.""")
    notes: Optional[str] = Field(None, description="""Notes about the experiment.""")
    pharmacology: Optional[str] = Field(None, description="""Description of drugs used, including how and when they were administered. Anesthesia(s), painkiller(s), etc., plus dosage, concentration, etc.""")
    protocol: Optional[str] = Field(None, description="""Experimental protocol, if applicable. e.g., include IACUC protocol number.""")
    related_publications: Optional[List[str]] = Field(default_factory=list, description="""Publication information. PMID, DOI, URL, etc.""")
    session_id: Optional[str] = Field(None, description="""Lab-specific ID for the session.""")
    slices: Optional[str] = Field(None, description="""Description of slices, including information about preparation thickness, orientation, temperature, and bath solution.""")
    source_script: Optional[NWBFileGeneralSourceScript] = Field(None, description="""Script file or link to public source code used to create this NWB file.""")
    stimulus: Optional[str] = Field(None, description="""Notes about stimuli, such as how and where they were presented.""")
    surgery: Optional[str] = Field(None, description="""Narrative description about surgery/surgeries, including date(s) and who performed surgery.""")
    virus: Optional[str] = Field(None, description="""Information about virus(es) used in experiments, including virus ID, source, date made, injection location, volume, etc.""")
    lab_meta_data: Optional[List[LabMetaData]] = Field(default_factory=list, description="""Place-holder than can be extended so that lab-specific meta-data can be placed in /general.""")
    devices: Optional[List[Device]] = Field(default_factory=list, description="""Description of hardware devices used during experiment, e.g., monitors, ADC boards, microscopes, etc.""")
    subject: Optional[Subject] = Field(None, description="""Information about the animal or person from which the data was measured.""")
    extracellular_ephys: Optional[NWBFileGeneralExtracellularEphys] = Field(None, description="""Metadata related to extracellular electrophysiology.""")
    intracellular_ephys: Optional[NWBFileGeneralIntracellularEphys] = Field(None, description="""Metadata related to intracellular electrophysiology.""")
    optogenetics: Optional[List[OptogeneticStimulusSite]] = Field(default_factory=list, description="""Metadata describing optogenetic stimuluation.""")
    optophysiology: Optional[List[ImagingPlane]] = Field(default_factory=list, description="""Metadata related to optophysiology.""")
    

class NWBFileGeneralSourceScript(ConfiguredBaseModel):
    """
    Script file or link to public source code used to create this NWB file.
    """
    name: str = Field("source_script", const=True)
    file_name: Optional[str] = Field(None, description="""Name of script file.""")
    

class NWBFileGeneralExtracellularEphys(ConfiguredBaseModel):
    """
    Metadata related to extracellular electrophysiology.
    """
    name: str = Field("extracellular_ephys", const=True)
    electrode_group: Optional[List[ElectrodeGroup]] = Field(default_factory=list, description="""Physical group of electrodes.""")
    electrodes: Optional[DynamicTable] = Field(None, description="""A table of all electrodes (i.e. channels) used for recording.""")
    

class NWBFileGeneralIntracellularEphys(ConfiguredBaseModel):
    """
    Metadata related to intracellular electrophysiology.
    """
    name: str = Field("intracellular_ephys", const=True)
    filtering: Optional[str] = Field(None, description="""[DEPRECATED] Use IntracellularElectrode.filtering instead. Description of filtering used. Includes filtering type and parameters, frequency fall-off, etc. If this changes between TimeSeries, filter description should be stored as a text attribute for each TimeSeries.""")
    intracellular_electrode: Optional[List[IntracellularElectrode]] = Field(default_factory=list, description="""An intracellular electrode.""")
    sweep_table: Optional[SweepTable] = Field(None, description="""[DEPRECATED] Table used to group different PatchClampSeries. SweepTable is being replaced by IntracellularRecordingsTable and SimultaneousRecordingsTable tables. Additional SequentialRecordingsTable, RepetitionsTable and ExperimentalConditions tables provide enhanced support for experiment metadata.""")
    intracellular_recordings: Optional[IntracellularRecordingsTable] = Field(None, description="""A table to group together a stimulus and response from a single electrode and a single simultaneous recording. Each row in the table represents a single recording consisting typically of a stimulus and a corresponding response. In some cases, however, only a stimulus or a response are recorded as as part of an experiment. In this case both, the stimulus and response will point to the same TimeSeries while the idx_start and count of the invalid column will be set to -1, thus, indicating that no values have been recorded for the stimulus or response, respectively. Note, a recording MUST contain at least a stimulus or a response. Typically the stimulus and response are PatchClampSeries. However, the use of AD/DA channels that are not associated to an electrode is also common in intracellular electrophysiology, in which case other TimeSeries may be used.""")
    simultaneous_recordings: Optional[SimultaneousRecordingsTable] = Field(None, description="""A table for grouping different intracellular recordings from the IntracellularRecordingsTable table together that were recorded simultaneously from different electrodes""")
    sequential_recordings: Optional[SequentialRecordingsTable] = Field(None, description="""A table for grouping different sequential recordings from the SimultaneousRecordingsTable table together. This is typically used to group together sequential recordings where the a sequence of stimuli of the same type with varying parameters have been presented in a sequence.""")
    repetitions: Optional[RepetitionsTable] = Field(None, description="""A table for grouping different sequential intracellular recordings together. With each SequentialRecording typically representing a particular type of stimulus, the RepetitionsTable table is typically used to group sets of stimuli applied in sequence.""")
    experimental_conditions: Optional[ExperimentalConditionsTable] = Field(None, description="""A table for grouping different intracellular recording repetitions together that belong to the same experimental experimental_conditions.""")
    

class NWBFileIntervals(ConfiguredBaseModel):
    """
    Experimental intervals, whether that be logically distinct sub-experiments having a particular scientific goal, trials (see trials subgroup) during an experiment, or epochs (see epochs subgroup) deriving from analysis of data.
    """
    name: str = Field("intervals", const=True)
    epochs: Optional[TimeIntervals] = Field(None, description="""Divisions in time marking experimental stages or sub-divisions of a single recording session.""")
    trials: Optional[TimeIntervals] = Field(None, description="""Repeated experimental events that have a logical grouping.""")
    invalid_times: Optional[TimeIntervals] = Field(None, description="""Time intervals that should be removed from analysis.""")
    time_intervals: Optional[List[TimeIntervals]] = Field(default_factory=list, description="""Optional additional table(s) for describing other experimental time intervals.""")
    

class SubjectAge(ConfiguredBaseModel):
    """
    Age of subject. Can be supplied instead of 'date_of_birth'.
    """
    name: str = Field("age", const=True)
    reference: Optional[str] = Field(None, description="""Age is with reference to this event. Can be 'birth' or 'gestational'. If reference is omitted, 'birth' is implied.""")
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
NWBFileStimulus.model_rebuild()
NWBFileGeneral.model_rebuild()
NWBFileGeneralSourceScript.model_rebuild()
NWBFileGeneralExtracellularEphys.model_rebuild()
NWBFileGeneralIntracellularEphys.model_rebuild()
NWBFileIntervals.model_rebuild()
SubjectAge.model_rebuild()
    