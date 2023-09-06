import pytest
from ..fixtures import nwb_core_fixture

from nwb_schema_language import Dataset, Group, Schema

@pytest.mark.parametrize(
    ['schema_name'],
    [
        ['core.nwb.file']
    ]
)
def test_schema_build(nwb_core_fixture, schema_name):
    schema = [sch for sch in nwb_core_fixture.schemas if sch.name == schema_name][0]
    res = schema.build()