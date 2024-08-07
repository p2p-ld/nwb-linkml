"""
Mapping functions for handling HDMF classes like DynamicTables
"""

from typing import Any, List, Optional, Type

import dask.array as da
import h5py
import numpy as np
from numpydantic import NDArray
from numpydantic.interface.hdf5 import H5ArrayPath
from pydantic import BaseModel, create_model

from nwb_linkml.maps.dtype import struct_from_dtype
from nwb_linkml.types.hdf5 import HDF5_Path


def model_from_dynamictable(group: h5py.Group, base: Optional[BaseModel] = None) -> Type[BaseModel]:
    """
    Create a pydantic model from a dynamic table
    """
    colnames = group.attrs["colnames"]
    types = {}
    for col in colnames:

        nptype = group[col].dtype
        nptype = struct_from_dtype(nptype) if nptype.type == np.void else nptype.type

        type_ = Optional[NDArray[Any, nptype]]

        # FIXME: handling nested column types that appear only in some versions?
        # types[col] = (List[type_ | None], ...)
        types[col] = (type_, None)

    model = create_model(group.name.split("/")[-1], **types, __base__=base)
    return model


def dynamictable_to_model(
    group: h5py.Group,
    model: Optional[Type[BaseModel]] = None,
    base: Optional[Type[BaseModel]] = None,
) -> BaseModel:
    """
    Instantiate a dynamictable model

    Calls :func:`.model_from_dynamictable` if ``model`` is not provided.
    """
    if model is None:
        model = model_from_dynamictable(group, base)

    items = {}
    for col, col_type in model.model_fields.items():
        if col not in group:
            if col in group.attrs:
                items[col] = group.attrs[col]
            continue

        if col_type.annotation is HDF5_Path:
            items[col] = [HDF5_Path(group[d].name) for d in group[col][:]]
        else:
            try:
                items[col] = da.from_array(group[col])
            except NotImplementedError:
                items[col] = H5ArrayPath(file=group.file.filename, path=group[col].name)

    return model.model_construct(hdf5_path=group.name, name=group.name.split("/")[-1], **items)


def dereference_reference_vector(dset: h5py.Dataset, data: Optional[List[Any]]) -> List:
    """
    Given a compound dataset with indices, counts, and object references, dereference to values

    Data is of the form
    (idx_start, count, target)
    """
    # assume all these references are to the same target
    # and the index is in the 3rd position
    if data is None:
        data = dset[:]

    target = dset.parent.get(data[0][-1])
    res = [target[d[0] : d[0] + d[1]] for d in data]
    return res
