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
version = "2.6.0-alpha"

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
    
    

class ImagingRetinotopyAxis1PhaseMap(ConfiguredBaseModel):
    """
    Phase response to stimulus on the first measured axis.
    """
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    unit: Optional[str] = Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array: Optional[ImagingRetinotopyAxis1PhaseMapArray] = Field(None)
    

class ImagingRetinotopyAxis1PowerMap(ConfiguredBaseModel):
    """
    Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.
    """
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    unit: Optional[str] = Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array: Optional[ImagingRetinotopyAxis1PowerMapArray] = Field(None)
    

class ImagingRetinotopyAxis2PhaseMap(ConfiguredBaseModel):
    """
    Phase response to stimulus on the second measured axis.
    """
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    unit: Optional[str] = Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array: Optional[ImagingRetinotopyAxis2PhaseMapArray] = Field(None)
    

class ImagingRetinotopyAxis2PowerMap(ConfiguredBaseModel):
    """
    Power response on the second measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.
    """
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    unit: Optional[str] = Field(None, description="""Unit that axis data is stored in (e.g., degrees).""")
    array: Optional[ImagingRetinotopyAxis2PowerMapArray] = Field(None)
    

class ImagingRetinotopyAxisDescriptions(ConfiguredBaseModel):
    """
    Two-element array describing the contents of the two response axis fields. Description should be something like ['altitude', 'azimuth'] or '['radius', 'theta'].
    """
    array: Optional[ImagingRetinotopyAxisDescriptionsArray] = Field(None)
    

class ImagingRetinotopyFocalDepthImage(ConfiguredBaseModel):
    """
    Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].
    """
    bits_per_pixel: Optional[int] = Field(None, description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value.""")
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    focal_depth: Optional[float] = Field(None, description="""Focal depth offset, in meters.""")
    format: Optional[str] = Field(None, description="""Format of image. Right now only 'raw' is supported.""")
    array: Optional[ImagingRetinotopyFocalDepthImageArray] = Field(None)
    

class ImagingRetinotopySignMap(ConfiguredBaseModel):
    """
    Sine of the angle between the direction of the gradient in axis_1 and axis_2.
    """
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    array: Optional[ImagingRetinotopySignMapArray] = Field(None)
    

class ImagingRetinotopyVasculatureImage(ConfiguredBaseModel):
    """
    Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]
    """
    bits_per_pixel: Optional[int] = Field(None, description="""Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value""")
    dimension: Optional[int] = Field(None, description="""Number of rows and columns in the image. NOTE: row, column representation is equivalent to height, width.""")
    field_of_view: Optional[float] = Field(None, description="""Size of viewing area, in meters.""")
    format: Optional[str] = Field(None, description="""Format of image. Right now only 'raw' is supported.""")
    array: Optional[ImagingRetinotopyVasculatureImageArray] = Field(None)
    

class Arraylike(ConfiguredBaseModel):
    """
    Container for arraylike information held in the dims, shape, and dtype properties.this is a special case to be interpreted by downstream i/o. this class has no slotsand is abstract by default.- Each slot within a subclass indicates a possible dimension.- Only dimensions that are present in all the dimension specifiers in the  original schema are required.- Shape requirements are indicated using max/min cardinalities on the slot.
    """
    None
    

class ImagingRetinotopyAxis1PhaseMapArray(Arraylike):
    
    num_rows: Optional[float] = Field(None)
    num_cols: Optional[float] = Field(None)
    

class ImagingRetinotopyAxis1PowerMapArray(Arraylike):
    
    num_rows: Optional[float] = Field(None)
    num_cols: Optional[float] = Field(None)
    

class ImagingRetinotopyAxis2PhaseMapArray(Arraylike):
    
    num_rows: Optional[float] = Field(None)
    num_cols: Optional[float] = Field(None)
    

class ImagingRetinotopyAxis2PowerMapArray(Arraylike):
    
    num_rows: Optional[float] = Field(None)
    num_cols: Optional[float] = Field(None)
    

class ImagingRetinotopyAxisDescriptionsArray(Arraylike):
    
    axis_1_axis_2: str = Field(...)
    

class ImagingRetinotopyFocalDepthImageArray(Arraylike):
    
    num_rows: Optional[int] = Field(None)
    num_cols: Optional[int] = Field(None)
    

class ImagingRetinotopySignMapArray(Arraylike):
    
    num_rows: Optional[float] = Field(None)
    num_cols: Optional[float] = Field(None)
    

class ImagingRetinotopyVasculatureImageArray(Arraylike):
    
    num_rows: Optional[int] = Field(None)
    num_cols: Optional[int] = Field(None)
    

class ImageArray(Arraylike):
    
    x: float = Field(...)
    y: float = Field(...)
    r_g_b: Optional[float] = Field(None)
    r_g_b_a: Optional[float] = Field(None)
    

class ImageReferencesArray(Arraylike):
    
    num_images: Image = Field(...)
    

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
    

class NWBData(Data):
    """
    An abstract data type for a dataset.
    """
    None
    

class Image(NWBData):
    """
    An abstract data type for an image. Shape can be 2-D (x, y), or 3-D where the third dimension can have three or four elements, e.g. (x, y, (r, g, b)) or (x, y, (r, g, b, a)).
    """
    resolution: Optional[float] = Field(None, description="""Pixel resolution of the image, in pixels per centimeter.""")
    description: Optional[str] = Field(None, description="""Description of the image.""")
    array: Optional[ImageArray] = Field(None)
    

class ImageReferences(NWBData):
    """
    Ordered dataset of references to Image objects.
    """
    array: Optional[ImageReferencesArray] = Field(None)
    

class ImagesOrderOfImages(ImageReferences):
    """
    Ordered dataset of references to Image objects stored in the parent group. Each Image object in the Images group should be stored once and only once, so the dataset should have the same length as the number of images.
    """
    array: Optional[ImageReferencesArray] = Field(None)
    

class VectorData(Data):
    """
    An n-dimensional dataset representing a column of a DynamicTable. If used without an accompanying VectorIndex, first dimension is along the rows of the DynamicTable and each step along the first dimension is a cell of the larger table. VectorData can also be used to represent a ragged array if paired with a VectorIndex. This allows for storing arrays of varying length in a single cell of the DynamicTable by indexing into this VectorData. The first vector is at VectorData[0:VectorIndex[0]]. The second vector is at VectorData[VectorIndex[0]:VectorIndex[1]], and so on.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class TimeSeriesReferenceVectorData(VectorData):
    """
    Column storing references to a TimeSeries (rows). For each TimeSeries this VectorData column stores the start_index and count to indicate the range in time to be selected as well as an object reference to the TimeSeries.
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
    

class ImagingRetinotopy(NWBDataInterface):
    """
    Intrinsic signal optical imaging or widefield imaging for measuring retinotopy. Stores orthogonal maps (e.g., altitude/azimuth; radius/theta) of responses to specific stimuli and a combined polarity map from which to identify visual areas. This group does not store the raw responses imaged during retinotopic mapping or the stimuli presented, but rather the resulting phase and power maps after applying a Fourier transform on the averaged responses. Note: for data consistency, all images and arrays are stored in the format [row][column] and [row, col], which equates to [y][x]. Field of view and dimension arrays may appear backward (i.e., y before x).
    """
    axis_1_phase_map: ImagingRetinotopyAxis1PhaseMap = Field(..., description="""Phase response to stimulus on the first measured axis.""")
    axis_1_power_map: Optional[ImagingRetinotopyAxis1PowerMap] = Field(None, description="""Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.""")
    axis_2_phase_map: ImagingRetinotopyAxis2PhaseMap = Field(..., description="""Phase response to stimulus on the second measured axis.""")
    axis_2_power_map: Optional[ImagingRetinotopyAxis2PowerMap] = Field(None, description="""Power response on the second measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.""")
    axis_descriptions: ImagingRetinotopyAxisDescriptions = Field(..., description="""Two-element array describing the contents of the two response axis fields. Description should be something like ['altitude', 'azimuth'] or '['radius', 'theta'].""")
    focal_depth_image: Optional[ImagingRetinotopyFocalDepthImage] = Field(None, description="""Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].""")
    sign_map: Optional[ImagingRetinotopySignMap] = Field(None, description="""Sine of the angle between the direction of the gradient in axis_1 and axis_2.""")
    vasculature_image: ImagingRetinotopyVasculatureImage = Field(..., description="""Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]""")
    

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
    

class DynamicTable(Container):
    """
    A group containing multiple datasets that are aligned on the first dimension (Currently, this requirement if left up to APIs to check and enforce). These datasets represent different columns in the table. Apart from a column that contains unique identifiers for each row, there are no other required datasets. Users are free to add any number of custom VectorData objects (columns) here. DynamicTable also supports ragged array columns, where each element can be of a different size. To add a ragged array column, use a VectorIndex type to index the corresponding VectorData type. See documentation for VectorData and VectorIndex for more details. Unlike a compound data type, which is analogous to storing an array-of-structs, a DynamicTable can be thought of as a struct-of-arrays. This provides an alternative structure to choose from when optimizing storage for anticipated access patterns. Additionally, this type provides a way of creating a table without having to define a compound type up front. Although this convenience may be attractive, users should think carefully about how data will be accessed. DynamicTable is more appropriate for column-centric access, whereas a dataset with a compound type would be more appropriate for row-centric access. Finally, data size should also be taken into account. For small tables, performance loss may be an acceptable trade-off for the flexibility of a DynamicTable.
    """
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
    

class TwoPhotonSeriesFieldOfView(ConfiguredBaseModel):
    """
    Width, height and depth of image, or imaged area, in meters.
    """
    array: Optional[TwoPhotonSeriesFieldOfViewArray] = Field(None)
    

class TwoPhotonSeriesFieldOfViewArray(Arraylike):
    
    width|height: Optional[float] = Field(None)
    width|height|depth: Optional[float] = Field(None)
    

