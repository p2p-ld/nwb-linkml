"""
Pydantic models that behave like pandas dataframes

.. note::

    This is currently unused but kept in place as a stub in case it is worth revisiting in the future.
    It turned out to be too momentarily difficult to make lazy-loading work with dask arrays per column
    while still keeping pandas-like API intact. In the future we should investigate modifying the
    :func:`dask.dataframe.read_hdf` function to treat individual hdf5 datasets like columns

    pandas has been removed from dependencies for now, as it not used elsewhere, but it is
    left in this module since it is necessary for it to make sense.
"""

import ast
import pdb
from typing import List, Any, get_origin, get_args, Union, Optional, Dict, Type
from types import NoneType

import h5py
import numpy as np
import pandas as pd
from pydantic import (
    BaseModel,
    model_serializer,
    SerializerFunctionWrapHandler,
    ConfigDict,
    model_validator,
)

from nwb_linkml.maps.hdmf import model_from_dynamictable, dereference_reference_vector
from nwb_linkml.types.hdf5 import HDF5_Path


class DataFrame(BaseModel, pd.DataFrame):
    """
    Pydantic model root class that mimics a pandas dataframe.

    Notes:

        The synchronization between the underlying lists in the pydantic model
        and the derived dataframe is partial, and at the moment unidirectional.
        This class is primarily intended for reading from tables stored in
        NWB files rather than being able to manipulate them.

        The dataframe IS updated when new values are *assigned* to a field.

        eg.::

            MyModel.fieldval = [1,2,3]

        But the dataframe is NOT updated when existing values are updated.

        eg.::

            MyModel.fieldval.append(4)

        In that case you need to call :meth:`.update_df` manually.

        Additionally, if the dataframe is modified, the underlying lists are NOT updated,
        but when the model is dumped to a dictionary or serialized, the dataframe IS used,
        so changes will be reflected then.

        Fields that shadow pandas methods WILL prevent them from being usable, except
        by directly accessing the dataframe like ``mymodel._df``

    """

    _df: pd.DataFrame = None
    model_config = ConfigDict(validate_assignment=True)

    def __init__(self, **kwargs):
        # pdb.set_trace()
        super().__init__(**kwargs)

        self._df = self.__make_df()

    def __make_df(self) -> pd.DataFrame:
        # make dict that can handle ragged arrays and NoneTypes
        items = {k: v for k, v in self.__dict__.items() if k in self.model_fields}

        df_dict = {
            k: (pd.Series(v) if isinstance(v, list) else pd.Series([v])) for k, v in items.items()
        }
        df = pd.DataFrame(df_dict)
        # replace Nans with None
        df = df.fillna(np.nan).replace([np.nan], [None])
        return df

    def update_df(self):
        """
        Update the internal dataframe in the case that the model values are changed
        in a way that we can't detect, like appending to one of the lists.

        """
        self._df = self.__make_df()

    def __getattr__(self, item: str):
        """
        Mimic pandas dataframe and pydantic model behavior
        """
        if item in ("df", "_df"):
            return self.__pydantic_private__["_df"]
        elif item in self.model_fields.keys():
            return self._df[item]
        else:
            try:
                return object.__getattribute__(self._df, item)
            except AttributeError:
                return object.__getattribute__(self, item)

    @model_validator(mode="after")
    def recreate_df(self):
        """
        Remake DF when validating (eg. when updating values on assignment)
        """
        self.update_df()

    @model_serializer(mode="wrap", when_used="always")
    def serialize_model(self, nxt: SerializerFunctionWrapHandler) -> Dict[str, Any]:
        """
        We don't handle values that are changed on the dataframe by directly
        updating the underlying model lists, but we implicitly handle them
        by using the dataframe as the source when serializing
        """
        if self._df is None:
            return nxt(self)
        else:
            out = self._df.to_dict("list")
            # remove Nones
            out = {k: [inner_v for inner_v in v if inner_v is not None] for k, v in out.items()}
            return nxt(self.__class__(**out))


def dynamictable_to_df(
    group: h5py.Group, model: Optional[Type[DataFrame]] = None, base: Optional[BaseModel] = None
) -> DataFrame:
    if model is None:
        model = model_from_dynamictable(group, base)

    items = {}
    for col, col_type in model.model_fields.items():
        if col not in group.keys():
            continue
        idxname = col + "_index"
        if idxname in group.keys():
            idx = group.get(idxname)[:]
            data = group.get(col)[idx - 1]
        else:
            data = group.get(col)[:]

        # Handle typing inside of list
        if isinstance(data[0], bytes):
            data = data.astype("unicode")
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
        elif isinstance(data[0], tuple) and any(
            [isinstance(d, h5py.h5r.Reference) for d in data[0]]
        ):
            # references stored inside a tuple, reference + location.
            # dereference them!?
            dset = group.get(col)
            names = dset.dtype.names
            if names is not None and names[0] == "idx_start" and names[1] == "count":
                data = dereference_reference_vector(dset, data)

        else:
            data = data.tolist()

        # After list, check if we need to put this thing inside of
        # another class, as indicated by the enclosing model

        items[col] = data

    return model(hdf5_path=group.name, name=group.name.split("/")[-1], **items)
