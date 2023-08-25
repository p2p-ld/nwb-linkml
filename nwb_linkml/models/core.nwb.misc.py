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
    
    

class AbstractFeatureSeriesData(ConfiguredBaseModel):
    """
    Values of each feature at each time.
    """
    unit: Optional[str] = Field(None, description="""Since there can be different units for different features, store the units in 'feature_units'. The default value for this attribute is \"see 'feature_units'\".""")
    array: Optional[AbstractFeatureSeriesDataArray] = Field(None)
    

class AbstractFeatureSeriesFeatureUnits(ConfiguredBaseModel):
    """
    Units of each feature.
    """
    array: Optional[AbstractFeatureSeriesFeatureUnitsArray] = Field(None)
    

class AbstractFeatureSeriesFeatures(ConfiguredBaseModel):
    """
    Description of the features represented in TimeSeries::data.
    """
    array: Optional[AbstractFeatureSeriesFeaturesArray] = Field(None)
    

class AnnotationSeriesData(ConfiguredBaseModel):
    """
    Annotations made during an experiment.
    """
    resolution: Optional[float] = Field(None, description="""Smallest meaningful difference between values in data. Annotations have no units, so the value is fixed to -1.0.""")
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. Annotations have no units, so the value is fixed to 'n/a'.""")
    array: Optional[AnnotationSeriesDataArray] = Field(None)
    

class IntervalSeriesData(ConfiguredBaseModel):
    """
    Use values >0 if interval started, <0 if interval ended.
    """
    resolution: Optional[float] = Field(None, description="""Smallest meaningful difference between values in data. Annotations have no units, so the value is fixed to -1.0.""")
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. Annotations have no units, so the value is fixed to 'n/a'.""")
    array: Optional[IntervalSeriesDataArray] = Field(None)
    

class DecompositionSeriesData(ConfiguredBaseModel):
    """
    Data decomposed into frequency bands.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""")
    array: Optional[DecompositionSeriesDataArray] = Field(None)
    

class DecompositionSeriesMetric(ConfiguredBaseModel):
    """
    The metric used, e.g. phase, amplitude, power.
    """
    None
    

class Arraylike(ConfiguredBaseModel):
    """
    Container for arraylike information held in the dims, shape, and dtype properties.this is a special case to be interpreted by downstream i/o. this class has no slotsand is abstract by default.- Each slot within a subclass indicates a possible dimension.- Only dimensions that are present in all the dimension specifiers in the  original schema are required.- Shape requirements are indicated using max/min cardinalities on the slot.
    """
    None
    

class AbstractFeatureSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    num_features: Optional[float] = Field(None)
    

class AbstractFeatureSeriesFeatureUnitsArray(Arraylike):
    
    num_features: str = Field(...)
    

class AbstractFeatureSeriesFeaturesArray(Arraylike):
    
    num_features: str = Field(...)
    

class AnnotationSeriesDataArray(Arraylike):
    
    num_times: str = Field(...)
    

class IntervalSeriesDataArray(Arraylike):
    
    num_times: int = Field(...)
    

class DecompositionSeriesDataArray(Arraylike):
    
    num_times: Optional[float] = Field(None)
    num_channels: Optional[float] = Field(None)
    num_bands: Optional[float] = Field(None)
    

class DecompositionSeriesBandsBandLimitsArray(Arraylike):
    
    num_bands: Optional[float] = Field(None)
    low_high: Optional[float] = Field(None)
    

class DecompositionSeriesBandsBandMeanArray(Arraylike):
    
    num_bands: float = Field(...)
    

class DecompositionSeriesBandsBandStdevArray(Arraylike):
    
    num_bands: float = Field(...)
    

class UnitsObsIntervalsArray(Arraylike):
    
    num_intervals: Optional[float] = Field(None)
    start|end: Optional[float] = Field(None)
    

