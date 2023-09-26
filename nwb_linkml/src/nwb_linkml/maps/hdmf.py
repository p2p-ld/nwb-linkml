"""
Mapping functions for handling HDMF classes like DynamicTables
"""
import pdb
from typing import List, Type, Optional, Any
import ast
from nwb_linkml.types import DataFrame
import h5py
from pydantic import create_model, BaseModel
from nwb_linkml.maps import dtype
import numpy as np
from nwb_linkml.types.hdf5 import HDF5_Path
from nwb_linkml.types.ndarray import NDArray

def model_from_dynamictable(group:h5py.Group, base:Optional[BaseModel] = None) -> Type[DataFrame]:
    colnames = group.attrs['colnames']
    types = {}
    for col in colnames:
        idxname = col + '_index'
        if idxname in group.keys():
            idx = group.get(idxname)[0]
            dset = group.get(col)
            item = dset[idx]
        else:
            dset = group.get(col)
            item = dset[0]
        # read the first entry to see what we got

        if isinstance(item, bytes):
            item = item.decode('utf-8')
        if isinstance(item, str):
            # try to see if this is actually a list or smth encoded as a string
            try:
                item = ast.literal_eval(item)
            except (ValueError, SyntaxError):
                pass

        type_ = type(item)
        type_ = dtype.np_to_python.get(type_, type_)
        if type_ is h5py.h5r.Reference:
            type_ = HDF5_Path
        elif type_ is np.ndarray:
            type_ = NDArray

        if type_ is not np.void:
            # FIXME: handling nested column types that appear only in some versions?
            types[col] = (List[type_ | None], ...)

    if base is None:
        base = DataFrame
    else:
        base = (DataFrame, base)


    model = create_model(group.name.split('/')[-1], **types, __base__=base)
    return model


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

