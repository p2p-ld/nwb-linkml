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
    VectorData,
    VectorIndex
)

from .nwb_language import (
    Arraylike
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


class TwoPhotonSeriesFieldOfView(ConfiguredBaseModel):
    """
    Width, height and depth of image, or imaged area, in meters.
    """
    name: str = Field("field_of_view", const=True)
    array: Optional[Union[
        NDArray[Shape["2 width|height"], Float32],
        NDArray[Shape["2 width|height, 3 width|height|depth"], Float32]
    ]] = Field(None)
    

class TwoPhotonSeriesFieldOfViewArray(Arraylike):
    
    width|height: Optional[float] = Field(None)
    width|height|depth: Optional[float] = Field(None)
    

class RoiResponseSeriesData(ConfiguredBaseModel):
    """
    Signals from ROIs.
    """
    name: str = Field("data", const=True)
    array: Optional[Union[
        NDArray[Shape["* num_times"], Number],
        NDArray[Shape["* num_times, * num_ROIs"], Number]
    ]] = Field(None)
    

class RoiResponseSeriesDataArray(Arraylike):
    
    num_times: float = Field(...)
    num_ROIs: Optional[float] = Field(None)
    

class RoiResponseSeriesRois(DynamicTableRegion):
    """
    DynamicTableRegion referencing into an ROITable containing information on the ROIs stored in this timeseries.
    """
    name: str = Field("rois", const=True)
    table: Optional[DynamicTable] = Field(None, description="""Reference to the DynamicTable object that this region applies to.""")
    description: Optional[str] = Field(None, description="""Description of what this table region points to.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class PlaneSegmentationImageMask(VectorData):
    """
    ROI masks for each ROI. Each image mask is the size of the original imaging plane (or volume) and members of the ROI are finite non-zero.
    """
    name: str = Field("image_mask", const=True)
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class PlaneSegmentationPixelMaskIndex(VectorIndex):
    """
    Index into pixel_mask.
    """
    name: str = Field("pixel_mask_index", const=True)
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class PlaneSegmentationVoxelMaskIndex(VectorIndex):
    """
    Index into voxel_mask.
    """
    name: str = Field("voxel_mask_index", const=True)
    target: Optional[VectorData] = Field(None, description="""Reference to the target dataset that this index applies to.""")
    description: Optional[str] = Field(None, description="""Description of what these vectors represent.""")
    array: Optional[Union[
        NDArray[Shape["* dim0"], Any],
        NDArray[Shape["* dim0, * dim1"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2"], Any],
        NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any]
    ]] = Field(None)
    

class ImagingPlaneManifold(ConfiguredBaseModel):
    """
    DEPRECATED Physical position of each pixel. 'xyz' represents the position of the pixel relative to the defined coordinate space. Deprecated in favor of origin_coords and grid_spacing.
    """
    name: str = Field("manifold", const=True)
    conversion: Optional[float] = Field(None, description="""Scalar to multiply each element in data to convert it to the specified 'unit'. If the data are stored in acquisition system units or other units that require a conversion to be interpretable, multiply the data by 'conversion' to convert the data to the specified 'unit'. e.g. if the data acquisition system stores values in this object as pixels from x = -500 to 499, y = -500 to 499 that correspond to a 2 m x 2 m range, then the 'conversion' multiplier to get from raw data acquisition pixel units to meters is 2/1000.""")
    unit: Optional[str] = Field(None, description="""Base unit of measurement for working with the data. The default value is 'meters'.""")
    array: Optional[Union[
        NDArray[Shape["* height, * width, 3 x_y_z"], Float32],
        NDArray[Shape["* height, * width, 3 x_y_z, * depth"], Float32]
    ]] = Field(None)
    

class ImagingPlaneManifoldArray(Arraylike):
    
    height: float = Field(...)
    width: float = Field(...)
    x_y_z: float = Field(...)
    depth: Optional[float] = Field(None)
    

class ImagingPlaneOriginCoords(ConfiguredBaseModel):
    """
    Physical location of the first element of the imaging plane (0, 0) for 2-D data or (0, 0, 0) for 3-D data. See also reference_frame for what the physical location is relative to (e.g., bregma).
    """
    name: str = Field("origin_coords", const=True)
    unit: Optional[str] = Field(None, description="""Measurement units for origin_coords. The default value is 'meters'.""")
    array: Optional[Union[
        NDArray[Shape["2 x_y"], Float32],
        NDArray[Shape["2 x_y, 3 x_y_z"], Float32]
    ]] = Field(None)
    

class ImagingPlaneOriginCoordsArray(Arraylike):
    
    x_y: Optional[float] = Field(None)
    x_y_z: Optional[float] = Field(None)
    

class ImagingPlaneGridSpacing(ConfiguredBaseModel):
    """
    Space between pixels in (x, y) or voxels in (x, y, z) directions, in the specified unit. Assumes imaging plane is a regular grid. See also reference_frame to interpret the grid.
    """
    name: str = Field("grid_spacing", const=True)
    unit: Optional[str] = Field(None, description="""Measurement units for grid_spacing. The default value is 'meters'.""")
    array: Optional[Union[
        NDArray[Shape["2 x_y"], Float32],
        NDArray[Shape["2 x_y, 3 x_y_z"], Float32]
    ]] = Field(None)
    

class ImagingPlaneGridSpacingArray(Arraylike):
    
    x_y: Optional[float] = Field(None)
    x_y_z: Optional[float] = Field(None)
    


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
TwoPhotonSeriesFieldOfView.model_rebuild()
TwoPhotonSeriesFieldOfViewArray.model_rebuild()
RoiResponseSeriesData.model_rebuild()
RoiResponseSeriesDataArray.model_rebuild()
RoiResponseSeriesRois.model_rebuild()
PlaneSegmentationImageMask.model_rebuild()
PlaneSegmentationPixelMaskIndex.model_rebuild()
PlaneSegmentationVoxelMaskIndex.model_rebuild()
ImagingPlaneManifold.model_rebuild()
ImagingPlaneManifoldArray.model_rebuild()
ImagingPlaneOriginCoords.model_rebuild()
ImagingPlaneOriginCoordsArray.model_rebuild()
ImagingPlaneGridSpacing.model_rebuild()
ImagingPlaneGridSpacingArray.model_rebuild()
    