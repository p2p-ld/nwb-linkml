import pdb

import pytest
from ..fixtures import nwb_core_fixture
from nwb_schema_language import Dataset, Group
from nwb_linkml.adapters import SchemaAdapter


@pytest.mark.parametrize(
    ["class_name", "schema_file", "namespace_name"],
    [
        ("DynamicTable", "table.yaml", "hdmf-common"),
        ("Container", "base.yaml", "hdmf-common"),
        ("TimeSeries", "nwb.base.yaml", "core"),
        ("ImageSeries", "nwb.image.yaml", "core"),
    ],
)
def test_find_type_source(nwb_core_fixture, class_name, schema_file, namespace_name):
    defining_sch = nwb_core_fixture.find_type_source(class_name)
    assert defining_sch.path.name == schema_file
    assert namespace_name == defining_sch.namespace


def test_populate_imports(nwb_core_fixture):
    nwb_core_fixture.populate_imports()
    schema: SchemaAdapter
    assert len(nwb_core_fixture.schemas) > 0
    for schema in nwb_core_fixture.schemas:
        need_imports = [
            nwb_core_fixture.find_type_source(cls.neurodata_type_def).namespace
            for cls in schema.created_classes
            if cls.neurodata_type_inc is not None
        ]
        need_imports = [i for i in need_imports if i != schema.namespace]
        for i in need_imports:
            assert i in schema.imports


def test_build(nwb_core_fixture):
    pass


def test_skip_imports(nwb_core_fixture):
    """
    We can build just the namespace in question without also building the other namespaces that it imports
    """
    res = nwb_core_fixture.build(skip_imports=True)

    # we shouldn't have any of the hdmf-common schema in with us
    namespaces = [sch.annotations["namespace"].value for sch in res.schemas]
    assert all([ns == "core" for ns in namespaces])
