from nwb_linkml.adapters.dataset import (
    MapScalar,
)
from nwb_schema_language import Dataset


def test_nothing(nwb_core_fixture):
    pass


def _compare_dicts(dict1, dict2) -> bool:
    """just in one direction - that all the entries in dict1 are in dict2"""
    assert all([dict1[k] == dict2[k] for k in dict1.keys()])
    # assert all([dict1[k] == dict2[k] for k in dict2.keys()])


def test_map_scalar():

    model = {
        "name": "MyScalar",
        "doc": "This should be a scalar",
        "dtype": "int32",
        "quantity": "?",
    }
    test = {
        "name": "MyScalar",
        "description": "This should be a scalar",
        "multivalued": False,
        "range": "int32",
        "required": False,
    }

    dataset = Dataset(**model)
    assert MapScalar.check(dataset)
    result = MapScalar.apply(dataset)
    assert len(result.classes) == 0
    _compare_dicts(test, result.slots[0])


def test_map_scalar_attributes():
    pass


def test_map_listlike():
    pass


def test_map_arraylike():
    pass


def test_map_arraylike_attributes():
    pass


def test_map_1d_vector():
    pass


def test_map_n_vectors():
    pass
