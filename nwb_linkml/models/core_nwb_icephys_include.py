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


from .hdmf_common_table import (
    DynamicTableRegion,
    VectorIndex
)

from .core_nwb_base import (
    TimeSeriesReferenceVectorData
)

from .core_nwb_icephys import (
    SimultaneousRecordingsTable,
    IntracellularElectrodesTable,
    IntracellularResponsesTable,
    SequentialRecordingsTable,
    IntracellularRecordingsTable,
    IntracellularStimuliTable,
    RepetitionsTable
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


class PatchClampSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage or current.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    data: List[float] = Field(default_factory=list, description="""Recorded voltage or current.""")
    

class CurrentClampSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. which is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    

class CurrentClampStimulusSeriesData(ConfiguredBaseModel):
    """
    Stimulus current applied.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. which is fixed to 'amperes'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    

class VoltageClampSeriesData(ConfiguredBaseModel):
    """
    Recorded current.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. which is fixed to 'amperes'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    

class VoltageClampSeriesCapacitanceFast(ConfiguredBaseModel):
    """
    Fast capacitance, in farads.
    """
    unit: Optional[str] = Field(None, description="""Unit of measurement for capacitance_fast, which is fixed to 'farads'.""")
    

class VoltageClampSeriesCapacitanceSlow(ConfiguredBaseModel):
    """
    Slow capacitance, in farads.
    """
    unit: Optional[str] = Field(None, description="""Unit of measurement for capacitance_fast, which is fixed to 'farads'.""")
    

class VoltageClampSeriesResistanceCompBandwidth(ConfiguredBaseModel):
    """
    Resistance compensation bandwidth, in hertz.
    """
    unit: Optional[str] = Field(None, description="""Unit of measurement for resistance_comp_bandwidth, which is fixed to 'hertz'.""")
    

class VoltageClampSeriesResistanceCompCorrection(ConfiguredBaseModel):
    """
    Resistance compensation correction, in percent.
    """
    unit: Optional[str] = Field(None, description="""Unit of measurement for resistance_comp_correction, which is fixed to 'percent'.""")
    

class VoltageClampSeriesResistanceCompPrediction(ConfiguredBaseModel):
    """
    Resistance compensation prediction, in percent.
    """
    unit: Optional[str] = Field(None, description="""Unit of measurement for resistance_comp_prediction, which is fixed to 'percent'.""")
    

class VoltageClampSeriesWholeCellCapacitanceComp(ConfiguredBaseModel):
    """
    Whole cell capacitance compensation, in farads.
    """
    unit: Optional[str] = Field(None, description="""Unit of measurement for whole_cell_capacitance_comp, which is fixed to 'farads'.""")
    

class VoltageClampSeriesWholeCellSeriesResistanceComp(ConfiguredBaseModel):
    """
    Whole cell series resistance compensation, in ohms.
    """
    unit: Optional[str] = Field(None, description="""Unit of measurement for whole_cell_series_resistance_comp, which is fixed to 'ohms'.""")
    

class VoltageClampStimulusSeriesData(ConfiguredBaseModel):
    """
    Stimulus voltage applied.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. which is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    

class SweepTableSeriesIndex(VectorIndex):
    """
    Index for series.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class IntracellularStimuliTableStimulus(TimeSeriesReferenceVectorData):
    """
    Column storing the reference to the recorded stimulus for the recording (rows).
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class IntracellularResponsesTableResponse(TimeSeriesReferenceVectorData):
    """
    Column storing the reference to the recorded response for the recording (rows)
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class IntracellularRecordingsTableElectrodes(IntracellularElectrodesTable):
    """
    Table for storing intracellular electrode related metadata.
    """
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    electrode: Optional[List[IntracellularElectrode]] = Field(default_factory=list, description="""Column for storing the reference to the intracellular electrode.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularRecordingsTableStimuli(IntracellularStimuliTable):
    """
    Table for storing intracellular stimulus related metadata.
    """
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    stimulus: IntracellularStimuliTableStimulus = Field(..., description="""Column storing the reference to the recorded stimulus for the recording (rows).""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularRecordingsTableResponses(IntracellularResponsesTable):
    """
    Table for storing intracellular response related metadata.
    """
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    response: IntracellularResponsesTableResponse = Field(..., description="""Column storing the reference to the recorded response for the recording (rows)""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class SimultaneousRecordingsTableRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the IntracellularRecordingsTable table.
    """
    table: Optional[IntracellularRecordingsTable] = Field(None, description="""Reference to the IntracellularRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class SimultaneousRecordingsTableRecordingsIndex(VectorIndex):
    """
    Index dataset for the recordings column.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class SequentialRecordingsTableSimultaneousRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the SimultaneousRecordingsTable table.
    """
    table: Optional[SimultaneousRecordingsTable] = Field(None, description="""Reference to the SimultaneousRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class SequentialRecordingsTableSimultaneousRecordingsIndex(VectorIndex):
    """
    Index dataset for the simultaneous_recordings column.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class RepetitionsTableSequentialRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the SequentialRecordingsTable table.
    """
    table: Optional[SequentialRecordingsTable] = Field(None, description="""Reference to the SequentialRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class RepetitionsTableSequentialRecordingsIndex(VectorIndex):
    """
    Index dataset for the sequential_recordings column.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class ExperimentalConditionsTableRepetitions(DynamicTableRegion):
    """
    A reference to one or more rows in the RepetitionsTable table.
    """
    table: Optional[RepetitionsTable] = Field(None, description="""Reference to the RepetitionsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    

class ExperimentalConditionsTableRepetitionsIndex(VectorIndex):
    """
    Index dataset for the repetitions column.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], ]] = Field(None)
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
PatchClampSeriesData.update_forward_refs()
CurrentClampSeriesData.update_forward_refs()
CurrentClampStimulusSeriesData.update_forward_refs()
VoltageClampSeriesData.update_forward_refs()
VoltageClampSeriesCapacitanceFast.update_forward_refs()
VoltageClampSeriesCapacitanceSlow.update_forward_refs()
VoltageClampSeriesResistanceCompBandwidth.update_forward_refs()
VoltageClampSeriesResistanceCompCorrection.update_forward_refs()
VoltageClampSeriesResistanceCompPrediction.update_forward_refs()
VoltageClampSeriesWholeCellCapacitanceComp.update_forward_refs()
VoltageClampSeriesWholeCellSeriesResistanceComp.update_forward_refs()
VoltageClampStimulusSeriesData.update_forward_refs()
SweepTableSeriesIndex.update_forward_refs()
IntracellularStimuliTableStimulus.update_forward_refs()
IntracellularResponsesTableResponse.update_forward_refs()
IntracellularRecordingsTableElectrodes.update_forward_refs()
IntracellularRecordingsTableStimuli.update_forward_refs()
IntracellularRecordingsTableResponses.update_forward_refs()
SimultaneousRecordingsTableRecordings.update_forward_refs()
SimultaneousRecordingsTableRecordingsIndex.update_forward_refs()
SequentialRecordingsTableSimultaneousRecordings.update_forward_refs()
SequentialRecordingsTableSimultaneousRecordingsIndex.update_forward_refs()
RepetitionsTableSequentialRecordings.update_forward_refs()
RepetitionsTableSequentialRecordingsIndex.update_forward_refs()
ExperimentalConditionsTableRepetitions.update_forward_refs()
ExperimentalConditionsTableRepetitionsIndex.update_forward_refs()
