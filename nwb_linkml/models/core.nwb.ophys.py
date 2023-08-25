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
    
    

class TwoPhotonSeriesFieldOfView(ConfiguredBaseModel):
    """
    Width, height and depth of image, or imaged area, in meters.
    """
    array: Optional[TwoPhotonSeriesFieldOfViewArray] = Field(None)
    

class RoiResponseSeriesData(ConfiguredBaseModel):
    """
    Signals from ROIs.
    """
    array: Optional[RoiResponseSeriesDataArray] = Field(None)
    

class PlaneSegmentationReferenceImages(ConfiguredBaseModel):
    """
    Image stacks that the segmentation masks apply to.
    """
    ImageSeries: Optional[List[ImageSeries]] = Field(default_factory=list, description="""One or more image stacks that the masks apply to (can be one-element stack).""")
    

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
    

class ImagingPlaneOriginCoords(ConfiguredBaseModel):
    """
    Physical location of the first element of the imaging plane (0, 0) for 2-D data or (0, 0, 0) for 3-D data. See also reference_frame for what the physical location is relative to (e.g., bregma).
    """
    unit: Optional[str] = Field(None, description="""Measurement units for origin_coords. The default value is 'meters'.""")
    array: Optional[ImagingPlaneOriginCoordsArray] = Field(None)
    

class ImagingPlaneGridSpacing(ConfiguredBaseModel):
    """
    Space between pixels in (x, y) or voxels in (x, y, z) directions, in the specified unit. Assumes imaging plane is a regular grid. See also reference_frame to interpret the grid.
    """
    unit: Optional[str] = Field(None, description="""Measurement units for grid_spacing. The default value is 'meters'.""")
    array: Optional[ImagingPlaneGridSpacingArray] = Field(None)
    

class ImagingPlaneReferenceFrame(ConfiguredBaseModel):
    """
    Describes reference frame of origin_coords and grid_spacing. For example, this can be a text description of the anatomical location and orientation of the grid defined by origin_coords and grid_spacing or the vectors needed to transform or rotate the grid to a common anatomical axis (e.g., AP/DV/ML). This field is necessary to interpret origin_coords and grid_spacing. If origin_coords and grid_spacing are not present, then this field is not required. For example, if the microscope takes 10 x 10 x 2 images, where the first value of the data matrix (index (0, 0, 0)) corresponds to (-1.2, -0.6, -2) mm relative to bregma, the spacing between pixels is 0.2 mm in x, 0.2 mm in y and 0.5 mm in z, and larger numbers in x means more anterior, larger numbers in y means more rightward, and larger numbers in z means more ventral, then enter the following -- origin_coords = (-1.2, -0.6, -2) grid_spacing = (0.2, 0.2, 0.5) reference_frame = \"Origin coordinates are relative to bregma. First dimension corresponds to anterior-posterior axis (larger index = more anterior). Second dimension corresponds to medial-lateral axis (larger index = more rightward). Third dimension corresponds to dorsal-ventral axis (larger index = more ventral).\"
    """
    None
    

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
    

class Arraylike(ConfiguredBaseModel):
    """
    Container for arraylike information held in the dims, shape, and dtype properties.this is a special case to be interpreted by downstream i/o. this class has no slotsand is abstract by default.- Each slot within a subclass indicates a possible dimension.- Only dimensions that are present in all the dimension specifiers in the  original schema are required.- Shape requirements are indicated using max/min cardinalities on the slot.
    """
    None
    

class TwoPhotonSeriesFieldOfViewArray(Arraylike):
    
    width|height: Optional[float] = Field(None)
    width|height|depth: Optional[float] = Field(None)
    

class RoiResponseSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    num_ROIs: Optional[float] = Field(None)
    

class PlaneSegmentationImageMaskArray(Arraylike):
    
    num_roi: Any = Field(...)
    num_x: Any = Field(...)
    num_y: Any = Field(...)
    num_z: Optional[Any] = Field(None)
    

class ImagingPlaneManifoldArray(Arraylike):
    
    height: float = Field(...)
    width: float = Field(...)
    x_y_z: float = Field(...)
    depth: Optional[float] = Field(None)
    

class ImagingPlaneOriginCoordsArray(Arraylike):
    
    x_y: Optional[float] = Field(None)
    x_y_z: Optional[float] = Field(None)
    

class ImagingPlaneGridSpacingArray(Arraylike):
    
    x_y: Optional[float] = Field(None)
    x_y_z: Optional[float] = Field(None)
    

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
    

