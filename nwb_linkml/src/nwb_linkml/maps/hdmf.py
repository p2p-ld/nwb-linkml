"""
Mapping functions for handling HDMF classes like DynamicTables
"""
from typing import List, Type, Optional, Any
import warnings


import h5py
from pydantic import create_model, BaseModel
import numpy as np
from nwb_linkml.types.hdf5 import HDF5_Path
from nwb_linkml.types.ndarray import NDArray, NDArrayProxy
import dask.array as da


def model_from_dynamictable(group:h5py.Group, base:Optional[BaseModel] = None) -> Type[BaseModel]:
    """
    Create a pydantic model from a dynamic table
    """
    colnames = group.attrs['colnames']
    types = {}
    for col in colnames:

        nptype = group[col].dtype.type
        if nptype == np.void:
            warnings.warn(f"Can't handle numpy void type for column {col} in {group.name}")
            continue
        type_ = Optional[NDArray[Any, nptype]]

        # FIXME: handling nested column types that appear only in some versions?
        #types[col] = (List[type_ | None], ...)
        types[col] = (type_, None)

    model = create_model(group.name.split('/')[-1], **types, __base__=base)
    return model


def dynamictable_to_model(
    group:h5py.Group,
    model:Optional[Type[BaseModel]]=None,
    base:Optional[Type[BaseModel]] = None) -> BaseModel:
    """
    Instantiate a dynamictable model

    Calls :func:`.model_from_dynamictable` if ``model`` is not provided.
    """
    if model is None:
        model = model_from_dynamictable(group, base)

    items = {}
    for col, col_type in model.model_fields.items():
        if col not in group.keys():
            if col in group.attrs:
                items[col] = group.attrs[col]
            continue

        if col_type.annotation is HDF5_Path:
            items[col] = [HDF5_Path(group[d].name) for d in group[col][:]]
        else:
            try:
                items[col] = da.from_array(group[col])
            except NotImplementedError:
                # if str in get_inner_types(col_type.annotation):
                #     # dask can't handle this, we just arrayproxy it
                items[col] = NDArrayProxy(h5f_file=group.file.filename, path=group[col].name)
                #else:
                #    warnings.warn(f"Dask can't handle object type arrays like {col} in {group.name}. Skipping")
                # pdb.set_trace()
                # # can't auto-chunk with "object" type
                # items[col] = da.from_array(group[col], chunks=-1)

    return model.model_construct(hdf5_path = group.name,
                 name = group.name.split('/')[-1],
                 **items)


def dereference_reference_vector(dset: h5py.Dataset, data:Optional[List[Any]]) -> List:
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
    res = [target[d[0]:d[0]+d[1]] for d in data]
    return res

