from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, Field
import sys
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


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


class FlatDType(str, Enum):
    
    
    float = "float"
    
    float32 = "float32"
    
    double = "double"
    
    float64 = "float64"
    
    long = "long"
    
    int64 = "int64"
    
    int = "int"
    
    int32 = "int32"
    
    int16 = "int16"
    
    short = "short"
    
    int8 = "int8"
    
    uint = "uint"
    
    uint32 = "uint32"
    
    uint16 = "uint16"
    
    uint8 = "uint8"
    
    uint64 = "uint64"
    
    numeric = "numeric"
    
    text = "text"
    
    utf = "utf"
    
    utf8 = "utf8"
    
    utf_8 = "utf_8"
    
    ascii = "ascii"
    
    bool = "bool"
    
    isodatetime = "isodatetime"
    
    

class PatchClampSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage or current.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    array: Optional[PatchClampSeriesDataArray] = Field(None)
    

class PatchClampSeriesGain(ConfiguredBaseModel):
    """
    Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).
    """
    None
    

class CurrentClampSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. which is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    

class CurrentClampSeriesBiasCurrent(ConfiguredBaseModel):
    """
    Bias current, in amps.
    """
    None
    

class CurrentClampSeriesBridgeBalance(ConfiguredBaseModel):
    """
    Bridge balance, in ohms.
    """
    None
    

class CurrentClampSeriesCapacitanceCompensation(ConfiguredBaseModel):
    """
    Capacitance compensation, in farads.
    """
    None
    

class IZeroClampSeriesBiasCurrent(ConfiguredBaseModel):
    """
    Bias current, in amps, fixed to 0.0.
    """
    None
    

class IZeroClampSeriesBridgeBalance(ConfiguredBaseModel):
    """
    Bridge balance, in ohms, fixed to 0.0.
    """
    None
    

class IZeroClampSeriesCapacitanceCompensation(ConfiguredBaseModel):
    """
    Capacitance compensation, in farads, fixed to 0.0.
    """
    None
    

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
    

class IntracellularElectrodeCellId(ConfiguredBaseModel):
    """
    unique ID of the cell
    """
    None
    

class IntracellularElectrodeDescription(ConfiguredBaseModel):
    """
    Description of electrode (e.g.,  whole-cell, sharp, etc.).
    """
    None
    

class IntracellularElectrodeFiltering(ConfiguredBaseModel):
    """
    Electrode specific filtering.
    """
    None
    

class IntracellularElectrodeInitialAccessResistance(ConfiguredBaseModel):
    """
    Initial access resistance.
    """
    None
    

class IntracellularElectrodeLocation(ConfiguredBaseModel):
    """
    Location of the electrode. Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.
    """
    None
    

class IntracellularElectrodeResistance(ConfiguredBaseModel):
    """
    Electrode resistance, in ohms.
    """
    None
    

class IntracellularElectrodeSeal(ConfiguredBaseModel):
    """
    Information about seal used for recording.
    """
    None
    

class IntracellularElectrodeSlice(ConfiguredBaseModel):
    """
    Information about slice used for recording.
    """
    None
    

class Arraylike(ConfiguredBaseModel):
    """
    Container for arraylike information held in the dims, shape, and dtype properties.this is a special case to be interpreted by downstream i/o. this class has no slotsand is abstract by default.- Each slot within a subclass indicates a possible dimension.- Only dimensions that are present in all the dimension specifiers in the  original schema are required.- Shape requirements are indicated using max/min cardinalities on the slot.
    """
    None
    

class PatchClampSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    

class VectorDataArray(Arraylike):
    
    dim0: Any = Field(...)
    dim1: Optional[Any] = Field(None)
    dim2: Optional[Any] = Field(None)
    dim3: Optional[Any] = Field(None)
    

class VectorIndexArray(Arraylike):
    
    num_rows: int = Field(...)
    

class ElementIdentifiersArray(Arraylike):
    
    num_elements: int = Field(...)
    

class DynamicTableRegionArray(Arraylike):
    
    num_rows: int = Field(...)
    

class DynamicTableIdArray(Arraylike):
    
    num_rows: int = Field(...)
    

class Data(ConfiguredBaseModel):
    """
    An abstract data type for a dataset.
    """
    None
    

