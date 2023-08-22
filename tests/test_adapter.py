import pytest
from rich import print
import pdb

from .fixtures import nwb_core_fixture
from nwb_schema_language import Attribute

def test_walk_adapter(nwb_core_fixture):
    base = nwb_core_fixture.schemas[0]
    assert base.path.name == "nwb.base.yaml"
    # type_incs = [inc for inc in base.walk(base)]
    type_incs = [inc for inc in base.walk_fields(base, 'neurodata_type_inc')]

    attributes = [a for a in base.walk_types(base, Attribute)]

    # pdb.set_trace()

@pytest.mark.parametrize(
    ['class_name','schema_file','namespace_name'],
    [
        ('DynamicTable', 'table.yaml', 'hdmf-common'),
        ('Container', 'base.yaml', 'hdmf-common'),
        ('TimeSeries', 'nwb.base.yaml', 'core'),
        ('ImageSeries', 'nwb.image.yaml', 'core')
    ]
)
def test_find_type_source(nwb_core_fixture, class_name, schema_file, namespace_name):
    defining_sch = nwb_core_fixture.find_type_source(class_name)
    assert defining_sch.path.name == schema_file
    assert namespace_name == defining_sch.namespace


def test_populate_imports(nwb_core_fixture):
    nwb_core_fixture.populate_imports()

    pdb.set_trace()