class PlaneSegmentationImageMask(VectorData):
    """
    ROI masks for each ROI. Each image mask is the size of the original imaging plane (or volume) and members of the ROI are finite non-zero.
    """
    array: Optional[PlaneSegmentationImageMaskArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class PlaneSegmentationPixelMask(VectorData):
    """
    Pixel masks for each ROI: a list of indices and weights for the ROI. Pixel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation
    """
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[VectorDataArray] = Field(None)
    

class PlaneSegmentationVoxelMask(VectorData):
    """
    Voxel masks for each ROI: a list of indices and weights for the ROI. Voxel masks are concatenated and parsing of this dataset is maintained by the PlaneSegmentation
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
    

class PlaneSegmentationPixelMaskIndex(VectorIndex):
    """
    Index into pixel_mask.
    """
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    array: Optional[VectorIndexArray] = Field(None)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    

class PlaneSegmentationVoxelMaskIndex(VectorIndex):
    """
    Index into voxel_mask.
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
    

class RoiResponseSeriesRois(DynamicTableRegion):
    """
    DynamicTableRegion referencing into an ROITable containing information on the ROIs stored in this timeseries.
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
    

class OpticalChannel(NWBContainer):
    """
    An optical channel used to record from an imaging plane.
    """
    description: OpticalChannelDescription = Field(..., description="""Description or other notes about the channel.""")
    emission_lambda: OpticalChannelEmissionLambda = Field(..., description="""Emission wavelength for channel, in nm.""")
    

class NWBDataInterface(NWBContainer):
    """
    An abstract data type for a generic container storing collections of data, as opposed to metadata.
    """
    None
    

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
    


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
TwoPhotonSeriesFieldOfView.update_forward_refs()
RoiResponseSeriesData.update_forward_refs()
PlaneSegmentationReferenceImages.update_forward_refs()
ImagingPlaneDescription.update_forward_refs()
ImagingPlaneExcitationLambda.update_forward_refs()
ImagingPlaneImagingRate.update_forward_refs()
ImagingPlaneIndicator.update_forward_refs()
ImagingPlaneLocation.update_forward_refs()
ImagingPlaneManifold.update_forward_refs()
ImagingPlaneOriginCoords.update_forward_refs()
ImagingPlaneGridSpacing.update_forward_refs()
ImagingPlaneReferenceFrame.update_forward_refs()
OpticalChannelDescription.update_forward_refs()
OpticalChannelEmissionLambda.update_forward_refs()
Arraylike.update_forward_refs()
TwoPhotonSeriesFieldOfViewArray.update_forward_refs()
RoiResponseSeriesDataArray.update_forward_refs()
PlaneSegmentationImageMaskArray.update_forward_refs()
ImagingPlaneManifoldArray.update_forward_refs()
ImagingPlaneOriginCoordsArray.update_forward_refs()
ImagingPlaneGridSpacingArray.update_forward_refs()
VectorDataArray.update_forward_refs()
VectorIndexArray.update_forward_refs()
ElementIdentifiersArray.update_forward_refs()
DynamicTableRegionArray.update_forward_refs()
DynamicTableIdArray.update_forward_refs()
Data.update_forward_refs()
VectorData.update_forward_refs()
PlaneSegmentationImageMask.update_forward_refs()
PlaneSegmentationPixelMask.update_forward_refs()
PlaneSegmentationVoxelMask.update_forward_refs()
VectorIndex.update_forward_refs()
PlaneSegmentationPixelMaskIndex.update_forward_refs()
PlaneSegmentationVoxelMaskIndex.update_forward_refs()
ElementIdentifiers.update_forward_refs()
DynamicTableRegion.update_forward_refs()
RoiResponseSeriesRois.update_forward_refs()
DynamicTableId.update_forward_refs()
Container.update_forward_refs()
DynamicTable.update_forward_refs()
PlaneSegmentation.update_forward_refs()
AlignedDynamicTable.update_forward_refs()
SimpleMultiContainer.update_forward_refs()
NWBData.update_forward_refs()
TimeSeriesReferenceVectorData.update_forward_refs()
Image.update_forward_refs()
ImageArray.update_forward_refs()
ImageReferences.update_forward_refs()
ImageReferencesArray.update_forward_refs()
NWBContainer.update_forward_refs()
ImagingPlane.update_forward_refs()
OpticalChannel.update_forward_refs()
NWBDataInterface.update_forward_refs()
DfOverF.update_forward_refs()
Fluorescence.update_forward_refs()
ImageSegmentation.update_forward_refs()
MotionCorrection.update_forward_refs()
CorrectedImageStack.update_forward_refs()
TimeSeries.update_forward_refs()
RoiResponseSeries.update_forward_refs()
CorrectedImageStackXyTranslation.update_forward_refs()
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