class VectorData(Data):
    """
    An n-dimensional dataset representing a column of a DynamicTable. If used without an accompanying VectorIndex, first dimension is along the rows of the DynamicTable and each step along the first dimension is a cell of the larger table. VectorData can also be used to represent a ragged array if paired with a VectorIndex. This allows for storing arrays of varying length in a single cell of the DynamicTable by indexing into this VectorData. The first vector is at VectorData[0:VectorIndex[0]]. The second vector is at VectorData[VectorIndex[0]:VectorIndex[1]], and so on.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class SweepTableSweepNumber(VectorData):
    """
    Sweep number of the PatchClampSeries in that row.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class SweepTableSeries(VectorData):
    """
    The PatchClampSeries with the sweep number in that row.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class IntracellularElectrodesTableElectrode(VectorData):
    """
    Column for storing the reference to the intracellular electrode.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class SequentialRecordingsTableStimulusType(VectorData):
    """
    The type of stimulus used for the sequential recording.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class VectorIndex(VectorData):
    """
    Used with VectorData to encode a ragged array. An array of indices into the first dimension of the target VectorData, and forming a map between the rows of a DynamicTable and the indices of the VectorData. The name of the VectorIndex is expected to be the name of the target VectorData object followed by \"_index\".
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class SweepTableSeriesIndex(VectorIndex):
    """
    Index for series.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class SimultaneousRecordingsTableRecordingsIndex(VectorIndex):
    """
    Index dataset for the recordings column.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class SequentialRecordingsTableSimultaneousRecordingsIndex(VectorIndex):
    """
    Index dataset for the simultaneous_recordings column.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class RepetitionsTableSequentialRecordingsIndex(VectorIndex):
    """
    Index dataset for the sequential_recordings column.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class ExperimentalConditionsTableRepetitionsIndex(VectorIndex):
    """
    Index dataset for the repetitions column.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class ElementIdentifiers(Data):
    """
    A list of unique identifiers for values within a dataset, e.g. rows of a DynamicTable.
    """
    array: Optional[ElementIdentifiersArray] = Field(None)
    

class DynamicTableRegion(VectorData):
    """
    DynamicTableRegion provides a link from one table to an index or region of another. The `table` attribute is a link to another `DynamicTable`, indicating which table is referenced, and the data is int(s) indicating the row(s) (0-indexed) of the target array. `DynamicTableRegion`s can be used to associate rows with repeated meta-data without data duplication. They can also be used to create hierarchical relationships between multiple `DynamicTable`s. `DynamicTableRegion` objects may be paired with a `VectorIndex` object to create ragged references, so a single cell of a `DynamicTable` can reference many rows of another `DynamicTable`.
    """
    table: Optional[DynamicTable] = Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class SimultaneousRecordingsTableRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the IntracellularRecordingsTable table.
    """
    table: Optional[IntracellularRecordingsTable] = Field(None, description="""Reference to the IntracellularRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class SequentialRecordingsTableSimultaneousRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the SimultaneousRecordingsTable table.
    """
    table: Optional[SimultaneousRecordingsTable] = Field(None, description="""Reference to the SimultaneousRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class RepetitionsTableSequentialRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the SequentialRecordingsTable table.
    """
    table: Optional[SequentialRecordingsTable] = Field(None, description="""Reference to the SequentialRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class ExperimentalConditionsTableRepetitions(DynamicTableRegion):
    """
    A reference to one or more rows in the RepetitionsTable table.
    """
    table: Optional[RepetitionsTable] = Field(None, description="""Reference to the RepetitionsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class DynamicTableId(ElementIdentifiers):
    """
    Array of unique identifiers for the rows of this dynamic table.
    """
    array: Optional[DynamicTableIdArray] = Field(None)
    

class Container(ConfiguredBaseModel):
    """
    An abstract data type for a group storing collections of data and metadata. Base type for all data and metadata containers.
    """
    None
    

class DynamicTable(Container):
    """
    A group containing multiple datasets that are aligned on the first dimension (Currently, this requirement if left up to APIs to check and enforce). These datasets represent different columns in the table. Apart from a column that contains unique identifiers for each row, there are no other required datasets. Users are free to add any number of custom VectorData objects (columns) here. DynamicTable also supports ragged array columns, where each element can be of a different size. To add a ragged array column, use a VectorIndex type to index the corresponding VectorData type. See documentation for VectorData and VectorIndex for more details. Unlike a compound data type, which is analogous to storing an array-of-structs, a DynamicTable can be thought of as a struct-of-arrays. This provides an alternative structure to choose from when optimizing storage for anticipated access patterns. Additionally, this type provides a way of creating a table without having to define a compound type up front. Although this convenience may be attractive, users should think carefully about how data will be accessed. DynamicTable is more appropriate for column-centric access, whereas a dataset with a compound type would be more appropriate for row-centric access. Finally, data size should also be taken into account. For small tables, performance loss may be an acceptable trade-off for the flexibility of a DynamicTable.
    """
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class SweepTable(DynamicTable):
    """
    [DEPRECATED] Table used to group different PatchClampSeries. SweepTable is being replaced by IntracellularRecordingsTable and SimultaneousRecordingsTable tables. Additional SequentialRecordingsTable, RepetitionsTable, and ExperimentalConditions tables provide enhanced support for experiment metadata.
    """
    sweep_number: SweepTableSweepNumber = Field(..., description="""Sweep number of the PatchClampSeries in that row.""")
    series: SweepTableSeries = Field(..., description="""The PatchClampSeries with the sweep number in that row.""")
    series_index: SweepTableSeriesIndex = Field(..., description="""Index for series.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularElectrodesTable(DynamicTable):
    """
    Table for storing intracellular electrode related metadata.
    """
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    electrode: IntracellularElectrodesTableElectrode = Field(..., description="""Column for storing the reference to the intracellular electrode.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularStimuliTable(DynamicTable):
    """
    Table for storing intracellular stimulus related metadata.
    """
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    stimulus: IntracellularStimuliTableStimulus = Field(..., description="""Column storing the reference to the recorded stimulus for the recording (rows).""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularResponsesTable(DynamicTable):
    """
    Table for storing intracellular response related metadata.
    """
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    response: IntracellularResponsesTableResponse = Field(..., description="""Column storing the reference to the recorded response for the recording (rows)""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularRecordingsTableElectrodes(IntracellularElectrodesTable):
    """
    Table for storing intracellular electrode related metadata.
    """
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    electrode: IntracellularElectrodesTableElectrode = Field(..., description="""Column for storing the reference to the intracellular electrode.""")
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
    

class SimultaneousRecordingsTable(DynamicTable):
    """
    A table for grouping different intracellular recordings from the IntracellularRecordingsTable table together that were recorded simultaneously from different electrodes.
    """
    recordings: SimultaneousRecordingsTableRecordings = Field(..., description="""A reference to one or more rows in the IntracellularRecordingsTable table.""")
    recordings_index: SimultaneousRecordingsTableRecordingsIndex = Field(..., description="""Index dataset for the recordings column.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class SequentialRecordingsTable(DynamicTable):
    """
    A table for grouping different sequential recordings from the SimultaneousRecordingsTable table together. This is typically used to group together sequential recordings where a sequence of stimuli of the same type with varying parameters have been presented in a sequence.
    """
    simultaneous_recordings: SequentialRecordingsTableSimultaneousRecordings = Field(..., description="""A reference to one or more rows in the SimultaneousRecordingsTable table.""")
    simultaneous_recordings_index: SequentialRecordingsTableSimultaneousRecordingsIndex = Field(..., description="""Index dataset for the simultaneous_recordings column.""")
    stimulus_type: SequentialRecordingsTableStimulusType = Field(..., description="""The type of stimulus used for the sequential recording.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class RepetitionsTable(DynamicTable):
    """
    A table for grouping different sequential intracellular recordings together. With each SequentialRecording typically representing a particular type of stimulus, the RepetitionsTable table is typically used to group sets of stimuli applied in sequence.
    """
    sequential_recordings: RepetitionsTableSequentialRecordings = Field(..., description="""A reference to one or more rows in the SequentialRecordingsTable table.""")
    sequential_recordings_index: RepetitionsTableSequentialRecordingsIndex = Field(..., description="""Index dataset for the sequential_recordings column.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class ExperimentalConditionsTable(DynamicTable):
    """
    A table for grouping different intracellular recording repetitions together that belong to the same experimental condition.
    """
    repetitions: ExperimentalConditionsTableRepetitions = Field(..., description="""A reference to one or more rows in the RepetitionsTable table.""")
    repetitions_index: ExperimentalConditionsTableRepetitionsIndex = Field(..., description="""Index dataset for the repetitions column.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class AlignedDynamicTable(DynamicTable):
    """
    DynamicTable container that supports storing a collection of sub-tables. Each sub-table is a DynamicTable itself that is aligned with the main table by row index. I.e., all DynamicTables stored in this group MUST have the same number of rows. This type effectively defines a 2-level table in which the main data is stored in the main table implemented by this type and additional columns of the table are grouped into categories, with each category being represented by a separate DynamicTable stored within the group.
    """
    categories: Optional[str] = Field(None, description="""The names of the categories in this AlignedDynamicTable. Each category is represented by one DynamicTable stored in the parent group. This attribute should be used to specify an order of categories and the category names must match the names of the corresponding DynamicTable in the group.""")
    DynamicTable: Optional[List[DynamicTable]] = Field(default_factory=list, description="""A DynamicTable representing a particular category for columns in the AlignedDynamicTable parent container. The table MUST be aligned with (i.e., have the same number of rows) as all other DynamicTables stored in the AlignedDynamicTable parent container. The name of the category is given by the name of the DynamicTable and its description by the description attribute of the DynamicTable.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularRecordingsTable(AlignedDynamicTable):
    """
    A table to group together a stimulus and response from a single electrode and a single simultaneous recording. Each row in the table represents a single recording consisting typically of a stimulus and a corresponding response. In some cases, however, only a stimulus or a response is recorded as part of an experiment. In this case, both the stimulus and response will point to the same TimeSeries while the idx_start and count of the invalid column will be set to -1, thus, indicating that no values have been recorded for the stimulus or response, respectively. Note, a recording MUST contain at least a stimulus or a response. Typically the stimulus and response are PatchClampSeries. However, the use of AD/DA channels that are not associated to an electrode is also common in intracellular electrophysiology, in which case other TimeSeries may be used.
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
    

class SimpleMultiContainer(Container):
    """
    A simple Container for holding onto multiple containers.
    """
    Data: Optional[List[Data]] = Field(default_factory=list, description="""Data objects held within this SimpleMultiContainer.""")
    Container: Optional[List[Container]] = Field(default_factory=list, description="""Container objects held within this SimpleMultiContainer.""")
    

class NWBData(Data):
    """
    An abstract data type for a dataset.
    """
    None
    

class TimeSeriesReferenceVectorData(VectorData):
    """
    Column storing references to a TimeSeries (rows). For each TimeSeries this VectorData column stores the start_index and count to indicate the range in time to be selected as well as an object reference to the TimeSeries.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class IntracellularStimuliTableStimulus(TimeSeriesReferenceVectorData):
    """
    Column storing the reference to the recorded stimulus for the recording (rows).
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class IntracellularResponsesTableResponse(TimeSeriesReferenceVectorData):
    """
    Column storing the reference to the recorded response for the recording (rows)
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class Image(NWBData):
    """
    An abstract data type for an image. Shape can be 2-D (x, y), or 3-D where the third dimension can have three or four elements, e.g. (x, y, (r, g, b)) or (x, y, (r, g, b, a)).
    """
    resolution: Optional[float] = Field(None, description="""Pixel resolution of the image, in pixels per centimeter.""")
    description: Optional[str] = Field(None, description="""Description of the image.""")
    array: Optional[ImageArray] = Field(None)
    

class ImageArray(Arraylike):
    
    x: float = Field(...)
    y: float = Field(...)
    r_g_b: Optional[float] = Field(None)
    r_g_b_a: Optional[float] = Field(None)
    

class ImageReferences(NWBData):
    """
    Ordered dataset of references to Image objects.
    """
    array: Optional[ImageReferencesArray] = Field(None)
    

class ImageReferencesArray(Arraylike):
    
    num_images: Image = Field(...)
    

class NWBContainer(Container):
    """
    An abstract data type for a generic container storing collections of data and metadata. Base type for all data and metadata containers.
    """
    None
    

class IntracellularElectrode(NWBContainer):
    """
    An intracellular electrode and its metadata.
    """
    cell_id: Optional[IntracellularElectrodeCellId] = Field(None, description="""unique ID of the cell""")
    description: IntracellularElectrodeDescription = Field(..., description="""Description of electrode (e.g.,  whole-cell, sharp, etc.).""")
    filtering: Optional[IntracellularElectrodeFiltering] = Field(None, description="""Electrode specific filtering.""")
    initial_access_resistance: Optional[IntracellularElectrodeInitialAccessResistance] = Field(None, description="""Initial access resistance.""")
    location: Optional[IntracellularElectrodeLocation] = Field(None, description="""Location of the electrode. Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""")
    resistance: Optional[IntracellularElectrodeResistance] = Field(None, description="""Electrode resistance, in ohms.""")
    seal: Optional[IntracellularElectrodeSeal] = Field(None, description="""Information about seal used for recording.""")
    slice: Optional[IntracellularElectrodeSlice] = Field(None, description="""Information about slice used for recording.""")
    

class NWBDataInterface(NWBContainer):
    """
    An abstract data type for a generic container storing collections of data, as opposed to metadata.
    """
    None
    

class TimeSeries(NWBDataInterface):
    """
    General purpose time series.
    """
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    data: TimeSeriesData = Field(..., description="""Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension should always represent time. This can also be used to store binary data (e.g., image frames). This can also be a link to data stored in an external file.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class PatchClampSeries(TimeSeries):
    """
    An abstract base class for patch-clamp data - stimulus or response, current or voltage.
    """
    stimulus_description: Optional[str] = Field(None, description="""Protocol/stimulus name for this patch-clamp dataset.""")
    sweep_number: Optional[int] = Field(None, description="""Sweep number, allows to group different PatchClampSeries together.""")
    data: PatchClampSeriesData = Field(..., description="""Recorded voltage or current.""")
    gain: Optional[PatchClampSeriesGain] = Field(None, description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class CurrentClampSeries(PatchClampSeries):
    """
    Voltage data from an intracellular current-clamp recording. A corresponding CurrentClampStimulusSeries (stored separately as a stimulus) is used to store the current injected.
    """
    data: CurrentClampSeriesData = Field(..., description="""Recorded voltage.""")
    bias_current: Optional[CurrentClampSeriesBiasCurrent] = Field(None, description="""Bias current, in amps.""")
    bridge_balance: Optional[CurrentClampSeriesBridgeBalance] = Field(None, description="""Bridge balance, in ohms.""")
    capacitance_compensation: Optional[CurrentClampSeriesCapacitanceCompensation] = Field(None, description="""Capacitance compensation, in farads.""")
    stimulus_description: Optional[str] = Field(None, description="""Protocol/stimulus name for this patch-clamp dataset.""")
    sweep_number: Optional[int] = Field(None, description="""Sweep number, allows to group different PatchClampSeries together.""")
    gain: Optional[PatchClampSeriesGain] = Field(None, description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class IZeroClampSeries(CurrentClampSeries):
    """
    Voltage data from an intracellular recording when all current and amplifier settings are off (i.e., CurrentClampSeries fields will be zero). There is no CurrentClampStimulusSeries associated with an IZero series because the amplifier is disconnected and no stimulus can reach the cell.
    """
    stimulus_description: Optional[str] = Field(None, description="""An IZeroClampSeries has no stimulus, so this attribute is automatically set to \"N/A\"""")
    bias_current: IZeroClampSeriesBiasCurrent = Field(..., description="""Bias current, in amps, fixed to 0.0.""")
    bridge_balance: IZeroClampSeriesBridgeBalance = Field(..., description="""Bridge balance, in ohms, fixed to 0.0.""")
    capacitance_compensation: IZeroClampSeriesCapacitanceCompensation = Field(..., description="""Capacitance compensation, in farads, fixed to 0.0.""")
    data: CurrentClampSeriesData = Field(..., description="""Recorded voltage.""")
    sweep_number: Optional[int] = Field(None, description="""Sweep number, allows to group different PatchClampSeries together.""")
    gain: Optional[PatchClampSeriesGain] = Field(None, description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class CurrentClampStimulusSeries(PatchClampSeries):
    """
    Stimulus current applied during current clamp recording.
    """
    data: CurrentClampStimulusSeriesData = Field(..., description="""Stimulus current applied.""")
    stimulus_description: Optional[str] = Field(None, description="""Protocol/stimulus name for this patch-clamp dataset.""")
    sweep_number: Optional[int] = Field(None, description="""Sweep number, allows to group different PatchClampSeries together.""")
    gain: Optional[PatchClampSeriesGain] = Field(None, description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class VoltageClampSeries(PatchClampSeries):
    """
    Current data from an intracellular voltage-clamp recording. A corresponding VoltageClampStimulusSeries (stored separately as a stimulus) is used to store the voltage injected.
    """
    data: VoltageClampSeriesData = Field(..., description="""Recorded current.""")
    capacitance_fast: Optional[VoltageClampSeriesCapacitanceFast] = Field(None, description="""Fast capacitance, in farads.""")
    capacitance_slow: Optional[VoltageClampSeriesCapacitanceSlow] = Field(None, description="""Slow capacitance, in farads.""")
    resistance_comp_bandwidth: Optional[VoltageClampSeriesResistanceCompBandwidth] = Field(None, description="""Resistance compensation bandwidth, in hertz.""")
    resistance_comp_correction: Optional[VoltageClampSeriesResistanceCompCorrection] = Field(None, description="""Resistance compensation correction, in percent.""")
    resistance_comp_prediction: Optional[VoltageClampSeriesResistanceCompPrediction] = Field(None, description="""Resistance compensation prediction, in percent.""")
    whole_cell_capacitance_comp: Optional[VoltageClampSeriesWholeCellCapacitanceComp] = Field(None, description="""Whole cell capacitance compensation, in farads.""")
    whole_cell_series_resistance_comp: Optional[VoltageClampSeriesWholeCellSeriesResistanceComp] = Field(None, description="""Whole cell series resistance compensation, in ohms.""")
    stimulus_description: Optional[str] = Field(None, description="""Protocol/stimulus name for this patch-clamp dataset.""")
    sweep_number: Optional[int] = Field(None, description="""Sweep number, allows to group different PatchClampSeries together.""")
    gain: Optional[PatchClampSeriesGain] = Field(None, description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class VoltageClampStimulusSeries(PatchClampSeries):
    """
    Stimulus voltage applied during a voltage clamp recording.
    """
    data: VoltageClampStimulusSeriesData = Field(..., description="""Stimulus voltage applied.""")
    stimulus_description: Optional[str] = Field(None, description="""Protocol/stimulus name for this patch-clamp dataset.""")
    sweep_number: Optional[int] = Field(None, description="""Sweep number, allows to group different PatchClampSeries together.""")
    gain: Optional[PatchClampSeriesGain] = Field(None, description="""Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class TimeSeriesData(ConfiguredBaseModel):
    """
    Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension should always represent time. This can also be used to store binary data (e.g., image frames). This can also be a link to data stored in an external file.
    """
    conversion: Optional[float] = Field(None, description="""Scalar to multiply each element in data to convert it to the specified 'unit'. If the data are stored in acquisition system units or other units that require a conversion to be interpretable, multiply the data by 'conversion' to convert the data to the specified 'unit'. e.g. if the data acquisition system stores values in this object as signed 16-bit integers (int16 range -32,768 to 32,767) that correspond to a 5V range (-2.5V to 2.5V), and the data acquisition system gain is 8000X, then the 'conversion' multiplier to get from raw data acquisition values to recorded volts is 2.5/32768/8000 = 9.5367e-9.""")
    offset: Optional[float] = Field(None, description="""Scalar to add to the data after scaling by 'conversion' to finalize its coercion to the specified 'unit'. Two common examples of this include (a) data stored in an unsigned type that requires a shift after scaling to re-center the data, and (b) specialized recording devices that naturally cause a scalar offset with respect to the true units.""")
    resolution: Optional[float] = Field(None, description="""Smallest meaningful difference between values in data, stored in the specified by unit, e.g., the change in value of the least significant bit, or a larger number if signal noise is known to be present. If unknown, use -1.0.""")
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    continuity: Optional[str] = Field(None, description="""Optionally describe the continuity of the data. Can be \"continuous\", \"instantaneous\", or \"step\". For example, a voltage trace would be \"continuous\", because samples are recorded from a continuous process. An array of lick times would be \"instantaneous\", because the data represents distinct moments in time. Times of image presentations would be \"step\" because the picture remains the same until the next timepoint. This field is optional, but is useful in providing information about the underlying data. It may inform the way this data is interpreted, the way it is visualized, and what analysis methods are applicable.""")
    array: Optional[TimeSeriesDataArray] = Field(None)
    

class TimeSeriesDataArray(Arraylike):
    
    num_times: Any = Field(...)
    num_DIM2: Optional[Any] = Field(None)
    num_DIM3: Optional[Any] = Field(None)
    num_DIM4: Optional[Any] = Field(None)
    

class TimeSeriesStartingTime(ConfiguredBaseModel):
    """
    Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.
    """
    rate: Optional[float] = Field(None, description="""Sampling rate, in Hz.""")
    unit: Optional[str] = Field(None, description="""Unit of measurement for time, which is fixed to 'seconds'.""")
    

class TimeSeriesTimestamps(ConfiguredBaseModel):
    """
    Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.
    """
    interval: Optional[int] = Field(None, description="""Value is '1'""")
    unit: Optional[str] = Field(None, description="""Unit of measurement for timestamps, which is fixed to 'seconds'.""")
    array: Optional[TimeSeriesTimestampsArray] = Field(None)
    

class TimeSeriesTimestampsArray(Arraylike):
    
    num_times: float = Field(...)
    

class TimeSeriesControl(ConfiguredBaseModel):
    """
    Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.
    """
    array: Optional[TimeSeriesControlArray] = Field(None)
    

class TimeSeriesControlArray(Arraylike):
    
    num_times: int = Field(...)
    

class TimeSeriesControlDescription(ConfiguredBaseModel):
    """
    Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.
    """
    array: Optional[TimeSeriesControlDescriptionArray] = Field(None)
    

class TimeSeriesControlDescriptionArray(Arraylike):
    
    num_control_values: str = Field(...)
    

class TimeSeriesSync(ConfiguredBaseModel):
    """
    Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.
    """
    None
    

class ProcessingModule(NWBContainer):
    """
    A collection of processed data.
    """
    description: Optional[str] = Field(None, description="""Description of this collection of processed data.""")
    NWBDataInterface: Optional[List[NWBDataInterface]] = Field(default_factory=list, description="""Data objects stored in this collection.""")
    DynamicTable: Optional[List[DynamicTable]] = Field(default_factory=list, description="""Tables stored in this collection.""")
    

class Images(NWBDataInterface):
    """
    A collection of images with an optional way to specify the order of the images using the \"order_of_images\" dataset. An order must be specified if the images are referenced by index, e.g., from an IndexSeries.
    """
    description: Optional[str] = Field(None, description="""Description of this collection of images.""")
    Image: List[Image] = Field(default_factory=list, description="""Images stored in this collection.""")
    order_of_images: Optional[ImagesOrderOfImages] = Field(None, description="""Ordered dataset of references to Image objects stored in the parent group. Each Image object in the Images group should be stored once and only once, so the dataset should have the same length as the number of images.""")
    

class ImagesOrderOfImages(ImageReferences):
    """
    Ordered dataset of references to Image objects stored in the parent group. Each Image object in the Images group should be stored once and only once, so the dataset should have the same length as the number of images.
    """
    array: Optional[ImageReferencesArray] = Field(None)
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
PatchClampSeriesData.update_forward_refs()
PatchClampSeriesGain.update_forward_refs()
CurrentClampSeriesData.update_forward_refs()
CurrentClampSeriesBiasCurrent.update_forward_refs()
CurrentClampSeriesBridgeBalance.update_forward_refs()
CurrentClampSeriesCapacitanceCompensation.update_forward_refs()
IZeroClampSeriesBiasCurrent.update_forward_refs()
IZeroClampSeriesBridgeBalance.update_forward_refs()
IZeroClampSeriesCapacitanceCompensation.update_forward_refs()
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
IntracellularElectrodeCellId.update_forward_refs()
IntracellularElectrodeDescription.update_forward_refs()
IntracellularElectrodeFiltering.update_forward_refs()
IntracellularElectrodeInitialAccessResistance.update_forward_refs()
IntracellularElectrodeLocation.update_forward_refs()
IntracellularElectrodeResistance.update_forward_refs()
IntracellularElectrodeSeal.update_forward_refs()
IntracellularElectrodeSlice.update_forward_refs()
Arraylike.update_forward_refs()
PatchClampSeriesDataArray.update_forward_refs()
VectorDataArray.update_forward_refs()
VectorIndexArray.update_forward_refs()
ElementIdentifiersArray.update_forward_refs()
DynamicTableRegionArray.update_forward_refs()
DynamicTableIdArray.update_forward_refs()
Data.update_forward_refs()
VectorData.update_forward_refs()
SweepTableSweepNumber.update_forward_refs()
SweepTableSeries.update_forward_refs()
IntracellularElectrodesTableElectrode.update_forward_refs()
SequentialRecordingsTableStimulusType.update_forward_refs()
VectorIndex.update_forward_refs()
SweepTableSeriesIndex.update_forward_refs()
SimultaneousRecordingsTableRecordingsIndex.update_forward_refs()
SequentialRecordingsTableSimultaneousRecordingsIndex.update_forward_refs()
RepetitionsTableSequentialRecordingsIndex.update_forward_refs()
ExperimentalConditionsTableRepetitionsIndex.update_forward_refs()
ElementIdentifiers.update_forward_refs()
DynamicTableRegion.update_forward_refs()
SimultaneousRecordingsTableRecordings.update_forward_refs()
SequentialRecordingsTableSimultaneousRecordings.update_forward_refs()
RepetitionsTableSequentialRecordings.update_forward_refs()
ExperimentalConditionsTableRepetitions.update_forward_refs()
DynamicTableId.update_forward_refs()
Container.update_forward_refs()
DynamicTable.update_forward_refs()
SweepTable.update_forward_refs()
IntracellularElectrodesTable.update_forward_refs()
IntracellularStimuliTable.update_forward_refs()
IntracellularResponsesTable.update_forward_refs()
IntracellularRecordingsTableElectrodes.update_forward_refs()
IntracellularRecordingsTableStimuli.update_forward_refs()
IntracellularRecordingsTableResponses.update_forward_refs()
SimultaneousRecordingsTable.update_forward_refs()
SequentialRecordingsTable.update_forward_refs()
RepetitionsTable.update_forward_refs()
ExperimentalConditionsTable.update_forward_refs()
AlignedDynamicTable.update_forward_refs()
IntracellularRecordingsTable.update_forward_refs()
SimpleMultiContainer.update_forward_refs()
NWBData.update_forward_refs()
TimeSeriesReferenceVectorData.update_forward_refs()
IntracellularStimuliTableStimulus.update_forward_refs()
IntracellularResponsesTableResponse.update_forward_refs()
Image.update_forward_refs()
ImageArray.update_forward_refs()
ImageReferences.update_forward_refs()
ImageReferencesArray.update_forward_refs()
NWBContainer.update_forward_refs()
IntracellularElectrode.update_forward_refs()
NWBDataInterface.update_forward_refs()
TimeSeries.update_forward_refs()
PatchClampSeries.update_forward_refs()
CurrentClampSeries.update_forward_refs()
IZeroClampSeries.update_forward_refs()
CurrentClampStimulusSeries.update_forward_refs()
VoltageClampSeries.update_forward_refs()
VoltageClampStimulusSeries.update_forward_refs()
TimeSeriesData.update_forward_refs()
TimeSeriesDataArray.update_forward_refs()
TimeSeriesStartingTime.update_forward_refs()
TimeSeriesTimestamps.update_forward_refs()
TimeSeriesTimestampsArray.update_forward_refs()
TimeSeriesControl.update_forward_refs()
TimeSeriesControlArray.update_forward_refs()
TimeSeriesControlDescription.update_forward_refs()
TimeSeriesControlDescriptionArray.update_forward_refs()
TimeSeriesSync.update_forward_refs()
ProcessingModule.update_forward_refs()
Images.update_forward_refs()
ImagesOrderOfImages.update_forward_refs()
