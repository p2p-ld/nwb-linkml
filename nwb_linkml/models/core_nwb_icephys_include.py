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

from .core_nwb_icephys import (
    SequentialRecordingsTable,
    RepetitionsTable,
    SimultaneousRecordingsTable,
    IntracellularRecordingsTable
)

from .core_nwb_base import (
    TimeSeriesReferenceVectorData
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


class CurrentClampSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage.
    """
    name: str = Field("data", const=True)
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. which is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    

class CurrentClampStimulusSeriesData(ConfiguredBaseModel):
    """
    Stimulus current applied.
    """
    name: str = Field("data", const=True)
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. which is fixed to 'amperes'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    

class VoltageClampSeriesData(ConfiguredBaseModel):
    """
    Recorded current.
    """
    name: str = Field("data", const=True)
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. which is fixed to 'amperes'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    

class VoltageClampSeriesCapacitanceFast(ConfiguredBaseModel):
    """
    Fast capacitance, in farads.
    """
    name: str = Field("capacitance_fast", const=True)
    unit: Optional[str] = Field(None, description="""Unit of measurement for capacitance_fast, which is fixed to 'farads'.""")
    

class VoltageClampSeriesCapacitanceSlow(ConfiguredBaseModel):
    """
    Slow capacitance, in farads.
    """
    name: str = Field("capacitance_slow", const=True)
    unit: Optional[str] = Field(None, description="""Unit of measurement for capacitance_fast, which is fixed to 'farads'.""")
    

class VoltageClampSeriesResistanceCompBandwidth(ConfiguredBaseModel):
    """
    Resistance compensation bandwidth, in hertz.
    """
    name: str = Field("resistance_comp_bandwidth", const=True)
    unit: Optional[str] = Field(None, description="""Unit of measurement for resistance_comp_bandwidth, which is fixed to 'hertz'.""")
    

class VoltageClampSeriesResistanceCompCorrection(ConfiguredBaseModel):
    """
    Resistance compensation correction, in percent.
    """
    name: str = Field("resistance_comp_correction", const=True)
    unit: Optional[str] = Field(None, description="""Unit of measurement for resistance_comp_correction, which is fixed to 'percent'.""")
    

class VoltageClampSeriesResistanceCompPrediction(ConfiguredBaseModel):
    """
    Resistance compensation prediction, in percent.
    """
    name: str = Field("resistance_comp_prediction", const=True)
    unit: Optional[str] = Field(None, description="""Unit of measurement for resistance_comp_prediction, which is fixed to 'percent'.""")
    

class VoltageClampSeriesWholeCellCapacitanceComp(ConfiguredBaseModel):
    """
    Whole cell capacitance compensation, in farads.
    """
    name: str = Field("whole_cell_capacitance_comp", const=True)
    unit: Optional[str] = Field(None, description="""Unit of measurement for whole_cell_capacitance_comp, which is fixed to 'farads'.""")
    

class VoltageClampSeriesWholeCellSeriesResistanceComp(ConfiguredBaseModel):
    """
    Whole cell series resistance compensation, in ohms.
    """
    name: str = Field("whole_cell_series_resistance_comp", const=True)
    unit: Optional[str] = Field(None, description="""Unit of measurement for whole_cell_series_resistance_comp, which is fixed to 'ohms'.""")
    

class VoltageClampStimulusSeriesData(ConfiguredBaseModel):
    """
    Stimulus voltage applied.
    """
    name: str = Field("data", const=True)
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. which is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    

class SweepTableSeriesIndex(VectorIndex):
    """
    Index for series.
    """
    name: str = Field("series_index", const=True)
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class IntracellularStimuliTableStimulus(TimeSeriesReferenceVectorData):
    """
    Column storing the reference to the recorded stimulus for the recording (rows).
    """
    name: str = Field("stimulus", const=True)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class IntracellularResponsesTableResponse(TimeSeriesReferenceVectorData):
    """
    Column storing the reference to the recorded response for the recording (rows)
    """
    name: str = Field("response", const=True)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class SimultaneousRecordingsTableRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the IntracellularRecordingsTable table.
    """
    name: str = Field("recordings", const=True)
    table: Optional[IntracellularRecordingsTable] = Field(None, description="""Reference to the IntracellularRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class SimultaneousRecordingsTableRecordingsIndex(VectorIndex):
    """
    Index dataset for the recordings column.
    """
    name: str = Field("recordings_index", const=True)
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class SequentialRecordingsTableSimultaneousRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the SimultaneousRecordingsTable table.
    """
    name: str = Field("simultaneous_recordings", const=True)
    table: Optional[SimultaneousRecordingsTable] = Field(None, description="""Reference to the SimultaneousRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class SequentialRecordingsTableSimultaneousRecordingsIndex(VectorIndex):
    """
    Index dataset for the simultaneous_recordings column.
    """
    name: str = Field("simultaneous_recordings_index", const=True)
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class RepetitionsTableSequentialRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the SequentialRecordingsTable table.
    """
    name: str = Field("sequential_recordings", const=True)
    table: Optional[SequentialRecordingsTable] = Field(None, description="""Reference to the SequentialRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class RepetitionsTableSequentialRecordingsIndex(VectorIndex):
    """
    Index dataset for the sequential_recordings column.
    """
    name: str = Field("sequential_recordings_index", const=True)
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class ExperimentalConditionsTableRepetitions(DynamicTableRegion):
    """
    A reference to one or more rows in the RepetitionsTable table.
    """
    name: str = Field("repetitions", const=True)
    table: Optional[RepetitionsTable] = Field(None, description="""Reference to the RepetitionsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class ExperimentalConditionsTableRepetitionsIndex(VectorIndex):
    """
    Index dataset for the repetitions column.
    """
    name: str = Field("repetitions_index", const=True)
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
CurrentClampSeriesData.model_rebuild()
CurrentClampStimulusSeriesData.model_rebuild()
VoltageClampSeriesData.model_rebuild()
VoltageClampSeriesCapacitanceFast.model_rebuild()
VoltageClampSeriesCapacitanceSlow.model_rebuild()
VoltageClampSeriesResistanceCompBandwidth.model_rebuild()
VoltageClampSeriesResistanceCompCorrection.model_rebuild()
VoltageClampSeriesResistanceCompPrediction.model_rebuild()
VoltageClampSeriesWholeCellCapacitanceComp.model_rebuild()
VoltageClampSeriesWholeCellSeriesResistanceComp.model_rebuild()
VoltageClampStimulusSeriesData.model_rebuild()
SweepTableSeriesIndex.model_rebuild()
IntracellularStimuliTableStimulus.model_rebuild()
IntracellularResponsesTableResponse.model_rebuild()
SimultaneousRecordingsTableRecordings.model_rebuild()
SimultaneousRecordingsTableRecordingsIndex.model_rebuild()
SequentialRecordingsTableSimultaneousRecordings.model_rebuild()
SequentialRecordingsTableSimultaneousRecordingsIndex.model_rebuild()
RepetitionsTableSequentialRecordings.model_rebuild()
RepetitionsTableSequentialRecordingsIndex.model_rebuild()
ExperimentalConditionsTableRepetitions.model_rebuild()
ExperimentalConditionsTableRepetitionsIndex.model_rebuild()
    