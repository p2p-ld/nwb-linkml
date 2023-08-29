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


from .core_nwb_file_include import (
    NWBFileScratch,
    NWBFileGeneral,
    NWBFileIntervals,
    NWBFileFileCreateDate,
    NWBFileUnits,
    SubjectAge,
    NWBFileStimulus,
    NWBFileAcquisition,
    NWBFileProcessing,
    NWBFileAnalysis
)

from .core_nwb_base import (
    NWBContainer,
    NWBData
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


class ScratchData(NWBData):
    """
    Any one-off datasets
    """
    notes: Optional[str] = Field(None, description="""Any notes the user has about the dataset being stored""")
    

class NWBFile(NWBContainer):
    """
    An NWB file storing cellular-based neurophysiology data from a single experimental session.
    """
    nwb_version: Optional[str] = Field(None, description="""File version string. Use semantic versioning, e.g. 1.2.1. This will be the name of the format with trailing major, minor and patch numbers.""")
    file_create_date: NWBFileFileCreateDate = Field(..., description="""A record of the date the file was created and of subsequent modifications. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted strings: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds. The file can be created after the experiment was run, so this may differ from the experiment start time. Each modification to the nwb file adds a new entry to the array.""")
    identifier: str = Field(..., description="""A unique text identifier for the file. For example, concatenated lab name, file creation date/time and experimentalist, or a hash of these and/or other values. The goal is that the string should be unique to all other files.""")
    session_description: str = Field(..., description="""A description of the experimental session and data in the file.""")
    session_start_time: date = Field(..., description="""Date and time of the experiment/session start. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted string: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds.""")
    timestamps_reference_time: date = Field(..., description="""Date and time corresponding to time zero of all timestamps. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted string: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds. All times stored in the file use this time as reference (i.e., time zero).""")
    acquisition: NWBFileAcquisition = Field(..., description="""Data streams recorded from the system, including ephys, ophys, tracking, etc. This group should be read-only after the experiment is completed and timestamps are corrected to a common timebase. The data stored here may be links to raw data stored in external NWB files. This will allow keeping bulky raw data out of the file while preserving the option of keeping some/all in the file. Acquired data includes tracking and experimental data streams (i.e., everything measured from the system). If bulky data is stored in the /acquisition group, the data can exist in a separate NWB file that is linked to by the file being used for processing and analysis.""")
    analysis: NWBFileAnalysis = Field(..., description="""Lab-specific and custom scientific analysis of data. There is no defined format for the content of this group - the format is up to the individual user/lab. To facilitate sharing analysis data between labs, the contents here should be stored in standard types (e.g., neurodata_types) and appropriately documented. The file can store lab-specific and custom data analysis without restriction on its form or schema, reducing data formatting restrictions on end users. Such data should be placed in the analysis group. The analysis data should be documented so that it could be shared with other labs.""")
    scratch: Optional[NWBFileScratch] = Field(None, description="""A place to store one-off analysis results. Data placed here is not intended for sharing. By placing data here, users acknowledge that there is no guarantee that their data meets any standard.""")
    processing: NWBFileProcessing = Field(..., description="""The home for ProcessingModules. These modules perform intermediate analysis of data that is necessary to perform before scientific analysis. Examples include spike clustering, extracting position from tracking data, stitching together image slices. ProcessingModules can be large and express many data sets from relatively complex analysis (e.g., spike detection and clustering) or small, representing extraction of position information from tracking video, or even binary lick/no-lick decisions. Common software tools (e.g., klustakwik, MClust) are expected to read/write data here.  'Processing' refers to intermediate analysis of the acquired data to make it more amenable to scientific analysis.""")
    stimulus: NWBFileStimulus = Field(..., description="""Data pushed into the system (eg, video stimulus, sound, voltage, etc) and secondary representations of that data (eg, measurements of something used as a stimulus). This group should be made read-only after experiment complete and timestamps are corrected to common timebase. Stores both presented stimuli and stimulus templates, the latter in case the same stimulus is presented multiple times, or is pulled from an external stimulus library. Stimuli are here defined as any signal that is pushed into the system as part of the experiment (eg, sound, video, voltage, etc). Many different experiments can use the same stimuli, and stimuli can be re-used during an experiment. The stimulus group is organized so that one version of template stimuli can be stored and these be used multiple times. These templates can exist in the present file or can be linked to a remote library file.""")
    general: NWBFileGeneral = Field(..., description="""Experimental metadata, including protocol, notes and description of hardware device(s).  The metadata stored in this section should be used to describe the experiment. Metadata necessary for interpreting the data is stored with the data. General experimental metadata, including animal strain, experimental protocols, experimenter, devices, etc, are stored under 'general'. Core metadata (e.g., that required to interpret data fields) is stored with the data itself, and implicitly defined by the file specification (e.g., time is in seconds). The strategy used here for storing non-core metadata is to use free-form text fields, such as would appear in sentences or paragraphs from a Methods section. Metadata fields are text to enable them to be more general, for example to represent ranges instead of numerical values. Machine-readable metadata is stored as attributes to these free-form datasets. All entries in the below table are to be included when data is present. Unused groups (e.g., intracellular_ephys in an optophysiology experiment) should not be created unless there is data to store within them.""")
    intervals: Optional[NWBFileIntervals] = Field(None, description="""Experimental intervals, whether that be logically distinct sub-experiments having a particular scientific goal, trials (see trials subgroup) during an experiment, or epochs (see epochs subgroup) deriving from analysis of data.""")
    units: Optional[NWBFileUnits] = Field(None, description="""Data about sorted spike units.""")
    

class LabMetaData(NWBContainer):
    """
    Lab-specific meta-data.
    """
    None
    

class Subject(NWBContainer):
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
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
ScratchData.update_forward_refs()
NWBFile.update_forward_refs()
LabMetaData.update_forward_refs()
Subject.update_forward_refs()
