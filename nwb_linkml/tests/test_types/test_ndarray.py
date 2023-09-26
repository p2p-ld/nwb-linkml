import pdb
from typing import Union, Optional, Any

import pytest

import numpy as np

from pydantic import BaseModel, ValidationError, Field
from nwb_linkml.types.ndarray import NDArray
from nptyping import Shape, Number

from ..fixtures import data_dir
def test_ndarray_type():

    class Model(BaseModel):
        array: NDArray[Shape["2 x, * y"], Number]

    schema = Model.model_json_schema()
    assert schema['properties']['array']['items'] == {'items': {'type': 'number'}, 'type': 'array'}
    assert schema['properties']['array']['maxItems'] == 2
    assert schema['properties']['array']['minItems'] == 2

    # models should instantiate correctly!
    instance = Model(array=np.zeros((2,3)))

    with pytest.raises(ValidationError):
        instance = Model(array=np.zeros((4,6)))

    with pytest.raises(ValidationError):
        instance = Model(array=np.ones((2,3), dtype=bool))


def test_ndarray_union():
    class Model(BaseModel):
        array: Optional[Union[
            NDArray[Shape["* x, * y"], Number],
            NDArray[Shape["* x, * y, 3 r_g_b"], Number],
            NDArray[Shape["* x, * y, 3 r_g_b, 4 r_g_b_a"], Number]
        ]] = Field(None)

    instance = Model()
    instance = Model(array=np.random.random((5,10)))
    instance = Model(array=np.random.random((5,10,3)))
    instance = Model(array=np.random.random((5,10,3,4)))

    with pytest.raises(ValidationError):
        instance = Model(array=np.random.random((5,)))

    with pytest.raises(ValidationError):
        instance = Model(array=np.random.random((5,10,4)))

    with pytest.raises(ValidationError):
        instance = Model(array=np.random.random((5,10,3,6)))

    with pytest.raises(ValidationError):
        instance = Model(array=np.random.random((5,10,4,6)))

@pytest.mark.skip()
def test_ndarray_proxy(data_dir):
    h5f_source = data_dir / 'aibs_ecephys.nwb'