class UnitsWaveformMeanArray(Arraylike):
    
    num_units: float = Field(...)
    num_samples: float = Field(...)
    num_electrodes: Optional[float] = Field(None)
    

class UnitsWaveformSdArray(Arraylike):
    
    num_units: float = Field(...)
    num_samples: float = Field(...)
    num_electrodes: Optional[float] = Field(None)
    

class UnitsWaveformsArray(Arraylike):
    
    num_waveforms: Optional[float] = Field(None)
    num_samples: Optional[float] = Field(None)
    

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
    

class DecompositionSeriesBandsBandName(VectorData):
    """
    Name of the band, e.g. theta.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class DecompositionSeriesBandsBandLimits(VectorData):
    """
    Low and high limit of each band in Hz. If it is a Gaussian filter, use 2 SD on either side of the center.
    """
    array: Optional[DecompositionSeriesBandsBandLimitsArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class DecompositionSeriesBandsBandMean(VectorData):
    """
    The mean Gaussian filters, in Hz.
    """
    array: Optional[DecompositionSeriesBandsBandMeanArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class DecompositionSeriesBandsBandStdev(VectorData):
    """
    The standard deviation of Gaussian filters, in Hz.
    """
    array: Optional[DecompositionSeriesBandsBandStdevArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsSpikeTimes(VectorData):
    """
    Spike times for each unit in seconds.
    """
    resolution: Optional[float] = Field(None, description="""The smallest possible difference between two spike times. Usually 1 divided by the acquisition sampling rate from which spike times were extracted, but could be larger if the acquisition time series was downsampled or smaller if the acquisition time series was smoothed/interpolated and it is possible for the spike time to be between samples.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class UnitsObsIntervals(VectorData):
    """
    Observation intervals for each unit.
    """
    array: Optional[UnitsObsIntervalsArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsElectrodeGroup(VectorData):
    """
    Electrode group that each spike unit came from.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class UnitsWaveformMean(VectorData):
    """
    Spike waveform mean for each spike unit.
    """
    sampling_rate: Optional[float] = Field(None, description="""Sampling rate, in hertz.""")
    unit: Optional[str] = Field(None, description="""Unit of measurement. This value is fixed to 'volts'.""")
    array: Optional[UnitsWaveformMeanArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsWaveformSd(VectorData):
    """
    Spike waveform standard deviation for each spike unit.
    """
    sampling_rate: Optional[float] = Field(None, description="""Sampling rate, in hertz.""")
    unit: Optional[str] = Field(None, description="""Unit of measurement. This value is fixed to 'volts'.""")
    array: Optional[UnitsWaveformSdArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsWaveforms(VectorData):
    """
    Individual waveforms for each spike on each electrode. This is a doubly indexed column. The 'waveforms_index' column indexes which waveforms in this column belong to the same spike event for a given unit, where each waveform was recorded from a different electrode. The 'waveforms_index_index' column indexes the 'waveforms_index' column to indicate which spike events belong to a given unit. For example, if the 'waveforms_index_index' column has values [2, 5, 6], then the first 2 elements of the 'waveforms_index' column correspond to the 2 spike events of the first unit, the next 3 elements of the 'waveforms_index' column correspond to the 3 spike events of the second unit, and the next 1 element of the 'waveforms_index' column corresponds to the 1 spike event of the third unit. If the 'waveforms_index' column has values [3, 6, 8, 10, 12, 13], then the first 3 elements of the 'waveforms' column contain the 3 spike waveforms that were recorded from 3 different electrodes for the first spike time of the first unit. See https://nwb-schema.readthedocs.io/en/stable/format_description.html#doubly-ragged-arrays for a graphical representation of this example. When there is only one electrode for each unit (i.e., each spike time is associated with a single waveform), then the 'waveforms_index' column will have values 1, 2, ..., N, where N is the number of spike events. The number of electrodes for each spike event should be the same within a given unit. The 'electrodes' column should be used to indicate which electrodes are associated with each unit, and the order of the waveforms within a given unit x spike event should be in the same order as the electrodes referenced in the 'electrodes' column of this table. The number of samples for each waveform must be the same.
    """
    sampling_rate: Optional[float] = Field(None, description="""Sampling rate, in hertz.""")
    unit: Optional[str] = Field(None, description="""Unit of measurement. This value is fixed to 'volts'.""")
    array: Optional[UnitsWaveformsArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class VectorIndex(VectorData):
    """
    Used with VectorData to encode a ragged array. An array of indices into the first dimension of the target VectorData, and forming a map between the rows of a DynamicTable and the indices of the VectorData. The name of the VectorIndex is expected to be the name of the target VectorData object followed by \"_index\".
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsSpikeTimesIndex(VectorIndex):
    """
    Index into the spike_times dataset.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsObsIntervalsIndex(VectorIndex):
    """
    Index into the obs_intervals dataset.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsElectrodesIndex(VectorIndex):
    """
    Index into electrodes.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsWaveformsIndex(VectorIndex):
    """
    Index into the waveforms dataset. One value for every spike event. See 'waveforms' for more detail.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsWaveformsIndexIndex(VectorIndex):
    """
    Index into the waveforms_index dataset. One value for every unit (row in the table). See 'waveforms' for more detail.
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
    

class DecompositionSeriesSourceChannels(DynamicTableRegion):
    """
    DynamicTableRegion pointer to the channels that this decomposition series was generated from.
    """
    table: Optional[DynamicTable] = Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class UnitsElectrodes(DynamicTableRegion):
    """
    Electrode that each spike unit came from, specified using a DynamicTableRegion.
    """
    table: Optional[DynamicTable] = Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
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
    

class DecompositionSeriesBands(DynamicTable):
    """
    Table for describing the bands that this series was generated from. There should be one row in this table for each band.
    """
    band_name: DecompositionSeriesBandsBandName = Field(..., description="""Name of the band, e.g. theta.""")
    band_limits: DecompositionSeriesBandsBandLimits = Field(..., description="""Low and high limit of each band in Hz. If it is a Gaussian filter, use 2 SD on either side of the center.""")
    band_mean: DecompositionSeriesBandsBandMean = Field(..., description="""The mean Gaussian filters, in Hz.""")
    band_stdev: DecompositionSeriesBandsBandStdev = Field(..., description="""The standard deviation of Gaussian filters, in Hz.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class Units(DynamicTable):
    """
    Data about spiking units. Event times of observed units (e.g. cell, synapse, etc.) should be concatenated and stored in spike_times.
    """
    spike_times_index: Optional[UnitsSpikeTimesIndex] = Field(None, description="""Index into the spike_times dataset.""")
    spike_times: Optional[UnitsSpikeTimes] = Field(None, description="""Spike times for each unit in seconds.""")
    obs_intervals_index: Optional[UnitsObsIntervalsIndex] = Field(None, description="""Index into the obs_intervals dataset.""")
    obs_intervals: Optional[UnitsObsIntervals] = Field(None, description="""Observation intervals for each unit.""")
    electrodes_index: Optional[UnitsElectrodesIndex] = Field(None, description="""Index into electrodes.""")
    electrodes: Optional[UnitsElectrodes] = Field(None, description="""Electrode that each spike unit came from, specified using a DynamicTableRegion.""")
    electrode_group: Optional[UnitsElectrodeGroup] = Field(None, description="""Electrode group that each spike unit came from.""")
    waveform_mean: Optional[UnitsWaveformMean] = Field(None, description="""Spike waveform mean for each spike unit.""")
    waveform_sd: Optional[UnitsWaveformSd] = Field(None, description="""Spike waveform standard deviation for each spike unit.""")
    waveforms: Optional[UnitsWaveforms] = Field(None, description="""Individual waveforms for each spike on each electrode. This is a doubly indexed column. The 'waveforms_index' column indexes which waveforms in this column belong to the same spike event for a given unit, where each waveform was recorded from a different electrode. The 'waveforms_index_index' column indexes the 'waveforms_index' column to indicate which spike events belong to a given unit. For example, if the 'waveforms_index_index' column has values [2, 5, 6], then the first 2 elements of the 'waveforms_index' column correspond to the 2 spike events of the first unit, the next 3 elements of the 'waveforms_index' column correspond to the 3 spike events of the second unit, and the next 1 element of the 'waveforms_index' column corresponds to the 1 spike event of the third unit. If the 'waveforms_index' column has values [3, 6, 8, 10, 12, 13], then the first 3 elements of the 'waveforms' column contain the 3 spike waveforms that were recorded from 3 different electrodes for the first spike time of the first unit. See https://nwb-schema.readthedocs.io/en/stable/format_description.html#doubly-ragged-arrays for a graphical representation of this example. When there is only one electrode for each unit (i.e., each spike time is associated with a single waveform), then the 'waveforms_index' column will have values 1, 2, ..., N, where N is the number of spike events. The number of electrodes for each spike event should be the same within a given unit. The 'electrodes' column should be used to indicate which electrodes are associated with each unit, and the order of the waveforms within a given unit x spike event should be in the same order as the electrodes referenced in the 'electrodes' column of this table. The number of samples for each waveform must be the same.""")
    waveforms_index: Optional[UnitsWaveformsIndex] = Field(None, description="""Index into the waveforms dataset. One value for every spike event. See 'waveforms' for more detail.""")
    waveforms_index_index: Optional[UnitsWaveformsIndexIndex] = Field(None, description="""Index into the waveforms_index dataset. One value for every unit (row in the table). See 'waveforms' for more detail.""")
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
    

class AbstractFeatureSeries(TimeSeries):
    """
    Abstract features, such as quantitative descriptions of sensory stimuli. The TimeSeries::data field is a 2D array, storing those features (e.g., for visual grating stimulus this might be orientation, spatial frequency and contrast). Null stimuli (eg, uniform gray) can be marked as being an independent feature (eg, 1.0 for gray, 0.0 for actual stimulus) or by storing NaNs for feature values, or through use of the TimeSeries::control fields. A set of features is considered to persist until the next set of features is defined. The final set of features stored should be the null set. This is useful when storing the raw stimulus is impractical.
    """
    data: AbstractFeatureSeriesData = Field(..., description="""Values of each feature at each time.""")
    feature_units: Optional[AbstractFeatureSeriesFeatureUnits] = Field(None, description="""Units of each feature.""")
    features: AbstractFeatureSeriesFeatures = Field(..., description="""Description of the features represented in TimeSeries::data.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class AnnotationSeries(TimeSeries):
    """
    Stores user annotations made during an experiment. The data[] field stores a text array, and timestamps are stored for each annotation (ie, interval=1). This is largely an alias to a standard TimeSeries storing a text array but that is identifiable as storing annotations in a machine-readable way.
    """
    data: AnnotationSeriesData = Field(..., description="""Annotations made during an experiment.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class IntervalSeries(TimeSeries):
    """
    Stores intervals of data. The timestamps field stores the beginning and end of intervals. The data field stores whether the interval just started (>0 value) or ended (<0 value). Different interval types can be represented in the same series by using multiple key values (eg, 1 for feature A, 2 for feature B, 3 for feature C, etc). The field data stores an 8-bit integer. This is largely an alias of a standard TimeSeries but that is identifiable as representing time intervals in a machine-readable way.
    """
    data: IntervalSeriesData = Field(..., description="""Use values >0 if interval started, <0 if interval ended.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class DecompositionSeries(TimeSeries):
    """
    Spectral analysis of a time series, e.g. of an LFP or a speech signal.
    """
    data: DecompositionSeriesData = Field(..., description="""Data decomposed into frequency bands.""")
    metric: DecompositionSeriesMetric = Field(..., description="""The metric used, e.g. phase, amplitude, power.""")
    source_channels: Optional[DecompositionSeriesSourceChannels] = Field(None, description="""DynamicTableRegion pointer to the channels that this decomposition series was generated from.""")
    bands: DecompositionSeriesBands = Field(..., description="""Table for describing the bands that this series was generated from. There should be one row in this table for each band.""")
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
AbstractFeatureSeriesData.update_forward_refs()
AbstractFeatureSeriesFeatureUnits.update_forward_refs()
AbstractFeatureSeriesFeatures.update_forward_refs()
AnnotationSeriesData.update_forward_refs()
IntervalSeriesData.update_forward_refs()
DecompositionSeriesData.update_forward_refs()
DecompositionSeriesMetric.update_forward_refs()
Arraylike.update_forward_refs()
AbstractFeatureSeriesDataArray.update_forward_refs()
AbstractFeatureSeriesFeatureUnitsArray.update_forward_refs()
AbstractFeatureSeriesFeaturesArray.update_forward_refs()
AnnotationSeriesDataArray.update_forward_refs()
IntervalSeriesDataArray.update_forward_refs()
DecompositionSeriesDataArray.update_forward_refs()
DecompositionSeriesBandsBandLimitsArray.update_forward_refs()
DecompositionSeriesBandsBandMeanArray.update_forward_refs()
DecompositionSeriesBandsBandStdevArray.update_forward_refs()
UnitsObsIntervalsArray.update_forward_refs()
UnitsWaveformMeanArray.update_forward_refs()
UnitsWaveformSdArray.update_forward_refs()
UnitsWaveformsArray.update_forward_refs()
VectorDataArray.update_forward_refs()
VectorIndexArray.update_forward_refs()
ElementIdentifiersArray.update_forward_refs()
DynamicTableRegionArray.update_forward_refs()
DynamicTableIdArray.update_forward_refs()
Data.update_forward_refs()
VectorData.update_forward_refs()
DecompositionSeriesBandsBandName.update_forward_refs()
DecompositionSeriesBandsBandLimits.update_forward_refs()
DecompositionSeriesBandsBandMean.update_forward_refs()
DecompositionSeriesBandsBandStdev.update_forward_refs()
UnitsSpikeTimes.update_forward_refs()
UnitsObsIntervals.update_forward_refs()
UnitsElectrodeGroup.update_forward_refs()
UnitsWaveformMean.update_forward_refs()
UnitsWaveformSd.update_forward_refs()
UnitsWaveforms.update_forward_refs()
VectorIndex.update_forward_refs()
UnitsSpikeTimesIndex.update_forward_refs()
UnitsObsIntervalsIndex.update_forward_refs()
UnitsElectrodesIndex.update_forward_refs()
UnitsWaveformsIndex.update_forward_refs()
UnitsWaveformsIndexIndex.update_forward_refs()
ElementIdentifiers.update_forward_refs()
DynamicTableRegion.update_forward_refs()
DecompositionSeriesSourceChannels.update_forward_refs()
UnitsElectrodes.update_forward_refs()
DynamicTableId.update_forward_refs()
Container.update_forward_refs()
DynamicTable.update_forward_refs()
DecompositionSeriesBands.update_forward_refs()
Units.update_forward_refs()
AlignedDynamicTable.update_forward_refs()
SimpleMultiContainer.update_forward_refs()
NWBData.update_forward_refs()
TimeSeriesReferenceVectorData.update_forward_refs()
Image.update_forward_refs()
ImageArray.update_forward_refs()
ImageReferences.update_forward_refs()
ImageReferencesArray.update_forward_refs()
NWBContainer.update_forward_refs()
NWBDataInterface.update_forward_refs()
TimeSeries.update_forward_refs()
AbstractFeatureSeries.update_forward_refs()
AnnotationSeries.update_forward_refs()
IntervalSeries.update_forward_refs()
DecompositionSeries.update_forward_refs()
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
