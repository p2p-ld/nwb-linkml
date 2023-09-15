from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, Field
from nptyping import Shape, Float, Float32, Double, Float64, LongLong, Int64, Int, Int32, Int16, Short, Int8, UInt, UInt32, UInt16, UInt8, UInt64, Number, String, Unicode, Unicode, Unicode, String, Bool, Datetime64
from nwb_linkml.types import NDArray
import sys
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


from .core_nwb_epoch import (
    TimeIntervals
)

from .core_nwb_icephys import (
    SweepTable,
    IntracellularElectrode
)

from .core_nwb_base import (
    NWBDataInterface,
    TimeSeries,
    ProcessingModule,
    NWBContainer
)

from .core_nwb_ogen import (
    OptogeneticStimulusSite
)

from .core_nwb_ophys import (
    ImagingPlane
)

from .core_nwb_misc import (
    Units
)

from .core_nwb_device import (
    Device
)

from ...hdmf_common.v1_1_3.hdmf_common_table import (
    VectorIndex,
    VectorData,
    DynamicTable
)

from .core_nwb_ecephys import (
    ElectrodeGroup
)


metamodel_version = "None"
version = "2.2.2"

class ConfiguredBaseModel(BaseModel,
                validate_assignment = True,
                validate_default = True,
                extra = 'forbid',
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass


class NWBFile(NWBContainer):
    """
    An NWB:N file storing cellular-based neurophysiology data from a single experimental session.
    """
    name:Literal["root"]= Field("root")
    nwb_version:Optional[str]= Field(None, description="""File version string. Use semantic versioning, e.g. 1.2.1. This will be the name of the format with trailing major, minor and patch numbers.""")
    file_create_date:List[datetime ]= Field(default_factory=list, description="""A record of the date the file was created and of subsequent modifications. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted strings: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds. The file can be created after the experiment was run, so this may differ from the experiment start time. Each modification to the nwb file adds a new entry to the array.""")
    identifier:str= Field(..., description="""A unique text identifier for the file. For example, concatenated lab name, file creation date/time and experimentalist, or a hash of these and/or other values. The goal is that the string should be unique to all other files.""")
    session_description:str= Field(..., description="""A description of the experimental session and data in the file.""")
    session_start_time:datetime = Field(..., description="""Date and time of the experiment/session start. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted string: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds.""")
    timestamps_reference_time:datetime = Field(..., description="""Date and time corresponding to time zero of all timestamps. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted string: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds. All times stored in the file use this time as reference (i.e., time zero).""")
    acquisition:Optional[List[Union[DynamicTable, NWBDataInterface]]]= Field(default_factory=list, description="""Data streams recorded from the system, including ephys, ophys, tracking, etc. This group should be read-only after the experiment is completed and timestamps are corrected to a common timebase. The data stored here may be links to raw data stored in external NWB files. This will allow keeping bulky raw data out of the file while preserving the option of keeping some/all in the file. Acquired data includes tracking and experimental data streams (i.e., everything measured from the system). If bulky data is stored in the /acquisition group, the data can exist in a separate NWB file that is linked to by the file being used for processing and analysis.""")
    analysis:Optional[List[Union[DynamicTable, NWBContainer]]]= Field(default_factory=list, description="""Lab-specific and custom scientific analysis of data. There is no defined format for the content of this group - the format is up to the individual user/lab. To facilitate sharing analysis data between labs, the contents here should be stored in standard types (e.g., neurodata_types) and appropriately documented. The file can store lab-specific and custom data analysis without restriction on its form or schema, reducing data formatting restrictions on end users. Such data should be placed in the analysis group. The analysis data should be documented so that it could be shared with other labs.""")
    scratch:Optional[List[Union[DynamicTable, NWBContainer]]]= Field(default_factory=list, description="""A place to store one-off analysis results. Data placed here is not intended for sharing. By placing data here, users acknowledge that there is no guarantee that their data meets any standard.""")
    processing:Optional[List[ProcessingModule]]= Field(default_factory=list, description="""The home for ProcessingModules. These modules perform intermediate analysis of data that is necessary to perform before scientific analysis. Examples include spike clustering, extracting position from tracking data, stitching together image slices. ProcessingModules can be large and express many data sets from relatively complex analysis (e.g., spike detection and clustering) or small, representing extraction of position information from tracking video, or even binary lick/no-lick decisions. Common software tools (e.g., klustakwik, MClust) are expected to read/write data here.  'Processing' refers to intermediate analysis of the acquired data to make it more amenable to scientific analysis.""")
    stimulus:NWBFileStimulus= Field(..., description="""Data pushed into the system (eg, video stimulus, sound, voltage, etc) and secondary representations of that data (eg, measurements of something used as a stimulus). This group should be made read-only after experiment complete and timestamps are corrected to common timebase. Stores both presented stimuli and stimulus templates, the latter in case the same stimulus is presented multiple times, or is pulled from an external stimulus library. Stimuli are here defined as any signal that is pushed into the system as part of the experiment (eg, sound, video, voltage, etc). Many different experiments can use the same stimuli, and stimuli can be re-used during an experiment. The stimulus group is organized so that one version of template stimuli can be stored and these be used multiple times. These templates can exist in the present file or can be linked to a remote library file.""")
    general:NWBFileGeneral= Field(..., description="""Experimental metadata, including protocol, notes and description of hardware device(s).  The metadata stored in this section should be used to describe the experiment. Metadata necessary for interpreting the data is stored with the data. General experimental metadata, including animal strain, experimental protocols, experimenter, devices, etc, are stored under 'general'. Core metadata (e.g., that required to interpret data fields) is stored with the data itself, and implicitly defined by the file specification (e.g., time is in seconds). The strategy used here for storing non-core metadata is to use free-form text fields, such as would appear in sentences or paragraphs from a Methods section. Metadata fields are text to enable them to be more general, for example to represent ranges instead of numerical values. Machine-readable metadata is stored as attributes to these free-form datasets. All entries in the below table are to be included when data is present. Unused groups (e.g., intracellular_ephys in an optophysiology experiment) should not be created unless there is data to store within them.""")
    intervals:Optional[NWBFileIntervals]= Field(None, description="""Experimental intervals, whether that be logically distinct sub-experiments having a particular scientific goal, trials (see trials subgroup) during an experiment, or epochs (see epochs subgroup) deriving from analysis of data.""")
    units:Optional[Units]= Field(None, description="""Data about sorted spike units.""")
    

class NWBFileStimulus(ConfiguredBaseModel):
    """
    Data pushed into the system (eg, video stimulus, sound, voltage, etc) and secondary representations of that data (eg, measurements of something used as a stimulus). This group should be made read-only after experiment complete and timestamps are corrected to common timebase. Stores both presented stimuli and stimulus templates, the latter in case the same stimulus is presented multiple times, or is pulled from an external stimulus library. Stimuli are here defined as any signal that is pushed into the system as part of the experiment (eg, sound, video, voltage, etc). Many different experiments can use the same stimuli, and stimuli can be re-used during an experiment. The stimulus group is organized so that one version of template stimuli can be stored and these be used multiple times. These templates can exist in the present file or can be linked to a remote library file.
    """
    name:Literal["stimulus"]= Field("stimulus")
    presentation:Optional[List[TimeSeries]]= Field(default_factory=list, description="""Stimuli presented during the experiment.""")
    templates:Optional[List[TimeSeries]]= Field(default_factory=list, description="""Template stimuli. Timestamps in templates are based on stimulus design and are relative to the beginning of the stimulus. When templates are used, the stimulus instances must convert presentation times to the experiment`s time reference frame.""")
    

class NWBFileGeneral(ConfiguredBaseModel):
    """
    Experimental metadata, including protocol, notes and description of hardware device(s).  The metadata stored in this section should be used to describe the experiment. Metadata necessary for interpreting the data is stored with the data. General experimental metadata, including animal strain, experimental protocols, experimenter, devices, etc, are stored under 'general'. Core metadata (e.g., that required to interpret data fields) is stored with the data itself, and implicitly defined by the file specification (e.g., time is in seconds). The strategy used here for storing non-core metadata is to use free-form text fields, such as would appear in sentences or paragraphs from a Methods section. Metadata fields are text to enable them to be more general, for example to represent ranges instead of numerical values. Machine-readable metadata is stored as attributes to these free-form datasets. All entries in the below table are to be included when data is present. Unused groups (e.g., intracellular_ephys in an optophysiology experiment) should not be created unless there is data to store within them.
    """
    name:Literal["general"]= Field("general")
    data_collection:Optional[str]= Field(None, description="""Notes about data collection and analysis.""")
    experiment_description:Optional[str]= Field(None, description="""General description of the experiment.""")
    experimenter:Optional[List[str]]= Field(default_factory=list, description="""Name of person(s) who performed the experiment. Can also specify roles of different people involved.""")
    institution:Optional[str]= Field(None, description="""Institution(s) where experiment was performed.""")
    keywords:Optional[List[str]]= Field(default_factory=list, description="""Terms to search over.""")
    lab:Optional[str]= Field(None, description="""Laboratory where experiment was performed.""")
    notes:Optional[str]= Field(None, description="""Notes about the experiment.""")
    pharmacology:Optional[str]= Field(None, description="""Description of drugs used, including how and when they were administered. Anesthesia(s), painkiller(s), etc., plus dosage, concentration, etc.""")
    protocol:Optional[str]= Field(None, description="""Experimental protocol, if applicable. e.g., include IACUC protocol number.""")
    related_publications:Optional[List[str]]= Field(default_factory=list, description="""Publication information. PMID, DOI, URL, etc.""")
    session_id:Optional[str]= Field(None, description="""Lab-specific ID for the session.""")
    slices:Optional[str]= Field(None, description="""Description of slices, including information about preparation thickness, orientation, temperature, and bath solution.""")
    source_script:Optional[NWBFileGeneralSourceScript]= Field(None, description="""Script file or link to public source code used to create this NWB file.""")
    stimulus:Optional[str]= Field(None, description="""Notes about stimuli, such as how and where they were presented.""")
    surgery:Optional[str]= Field(None, description="""Narrative description about surgery/surgeries, including date(s) and who performed surgery.""")
    virus:Optional[str]= Field(None, description="""Information about virus(es) used in experiments, including virus ID, source, date made, injection location, volume, etc.""")
    nwb_container:Optional[List[NWBContainer]]= Field(default_factory=list, description="""Place-holder than can be extended so that lab-specific meta-data can be placed in /general.""")
    devices:Optional[List[Device]]= Field(default_factory=list, description="""Description of hardware devices used during experiment, e.g., monitors, ADC boards, microscopes, etc.""")
    subject:Optional[Subject]= Field(None, description="""Information about the animal or person from which the data was measured.""")
    extracellular_ephys:Optional[NWBFileGeneralExtracellularEphys]= Field(None, description="""Metadata related to extracellular electrophysiology.""")
    intracellular_ephys:Optional[NWBFileGeneralIntracellularEphys]= Field(None, description="""Metadata related to intracellular electrophysiology.""")
    optogenetics:Optional[List[OptogeneticStimulusSite]]= Field(default_factory=list, description="""Metadata describing optogenetic stimuluation.""")
    optophysiology:Optional[List[ImagingPlane]]= Field(default_factory=list, description="""Metadata related to optophysiology.""")
    

class NWBFileGeneralSourceScript(ConfiguredBaseModel):
    """
    Script file or link to public source code used to create this NWB file.
    """
    name:Literal["source_script"]= Field("source_script")
    file_name:Optional[str]= Field(None, description="""Name of script file.""")
    value:str= Field(...)
    

class Subject(NWBContainer):
    """
    Information about the animal or person from which the data was measured.
    """
    name:Literal["subject"]= Field("subject")
    age:Optional[str]= Field(None, description="""Age of subject. Can be supplied instead of 'date_of_birth'.""")
    date_of_birth:Optional[datetime ]= Field(None, description="""Date of birth of subject. Can be supplied instead of 'age'.""")
    description:Optional[str]= Field(None, description="""Description of subject and where subject came from (e.g., breeder, if animal).""")
    genotype:Optional[str]= Field(None, description="""Genetic strain. If absent, assume Wild Type (WT).""")
    sex:Optional[str]= Field(None, description="""Gender of subject.""")
    species:Optional[str]= Field(None, description="""Species of subject.""")
    subject_id:Optional[str]= Field(None, description="""ID of animal/person used/participating in experiment (lab convention).""")
    weight:Optional[str]= Field(None, description="""Weight at time of experiment, at time of surgery and at other important times.""")
    

class NWBFileGeneralExtracellularEphys(ConfiguredBaseModel):
    """
    Metadata related to extracellular electrophysiology.
    """
    name:Literal["extracellular_ephys"]= Field("extracellular_ephys")
    electrode_group:Optional[List[ElectrodeGroup]]= Field(default_factory=list, description="""Physical group of electrodes.""")
    electrodes:Optional[NWBFileGeneralExtracellularEphysElectrodes]= Field(None, description="""A table of all electrodes (i.e. channels) used for recording.""")
    

class NWBFileGeneralExtracellularEphysElectrodes(DynamicTable):
    """
    A table of all electrodes (i.e. channels) used for recording.
    """
    name:Literal["electrodes"]= Field("electrodes")
    x:Optional[List[float]]= Field(default_factory=list, description="""x coordinate of the channel location in the brain (+x is posterior).""")
    y:Optional[List[float]]= Field(default_factory=list, description="""y coordinate of the channel location in the brain (+y is inferior).""")
    z:Optional[List[float]]= Field(default_factory=list, description="""z coordinate of the channel location in the brain (+z is right).""")
    imp:Optional[List[float]]= Field(default_factory=list, description="""Impedance of the channel.""")
    location:Optional[List[str]]= Field(default_factory=list, description="""Location of the electrode (channel). Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""")
    filtering:Optional[List[float]]= Field(default_factory=list, description="""Description of hardware filtering.""")
    group:Optional[List[ElectrodeGroup]]= Field(default_factory=list, description="""Reference to the ElectrodeGroup this electrode is a part of.""")
    group_name:Optional[List[str]]= Field(default_factory=list, description="""Name of the ElectrodeGroup this electrode is a part of.""")
    rel_x:Optional[List[float]]= Field(default_factory=list, description="""x coordinate in electrode group""")
    rel_y:Optional[List[float]]= Field(default_factory=list, description="""y coordinate in electrode group""")
    rel_z:Optional[List[float]]= Field(default_factory=list, description="""z coordinate in electrode group""")
    reference:Optional[List[str]]= Field(default_factory=list, description="""Description of the reference used for this electrode.""")
    colnames:Optional[str]= Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description:Optional[str]= Field(None, description="""Description of what is in this dynamic table.""")
    id:List[int]= Field(default_factory=list, description="""Array of unique identifiers for the rows of this dynamic table.""")
    vector_data:Optional[List[VectorData]]= Field(default_factory=list, description="""Vector columns of this dynamic table.""")
    vector_index:Optional[List[VectorIndex]]= Field(default_factory=list, description="""Indices for the vector columns of this dynamic table.""")
    

class NWBFileGeneralIntracellularEphys(ConfiguredBaseModel):
    """
    Metadata related to intracellular electrophysiology.
    """
    name:Literal["intracellular_ephys"]= Field("intracellular_ephys")
    filtering:Optional[str]= Field(None, description="""Description of filtering used. Includes filtering type and parameters, frequency fall-off, etc. If this changes between TimeSeries, filter description should be stored as a text attribute for each TimeSeries.""")
    intracellular_electrode:Optional[List[IntracellularElectrode]]= Field(default_factory=list, description="""An intracellular electrode.""")
    sweep_table:Optional[SweepTable]= Field(None, description="""The table which groups different PatchClampSeries together.""")
    

class NWBFileIntervals(ConfiguredBaseModel):
    """
    Experimental intervals, whether that be logically distinct sub-experiments having a particular scientific goal, trials (see trials subgroup) during an experiment, or epochs (see epochs subgroup) deriving from analysis of data.
    """
    name:Literal["intervals"]= Field("intervals")
    epochs:Optional[TimeIntervals]= Field(None, description="""Divisions in time marking experimental stages or sub-divisions of a single recording session.""")
    trials:Optional[TimeIntervals]= Field(None, description="""Repeated experimental events that have a logical grouping.""")
    invalid_times:Optional[TimeIntervals]= Field(None, description="""Time intervals that should be removed from analysis.""")
    time_intervals:Optional[List[TimeIntervals]]= Field(default_factory=list, description="""Optional additional table(s) for describing other experimental time intervals.""")
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
NWBFile.model_rebuild()
NWBFileStimulus.model_rebuild()
NWBFileGeneral.model_rebuild()
NWBFileGeneralSourceScript.model_rebuild()
Subject.model_rebuild()
NWBFileGeneralExtracellularEphys.model_rebuild()
NWBFileGeneralExtracellularEphysElectrodes.model_rebuild()
NWBFileGeneralIntracellularEphys.model_rebuild()
NWBFileIntervals.model_rebuild()
    