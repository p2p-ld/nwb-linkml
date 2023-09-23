"""
Pydantic models that behave like pandas dataframes
"""
import pdb
from typing import List, Any, get_origin, get_args, Union, Optional, Dict
from types import NoneType

import numpy as np
import pandas as pd
from pydantic import (
    BaseModel,
    model_serializer,
    SerializerFunctionWrapHandler,
    ConfigDict,
    model_validator
)

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
        items = {k:v for k,v in self.__dict__.items() if k in self.model_fields}

        df_dict = {k: (pd.Series(v) if isinstance(v, list) else pd.Series([v]))
                   for k,v in items.items()}
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
        if item in ('df', '_df'):
            return self.__pydantic_private__['_df']
        elif item in self.model_fields.keys():
            return self._df[item]
        else:
            try:
                return object.__getattribute__(self._df, item)
            except AttributeError:
                return object.__getattribute__(self, item)

    @model_validator(mode='after')
    def recreate_df(self):
        """
        Remake DF when validating (eg. when updating values on assignment)
        """
        self.update_df()

    @model_serializer(mode='wrap', when_used='always')
    def serialize_model(self, nxt: SerializerFunctionWrapHandler) -> Dict[str, Any]:
        """
        We don't handle values that are changed on the dataframe by directly
        updating the underlying model lists, but we implicitly handle them
        by using the dataframe as the source when serializing
        """
        if self._df is None:
            return nxt(self)
        else:
            out = self._df.to_dict('list')
            # remove Nones
            out = {
                k: [inner_v for inner_v in v if inner_v is not None]
                for k, v in out.items()
            }
            return nxt(self.__class__(**out))
