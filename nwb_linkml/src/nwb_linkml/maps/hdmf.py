"""
Mapping functions for handling HDMF classes like DynamicTables
"""
import pdb
from typing import List, Type, Optional
import ast
from nwb_linkml.types import DataFrame
import h5py
from pydantic import create_model
from nwb_linkml.maps import dtype
import numpy as np

def model_from_dynamictable(group:h5py.Group) -> Type[DataFrame]:
    colnames = group.attrs['colnames']
    types = {}
    for col in colnames:
        # read the first entry to see what we got
        dset = group.get(col)
        item = dset[0]
        if isinstance(item, bytes):
            item = item.decode('utf-8')
        if isinstance(item, str):
            # try to see if this is actually a list or smth encoded as a string
            try:
                item = ast.literal_eval(item)
            except ValueError:
                pass

        type_ = type(item)
        type_ = dtype.np_to_python.get(type_, type_)
        if type_ is not np.void:
            # FIXME: handling nested column types that appear only in some versions?
            types[col] = (List[type_ | None], ...)

    model = create_model(group.name.split('/')[-1], **types, __base__=DataFrame)
    return model


def dynamictable_to_df(group:h5py.Group, model:Optional[Type[DataFrame]]=None) -> DataFrame:
    if model is None:
        model = model_from_dynamictable(group)

    items = {}
    for col in model.model_fields.keys():
        data = group.get(col)[:]
        if isinstance(data[0], bytes):
            data = data.astype('unicode')
        if isinstance(data[0], str):
            try:
                eval_type = type(ast.literal_eval(data[0]))
            except ValueError:
                eval_type = str

            if eval_type is not str:
                eval_list = []
                for item in data.tolist():
                    try:
                        eval_list.append(ast.literal_eval(item))
                    except ValueError:
                        eval_list.append(None)
                items[col] = eval_list
                continue

        items[col] = data.tolist()

    pdb.set_trace()
    return model(**items)