class RoiResponseSeries(TimeSeries):
    """
    ROI responses over an imaging plane. The first dimension represents time. The second dimension, if present, represents ROIs.
    """
    data: RoiResponseSeriesData = Field(..., description="""Signals from ROIs.""")
    rois: RoiResponseSeriesRois = Field(..., description="""DynamicTableRegion referencing into an ROITable containing information on the ROIs stored in this timeseries.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class RoiResponseSeriesData(ConfiguredBaseModel):
    """
    Signals from ROIs.
    """
    array: Optional[RoiResponseSeriesDataArray] = Field(None)
    

class RoiResponseSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    num_ROIs: Optional[float] = Field(None)
    

class RoiResponseSeriesRois(DynamicTableRegion):
    """
    DynamicTableRegion referencing into an ROITable containing information on the ROIs stored in this timeseries.
    """
    table: Optional[DynamicTable] = Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class DfOverF(NWBDataInterface):
    """
    dF/F information about a region of interest (ROI). Storage hierarchy of dF/F should be the same as for segmentation (i.e., same names for ROIs and for image planes).
    """
    RoiResponseSeries: List[RoiResponseSeries] = Field(default_factory=list, description="""RoiResponseSeries object(s) containing dF/F for a ROI.""")
    

class Fluorescence(NWBDataInterface):
    """
    Fluorescence information about a region of interest (ROI). Storage hierarchy of fluorescence should be the same as for segmentation (ie, same names for ROIs and for image planes).
    """
    RoiResponseSeries: List[RoiResponseSeries] = Field(default_factory=list, description="""RoiResponseSeries object(s) containing fluorescence data for a ROI.""")
    

class ImageSegmentation(NWBDataInterface):
    """
    Stores pixels in an image that represent different regions of interest (ROIs) or masks. All segmentation for a given imaging plane is stored together, with storage for multiple imaging planes (masks) supported. Each ROI is stored in its own subgroup, with the ROI group containing both a 2D mask and a list of pixels that make up this mask. Segments can also be used for masking neuropil. If segmentation is allowed to change with time, a new imaging plane (or module) is required and ROI names should remain consistent between them.
    """
    PlaneSegmentation: List[PlaneSegmentation] = Field(default_factory=list, description="""Results from image segmentation of a specific imaging plane.""")
    

class PlaneSegmentation(DynamicTable):
    """
    Results from image segmentation of a specific imaging plane.
    """
    image_mask: Optional[PlaneSegmentationImageMask] = Field(None, description="""ROI masks for each ROI. Each image mask is the size of the original imaging plane (or volume) and members of the ROI are finite non-zero.""")
    pixel_mask_index: Optional[PlaneSegmentationPixelMaskIndex] = Field(None, description="""Index into pixel_mask.""")
    pixel_mask: Optional[PlaneSegmentationPixelMask] = Field(None, description="""Pixel masks for each ROI: a list of indices and weights for the ROI. Pixel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation""")
    voxel_mask_index: Optional[PlaneSegmentationVoxelMaskIndex] = Field(None, description="""Index into voxel_mask.""")
    voxel_mask: Optional[PlaneSegmentationVoxelMask] = Field(None, description="""Voxel masks for each ROI: a list of indices and weights for the ROI. Voxel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation""")
    reference_images: PlaneSegmentationReferenceImages = Field(..., description="""Image stacks that the segmentation masks apply to.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class PlaneSegmentationImageMask(VectorData):
    """
    ROI masks for each ROI. Each image mask is the size of the original imaging plane (or volume) and members of the ROI are finite non-zero.
    """
    array: Optional[PlaneSegmentationImageMaskArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class PlaneSegmentationImageMaskArray(Arraylike):
    
    num_roi: Any = Field(...)
    num_x: Any = Field(...)
    num_y: Any = Field(...)
    num_z: Optional[Any] = Field(None)
    

class PlaneSegmentationPixelMaskIndex(VectorIndex):
    """
    Index into pixel_mask.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class PlaneSegmentationPixelMask(VectorData):
    """
    Pixel masks for each ROI: a list of indices and weights for the ROI. Pixel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class PlaneSegmentationVoxelMaskIndex(VectorIndex):
    """
    Index into voxel_mask.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class PlaneSegmentationVoxelMask(VectorData):
    """
    Voxel masks for each ROI: a list of indices and weights for the ROI. Voxel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class PlaneSegmentationReferenceImages(ConfiguredBaseModel):
    """
    Image stacks that the segmentation masks apply to.
    """
    ImageSeries: Optional[List[ImageSeries]] = Field(default_factory=list, description="""One or more image stacks that the masks apply to (can be one-element stack).""")
    

class ImagingPlane(NWBContainer):
    """
    An imaging plane and its metadata.
    """
    description: Optional[ImagingPlaneDescription] = Field(None, description="""Description of the imaging plane.""")
    excitation_lambda: ImagingPlaneExcitationLambda = Field(..., description="""Excitation wavelength, in nm.""")
    imaging_rate: Optional[ImagingPlaneImagingRate] = Field(None, description="""Rate that images are acquired, in Hz. If the corresponding TimeSeries is present, the rate should be stored there instead.""")
    indicator: ImagingPlaneIndicator = Field(..., description="""Calcium indicator.""")
    location: ImagingPlaneLocation = Field(..., description="""Location of the imaging plane. Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""")
    manifold: Optional[ImagingPlaneManifold] = Field(None, description="""DEPRECATED Physical position of each pixel. 'xyz' represents the position of the pixel relative to the defined coordinate space. Deprecated in favor of origin_coords and grid_spacing.""")
    origin_coords: Optional[ImagingPlaneOriginCoords] = Field(None, description="""Physical location of the first element of the imaging plane (0, 0) for 2-D data or (0, 0, 0) for 3-D data. See also reference_frame for what the physical location is relative to (e.g., bregma).""")
    grid_spacing: Optional[ImagingPlaneGridSpacing] = Field(None, description="""Space between pixels in (x, y) or voxels in (x, y, z) directions, in the specified unit. Assumes imaging plane is a regular grid. See also reference_frame to interpret the grid.""")
    reference_frame: Optional[ImagingPlaneReferenceFrame] = Field(None, description="""Describes reference frame of origin_coords and grid_spacing. For example, this can be a text description of the anatomical location and orientation of the grid defined by origin_coords and grid_spacing or the vectors needed to transform or rotate the grid to a common anatomical axis (e.g., AP/DV/ML). This field is necessary to interpret origin_coords and grid_spacing. If origin_coords and grid_spacing are not present, then this field is not required. For example, if the microscope takes 10 x 10 x 2 images, where the first value of the data matrix (index (0, 0, 0)) corresponds to (-1.2, -0.6, -2) mm relative to bregma, the spacing between pixels is 0.2 mm in x, 0.2 mm in y and 0.5 mm in z, and larger numbers in x means more anterior, larger numbers in y means more rightward, and larger numbers in z means more ventral, then enter the following -- origin_coords = (-1.2, -0.6, -2) grid_spacing = (0.2, 0.2, 0.5) reference_frame = \"Origin coordinates are relative to bregma. First dimension corresponds to anterior-posterior axis (larger index = more anterior). Second dimension corresponds to medial-lateral axis (larger index = more rightward). Third dimension corresponds to dorsal-ventral axis (larger index = more ventral).\"""")
    OpticalChannel: List[OpticalChannel] = Field(default_factory=list, description="""An optical channel used to record from an imaging plane.""")
    

class ImagingPlaneDescription(ConfiguredBaseModel):
    """
    Description of the imaging plane.
    """
    None
    

class ImagingPlaneExcitationLambda(ConfiguredBaseModel):
    """
    Excitation wavelength, in nm.
    """
    None
    

class ImagingPlaneImagingRate(ConfiguredBaseModel):
    """
    Rate that images are acquired, in Hz. If the corresponding TimeSeries is present, the rate should be stored there instead.
    """
    None
    

class ImagingPlaneIndicator(ConfiguredBaseModel):
    """
    Calcium indicator.
    """
    None
    

class ImagingPlaneLocation(ConfiguredBaseModel):
    """
    Location of the imaging plane. Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.
    """
    None
    

class ImagingPlaneManifold(ConfiguredBaseModel):
    """
    DEPRECATED Physical position of each pixel. 'xyz' represents the position of the pixel relative to the defined coordinate space. Deprecated in favor of origin_coords and grid_spacing.
    """
    conversion: Optional[float] = Field(None, description="""Scalar to multiply each element in data to convert it to the specified 'unit'. If the data are stored in acquisition system units or other units that require a conversion to be interpretable, multiply the data by 'conversion' to convert the data to the specified 'unit'. e.g. if the data acquisition system stores values in this object as pixels from x = -500 to 499, y = -500 to 499 that correspond to a 2 m x 2 m range, then the 'conversion' multiplier to get from raw data acquisition pixel units to meters is 2/1000.""")
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. The default value is 'meters'.""")
    array: Optional[ImagingPlaneManifoldArray] = Field(None)
    

class ImagingPlaneManifoldArray(Arraylike):
    
    height: float = Field(...)
    width: float = Field(...)
    x_y_z: float = Field(...)
    depth: Optional[float] = Field(None)
    

class ImagingPlaneOriginCoords(ConfiguredBaseModel):
    """
    Physical location of the first element of the imaging plane (0, 0) for 2-D data or (0, 0, 0) for 3-D data. See also reference_frame for what the physical location is relative to (e.g., bregma).
    """
    unit: Optional[str] = Field(None, description="""Measurement units for origin_coords. The default value is 'meters'.""")
    array: Optional[ImagingPlaneOriginCoordsArray] = Field(None)
    

class ImagingPlaneOriginCoordsArray(Arraylike):
    
    x_y: Optional[float] = Field(None)
    x_y_z: Optional[float] = Field(None)
    

class ImagingPlaneGridSpacing(ConfiguredBaseModel):
    """
    Space between pixels in (x, y) or voxels in (x, y, z) directions, in the specified unit. Assumes imaging plane is a regular grid. See also reference_frame to interpret the grid.
    """
    unit: Optional[str] = Field(None, description="""Measurement units for grid_spacing. The default value is 'meters'.""")
    array: Optional[ImagingPlaneGridSpacingArray] = Field(None)
    

class ImagingPlaneGridSpacingArray(Arraylike):
    
    x_y: Optional[float] = Field(None)
    x_y_z: Optional[float] = Field(None)
    

class ImagingPlaneReferenceFrame(ConfiguredBaseModel):
    """
    Describes reference frame of origin_coords and grid_spacing. For example, this can be a text description of the anatomical location and orientation of the grid defined by origin_coords and grid_spacing or the vectors needed to transform or rotate the grid to a common anatomical axis (e.g., AP/DV/ML). This field is necessary to interpret origin_coords and grid_spacing. If origin_coords and grid_spacing are not present, then this field is not required. For example, if the microscope takes 10 x 10 x 2 images, where the first value of the data matrix (index (0, 0, 0)) corresponds to (-1.2, -0.6, -2) mm relative to bregma, the spacing between pixels is 0.2 mm in x, 0.2 mm in y and 0.5 mm in z, and larger numbers in x means more anterior, larger numbers in y means more rightward, and larger numbers in z means more ventral, then enter the following -- origin_coords = (-1.2, -0.6, -2) grid_spacing = (0.2, 0.2, 0.5) reference_frame = \"Origin coordinates are relative to bregma. First dimension corresponds to anterior-posterior axis (larger index = more anterior). Second dimension corresponds to medial-lateral axis (larger index = more rightward). Third dimension corresponds to dorsal-ventral axis (larger index = more ventral).\"
    """
    None
    

class OpticalChannel(NWBContainer):
    """
    An optical channel used to record from an imaging plane.
    """
    description: OpticalChannelDescription = Field(..., description="""Description or other notes about the channel.""")
    emission_lambda: OpticalChannelEmissionLambda = Field(..., description="""Emission wavelength for channel, in nm.""")
    

class OpticalChannelDescription(ConfiguredBaseModel):
    """
    Description or other notes about the channel.
    """
    None
    

class OpticalChannelEmissionLambda(ConfiguredBaseModel):
    """
    Emission wavelength for channel, in nm.
    """
    None
    

class MotionCorrection(NWBDataInterface):
    """
    An image stack where all frames are shifted (registered) to a common coordinate system, to account for movement and drift between frames. Note: each frame at each point in time is assumed to be 2-D (has only x & y dimensions).
    """
    CorrectedImageStack: List[CorrectedImageStack] = Field(default_factory=list, description="""Reuslts from motion correction of an image stack.""")
    

class CorrectedImageStack(NWBDataInterface):
    """
    Reuslts from motion correction of an image stack.
    """
    corrected: CorrectedImageStackCorrected = Field(..., description="""Image stack with frames shifted to the common coordinates.""")
    xy_translation: CorrectedImageStackXyTranslation = Field(..., description="""Stores the x,y delta necessary to align each frame to the common coordinates, for example, to align each frame to a reference image.""")
    

class CorrectedImageStackXyTranslation(TimeSeries):
    """
    Stores the x,y delta necessary to align each frame to the common coordinates, for example, to align each frame to a reference image.
    """
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    data: TimeSeriesData = Field(..., description="""Data values. Data can be in 1-D, 2-D, 3-D, or 4-D. The first dimension should always represent time. This can also be used to store binary data (e.g., image frames). This can also be a link to data stored in an external file.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class GrayscaleImage(Image):
    """
    A grayscale image.
    """
    array: Optional[GrayscaleImageArray] = Field(None)
    resolution: Optional[float] = Field(None, description="""Pixel resolution of the image, in pixels per centimeter.""")
    description: Optional[str] = Field(None, description="""Description of the image.""")
    

class GrayscaleImageArray(Arraylike):
    
    x: Optional[float] = Field(None)
    y: Optional[float] = Field(None)
    

class RGBImage(Image):
    """
    A color image.
    """
    array: Optional[RGBImageArray] = Field(None)
    resolution: Optional[float] = Field(None, description="""Pixel resolution of the image, in pixels per centimeter.""")
    description: Optional[str] = Field(None, description="""Description of the image.""")
    

class RGBImageArray(Arraylike):
    
    x: Optional[float] = Field(None)
    y: Optional[float] = Field(None)
    r_g_b: Optional[float] = Field(None)
    

class RGBAImage(Image):
    """
    A color image with transparency.
    """
    array: Optional[RGBAImageArray] = Field(None)
    resolution: Optional[float] = Field(None, description="""Pixel resolution of the image, in pixels per centimeter.""")
    description: Optional[str] = Field(None, description="""Description of the image.""")
    

class RGBAImageArray(Arraylike):
    
    x: Optional[float] = Field(None)
    y: Optional[float] = Field(None)
    r_g_b_a: Optional[float] = Field(None)
    

class ImageSeries(TimeSeries):
    """
    General image data that is common between acquisition and stimulus time series. Sometimes the image data is stored in the file in a raw format while other times it will be stored as a series of external image files in the host file system. The data field will either be binary data, if the data is stored in the NWB file, or empty, if the data is stored in an external image stack. [frame][x][y] or [frame][x][y][z].
    """
    data: ImageSeriesData = Field(..., description="""Binary data representing images across frames. If data are stored in an external file, this should be an empty 3D array.""")
    dimension: Optional[ImageSeriesDimension] = Field(None, description="""Number of pixels on x, y, (and z) axes.""")
    external_file: Optional[ImageSeriesExternalFile] = Field(None, description="""Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.""")
    format: Optional[ImageSeriesFormat] = Field(None, description="""Format of image. If this is 'external', then the attribute 'external_file' contains the path information to the image files. If this is 'raw', then the raw (single-channel) binary data is stored in the 'data' dataset. If this attribute is not present, then the default format='raw' case is assumed.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class OnePhotonSeries(ImageSeries):
    """
    Image stack recorded over time from 1-photon microscope.
    """
    pmt_gain: Optional[float] = Field(None, description="""Photomultiplier gain.""")
    scan_line_rate: Optional[float] = Field(None, description="""Lines imaged per second. This is also stored in /general/optophysiology but is kept here as it is useful information for analysis, and so good to be stored w/ the actual data.""")
    exposure_time: Optional[float] = Field(None, description="""Exposure time of the sample; often the inverse of the frequency.""")
    binning: Optional[int] = Field(None, description="""Amount of pixels combined into 'bins'; could be 1, 2, 4, 8, etc.""")
    power: Optional[float] = Field(None, description="""Power of the excitation in mW, if known.""")
    intensity: Optional[float] = Field(None, description="""Intensity of the excitation in mW/mm^2, if known.""")
    data: ImageSeriesData = Field(..., description="""Binary data representing images across frames. If data are stored in an external file, this should be an empty 3D array.""")
    dimension: Optional[ImageSeriesDimension] = Field(None, description="""Number of pixels on x, y, (and z) axes.""")
    external_file: Optional[ImageSeriesExternalFile] = Field(None, description="""Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.""")
    format: Optional[ImageSeriesFormat] = Field(None, description="""Format of image. If this is 'external', then the attribute 'external_file' contains the path information to the image files. If this is 'raw', then the raw (single-channel) binary data is stored in the 'data' dataset. If this attribute is not present, then the default format='raw' case is assumed.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class TwoPhotonSeries(ImageSeries):
    """
    Image stack recorded over time from 2-photon microscope.
    """
    pmt_gain: Optional[float] = Field(None, description="""Photomultiplier gain.""")
    scan_line_rate: Optional[float] = Field(None, description="""Lines imaged per second. This is also stored in /general/optophysiology but is kept here as it is useful information for analysis, and so good to be stored w/ the actual data.""")
    field_of_view: Optional[TwoPhotonSeriesFieldOfView] = Field(None, description="""Width, height and depth of image, or imaged area, in meters.""")
    data: ImageSeriesData = Field(..., description="""Binary data representing images across frames. If data are stored in an external file, this should be an empty 3D array.""")
    dimension: Optional[ImageSeriesDimension] = Field(None, description="""Number of pixels on x, y, (and z) axes.""")
    external_file: Optional[ImageSeriesExternalFile] = Field(None, description="""Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.""")
    format: Optional[ImageSeriesFormat] = Field(None, description="""Format of image. If this is 'external', then the attribute 'external_file' contains the path information to the image files. If this is 'raw', then the raw (single-channel) binary data is stored in the 'data' dataset. If this attribute is not present, then the default format='raw' case is assumed.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class CorrectedImageStackCorrected(ImageSeries):
    """
    Image stack with frames shifted to the common coordinates.
    """
    data: ImageSeriesData = Field(..., description="""Binary data representing images across frames. If data are stored in an external file, this should be an empty 3D array.""")
    dimension: Optional[ImageSeriesDimension] = Field(None, description="""Number of pixels on x, y, (and z) axes.""")
    external_file: Optional[ImageSeriesExternalFile] = Field(None, description="""Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.""")
    format: Optional[ImageSeriesFormat] = Field(None, description="""Format of image. If this is 'external', then the attribute 'external_file' contains the path information to the image files. If this is 'raw', then the raw (single-channel) binary data is stored in the 'data' dataset. If this attribute is not present, then the default format='raw' case is assumed.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class ImageSeriesData(ConfiguredBaseModel):
    """
    Binary data representing images across frames. If data are stored in an external file, this should be an empty 3D array.
    """
    array: Optional[ImageSeriesDataArray] = Field(None)
    

class ImageSeriesDataArray(Arraylike):
    
    frame: float = Field(...)
    x: float = Field(...)
    y: float = Field(...)
    z: Optional[float] = Field(None)
    

class ImageSeriesDimension(ConfiguredBaseModel):
    """
    Number of pixels on x, y, (and z) axes.
    """
    array: Optional[ImageSeriesDimensionArray] = Field(None)
    

class ImageSeriesDimensionArray(Arraylike):
    
    rank: int = Field(...)
    

class ImageSeriesExternalFile(ConfiguredBaseModel):
    """
    Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.
    """
    starting_frame: Optional[int] = Field(None, description="""Each external image may contain one or more consecutive frames of the full ImageSeries. This attribute serves as an index to indicate which frames each file contains, to facilitate random access. The 'starting_frame' attribute, hence, contains a list of frame numbers within the full ImageSeries of the first frame of each file listed in the parent 'external_file' dataset. Zero-based indexing is used (hence, the first element will always be zero). For example, if the 'external_file' dataset has three paths to files and the first file has 5 frames, the second file has 10 frames, and the third file has 20 frames, then this attribute will have values [0, 5, 15]. If there is a single external file that holds all of the frames of the ImageSeries (and so there is a single element in the 'external_file' dataset), then this attribute should have value [0].""")
    array: Optional[ImageSeriesExternalFileArray] = Field(None)
    

class ImageSeriesExternalFileArray(Arraylike):
    
    num_files: str = Field(...)
    

class ImageSeriesFormat(ConfiguredBaseModel):
    """
    Format of image. If this is 'external', then the attribute 'external_file' contains the path information to the image files. If this is 'raw', then the raw (single-channel) binary data is stored in the 'data' dataset. If this attribute is not present, then the default format='raw' case is assumed.
    """
    None
    

class ImageMaskSeries(ImageSeries):
    """
    An alpha mask that is applied to a presented visual stimulus. The 'data' array contains an array of mask values that are applied to the displayed image. Mask values are stored as RGBA. Mask can vary with time. The timestamps array indicates the starting time of a mask, and that mask pattern continues until it's explicitly changed.
    """
    data: ImageSeriesData = Field(..., description="""Binary data representing images across frames. If data are stored in an external file, this should be an empty 3D array.""")
    dimension: Optional[ImageSeriesDimension] = Field(None, description="""Number of pixels on x, y, (and z) axes.""")
    external_file: Optional[ImageSeriesExternalFile] = Field(None, description="""Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.""")
    format: Optional[ImageSeriesFormat] = Field(None, description="""Format of image. If this is 'external', then the attribute 'external_file' contains the path information to the image files. If this is 'raw', then the raw (single-channel) binary data is stored in the 'data' dataset. If this attribute is not present, then the default format='raw' case is assumed.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class OpticalSeries(ImageSeries):
    """
    Image data that is presented or recorded. A stimulus template movie will be stored only as an image. When the image is presented as stimulus, additional data is required, such as field of view (e.g., how much of the visual field the image covers, or how what is the area of the target being imaged). If the OpticalSeries represents acquired imaging data, orientation is also important.
    """
    distance: Optional[OpticalSeriesDistance] = Field(None, description="""Distance from camera/monitor to target/eye.""")
    field_of_view: Optional[OpticalSeriesFieldOfView] = Field(None, description="""Width, height and depth of image, or imaged area, in meters.""")
    data: OpticalSeriesData = Field(..., description="""Images presented to subject, either grayscale or RGB""")
    orientation: Optional[OpticalSeriesOrientation] = Field(None, description="""Description of image relative to some reference frame (e.g., which way is up). Must also specify frame of reference.""")
    dimension: Optional[ImageSeriesDimension] = Field(None, description="""Number of pixels on x, y, (and z) axes.""")
    external_file: Optional[ImageSeriesExternalFile] = Field(None, description="""Paths to one or more external file(s). The field is only present if format='external'. This is only relevant if the image series is stored in the file system as one or more image file(s). This field should NOT be used if the image is stored in another NWB file and that file is linked to this file.""")
    format: Optional[ImageSeriesFormat] = Field(None, description="""Format of image. If this is 'external', then the attribute 'external_file' contains the path information to the image files. If this is 'raw', then the raw (single-channel) binary data is stored in the 'data' dataset. If this attribute is not present, then the default format='raw' case is assumed.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class OpticalSeriesDistance(ConfiguredBaseModel):
    """
    Distance from camera/monitor to target/eye.
    """
    None
    

class OpticalSeriesFieldOfView(ConfiguredBaseModel):
    """
    Width, height and depth of image, or imaged area, in meters.
    """
    array: Optional[OpticalSeriesFieldOfViewArray] = Field(None)
    

class OpticalSeriesFieldOfViewArray(Arraylike):
    
    width_height: Optional[float] = Field(None)
    width_height_depth: Optional[float] = Field(None)
    

class OpticalSeriesData(ConfiguredBaseModel):
    """
    Images presented to subject, either grayscale or RGB
    """
    array: Optional[OpticalSeriesDataArray] = Field(None)
    

class OpticalSeriesDataArray(Arraylike):
    
    frame: float = Field(...)
    x: float = Field(...)
    y: float = Field(...)
    r_g_b: Optional[float] = Field(None)
    

class OpticalSeriesOrientation(ConfiguredBaseModel):
    """
    Description of image relative to some reference frame (e.g., which way is up). Must also specify frame of reference.
    """
    None
    

class IndexSeries(TimeSeries):
    """
    Stores indices to image frames stored in an ImageSeries. The purpose of the IndexSeries is to allow a static image stack to be stored in an Images object, and the images in the stack to be referenced out-of-order. This can be for the display of individual images, or of movie segments (as a movie is simply a series of images). The data field stores the index of the frame in the referenced Images object, and the timestamps array indicates when that image was displayed.
    """
    data: IndexSeriesData = Field(..., description="""Index of the image (using zero-indexing) in the linked Images object.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class IndexSeriesData(ConfiguredBaseModel):
    """
    Index of the image (using zero-indexing) in the linked Images object.
    """
    conversion: Optional[float] = Field(None, description="""This field is unused by IndexSeries.""")
    resolution: Optional[float] = Field(None, description="""This field is unused by IndexSeries.""")
    offset: Optional[float] = Field(None, description="""This field is unused by IndexSeries.""")
    unit: Optional[str] = Field(None, description="""This field is unused by IndexSeries and has the value N/A.""")
    array: Optional[IndexSeriesDataArray] = Field(None)
    

class IndexSeriesDataArray(Arraylike):
    
    num_times: int = Field(...)
    

class OptogeneticSeries(TimeSeries):
    """
    An optogenetic stimulus.
    """
    data: OptogeneticSeriesData = Field(..., description="""Applied power for optogenetic stimulus, in watts.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class OptogeneticSeriesData(ConfiguredBaseModel):
    """
    Applied power for optogenetic stimulus, in watts.
    """
    unit: Optional[str] = Field(None, description="""Unit of measurement for data, which is fixed to 'watts'.""")
    array: Optional[OptogeneticSeriesDataArray] = Field(None)
    

class OptogeneticSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    

class OptogeneticStimulusSite(NWBContainer):
    """
    A site of optogenetic stimulation.
    """
    description: OptogeneticStimulusSiteDescription = Field(..., description="""Description of stimulation site.""")
    excitation_lambda: OptogeneticStimulusSiteExcitationLambda = Field(..., description="""Excitation wavelength, in nm.""")
    location: OptogeneticStimulusSiteLocation = Field(..., description="""Location of the stimulation site. Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""")
    

class OptogeneticStimulusSiteDescription(ConfiguredBaseModel):
    """
    Description of stimulation site.
    """
    None
    

class OptogeneticStimulusSiteExcitationLambda(ConfiguredBaseModel):
    """
    Excitation wavelength, in nm.
    """
    None
    

class OptogeneticStimulusSiteLocation(ConfiguredBaseModel):
    """
    Location of the stimulation site. Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.
    """
    None
    

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
    

class PatchClampSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage or current.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    array: Optional[PatchClampSeriesDataArray] = Field(None)
    

class PatchClampSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    

class PatchClampSeriesGain(ConfiguredBaseModel):
    """
    Gain of the recording, in units Volt/Amp (v-clamp) or Volt/Volt (c-clamp).
    """
    None
    

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
    

class CurrentClampStimulusSeriesData(ConfiguredBaseModel):
    """
    Stimulus current applied.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. which is fixed to 'amperes'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    

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
    

class VoltageClampStimulusSeriesData(ConfiguredBaseModel):
    """
    Stimulus voltage applied.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. which is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    

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
    

class SweepTableSeriesIndex(VectorIndex):
    """
    Index for series.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class IntracellularElectrodesTable(DynamicTable):
    """
    Table for storing intracellular electrode related metadata.
    """
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    electrode: IntracellularElectrodesTableElectrode = Field(..., description="""Column for storing the reference to the intracellular electrode.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularElectrodesTableElectrode(VectorData):
    """
    Column for storing the reference to the intracellular electrode.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class IntracellularStimuliTable(DynamicTable):
    """
    Table for storing intracellular stimulus related metadata.
    """
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    stimulus: IntracellularStimuliTableStimulus = Field(..., description="""Column storing the reference to the recorded stimulus for the recording (rows).""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularStimuliTableStimulus(TimeSeriesReferenceVectorData):
    """
    Column storing the reference to the recorded stimulus for the recording (rows).
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class IntracellularResponsesTable(DynamicTable):
    """
    Table for storing intracellular response related metadata.
    """
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    response: IntracellularResponsesTableResponse = Field(..., description="""Column storing the reference to the recorded response for the recording (rows)""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class IntracellularResponsesTableResponse(TimeSeriesReferenceVectorData):
    """
    Column storing the reference to the recorded response for the recording (rows)
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

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
    

class SimultaneousRecordingsTableRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the IntracellularRecordingsTable table.
    """
    table: Optional[IntracellularRecordingsTable] = Field(None, description="""Reference to the IntracellularRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class SimultaneousRecordingsTableRecordingsIndex(VectorIndex):
    """
    Index dataset for the recordings column.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

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
    

class SequentialRecordingsTableSimultaneousRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the SimultaneousRecordingsTable table.
    """
    table: Optional[SimultaneousRecordingsTable] = Field(None, description="""Reference to the SimultaneousRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class SequentialRecordingsTableSimultaneousRecordingsIndex(VectorIndex):
    """
    Index dataset for the simultaneous_recordings column.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class SequentialRecordingsTableStimulusType(VectorData):
    """
    The type of stimulus used for the sequential recording.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

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
    

class RepetitionsTableSequentialRecordings(DynamicTableRegion):
    """
    A reference to one or more rows in the SequentialRecordingsTable table.
    """
    table: Optional[SequentialRecordingsTable] = Field(None, description="""Reference to the SequentialRecordingsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class RepetitionsTableSequentialRecordingsIndex(VectorIndex):
    """
    Index dataset for the sequential_recordings column.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

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
    

class ExperimentalConditionsTableRepetitions(DynamicTableRegion):
    """
    A reference to one or more rows in the RepetitionsTable table.
    """
    table: Optional[RepetitionsTable] = Field(None, description="""Reference to the RepetitionsTable table that this table region applies to. This specializes the attribute inherited from DynamicTableRegion to fix the type of table that can be referenced here.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class ExperimentalConditionsTableRepetitionsIndex(VectorIndex):
    """
    Index dataset for the repetitions column.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class ElectricalSeries(TimeSeries):
    """
    A time series of acquired voltage data from extracellular recordings. The data field is an int or float array storing data in volts. The first dimension should always represent time. The second dimension, if present, should represent channels.
    """
    filtering: Optional[str] = Field(None, description="""Filtering applied to all channels of the data. For example, if this ElectricalSeries represents high-pass-filtered data (also known as AP Band), then this value could be \"High-pass 4-pole Bessel filter at 500 Hz\". If this ElectricalSeries represents low-pass-filtered LFP data and the type of filter is unknown, then this value could be \"Low-pass filter at 300 Hz\". If a non-standard filter type is used, provide as much detail about the filter properties as possible.""")
    data: ElectricalSeriesData = Field(..., description="""Recorded voltage data.""")
    electrodes: ElectricalSeriesElectrodes = Field(..., description="""DynamicTableRegion pointer to the electrodes that this time series was generated from.""")
    channel_conversion: Optional[ElectricalSeriesChannelConversion] = Field(None, description="""Channel-specific conversion factor. Multiply the data in the 'data' dataset by these values along the channel axis (as indicated by axis attribute) AND by the global conversion factor in the 'conversion' attribute of 'data' to get the data values in Volts, i.e, data in Volts = data * data.conversion * channel_conversion. This approach allows for both global and per-channel data conversion factors needed to support the storage of electrical recordings as native values generated by data acquisition systems. If this dataset is not present, then there is no channel-specific conversion factor, i.e. it is 1 for all channels.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class ElectricalSeriesData(ConfiguredBaseModel):
    """
    Recorded voltage data.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. This value is fixed to 'volts'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion', followed by 'channel_conversion' (if present), and then add 'offset'.""")
    array: Optional[ElectricalSeriesDataArray] = Field(None)
    

class ElectricalSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    num_channels: Optional[float] = Field(None)
    num_samples: Optional[float] = Field(None)
    

class ElectricalSeriesElectrodes(DynamicTableRegion):
    """
    DynamicTableRegion pointer to the electrodes that this time series was generated from.
    """
    table: Optional[DynamicTable] = Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class ElectricalSeriesChannelConversion(ConfiguredBaseModel):
    """
    Channel-specific conversion factor. Multiply the data in the 'data' dataset by these values along the channel axis (as indicated by axis attribute) AND by the global conversion factor in the 'conversion' attribute of 'data' to get the data values in Volts, i.e, data in Volts = data * data.conversion * channel_conversion. This approach allows for both global and per-channel data conversion factors needed to support the storage of electrical recordings as native values generated by data acquisition systems. If this dataset is not present, then there is no channel-specific conversion factor, i.e. it is 1 for all channels.
    """
    axis: Optional[int] = Field(None, description="""The zero-indexed axis of the 'data' dataset that the channel-specific conversion factor corresponds to. This value is fixed to 1.""")
    array: Optional[ElectricalSeriesChannelConversionArray] = Field(None)
    

class ElectricalSeriesChannelConversionArray(Arraylike):
    
    num_channels: float = Field(...)
    

class SpikeEventSeries(ElectricalSeries):
    """
    Stores snapshots/snippets of recorded spike events (i.e., threshold crossings). This may also be raw data, as reported by ephys hardware. If so, the TimeSeries::description field should describe how events were detected. All SpikeEventSeries should reside in a module (under EventWaveform interface) even if the spikes were reported and stored by hardware. All events span the same recording channels and store snapshots of equal duration. TimeSeries::data array structure: [num events] [num channels] [num samples] (or [num events] [num samples] for single electrode).
    """
    data: SpikeEventSeriesData = Field(..., description="""Spike waveforms.""")
    timestamps: SpikeEventSeriesTimestamps = Field(..., description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time. Timestamps are required for the events. Unlike for TimeSeries, timestamps are required for SpikeEventSeries and are thus re-specified here.""")
    filtering: Optional[str] = Field(None, description="""Filtering applied to all channels of the data. For example, if this ElectricalSeries represents high-pass-filtered data (also known as AP Band), then this value could be \"High-pass 4-pole Bessel filter at 500 Hz\". If this ElectricalSeries represents low-pass-filtered LFP data and the type of filter is unknown, then this value could be \"Low-pass filter at 300 Hz\". If a non-standard filter type is used, provide as much detail about the filter properties as possible.""")
    electrodes: ElectricalSeriesElectrodes = Field(..., description="""DynamicTableRegion pointer to the electrodes that this time series was generated from.""")
    channel_conversion: Optional[ElectricalSeriesChannelConversion] = Field(None, description="""Channel-specific conversion factor. Multiply the data in the 'data' dataset by these values along the channel axis (as indicated by axis attribute) AND by the global conversion factor in the 'conversion' attribute of 'data' to get the data values in Volts, i.e, data in Volts = data * data.conversion * channel_conversion. This approach allows for both global and per-channel data conversion factors needed to support the storage of electrical recordings as native values generated by data acquisition systems. If this dataset is not present, then there is no channel-specific conversion factor, i.e. it is 1 for all channels.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class SpikeEventSeriesData(ConfiguredBaseModel):
    """
    Spike waveforms.
    """
    unit: Optional[str] = Field(None, description="""Unit of measurement for waveforms, which is fixed to 'volts'.""")
    array: Optional[SpikeEventSeriesDataArray] = Field(None)
    

class SpikeEventSeriesDataArray(Arraylike):
    
    num_events: float = Field(...)
    num_samples: float = Field(...)
    num_channels: Optional[float] = Field(None)
    

class SpikeEventSeriesTimestamps(ConfiguredBaseModel):
    """
    Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time. Timestamps are required for the events. Unlike for TimeSeries, timestamps are required for SpikeEventSeries and are thus re-specified here.
    """
    interval: Optional[int] = Field(None, description="""Value is '1'""")
    unit: Optional[str] = Field(None, description="""Unit of measurement for timestamps, which is fixed to 'seconds'.""")
    array: Optional[SpikeEventSeriesTimestampsArray] = Field(None)
    

class SpikeEventSeriesTimestampsArray(Arraylike):
    
    num_times: float = Field(...)
    

class FeatureExtraction(NWBDataInterface):
    """
    Features, such as PC1 and PC2, that are extracted from signals stored in a SpikeEventSeries or other source.
    """
    description: FeatureExtractionDescription = Field(..., description="""Description of features (eg, ''PC1'') for each of the extracted features.""")
    features: FeatureExtractionFeatures = Field(..., description="""Multi-dimensional array of features extracted from each event.""")
    times: FeatureExtractionTimes = Field(..., description="""Times of events that features correspond to (can be a link).""")
    electrodes: FeatureExtractionElectrodes = Field(..., description="""DynamicTableRegion pointer to the electrodes that this time series was generated from.""")
    

class FeatureExtractionDescription(ConfiguredBaseModel):
    """
    Description of features (eg, ''PC1'') for each of the extracted features.
    """
    array: Optional[FeatureExtractionDescriptionArray] = Field(None)
    

class FeatureExtractionDescriptionArray(Arraylike):
    
    num_features: str = Field(...)
    

class FeatureExtractionFeatures(ConfiguredBaseModel):
    """
    Multi-dimensional array of features extracted from each event.
    """
    array: Optional[FeatureExtractionFeaturesArray] = Field(None)
    

class FeatureExtractionFeaturesArray(Arraylike):
    
    num_events: Optional[float] = Field(None)
    num_channels: Optional[float] = Field(None)
    num_features: Optional[float] = Field(None)
    

class FeatureExtractionTimes(ConfiguredBaseModel):
    """
    Times of events that features correspond to (can be a link).
    """
    array: Optional[FeatureExtractionTimesArray] = Field(None)
    

class FeatureExtractionTimesArray(Arraylike):
    
    num_events: float = Field(...)
    

class FeatureExtractionElectrodes(DynamicTableRegion):
    """
    DynamicTableRegion pointer to the electrodes that this time series was generated from.
    """
    table: Optional[DynamicTable] = Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

class EventDetection(NWBDataInterface):
    """
    Detected spike events from voltage trace(s).
    """
    detection_method: EventDetectionDetectionMethod = Field(..., description="""Description of how events were detected, such as voltage threshold, or dV/dT threshold, as well as relevant values.""")
    source_idx: EventDetectionSourceIdx = Field(..., description="""Indices (zero-based) into source ElectricalSeries::data array corresponding to time of event. ''description'' should define what is meant by time of event (e.g., .25 ms before action potential peak, zero-crossing time, etc). The index points to each event from the raw data.""")
    times: EventDetectionTimes = Field(..., description="""Timestamps of events, in seconds.""")
    

class EventDetectionDetectionMethod(ConfiguredBaseModel):
    """
    Description of how events were detected, such as voltage threshold, or dV/dT threshold, as well as relevant values.
    """
    None
    

class EventDetectionSourceIdx(ConfiguredBaseModel):
    """
    Indices (zero-based) into source ElectricalSeries::data array corresponding to time of event. ''description'' should define what is meant by time of event (e.g., .25 ms before action potential peak, zero-crossing time, etc). The index points to each event from the raw data.
    """
    array: Optional[EventDetectionSourceIdxArray] = Field(None)
    

class EventDetectionSourceIdxArray(Arraylike):
    
    num_events: int = Field(...)
    

class EventDetectionTimes(ConfiguredBaseModel):
    """
    Timestamps of events, in seconds.
    """
    unit: Optional[str] = Field(None, description="""Unit of measurement for event times, which is fixed to 'seconds'.""")
    array: Optional[EventDetectionTimesArray] = Field(None)
    

class EventDetectionTimesArray(Arraylike):
    
    num_events: float = Field(...)
    

class EventWaveform(NWBDataInterface):
    """
    Represents either the waveforms of detected events, as extracted from a raw data trace in /acquisition, or the event waveforms that were stored during experiment acquisition.
    """
    SpikeEventSeries: Optional[List[SpikeEventSeries]] = Field(default_factory=list, description="""SpikeEventSeries object(s) containing detected spike event waveforms.""")
    

class FilteredEphys(NWBDataInterface):
    """
    Electrophysiology data from one or more channels that has been subjected to filtering. Examples of filtered data include Theta and Gamma (LFP has its own interface). FilteredEphys modules publish an ElectricalSeries for each filtered channel or set of channels. The name of each ElectricalSeries is arbitrary but should be informative. The source of the filtered data, whether this is from analysis of another time series or as acquired by hardware, should be noted in each's TimeSeries::description field. There is no assumed 1::1 correspondence between filtered ephys signals and electrodes, as a single signal can apply to many nearby electrodes, and one electrode may have different filtered (e.g., theta and/or gamma) signals represented. Filter properties should be noted in the ElectricalSeries 'filtering' attribute.
    """
    ElectricalSeries: List[ElectricalSeries] = Field(default_factory=list, description="""ElectricalSeries object(s) containing filtered electrophysiology data.""")
    

class LFP(NWBDataInterface):
    """
    LFP data from one or more channels. The electrode map in each published ElectricalSeries will identify which channels are providing LFP data. Filter properties should be noted in the ElectricalSeries 'filtering' attribute.
    """
    ElectricalSeries: List[ElectricalSeries] = Field(default_factory=list, description="""ElectricalSeries object(s) containing LFP data for one or more channels.""")
    

class ElectrodeGroup(NWBContainer):
    """
    A physical grouping of electrodes, e.g. a shank of an array.
    """
    description: Optional[str] = Field(None, description="""Description of this electrode group.""")
    location: Optional[str] = Field(None, description="""Location of electrode group. Specify the area, layer, comments on estimation of area/layer, etc. Use standard atlas names for anatomical regions when possible.""")
    position: Optional[ElectrodeGroupPosition] = Field(None, description="""stereotaxic or common framework coordinates""")
    

class ElectrodeGroupPosition(ConfiguredBaseModel):
    """
    stereotaxic or common framework coordinates
    """
    None
    

class ClusterWaveforms(NWBDataInterface):
    """
    DEPRECATED The mean waveform shape, including standard deviation, of the different clusters. Ideally, the waveform analysis should be performed on data that is only high-pass filtered. This is a separate module because it is expected to require updating. For example, IMEC probes may require different storage requirements to store/display mean waveforms, requiring a new interface or an extension of this one.
    """
    waveform_filtering: ClusterWaveformsWaveformFiltering = Field(..., description="""Filtering applied to data before generating mean/sd""")
    waveform_mean: ClusterWaveformsWaveformMean = Field(..., description="""The mean waveform for each cluster, using the same indices for each wave as cluster numbers in the associated Clustering module (i.e, cluster 3 is in array slot [3]). Waveforms corresponding to gaps in cluster sequence should be empty (e.g., zero- filled)""")
    waveform_sd: ClusterWaveformsWaveformSd = Field(..., description="""Stdev of waveforms for each cluster, using the same indices as in mean""")
    

class ClusterWaveformsWaveformFiltering(ConfiguredBaseModel):
    """
    Filtering applied to data before generating mean/sd
    """
    None
    

class ClusterWaveformsWaveformMean(ConfiguredBaseModel):
    """
    The mean waveform for each cluster, using the same indices for each wave as cluster numbers in the associated Clustering module (i.e, cluster 3 is in array slot [3]). Waveforms corresponding to gaps in cluster sequence should be empty (e.g., zero- filled)
    """
    array: Optional[ClusterWaveformsWaveformMeanArray] = Field(None)
    

class ClusterWaveformsWaveformMeanArray(Arraylike):
    
    num_clusters: Optional[float] = Field(None)
    num_samples: Optional[float] = Field(None)
    

class ClusterWaveformsWaveformSd(ConfiguredBaseModel):
    """
    Stdev of waveforms for each cluster, using the same indices as in mean
    """
    array: Optional[ClusterWaveformsWaveformSdArray] = Field(None)
    

class ClusterWaveformsWaveformSdArray(Arraylike):
    
    num_clusters: Optional[float] = Field(None)
    num_samples: Optional[float] = Field(None)
    

class Clustering(NWBDataInterface):
    """
    DEPRECATED Clustered spike data, whether from automatic clustering tools (e.g., klustakwik) or as a result of manual sorting.
    """
    description: ClusteringDescription = Field(..., description="""Description of clusters or clustering, (e.g. cluster 0 is noise, clusters curated using Klusters, etc)""")
    num: ClusteringNum = Field(..., description="""Cluster number of each event""")
    peak_over_rms: ClusteringPeakOverRms = Field(..., description="""Maximum ratio of waveform peak to RMS on any channel in the cluster (provides a basic clustering metric).""")
    times: ClusteringTimes = Field(..., description="""Times of clustered events, in seconds. This may be a link to times field in associated FeatureExtraction module.""")
    

class ClusteringDescription(ConfiguredBaseModel):
    """
    Description of clusters or clustering, (e.g. cluster 0 is noise, clusters curated using Klusters, etc)
    """
    None
    

class ClusteringNum(ConfiguredBaseModel):
    """
    Cluster number of each event
    """
    array: Optional[ClusteringNumArray] = Field(None)
    

class ClusteringNumArray(Arraylike):
    
    num_events: int = Field(...)
    

class ClusteringPeakOverRms(ConfiguredBaseModel):
    """
    Maximum ratio of waveform peak to RMS on any channel in the cluster (provides a basic clustering metric).
    """
    array: Optional[ClusteringPeakOverRmsArray] = Field(None)
    

class ClusteringPeakOverRmsArray(Arraylike):
    
    num_clusters: float = Field(...)
    

class ClusteringTimes(ConfiguredBaseModel):
    """
    Times of clustered events, in seconds. This may be a link to times field in associated FeatureExtraction module.
    """
    array: Optional[ClusteringTimesArray] = Field(None)
    

class ClusteringTimesArray(Arraylike):
    
    num_events: float = Field(...)
    

class SpatialSeries(TimeSeries):
    """
    Direction, e.g., of gaze or travel, or position. The TimeSeries::data field is a 2D array storing position or direction relative to some reference frame. Array structure: [num measurements] [num dimensions]. Each SpatialSeries has a text dataset reference_frame that indicates the zero-position, or the zero-axes for direction. For example, if representing gaze direction, 'straight-ahead' might be a specific pixel on the monitor, or some other point in space. For position data, the 0,0 point might be the top-left corner of an enclosure, as viewed from the tracking camera. The unit of data will indicate how to interpret SpatialSeries values.
    """
    data: SpatialSeriesData = Field(..., description="""1-D or 2-D array storing position or direction relative to some reference frame.""")
    reference_frame: Optional[SpatialSeriesReferenceFrame] = Field(None, description="""Description defining what exactly 'straight-ahead' means.""")
    description: Optional[str] = Field(None, description="""Description of the time series.""")
    comments: Optional[str] = Field(None, description="""Human-readable comments about the TimeSeries. This second descriptive field can be used to store additional information, or descriptive information if the primary description field is populated with a computer-readable string.""")
    starting_time: Optional[TimeSeriesStartingTime] = Field(None, description="""Timestamp of the first sample in seconds. When timestamps are uniformly spaced, the timestamp of the first sample can be specified and all subsequent ones calculated from the sampling rate attribute.""")
    timestamps: Optional[TimeSeriesTimestamps] = Field(None, description="""Timestamps for samples stored in data, in seconds, relative to the common experiment master-clock stored in NWBFile.timestamps_reference_time.""")
    control: Optional[TimeSeriesControl] = Field(None, description="""Numerical labels that apply to each time point in data for the purpose of querying and slicing data by these values. If present, the length of this array should be the same size as the first dimension of data.""")
    control_description: Optional[TimeSeriesControlDescription] = Field(None, description="""Description of each control value. Must be present if control is present. If present, control_description[0] should describe time points where control == 0.""")
    sync: Optional[TimeSeriesSync] = Field(None, description="""Lab-specific time and sync information as provided directly from hardware devices and that is necessary for aligning all acquired time information to a common timebase. The timestamp array stores time in the common timebase. This group will usually only be populated in TimeSeries that are stored external to the NWB file, in files storing raw data. Once timestamp data is calculated, the contents of 'sync' are mostly for archival purposes.""")
    

class SpatialSeriesData(ConfiguredBaseModel):
    """
    1-D or 2-D array storing position or direction relative to some reference frame.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. The default value is 'meters'. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion' and add 'offset'.""")
    array: Optional[SpatialSeriesDataArray] = Field(None)
    

class SpatialSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    x: Optional[float] = Field(None)
    xy: Optional[float] = Field(None)
    xyz: Optional[float] = Field(None)
    

class SpatialSeriesReferenceFrame(ConfiguredBaseModel):
    """
    Description defining what exactly 'straight-ahead' means.
    """
    None
    

class BehavioralEpochs(NWBDataInterface):
    """
    TimeSeries for storing behavioral epochs.  The objective of this and the other two Behavioral interfaces (e.g. BehavioralEvents and BehavioralTimeSeries) is to provide generic hooks for software tools/scripts. This allows a tool/script to take the output one specific interface (e.g., UnitTimes) and plot that data relative to another data modality (e.g., behavioral events) without having to define all possible modalities in advance. Declaring one of these interfaces means that one or more TimeSeries of the specified type is published. These TimeSeries should reside in a group having the same name as the interface. For example, if a BehavioralTimeSeries interface is declared, the module will have one or more TimeSeries defined in the module sub-group 'BehavioralTimeSeries'. BehavioralEpochs should use IntervalSeries. BehavioralEvents is used for irregular events. BehavioralTimeSeries is for continuous data.
    """
    IntervalSeries: Optional[List[IntervalSeries]] = Field(default_factory=list, description="""IntervalSeries object containing start and stop times of epochs.""")
    

class BehavioralEvents(NWBDataInterface):
    """
    TimeSeries for storing behavioral events. See description of <a href=\"#BehavioralEpochs\">BehavioralEpochs</a> for more details.
    """
    TimeSeries: Optional[List[TimeSeries]] = Field(default_factory=list, description="""TimeSeries object containing behavioral events.""")
    

class BehavioralTimeSeries(NWBDataInterface):
    """
    TimeSeries for storing Behavoioral time series data. See description of <a href=\"#BehavioralEpochs\">BehavioralEpochs</a> for more details.
    """
    TimeSeries: Optional[List[TimeSeries]] = Field(default_factory=list, description="""TimeSeries object containing continuous behavioral data.""")
    

class PupilTracking(NWBDataInterface):
    """
    Eye-tracking data, representing pupil size.
    """
    TimeSeries: List[TimeSeries] = Field(default_factory=list, description="""TimeSeries object containing time series data on pupil size.""")
    

class EyeTracking(NWBDataInterface):
    """
    Eye-tracking data, representing direction of gaze.
    """
    SpatialSeries: Optional[List[SpatialSeries]] = Field(default_factory=list, description="""SpatialSeries object containing data measuring direction of gaze.""")
    

class CompassDirection(NWBDataInterface):
    """
    With a CompassDirection interface, a module publishes a SpatialSeries object representing a floating point value for theta. The SpatialSeries::reference_frame field should indicate what direction corresponds to 0 and which is the direction of rotation (this should be clockwise). The si_unit for the SpatialSeries should be radians or degrees.
    """
    SpatialSeries: Optional[List[SpatialSeries]] = Field(default_factory=list, description="""SpatialSeries object containing direction of gaze travel.""")
    

class Position(NWBDataInterface):
    """
    Position data, whether along the x, x/y or x/y/z axis.
    """
    SpatialSeries: List[SpatialSeries] = Field(default_factory=list, description="""SpatialSeries object containing position data.""")
    

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
    

class AbstractFeatureSeriesData(ConfiguredBaseModel):
    """
    Values of each feature at each time.
    """
    unit: Optional[str] = Field(None, description="""Since there can be different units for different features, store the units in 'feature_units'. The default value for this attribute is \"see 'feature_units'\".""")
    array: Optional[AbstractFeatureSeriesDataArray] = Field(None)
    

class AbstractFeatureSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    num_features: Optional[float] = Field(None)
    

class AbstractFeatureSeriesFeatureUnits(ConfiguredBaseModel):
    """
    Units of each feature.
    """
    array: Optional[AbstractFeatureSeriesFeatureUnitsArray] = Field(None)
    

class AbstractFeatureSeriesFeatureUnitsArray(Arraylike):
    
    num_features: str = Field(...)
    

class AbstractFeatureSeriesFeatures(ConfiguredBaseModel):
    """
    Description of the features represented in TimeSeries::data.
    """
    array: Optional[AbstractFeatureSeriesFeaturesArray] = Field(None)
    

class AbstractFeatureSeriesFeaturesArray(Arraylike):
    
    num_features: str = Field(...)
    

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
    

class AnnotationSeriesData(ConfiguredBaseModel):
    """
    Annotations made during an experiment.
    """
    resolution: Optional[float] = Field(None, description="""Smallest meaningful difference between values in data. Annotations have no units, so the value is fixed to -1.0.""")
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. Annotations have no units, so the value is fixed to 'n/a'.""")
    array: Optional[AnnotationSeriesDataArray] = Field(None)
    

class AnnotationSeriesDataArray(Arraylike):
    
    num_times: str = Field(...)
    

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
    

class IntervalSeriesData(ConfiguredBaseModel):
    """
    Use values >0 if interval started, <0 if interval ended.
    """
    resolution: Optional[float] = Field(None, description="""Smallest meaningful difference between values in data. Annotations have no units, so the value is fixed to -1.0.""")
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. Annotations have no units, so the value is fixed to 'n/a'.""")
    array: Optional[IntervalSeriesDataArray] = Field(None)
    

class IntervalSeriesDataArray(Arraylike):
    
    num_times: int = Field(...)
    

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
    

class DecompositionSeriesData(ConfiguredBaseModel):
    """
    Data decomposed into frequency bands.
    """
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. Actual stored values are not necessarily stored in these units. To access the data in these units, multiply 'data' by 'conversion'.""")
    array: Optional[DecompositionSeriesDataArray] = Field(None)
    

class DecompositionSeriesDataArray(Arraylike):
    
    num_times: Optional[float] = Field(None)
    num_channels: Optional[float] = Field(None)
    num_bands: Optional[float] = Field(None)
    

class DecompositionSeriesMetric(ConfiguredBaseModel):
    """
    The metric used, e.g. phase, amplitude, power.
    """
    None
    

class DecompositionSeriesSourceChannels(DynamicTableRegion):
    """
    DynamicTableRegion pointer to the channels that this decomposition series was generated from.
    """
    table: Optional[DynamicTable] = Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

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
    

class DecompositionSeriesBandsBandLimitsArray(Arraylike):
    
    num_bands: Optional[float] = Field(None)
    low_high: Optional[float] = Field(None)
    

class DecompositionSeriesBandsBandMean(VectorData):
    """
    The mean Gaussian filters, in Hz.
    """
    array: Optional[DecompositionSeriesBandsBandMeanArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class DecompositionSeriesBandsBandMeanArray(Arraylike):
    
    num_bands: float = Field(...)
    

class DecompositionSeriesBandsBandStdev(VectorData):
    """
    The standard deviation of Gaussian filters, in Hz.
    """
    array: Optional[DecompositionSeriesBandsBandStdevArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class DecompositionSeriesBandsBandStdevArray(Arraylike):
    
    num_bands: float = Field(...)
    

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
    

class UnitsSpikeTimesIndex(VectorIndex):
    """
    Index into the spike_times dataset.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsSpikeTimes(VectorData):
    """
    Spike times for each unit in seconds.
    """
    resolution: Optional[float] = Field(None, description="""The smallest possible difference between two spike times. Usually 1 divided by the acquisition sampling rate from which spike times were extracted, but could be larger if the acquisition time series was downsampled or smaller if the acquisition time series was smoothed/interpolated and it is possible for the spike time to be between samples.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class UnitsObsIntervalsIndex(VectorIndex):
    """
    Index into the obs_intervals dataset.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsObsIntervals(VectorData):
    """
    Observation intervals for each unit.
    """
    array: Optional[UnitsObsIntervalsArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsObsIntervalsArray(Arraylike):
    
    num_intervals: Optional[float] = Field(None)
    start|end: Optional[float] = Field(None)
    

class UnitsElectrodesIndex(VectorIndex):
    """
    Index into electrodes.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsElectrodes(DynamicTableRegion):
    """
    Electrode that each spike unit came from, specified using a DynamicTableRegion.
    """
    table: Optional[DynamicTable] = Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[DynamicTableRegionArray] = Field(None)
    

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
    

class UnitsWaveformMeanArray(Arraylike):
    
    num_units: float = Field(...)
    num_samples: float = Field(...)
    num_electrodes: Optional[float] = Field(None)
    

class UnitsWaveformSd(VectorData):
    """
    Spike waveform standard deviation for each spike unit.
    """
    sampling_rate: Optional[float] = Field(None, description="""Sampling rate, in hertz.""")
    unit: Optional[str] = Field(None, description="""Unit of measurement. This value is fixed to 'volts'.""")
    array: Optional[UnitsWaveformSdArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsWaveformSdArray(Arraylike):
    
    num_units: float = Field(...)
    num_samples: float = Field(...)
    num_electrodes: Optional[float] = Field(None)
    

class UnitsWaveforms(VectorData):
    """
    Individual waveforms for each spike on each electrode. This is a doubly indexed column. The 'waveforms_index' column indexes which waveforms in this column belong to the same spike event for a given unit, where each waveform was recorded from a different electrode. The 'waveforms_index_index' column indexes the 'waveforms_index' column to indicate which spike events belong to a given unit. For example, if the 'waveforms_index_index' column has values [2, 5, 6], then the first 2 elements of the 'waveforms_index' column correspond to the 2 spike events of the first unit, the next 3 elements of the 'waveforms_index' column correspond to the 3 spike events of the second unit, and the next 1 element of the 'waveforms_index' column corresponds to the 1 spike event of the third unit. If the 'waveforms_index' column has values [3, 6, 8, 10, 12, 13], then the first 3 elements of the 'waveforms' column contain the 3 spike waveforms that were recorded from 3 different electrodes for the first spike time of the first unit. See https://nwb-schema.readthedocs.io/en/stable/format_description.html#doubly-ragged-arrays for a graphical representation of this example. When there is only one electrode for each unit (i.e., each spike time is associated with a single waveform), then the 'waveforms_index' column will have values 1, 2, ..., N, where N is the number of spike events. The number of electrodes for each spike event should be the same within a given unit. The 'electrodes' column should be used to indicate which electrodes are associated with each unit, and the order of the waveforms within a given unit x spike event should be in the same order as the electrodes referenced in the 'electrodes' column of this table. The number of samples for each waveform must be the same.
    """
    sampling_rate: Optional[float] = Field(None, description="""Sampling rate, in hertz.""")
    unit: Optional[str] = Field(None, description="""Unit of measurement. This value is fixed to 'volts'.""")
    array: Optional[UnitsWaveformsArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class UnitsWaveformsArray(Arraylike):
    
    num_waveforms: Optional[float] = Field(None)
    num_samples: Optional[float] = Field(None)
    

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
    identifier: NWBFileIdentifier = Field(..., description="""A unique text identifier for the file. For example, concatenated lab name, file creation date/time and experimentalist, or a hash of these and/or other values. The goal is that the string should be unique to all other files.""")
    session_description: NWBFileSessionDescription = Field(..., description="""A description of the experimental session and data in the file.""")
    session_start_time: NWBFileSessionStartTime = Field(..., description="""Date and time of the experiment/session start. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted string: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds.""")
    timestamps_reference_time: NWBFileTimestampsReferenceTime = Field(..., description="""Date and time corresponding to time zero of all timestamps. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted string: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds. All times stored in the file use this time as reference (i.e., time zero).""")
    acquisition: NWBFileAcquisition = Field(..., description="""Data streams recorded from the system, including ephys, ophys, tracking, etc. This group should be read-only after the experiment is completed and timestamps are corrected to a common timebase. The data stored here may be links to raw data stored in external NWB files. This will allow keeping bulky raw data out of the file while preserving the option of keeping some/all in the file. Acquired data includes tracking and experimental data streams (i.e., everything measured from the system). If bulky data is stored in the /acquisition group, the data can exist in a separate NWB file that is linked to by the file being used for processing and analysis.""")
    analysis: NWBFileAnalysis = Field(..., description="""Lab-specific and custom scientific analysis of data. There is no defined format for the content of this group - the format is up to the individual user/lab. To facilitate sharing analysis data between labs, the contents here should be stored in standard types (e.g., neurodata_types) and appropriately documented. The file can store lab-specific and custom data analysis without restriction on its form or schema, reducing data formatting restrictions on end users. Such data should be placed in the analysis group. The analysis data should be documented so that it could be shared with other labs.""")
    scratch: Optional[NWBFileScratch] = Field(None, description="""A place to store one-off analysis results. Data placed here is not intended for sharing. By placing data here, users acknowledge that there is no guarantee that their data meets any standard.""")
    processing: NWBFileProcessing = Field(..., description="""The home for ProcessingModules. These modules perform intermediate analysis of data that is necessary to perform before scientific analysis. Examples include spike clustering, extracting position from tracking data, stitching together image slices. ProcessingModules can be large and express many data sets from relatively complex analysis (e.g., spike detection and clustering) or small, representing extraction of position information from tracking video, or even binary lick/no-lick decisions. Common software tools (e.g., klustakwik, MClust) are expected to read/write data here.  'Processing' refers to intermediate analysis of the acquired data to make it more amenable to scientific analysis.""")
    stimulus: NWBFileStimulus = Field(..., description="""Data pushed into the system (eg, video stimulus, sound, voltage, etc) and secondary representations of that data (eg, measurements of something used as a stimulus). This group should be made read-only after experiment complete and timestamps are corrected to common timebase. Stores both presented stimuli and stimulus templates, the latter in case the same stimulus is presented multiple times, or is pulled from an external stimulus library. Stimuli are here defined as any signal that is pushed into the system as part of the experiment (eg, sound, video, voltage, etc). Many different experiments can use the same stimuli, and stimuli can be re-used during an experiment. The stimulus group is organized so that one version of template stimuli can be stored and these be used multiple times. These templates can exist in the present file or can be linked to a remote library file.""")
    general: NWBFileGeneral = Field(..., description="""Experimental metadata, including protocol, notes and description of hardware device(s).  The metadata stored in this section should be used to describe the experiment. Metadata necessary for interpreting the data is stored with the data. General experimental metadata, including animal strain, experimental protocols, experimenter, devices, etc, are stored under 'general'. Core metadata (e.g., that required to interpret data fields) is stored with the data itself, and implicitly defined by the file specification (e.g., time is in seconds). The strategy used here for storing non-core metadata is to use free-form text fields, such as would appear in sentences or paragraphs from a Methods section. Metadata fields are text to enable them to be more general, for example to represent ranges instead of numerical values. Machine-readable metadata is stored as attributes to these free-form datasets. All entries in the below table are to be included when data is present. Unused groups (e.g., intracellular_ephys in an optophysiology experiment) should not be created unless there is data to store within them.""")
    intervals: Optional[NWBFileIntervals] = Field(None, description="""Experimental intervals, whether that be logically distinct sub-experiments having a particular scientific goal, trials (see trials subgroup) during an experiment, or epochs (see epochs subgroup) deriving from analysis of data.""")
    units: Optional[NWBFileUnits] = Field(None, description="""Data about sorted spike units.""")
    

class NWBFileFileCreateDate(ConfiguredBaseModel):
    """
    A record of the date the file was created and of subsequent modifications. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted strings: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds. The file can be created after the experiment was run, so this may differ from the experiment start time. Each modification to the nwb file adds a new entry to the array.
    """
    array: Optional[NWBFileFileCreateDateArray] = Field(None)
    

class NWBFileFileCreateDateArray(Arraylike):
    
    num_modifications: date = Field(...)
    

class NWBFileIdentifier(ConfiguredBaseModel):
    """
    A unique text identifier for the file. For example, concatenated lab name, file creation date/time and experimentalist, or a hash of these and/or other values. The goal is that the string should be unique to all other files.
    """
    None
    

class NWBFileSessionDescription(ConfiguredBaseModel):
    """
    A description of the experimental session and data in the file.
    """
    None
    

class NWBFileSessionStartTime(ConfiguredBaseModel):
    """
    Date and time of the experiment/session start. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted string: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds.
    """
    None
    

class NWBFileTimestampsReferenceTime(ConfiguredBaseModel):
    """
    Date and time corresponding to time zero of all timestamps. The date is stored in UTC with local timezone offset as ISO 8601 extended formatted string: 2018-09-28T14:43:54.123+02:00. Dates stored in UTC end in \"Z\" with no timezone offset. Date accuracy is up to milliseconds. All times stored in the file use this time as reference (i.e., time zero).
    """
    None
    

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
    data_collection: Optional[NWBFileGeneralDataCollection] = Field(None, description="""Notes about data collection and analysis.""")
    experiment_description: Optional[NWBFileGeneralExperimentDescription] = Field(None, description="""General description of the experiment.""")
    experimenter: Optional[NWBFileGeneralExperimenter] = Field(None, description="""Name of person(s) who performed the experiment. Can also specify roles of different people involved.""")
    institution: Optional[NWBFileGeneralInstitution] = Field(None, description="""Institution(s) where experiment was performed.""")
    keywords: Optional[NWBFileGeneralKeywords] = Field(None, description="""Terms to search over.""")
    lab: Optional[NWBFileGeneralLab] = Field(None, description="""Laboratory where experiment was performed.""")
    notes: Optional[NWBFileGeneralNotes] = Field(None, description="""Notes about the experiment.""")
    pharmacology: Optional[NWBFileGeneralPharmacology] = Field(None, description="""Description of drugs used, including how and when they were administered. Anesthesia(s), painkiller(s), etc., plus dosage, concentration, etc.""")
    protocol: Optional[NWBFileGeneralProtocol] = Field(None, description="""Experimental protocol, if applicable. e.g., include IACUC protocol number.""")
    related_publications: Optional[NWBFileGeneralRelatedPublications] = Field(None, description="""Publication information. PMID, DOI, URL, etc.""")
    session_id: Optional[NWBFileGeneralSessionId] = Field(None, description="""Lab-specific ID for the session.""")
    slices: Optional[NWBFileGeneralSlices] = Field(None, description="""Description of slices, including information about preparation thickness, orientation, temperature, and bath solution.""")
    source_script: Optional[NWBFileGeneralSourceScript] = Field(None, description="""Script file or link to public source code used to create this NWB file.""")
    stimulus: Optional[NWBFileGeneralStimulus] = Field(None, description="""Notes about stimuli, such as how and where they were presented.""")
    surgery: Optional[NWBFileGeneralSurgery] = Field(None, description="""Narrative description about surgery/surgeries, including date(s) and who performed surgery.""")
    virus: Optional[NWBFileGeneralVirus] = Field(None, description="""Information about virus(es) used in experiments, including virus ID, source, date made, injection location, volume, etc.""")
    LabMetaData: Optional[List[LabMetaData]] = Field(default_factory=list, description="""Place-holder than can be extended so that lab-specific meta-data can be placed in /general.""")
    devices: Optional[NWBFileGeneralDevices] = Field(None, description="""Description of hardware devices used during experiment, e.g., monitors, ADC boards, microscopes, etc.""")
    subject: Optional[NWBFileGeneralSubject] = Field(None, description="""Information about the animal or person from which the data was measured.""")
    extracellular_ephys: Optional[NWBFileGeneralExtracellularEphys] = Field(None, description="""Metadata related to extracellular electrophysiology.""")
    intracellular_ephys: Optional[NWBFileGeneralIntracellularEphys] = Field(None, description="""Metadata related to intracellular electrophysiology.""")
    optogenetics: Optional[NWBFileGeneralOptogenetics] = Field(None, description="""Metadata describing optogenetic stimuluation.""")
    optophysiology: Optional[NWBFileGeneralOptophysiology] = Field(None, description="""Metadata related to optophysiology.""")
    

class NWBFileGeneralDataCollection(ConfiguredBaseModel):
    """
    Notes about data collection and analysis.
    """
    None
    

class NWBFileGeneralExperimentDescription(ConfiguredBaseModel):
    """
    General description of the experiment.
    """
    None
    

class NWBFileGeneralExperimenter(ConfiguredBaseModel):
    """
    Name of person(s) who performed the experiment. Can also specify roles of different people involved.
    """
    array: Optional[NWBFileGeneralExperimenterArray] = Field(None)
    

class NWBFileGeneralExperimenterArray(Arraylike):
    
    num_experimenters: str = Field(...)
    

class NWBFileGeneralInstitution(ConfiguredBaseModel):
    """
    Institution(s) where experiment was performed.
    """
    None
    

class NWBFileGeneralKeywords(ConfiguredBaseModel):
    """
    Terms to search over.
    """
    array: Optional[NWBFileGeneralKeywordsArray] = Field(None)
    

class NWBFileGeneralKeywordsArray(Arraylike):
    
    num_keywords: str = Field(...)
    

class NWBFileGeneralLab(ConfiguredBaseModel):
    """
    Laboratory where experiment was performed.
    """
    None
    

class NWBFileGeneralNotes(ConfiguredBaseModel):
    """
    Notes about the experiment.
    """
    None
    

class NWBFileGeneralPharmacology(ConfiguredBaseModel):
    """
    Description of drugs used, including how and when they were administered. Anesthesia(s), painkiller(s), etc., plus dosage, concentration, etc.
    """
    None
    

class NWBFileGeneralProtocol(ConfiguredBaseModel):
    """
    Experimental protocol, if applicable. e.g., include IACUC protocol number.
    """
    None
    

class NWBFileGeneralRelatedPublications(ConfiguredBaseModel):
    """
    Publication information. PMID, DOI, URL, etc.
    """
    array: Optional[NWBFileGeneralRelatedPublicationsArray] = Field(None)
    

class NWBFileGeneralRelatedPublicationsArray(Arraylike):
    
    num_publications: str = Field(...)
    

class NWBFileGeneralSessionId(ConfiguredBaseModel):
    """
    Lab-specific ID for the session.
    """
    None
    

class NWBFileGeneralSlices(ConfiguredBaseModel):
    """
    Description of slices, including information about preparation thickness, orientation, temperature, and bath solution.
    """
    None
    

class NWBFileGeneralSourceScript(ConfiguredBaseModel):
    """
    Script file or link to public source code used to create this NWB file.
    """
    file_name: Optional[str] = Field(None, description="""Name of script file.""")
    

class NWBFileGeneralStimulus(ConfiguredBaseModel):
    """
    Notes about stimuli, such as how and where they were presented.
    """
    None
    

class NWBFileGeneralSurgery(ConfiguredBaseModel):
    """
    Narrative description about surgery/surgeries, including date(s) and who performed surgery.
    """
    None
    

class NWBFileGeneralVirus(ConfiguredBaseModel):
    """
    Information about virus(es) used in experiments, including virus ID, source, date made, injection location, volume, etc.
    """
    None
    

class NWBFileGeneralDevices(ConfiguredBaseModel):
    """
    Description of hardware devices used during experiment, e.g., monitors, ADC boards, microscopes, etc.
    """
    Device: Optional[List[Device]] = Field(default_factory=list, description="""Data acquisition devices.""")
    

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
    x: Optional[NWBFileGeneralExtracellularEphysElectrodesX] = Field(None, description="""x coordinate of the channel location in the brain (+x is posterior).""")
    y: Optional[NWBFileGeneralExtracellularEphysElectrodesY] = Field(None, description="""y coordinate of the channel location in the brain (+y is inferior).""")
    z: Optional[NWBFileGeneralExtracellularEphysElectrodesZ] = Field(None, description="""z coordinate of the channel location in the brain (+z is right).""")
    imp: Optional[NWBFileGeneralExtracellularEphysElectrodesImp] = Field(None, description="""Impedance of the channel, in ohms.""")
    location: NWBFileGeneralExtracellularEphysElectrodesLocation = Field(..., description="""Location of the electrode (channel). Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.""")
    filtering: Optional[NWBFileGeneralExtracellularEphysElectrodesFiltering] = Field(None, description="""Description of hardware filtering, including the filter name and frequency cutoffs.""")
    group: NWBFileGeneralExtracellularEphysElectrodesGroup = Field(..., description="""Reference to the ElectrodeGroup this electrode is a part of.""")
    group_name: NWBFileGeneralExtracellularEphysElectrodesGroupName = Field(..., description="""Name of the ElectrodeGroup this electrode is a part of.""")
    rel_x: Optional[NWBFileGeneralExtracellularEphysElectrodesRelX] = Field(None, description="""x coordinate in electrode group""")
    rel_y: Optional[NWBFileGeneralExtracellularEphysElectrodesRelY] = Field(None, description="""y coordinate in electrode group""")
    rel_z: Optional[NWBFileGeneralExtracellularEphysElectrodesRelZ] = Field(None, description="""z coordinate in electrode group""")
    reference: Optional[NWBFileGeneralExtracellularEphysElectrodesReference] = Field(None, description="""Description of the reference electrode and/or reference scheme used for this electrode, e.g., \"stainless steel skull screw\" or \"online common average referencing\".""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class NWBFileGeneralExtracellularEphysElectrodesX(VectorData):
    """
    x coordinate of the channel location in the brain (+x is posterior).
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class NWBFileGeneralExtracellularEphysElectrodesY(VectorData):
    """
    y coordinate of the channel location in the brain (+y is inferior).
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class NWBFileGeneralExtracellularEphysElectrodesZ(VectorData):
    """
    z coordinate of the channel location in the brain (+z is right).
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class NWBFileGeneralExtracellularEphysElectrodesImp(VectorData):
    """
    Impedance of the channel, in ohms.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class NWBFileGeneralExtracellularEphysElectrodesLocation(VectorData):
    """
    Location of the electrode (channel). Specify the area, layer, comments on estimation of area/layer, stereotaxic coordinates if in vivo, etc. Use standard atlas names for anatomical regions when possible.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class NWBFileGeneralExtracellularEphysElectrodesFiltering(VectorData):
    """
    Description of hardware filtering, including the filter name and frequency cutoffs.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class NWBFileGeneralExtracellularEphysElectrodesGroup(VectorData):
    """
    Reference to the ElectrodeGroup this electrode is a part of.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class NWBFileGeneralExtracellularEphysElectrodesGroupName(VectorData):
    """
    Name of the ElectrodeGroup this electrode is a part of.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class NWBFileGeneralExtracellularEphysElectrodesRelX(VectorData):
    """
    x coordinate in electrode group
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class NWBFileGeneralExtracellularEphysElectrodesRelY(VectorData):
    """
    y coordinate in electrode group
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class NWBFileGeneralExtracellularEphysElectrodesRelZ(VectorData):
    """
    z coordinate in electrode group
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class NWBFileGeneralExtracellularEphysElectrodesReference(VectorData):
    """
    Description of the reference electrode and/or reference scheme used for this electrode, e.g., \"stainless steel skull screw\" or \"online common average referencing\".
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class NWBFileGeneralIntracellularEphys(ConfiguredBaseModel):
    """
    Metadata related to intracellular electrophysiology.
    """
    filtering: Optional[NWBFileGeneralIntracellularEphysFiltering] = Field(None, description="""[DEPRECATED] Use IntracellularElectrode.filtering instead. Description of filtering used. Includes filtering type and parameters, frequency fall-off, etc. If this changes between TimeSeries, filter description should be stored as a text attribute for each TimeSeries.""")
    IntracellularElectrode: Optional[List[IntracellularElectrode]] = Field(default_factory=list, description="""An intracellular electrode.""")
    sweep_table: Optional[NWBFileGeneralIntracellularEphysSweepTable] = Field(None, description="""[DEPRECATED] Table used to group different PatchClampSeries. SweepTable is being replaced by IntracellularRecordingsTable and SimultaneousRecordingsTable tables. Additional SequentialRecordingsTable, RepetitionsTable and ExperimentalConditions tables provide enhanced support for experiment metadata.""")
    intracellular_recordings: Optional[NWBFileGeneralIntracellularEphysIntracellularRecordings] = Field(None, description="""A table to group together a stimulus and response from a single electrode and a single simultaneous recording. Each row in the table represents a single recording consisting typically of a stimulus and a corresponding response. In some cases, however, only a stimulus or a response are recorded as as part of an experiment. In this case both, the stimulus and response will point to the same TimeSeries while the idx_start and count of the invalid column will be set to -1, thus, indicating that no values have been recorded for the stimulus or response, respectively. Note, a recording MUST contain at least a stimulus or a response. Typically the stimulus and response are PatchClampSeries. However, the use of AD/DA channels that are not associated to an electrode is also common in intracellular electrophysiology, in which case other TimeSeries may be used.""")
    simultaneous_recordings: Optional[NWBFileGeneralIntracellularEphysSimultaneousRecordings] = Field(None, description="""A table for grouping different intracellular recordings from the IntracellularRecordingsTable table together that were recorded simultaneously from different electrodes""")
    sequential_recordings: Optional[NWBFileGeneralIntracellularEphysSequentialRecordings] = Field(None, description="""A table for grouping different sequential recordings from the SimultaneousRecordingsTable table together. This is typically used to group together sequential recordings where the a sequence of stimuli of the same type with varying parameters have been presented in a sequence.""")
    repetitions: Optional[NWBFileGeneralIntracellularEphysRepetitions] = Field(None, description="""A table for grouping different sequential intracellular recordings together. With each SequentialRecording typically representing a particular type of stimulus, the RepetitionsTable table is typically used to group sets of stimuli applied in sequence.""")
    experimental_conditions: Optional[NWBFileGeneralIntracellularEphysExperimentalConditions] = Field(None, description="""A table for grouping different intracellular recording repetitions together that belong to the same experimental experimental_conditions.""")
    

class NWBFileGeneralIntracellularEphysFiltering(ConfiguredBaseModel):
    """
    [DEPRECATED] Use IntracellularElectrode.filtering instead. Description of filtering used. Includes filtering type and parameters, frequency fall-off, etc. If this changes between TimeSeries, filter description should be stored as a text attribute for each TimeSeries.
    """
    None
    

class NWBFileGeneralIntracellularEphysSweepTable(SweepTable):
    """
    [DEPRECATED] Table used to group different PatchClampSeries. SweepTable is being replaced by IntracellularRecordingsTable and SimultaneousRecordingsTable tables. Additional SequentialRecordingsTable, RepetitionsTable and ExperimentalConditions tables provide enhanced support for experiment metadata.
    """
    sweep_number: SweepTableSweepNumber = Field(..., description="""Sweep number of the PatchClampSeries in that row.""")
    series: SweepTableSeries = Field(..., description="""The PatchClampSeries with the sweep number in that row.""")
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
    stimulus_type: SequentialRecordingsTableStimulusType = Field(..., description="""The type of stimulus used for the sequential recording.""")
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
    date_of_birth: Optional[SubjectDateOfBirth] = Field(None, description="""Date of birth of subject. Can be supplied instead of 'age'.""")
    description: Optional[SubjectDescription] = Field(None, description="""Description of subject and where subject came from (e.g., breeder, if animal).""")
    genotype: Optional[SubjectGenotype] = Field(None, description="""Genetic strain. If absent, assume Wild Type (WT).""")
    sex: Optional[SubjectSex] = Field(None, description="""Gender of subject.""")
    species: Optional[SubjectSpecies] = Field(None, description="""Species of subject.""")
    strain: Optional[SubjectStrain] = Field(None, description="""Strain of subject.""")
    subject_id: Optional[SubjectSubjectId] = Field(None, description="""ID of animal/person used/participating in experiment (lab convention).""")
    weight: Optional[SubjectWeight] = Field(None, description="""Weight at time of experiment, at time of surgery and at other important times.""")
    

class NWBFileGeneralSubject(Subject):
    """
    Information about the animal or person from which the data was measured.
    """
    age: Optional[SubjectAge] = Field(None, description="""Age of subject. Can be supplied instead of 'date_of_birth'.""")
    date_of_birth: Optional[SubjectDateOfBirth] = Field(None, description="""Date of birth of subject. Can be supplied instead of 'age'.""")
    description: Optional[SubjectDescription] = Field(None, description="""Description of subject and where subject came from (e.g., breeder, if animal).""")
    genotype: Optional[SubjectGenotype] = Field(None, description="""Genetic strain. If absent, assume Wild Type (WT).""")
    sex: Optional[SubjectSex] = Field(None, description="""Gender of subject.""")
    species: Optional[SubjectSpecies] = Field(None, description="""Species of subject.""")
    strain: Optional[SubjectStrain] = Field(None, description="""Strain of subject.""")
    subject_id: Optional[SubjectSubjectId] = Field(None, description="""ID of animal/person used/participating in experiment (lab convention).""")
    weight: Optional[SubjectWeight] = Field(None, description="""Weight at time of experiment, at time of surgery and at other important times.""")
    

class SubjectAge(ConfiguredBaseModel):
    """
    Age of subject. Can be supplied instead of 'date_of_birth'.
    """
    reference: Optional[str] = Field(None, description="""Age is with reference to this event. Can be 'birth' or 'gestational'. If reference is omitted, 'birth' is implied.""")
    

class SubjectDateOfBirth(ConfiguredBaseModel):
    """
    Date of birth of subject. Can be supplied instead of 'age'.
    """
    None
    

class SubjectDescription(ConfiguredBaseModel):
    """
    Description of subject and where subject came from (e.g., breeder, if animal).
    """
    None
    

class SubjectGenotype(ConfiguredBaseModel):
    """
    Genetic strain. If absent, assume Wild Type (WT).
    """
    None
    

class SubjectSex(ConfiguredBaseModel):
    """
    Gender of subject.
    """
    None
    

class SubjectSpecies(ConfiguredBaseModel):
    """
    Species of subject.
    """
    None
    

class SubjectStrain(ConfiguredBaseModel):
    """
    Strain of subject.
    """
    None
    

class SubjectSubjectId(ConfiguredBaseModel):
    """
    ID of animal/person used/participating in experiment (lab convention).
    """
    None
    

class SubjectWeight(ConfiguredBaseModel):
    """
    Weight at time of experiment, at time of surgery and at other important times.
    """
    None
    

class TimeIntervals(DynamicTable):
    """
    A container for aggregating epoch data and the TimeSeries that each epoch applies to.
    """
    start_time: TimeIntervalsStartTime = Field(..., description="""Start time of epoch, in seconds.""")
    stop_time: TimeIntervalsStopTime = Field(..., description="""Stop time of epoch, in seconds.""")
    tags: Optional[TimeIntervalsTags] = Field(None, description="""User-defined tags that identify or categorize events.""")
    tags_index: Optional[TimeIntervalsTagsIndex] = Field(None, description="""Index for tags.""")
    timeseries: Optional[TimeIntervalsTimeseries] = Field(None, description="""An index into a TimeSeries object.""")
    timeseries_index: Optional[TimeIntervalsTimeseriesIndex] = Field(None, description="""Index for timeseries.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class NWBFileIntervalsEpochs(TimeIntervals):
    """
    Divisions in time marking experimental stages or sub-divisions of a single recording session.
    """
    start_time: TimeIntervalsStartTime = Field(..., description="""Start time of epoch, in seconds.""")
    stop_time: TimeIntervalsStopTime = Field(..., description="""Stop time of epoch, in seconds.""")
    tags: Optional[TimeIntervalsTags] = Field(None, description="""User-defined tags that identify or categorize events.""")
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
    start_time: TimeIntervalsStartTime = Field(..., description="""Start time of epoch, in seconds.""")
    stop_time: TimeIntervalsStopTime = Field(..., description="""Stop time of epoch, in seconds.""")
    tags: Optional[TimeIntervalsTags] = Field(None, description="""User-defined tags that identify or categorize events.""")
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
    start_time: TimeIntervalsStartTime = Field(..., description="""Start time of epoch, in seconds.""")
    stop_time: TimeIntervalsStopTime = Field(..., description="""Stop time of epoch, in seconds.""")
    tags: Optional[TimeIntervalsTags] = Field(None, description="""User-defined tags that identify or categorize events.""")
    tags_index: Optional[TimeIntervalsTagsIndex] = Field(None, description="""Index for tags.""")
    timeseries: Optional[TimeIntervalsTimeseries] = Field(None, description="""An index into a TimeSeries object.""")
    timeseries_index: Optional[TimeIntervalsTimeseriesIndex] = Field(None, description="""Index for timeseries.""")
    colnames: Optional[str] = Field(None, description="""The names of the columns in this table. This should be used to specify an order to the columns.""")
    description: Optional[str] = Field(None, description="""Description of what is in this dynamic table.""")
    id: DynamicTableId = Field(..., description="""Array of unique identifiers for the rows of this dynamic table.""")
    VectorData: Optional[List[VectorData]] = Field(default_factory=list, description="""Vector columns, including index columns, of this dynamic table.""")
    

class TimeIntervalsStartTime(VectorData):
    """
    Start time of epoch, in seconds.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class TimeIntervalsStopTime(VectorData):
    """
    Stop time of epoch, in seconds.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class TimeIntervalsTags(VectorData):
    """
    User-defined tags that identify or categorize events.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class TimeIntervalsTagsIndex(VectorIndex):
    """
    Index for tags.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class TimeIntervalsTimeseries(TimeSeriesReferenceVectorData):
    """
    An index into a TimeSeries object.
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class TimeIntervalsTimeseriesIndex(VectorIndex):
    """
    Index for timeseries.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class Device(NWBContainer):
    """
    Metadata about a data acquisition device, e.g., recording system, electrode, microscope.
    """
    description: Optional[str] = Field(None, description="""Description of the device (e.g., model, firmware version, processing software version, etc.) as free-form text.""")
    manufacturer: Optional[str] = Field(None, description="""The name of the manufacturer of the device.""")
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
ImagingRetinotopyAxis1PhaseMap.update_forward_refs()
ImagingRetinotopyAxis1PowerMap.update_forward_refs()
ImagingRetinotopyAxis2PhaseMap.update_forward_refs()
ImagingRetinotopyAxis2PowerMap.update_forward_refs()
ImagingRetinotopyAxisDescriptions.update_forward_refs()
ImagingRetinotopyFocalDepthImage.update_forward_refs()
ImagingRetinotopySignMap.update_forward_refs()
ImagingRetinotopyVasculatureImage.update_forward_refs()
Arraylike.update_forward_refs()
ImagingRetinotopyAxis1PhaseMapArray.update_forward_refs()
ImagingRetinotopyAxis1PowerMapArray.update_forward_refs()
ImagingRetinotopyAxis2PhaseMapArray.update_forward_refs()
ImagingRetinotopyAxis2PowerMapArray.update_forward_refs()
ImagingRetinotopyAxisDescriptionsArray.update_forward_refs()
ImagingRetinotopyFocalDepthImageArray.update_forward_refs()
ImagingRetinotopySignMapArray.update_forward_refs()
ImagingRetinotopyVasculatureImageArray.update_forward_refs()
ImageArray.update_forward_refs()
ImageReferencesArray.update_forward_refs()
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
VectorDataArray.update_forward_refs()
VectorIndexArray.update_forward_refs()
ElementIdentifiersArray.update_forward_refs()
DynamicTableRegionArray.update_forward_refs()
DynamicTableIdArray.update_forward_refs()
Data.update_forward_refs()
NWBData.update_forward_refs()
Image.update_forward_refs()
ImageReferences.update_forward_refs()
ImagesOrderOfImages.update_forward_refs()
VectorData.update_forward_refs()
TimeSeriesReferenceVectorData.update_forward_refs()
VectorIndex.update_forward_refs()
ElementIdentifiers.update_forward_refs()
DynamicTableRegion.update_forward_refs()
DynamicTableId.update_forward_refs()
Container.update_forward_refs()
NWBContainer.update_forward_refs()
NWBDataInterface.update_forward_refs()
ImagingRetinotopy.update_forward_refs()
TimeSeries.update_forward_refs()
ProcessingModule.update_forward_refs()
Images.update_forward_refs()
DynamicTable.update_forward_refs()
AlignedDynamicTable.update_forward_refs()
SimpleMultiContainer.update_forward_refs()
TwoPhotonSeriesFieldOfView.update_forward_refs()
TwoPhotonSeriesFieldOfViewArray.update_forward_refs()
RoiResponseSeries.update_forward_refs()
RoiResponseSeriesData.update_forward_refs()
RoiResponseSeriesDataArray.update_forward_refs()
RoiResponseSeriesRois.update_forward_refs()
DfOverF.update_forward_refs()
Fluorescence.update_forward_refs()
ImageSegmentation.update_forward_refs()
PlaneSegmentation.update_forward_refs()
PlaneSegmentationImageMask.update_forward_refs()
PlaneSegmentationImageMaskArray.update_forward_refs()
PlaneSegmentationPixelMaskIndex.update_forward_refs()
PlaneSegmentationPixelMask.update_forward_refs()
PlaneSegmentationVoxelMaskIndex.update_forward_refs()
PlaneSegmentationVoxelMask.update_forward_refs()
PlaneSegmentationReferenceImages.update_forward_refs()
ImagingPlane.update_forward_refs()
ImagingPlaneDescription.update_forward_refs()
ImagingPlaneExcitationLambda.update_forward_refs()
ImagingPlaneImagingRate.update_forward_refs()
ImagingPlaneIndicator.update_forward_refs()
ImagingPlaneLocation.update_forward_refs()
ImagingPlaneManifold.update_forward_refs()
ImagingPlaneManifoldArray.update_forward_refs()
ImagingPlaneOriginCoords.update_forward_refs()
ImagingPlaneOriginCoordsArray.update_forward_refs()
ImagingPlaneGridSpacing.update_forward_refs()
ImagingPlaneGridSpacingArray.update_forward_refs()
ImagingPlaneReferenceFrame.update_forward_refs()
OpticalChannel.update_forward_refs()
OpticalChannelDescription.update_forward_refs()
OpticalChannelEmissionLambda.update_forward_refs()
MotionCorrection.update_forward_refs()
CorrectedImageStack.update_forward_refs()
CorrectedImageStackXyTranslation.update_forward_refs()
GrayscaleImage.update_forward_refs()
GrayscaleImageArray.update_forward_refs()
RGBImage.update_forward_refs()
RGBImageArray.update_forward_refs()
RGBAImage.update_forward_refs()
RGBAImageArray.update_forward_refs()
ImageSeries.update_forward_refs()
OnePhotonSeries.update_forward_refs()
TwoPhotonSeries.update_forward_refs()
CorrectedImageStackCorrected.update_forward_refs()
ImageSeriesData.update_forward_refs()
ImageSeriesDataArray.update_forward_refs()
ImageSeriesDimension.update_forward_refs()
ImageSeriesDimensionArray.update_forward_refs()
ImageSeriesExternalFile.update_forward_refs()
ImageSeriesExternalFileArray.update_forward_refs()
ImageSeriesFormat.update_forward_refs()
ImageMaskSeries.update_forward_refs()
OpticalSeries.update_forward_refs()
OpticalSeriesDistance.update_forward_refs()
OpticalSeriesFieldOfView.update_forward_refs()
OpticalSeriesFieldOfViewArray.update_forward_refs()
OpticalSeriesData.update_forward_refs()
OpticalSeriesDataArray.update_forward_refs()
OpticalSeriesOrientation.update_forward_refs()
IndexSeries.update_forward_refs()
IndexSeriesData.update_forward_refs()
IndexSeriesDataArray.update_forward_refs()
OptogeneticSeries.update_forward_refs()
OptogeneticSeriesData.update_forward_refs()
OptogeneticSeriesDataArray.update_forward_refs()
OptogeneticStimulusSite.update_forward_refs()
OptogeneticStimulusSiteDescription.update_forward_refs()
OptogeneticStimulusSiteExcitationLambda.update_forward_refs()
OptogeneticStimulusSiteLocation.update_forward_refs()
PatchClampSeries.update_forward_refs()
PatchClampSeriesData.update_forward_refs()
PatchClampSeriesDataArray.update_forward_refs()
PatchClampSeriesGain.update_forward_refs()
CurrentClampSeries.update_forward_refs()
CurrentClampSeriesData.update_forward_refs()
CurrentClampSeriesBiasCurrent.update_forward_refs()
CurrentClampSeriesBridgeBalance.update_forward_refs()
CurrentClampSeriesCapacitanceCompensation.update_forward_refs()
IZeroClampSeries.update_forward_refs()
IZeroClampSeriesBiasCurrent.update_forward_refs()
IZeroClampSeriesBridgeBalance.update_forward_refs()
IZeroClampSeriesCapacitanceCompensation.update_forward_refs()
CurrentClampStimulusSeries.update_forward_refs()
CurrentClampStimulusSeriesData.update_forward_refs()
VoltageClampSeries.update_forward_refs()
VoltageClampSeriesData.update_forward_refs()
VoltageClampSeriesCapacitanceFast.update_forward_refs()
VoltageClampSeriesCapacitanceSlow.update_forward_refs()
VoltageClampSeriesResistanceCompBandwidth.update_forward_refs()
VoltageClampSeriesResistanceCompCorrection.update_forward_refs()
VoltageClampSeriesResistanceCompPrediction.update_forward_refs()
VoltageClampSeriesWholeCellCapacitanceComp.update_forward_refs()
VoltageClampSeriesWholeCellSeriesResistanceComp.update_forward_refs()
VoltageClampStimulusSeries.update_forward_refs()
VoltageClampStimulusSeriesData.update_forward_refs()
IntracellularElectrode.update_forward_refs()
IntracellularElectrodeCellId.update_forward_refs()
IntracellularElectrodeDescription.update_forward_refs()
IntracellularElectrodeFiltering.update_forward_refs()
IntracellularElectrodeInitialAccessResistance.update_forward_refs()
IntracellularElectrodeLocation.update_forward_refs()
IntracellularElectrodeResistance.update_forward_refs()
IntracellularElectrodeSeal.update_forward_refs()
IntracellularElectrodeSlice.update_forward_refs()
SweepTable.update_forward_refs()
SweepTableSweepNumber.update_forward_refs()
SweepTableSeries.update_forward_refs()
SweepTableSeriesIndex.update_forward_refs()
IntracellularElectrodesTable.update_forward_refs()
IntracellularElectrodesTableElectrode.update_forward_refs()
IntracellularStimuliTable.update_forward_refs()
IntracellularStimuliTableStimulus.update_forward_refs()
IntracellularResponsesTable.update_forward_refs()
IntracellularResponsesTableResponse.update_forward_refs()
IntracellularRecordingsTable.update_forward_refs()
IntracellularRecordingsTableElectrodes.update_forward_refs()
IntracellularRecordingsTableStimuli.update_forward_refs()
IntracellularRecordingsTableResponses.update_forward_refs()
SimultaneousRecordingsTable.update_forward_refs()
SimultaneousRecordingsTableRecordings.update_forward_refs()
SimultaneousRecordingsTableRecordingsIndex.update_forward_refs()
SequentialRecordingsTable.update_forward_refs()
SequentialRecordingsTableSimultaneousRecordings.update_forward_refs()
SequentialRecordingsTableSimultaneousRecordingsIndex.update_forward_refs()
SequentialRecordingsTableStimulusType.update_forward_refs()
RepetitionsTable.update_forward_refs()
RepetitionsTableSequentialRecordings.update_forward_refs()
RepetitionsTableSequentialRecordingsIndex.update_forward_refs()
ExperimentalConditionsTable.update_forward_refs()
ExperimentalConditionsTableRepetitions.update_forward_refs()
ExperimentalConditionsTableRepetitionsIndex.update_forward_refs()
ElectricalSeries.update_forward_refs()
ElectricalSeriesData.update_forward_refs()
ElectricalSeriesDataArray.update_forward_refs()
ElectricalSeriesElectrodes.update_forward_refs()
ElectricalSeriesChannelConversion.update_forward_refs()
ElectricalSeriesChannelConversionArray.update_forward_refs()
SpikeEventSeries.update_forward_refs()
SpikeEventSeriesData.update_forward_refs()
SpikeEventSeriesDataArray.update_forward_refs()
SpikeEventSeriesTimestamps.update_forward_refs()
SpikeEventSeriesTimestampsArray.update_forward_refs()
FeatureExtraction.update_forward_refs()
FeatureExtractionDescription.update_forward_refs()
FeatureExtractionDescriptionArray.update_forward_refs()
FeatureExtractionFeatures.update_forward_refs()
FeatureExtractionFeaturesArray.update_forward_refs()
FeatureExtractionTimes.update_forward_refs()
FeatureExtractionTimesArray.update_forward_refs()
FeatureExtractionElectrodes.update_forward_refs()
EventDetection.update_forward_refs()
EventDetectionDetectionMethod.update_forward_refs()
EventDetectionSourceIdx.update_forward_refs()
EventDetectionSourceIdxArray.update_forward_refs()
EventDetectionTimes.update_forward_refs()
EventDetectionTimesArray.update_forward_refs()
EventWaveform.update_forward_refs()
FilteredEphys.update_forward_refs()
LFP.update_forward_refs()
ElectrodeGroup.update_forward_refs()
ElectrodeGroupPosition.update_forward_refs()
ClusterWaveforms.update_forward_refs()
ClusterWaveformsWaveformFiltering.update_forward_refs()
ClusterWaveformsWaveformMean.update_forward_refs()
ClusterWaveformsWaveformMeanArray.update_forward_refs()
ClusterWaveformsWaveformSd.update_forward_refs()
ClusterWaveformsWaveformSdArray.update_forward_refs()
Clustering.update_forward_refs()
ClusteringDescription.update_forward_refs()
ClusteringNum.update_forward_refs()
ClusteringNumArray.update_forward_refs()
ClusteringPeakOverRms.update_forward_refs()
ClusteringPeakOverRmsArray.update_forward_refs()
ClusteringTimes.update_forward_refs()
ClusteringTimesArray.update_forward_refs()
SpatialSeries.update_forward_refs()
SpatialSeriesData.update_forward_refs()
SpatialSeriesDataArray.update_forward_refs()
SpatialSeriesReferenceFrame.update_forward_refs()
BehavioralEpochs.update_forward_refs()
BehavioralEvents.update_forward_refs()
BehavioralTimeSeries.update_forward_refs()
PupilTracking.update_forward_refs()
EyeTracking.update_forward_refs()
CompassDirection.update_forward_refs()
Position.update_forward_refs()
AbstractFeatureSeries.update_forward_refs()
AbstractFeatureSeriesData.update_forward_refs()
AbstractFeatureSeriesDataArray.update_forward_refs()
AbstractFeatureSeriesFeatureUnits.update_forward_refs()
AbstractFeatureSeriesFeatureUnitsArray.update_forward_refs()
AbstractFeatureSeriesFeatures.update_forward_refs()
AbstractFeatureSeriesFeaturesArray.update_forward_refs()
AnnotationSeries.update_forward_refs()
AnnotationSeriesData.update_forward_refs()
AnnotationSeriesDataArray.update_forward_refs()
IntervalSeries.update_forward_refs()
IntervalSeriesData.update_forward_refs()
IntervalSeriesDataArray.update_forward_refs()
DecompositionSeries.update_forward_refs()
DecompositionSeriesData.update_forward_refs()
DecompositionSeriesDataArray.update_forward_refs()
DecompositionSeriesMetric.update_forward_refs()
DecompositionSeriesSourceChannels.update_forward_refs()
DecompositionSeriesBands.update_forward_refs()
DecompositionSeriesBandsBandName.update_forward_refs()
DecompositionSeriesBandsBandLimits.update_forward_refs()
DecompositionSeriesBandsBandLimitsArray.update_forward_refs()
DecompositionSeriesBandsBandMean.update_forward_refs()
DecompositionSeriesBandsBandMeanArray.update_forward_refs()
DecompositionSeriesBandsBandStdev.update_forward_refs()
DecompositionSeriesBandsBandStdevArray.update_forward_refs()
Units.update_forward_refs()
UnitsSpikeTimesIndex.update_forward_refs()
UnitsSpikeTimes.update_forward_refs()
UnitsObsIntervalsIndex.update_forward_refs()
UnitsObsIntervals.update_forward_refs()
UnitsObsIntervalsArray.update_forward_refs()
UnitsElectrodesIndex.update_forward_refs()
UnitsElectrodes.update_forward_refs()
UnitsElectrodeGroup.update_forward_refs()
UnitsWaveformMean.update_forward_refs()
UnitsWaveformMeanArray.update_forward_refs()
UnitsWaveformSd.update_forward_refs()
UnitsWaveformSdArray.update_forward_refs()
UnitsWaveforms.update_forward_refs()
UnitsWaveformsArray.update_forward_refs()
UnitsWaveformsIndex.update_forward_refs()
UnitsWaveformsIndexIndex.update_forward_refs()
ScratchData.update_forward_refs()
NWBFile.update_forward_refs()
NWBFileFileCreateDate.update_forward_refs()
NWBFileFileCreateDateArray.update_forward_refs()
NWBFileIdentifier.update_forward_refs()
NWBFileSessionDescription.update_forward_refs()
NWBFileSessionStartTime.update_forward_refs()
NWBFileTimestampsReferenceTime.update_forward_refs()
NWBFileAcquisition.update_forward_refs()
NWBFileAnalysis.update_forward_refs()
NWBFileScratch.update_forward_refs()
NWBFileProcessing.update_forward_refs()
NWBFileStimulus.update_forward_refs()
NWBFileStimulusPresentation.update_forward_refs()
NWBFileStimulusTemplates.update_forward_refs()
NWBFileGeneral.update_forward_refs()
NWBFileGeneralDataCollection.update_forward_refs()
NWBFileGeneralExperimentDescription.update_forward_refs()
NWBFileGeneralExperimenter.update_forward_refs()
NWBFileGeneralExperimenterArray.update_forward_refs()
NWBFileGeneralInstitution.update_forward_refs()
NWBFileGeneralKeywords.update_forward_refs()
NWBFileGeneralKeywordsArray.update_forward_refs()
NWBFileGeneralLab.update_forward_refs()
NWBFileGeneralNotes.update_forward_refs()
NWBFileGeneralPharmacology.update_forward_refs()
NWBFileGeneralProtocol.update_forward_refs()
NWBFileGeneralRelatedPublications.update_forward_refs()
NWBFileGeneralRelatedPublicationsArray.update_forward_refs()
NWBFileGeneralSessionId.update_forward_refs()
NWBFileGeneralSlices.update_forward_refs()
NWBFileGeneralSourceScript.update_forward_refs()
NWBFileGeneralStimulus.update_forward_refs()
NWBFileGeneralSurgery.update_forward_refs()
NWBFileGeneralVirus.update_forward_refs()
NWBFileGeneralDevices.update_forward_refs()
NWBFileGeneralExtracellularEphys.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodes.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodesX.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodesY.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodesZ.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodesImp.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodesLocation.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodesFiltering.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodesGroup.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodesGroupName.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodesRelX.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodesRelY.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodesRelZ.update_forward_refs()
NWBFileGeneralExtracellularEphysElectrodesReference.update_forward_refs()
NWBFileGeneralIntracellularEphys.update_forward_refs()
NWBFileGeneralIntracellularEphysFiltering.update_forward_refs()
NWBFileGeneralIntracellularEphysSweepTable.update_forward_refs()
NWBFileGeneralIntracellularEphysIntracellularRecordings.update_forward_refs()
NWBFileGeneralIntracellularEphysSimultaneousRecordings.update_forward_refs()
NWBFileGeneralIntracellularEphysSequentialRecordings.update_forward_refs()
NWBFileGeneralIntracellularEphysRepetitions.update_forward_refs()
NWBFileGeneralIntracellularEphysExperimentalConditions.update_forward_refs()
NWBFileGeneralOptogenetics.update_forward_refs()
NWBFileGeneralOptophysiology.update_forward_refs()
NWBFileIntervals.update_forward_refs()
NWBFileUnits.update_forward_refs()
LabMetaData.update_forward_refs()
Subject.update_forward_refs()
NWBFileGeneralSubject.update_forward_refs()
SubjectAge.update_forward_refs()
SubjectDateOfBirth.update_forward_refs()
SubjectDescription.update_forward_refs()
SubjectGenotype.update_forward_refs()
SubjectSex.update_forward_refs()
SubjectSpecies.update_forward_refs()
SubjectStrain.update_forward_refs()
SubjectSubjectId.update_forward_refs()
SubjectWeight.update_forward_refs()
TimeIntervals.update_forward_refs()
NWBFileIntervalsEpochs.update_forward_refs()
NWBFileIntervalsTrials.update_forward_refs()
NWBFileIntervalsInvalidTimes.update_forward_refs()
TimeIntervalsStartTime.update_forward_refs()
TimeIntervalsStopTime.update_forward_refs()
TimeIntervalsTags.update_forward_refs()
TimeIntervalsTagsIndex.update_forward_refs()
TimeIntervalsTimeseries.update_forward_refs()
TimeIntervalsTimeseriesIndex.update_forward_refs()
Device.update_forward_refs()
