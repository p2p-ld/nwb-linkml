import pytest

from pydantic import BaseModel, ValidationError
from typing import List, Union, Optional


@pytest.mark.skip()
def test_df():
    """
    Dataframe class should behave like both a pydantic model and a dataframe
    """
    import pandas as pd
    from nwb_linkml.types.df import DataFrame

    class MyDf(DataFrame):
        ints: List[int]
        strings: List[str]
        multi: List[int | str]
        opts: Optional[List[int]] = None

    good_kwargs = {
        "ints": [1, 2, 3],
        "strings": ["a", "b", "c"],
        "multi": [1, 2, "a", "d"],
        "opts": [],
    }
    bad_kwargs = {"ints": ["a", "b", "c"], "strings": [1, 2, 3], "multi": "d"}
    df = MyDf(**good_kwargs)
    assert isinstance(df, BaseModel)
    assert isinstance(df, pd.DataFrame)
    with pytest.raises(ValidationError):
        bad_df = MyDf(**bad_kwargs)

    # can we do pydantic stuff
    assert df.model_dump() == good_kwargs
    # these throw when they fail
    _ = df.model_dump_json()
    _ = df.model_json_schema()

    # can we do pandas stuff
    assert df["ints"].sum() == 6
    assert df.loc[2].to_list() == [3, "c", "a", None]
    # lmao

    # we don't include the model when dumping/doing the schema
    assert "df" not in df.model_json_schema()
    assert "_df" not in df.model_json_schema()

    # we update our dataframe when we assign
    assert df.ints == good_kwargs["ints"]
    assert df["ints"].tolist()[0:3] == good_kwargs["ints"]
    df.ints = [1, 2, 3, 4]
    assert df.ints == [1, 2, 3, 4]
    assert (df["ints"] == pd.Series([1, 2, 3, 4])).all()

    df["ints"] = df["ints"]._append(pd.Series(5))
