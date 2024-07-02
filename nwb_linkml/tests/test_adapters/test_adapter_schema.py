import pytest
from ..fixtures import nwb_core_fixture

from nwb_schema_language import Dataset, Group, Schema


@pytest.mark.parametrize(["schema_name"], [["core.nwb.file"]])
def test_schema_build(nwb_core_fixture, schema_name):
    schema = [sch for sch in nwb_core_fixture.schemas if sch.name == schema_name][0]
    res = schema.build()


def test_schema_repr(nwb_core_fixture):
    """
    Doesn't really make sense to test the string repr matches any particular value because it's
    strictly cosmetic, but we do test that it can be done
    """
    sch = nwb_core_fixture.schemas[0]
    repr_str = sch.__repr__()
    assert isinstance(repr_str, str)
