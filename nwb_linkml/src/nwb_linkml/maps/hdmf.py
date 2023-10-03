"""
Mapping functions for handling HDMF classes like DynamicTables
"""
import pdb
import warnings
from typing import List, Type, Optional, Any
import ast
from nwb_linkml.types import DataFrame
import h5py
from pydantic import create_model, BaseModel
from nwb_linkml.maps import dtype
import numpy as np
from nwb_linkml.types.hdf5 import HDF5_Path
from nwb_linkml.types.ndarray import NDArray, NDArrayProxy
from nwb_linkml.annotations import get_inner_types
import dask.array as da
import nptyping

def model_from_dynamictable(group:h5py.Group, base:Optional[BaseModel] = None) -> Type[DataFrame]:
    """
    Create a pydantic model from a dynamic table
    """
    colnames = group.attrs['colnames']
    types = {}
    for col in colnames:
        # idxname = col + '_index'
        # if idxname in group.keys():
        #     idx = group.get(idxname)[0]
        #     dset = group.get(col)
        #     item = dset[idx]
        # else:
        #     dset = group.get(col)
        #     item = dset[0]
        # # read the first entry to see what we got
        #
        # if isinstance(item, bytes):
        #     item = item.decode('utf-8')
        # if isinstance(item, str):
        #     # try to see if this is actually a list or smth encoded as a string
        #     try:
        #         item = ast.literal_eval(item)
        #     except (ValueError, SyntaxError):
        #         pass

        # Get a nptypes type for the array
        #pdb.set_trace()

        # type_ = type(item)
        # type_ = dtype.np_to_python.get(type_, type_)
        # if type_ is h5py.h5r.Reference:
        #     #type_ = HDF5_Path
        #     type_ = 'String'
        # elif type_ is np.ndarray:
        #     item: np.ndarray
        #     type_ = dtype.flat_to_npytyping[item.dtype.name]

        #if type_ is not np.void:
            #type_ = NDArray[Any, getattr(nptyping, dtype.flat_to_npytyping[item.dtype.name])]

        #nptype = nptyping.typing_.name_per_dtype[group[col].dtype.type]
        nptype = group[col].dtype.type
        if nptype == np.void:
            # warnings.warn(f"Cant handle numpy void type for column {col} in {group.name}")
            continue
        type_ = Optional[NDArray[Any, nptype]]


            # FIXME: handling nested column types that appear only in some versions?
        #types[col] = (List[type_ | None], ...)
        types[col] = (type_, None)

    # if base is None:
    #     #base = DataFrame
    #     base = BaseModel
    # else:
    #     base = (BaseModel, base)
    #     #base = (DataFrame, base)


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
                #    warnings.warn(f"Dask cant handle object type arrays like {col} in {group.name}. Skipping")
                # pdb.set_trace()
                # # can't auto-chunk with "object" type
                # items[col] = da.from_array(group[col], chunks=-1)

    return model.model_construct(hdf5_path = group.name,
                 name = group.name.split('/')[-1],
                 **items)




def dynamictable_to_df(group:h5py.Group,
                       model:Optional[Type[DataFrame]]=None,
                       base:Optional[BaseModel] = None) -> DataFrame:
    if model is None:
        model = model_from_dynamictable(group, base)

    items = {}
    for col, col_type in model.model_fields.items():
        if col not in group.keys():
            continue
        idxname = col + '_index'
        if idxname in group.keys():
            idx = group.get(idxname)[:]
            data = group.get(col)[idx-1]
        else:
            data = group.get(col)[:]

        # Handle typing inside of list
        if isinstance(data[0], bytes):
            data = data.astype('unicode')
        if isinstance(data[0], str):
            # lists and other compound data types can get flattened out to strings when stored
            # so we try and literal eval and recover them
            try:
                eval_type = type(ast.literal_eval(data[0]))
            except (ValueError, SyntaxError):
                eval_type = str

            # if we've found one of those, get the data type within it.
            if eval_type is not str:
                eval_list = []
                for item in data.tolist():
                    try:
                        eval_list.append(ast.literal_eval(item))
                    except ValueError:
                        eval_list.append(None)
                data = eval_list
        elif isinstance(data[0], h5py.h5r.Reference):
            data = [HDF5_Path(group[d].name) for d in data]
        elif isinstance(data[0], tuple) and any([isinstance(d, h5py.h5r.Reference) for d in data[0]]):
            # references stored inside a tuple, reference + location.
            # dereference them!?
            dset = group.get(col)
            names = dset.dtype.names
            if names is not None and names[0] == 'idx_start' and names[1] == 'count':
                data = dereference_reference_vector(dset, data)

        else:
            data = data.tolist()

        # After list, check if we need to put this thing inside of
        # another class, as indicated by the enclosing model



        items[col] = data

    return model(hdf5_path = group.name,
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

