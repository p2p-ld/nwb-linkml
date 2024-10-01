from pathlib import Path

import pytest

from nwb_linkml.adapters import NamespacesAdapter, SchemaAdapter
from nwb_schema_language import Attribute, Dataset, FlatDtype, Group, Namespace, Namespaces, Schema


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
    nwb_core_fixture._populate_imports()
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


def test_roll_down_inheritance():
    """
    Classes should receive and override the properties of their parents
    when they have neurodata_type_inc
    """
    parent_cls = Group(
        neurodata_type_def="Parent",
        doc="parent",
        attributes=[
            Attribute(name="a", dims=["a", "b"], shape=[1, 2], doc="a", value="a"),
            Attribute(name="b", dims=["c", "d"], shape=[3, 4], doc="b", value="b"),
        ],
        datasets=[
            Dataset(
                name="data",
                dims=["a", "b"],
                shape=[1, 2],
                doc="data",
                attributes=[
                    Attribute(name="c", dtype=FlatDtype.int32, doc="c"),
                    Attribute(name="d", dtype=FlatDtype.int32, doc="d"),
                ],
            )
        ],
    )
    parent_sch = Schema(source="parent.yaml")
    parent_ns = Namespaces(
        namespaces=[
            Namespace(
                author="hey",
                contact="sup",
                name="parent",
                doc="a parent",
                version="1",
                schema=[parent_sch],
            )
        ]
    )

    child_cls = Group(
        neurodata_type_def="Child",
        neurodata_type_inc="Parent",
        doc="child",
        attributes=[Attribute(name="a", doc="a", value="z")],
        datasets=[
            Dataset(
                name="data",
                doc="data again",
                attributes=[Attribute(name="c", doc="c", value="z"), Attribute(name="e", doc="e")],
            ),
        ],
        groups=[Group(name="untyped_child", neurodata_type_inc="Parent", doc="untyped child")],
    )
    child_sch = Schema(source="child.yaml")
    child_ns = Namespaces(
        namespaces=[
            Namespace(
                author="hey",
                contact="sup",
                name="child",
                doc="a child",
                version="1",
                schema=[child_sch, Schema(namespace="parent")],
            )
        ]
    )

    parent_schema_adapter = SchemaAdapter(path=Path("parent.yaml"), groups=[parent_cls])
    parent_ns_adapter = NamespacesAdapter(namespaces=parent_ns, schemas=[parent_schema_adapter])
    child_schema_adapter = SchemaAdapter(path=Path("child.yaml"), groups=[child_cls])
    child_ns_adapter = NamespacesAdapter(
        namespaces=child_ns, schemas=[child_schema_adapter], imported=[parent_ns_adapter]
    )

    child_ns_adapter.complete_namespaces()

    child = child_ns_adapter.get("Child")
    # overrides simple attrs
    assert child.doc == "child"
    # we don't receive attrs that aren't overridden in the child,
    # instead we let python/linkml inheritance handle that for us
    assert "b" not in [attr.name for attr in child.attributes]
    # overrides values while preserving remaining values when set
    attr_a = [attr for attr in child.attributes if attr.name == "a"][0]
    assert attr_a.value == "z"
    assert attr_a.dims == parent_cls.attributes[0].dims
    assert [attr.value for attr in child.attributes if attr.name == "a"][0] == "z"

    # preserve unset values in child datasets
    assert child.datasets[0].dtype == parent_cls.datasets[0].dtype
    assert child.datasets[0].dims == parent_cls.datasets[0].dims
    # we *do* get undeclared attrs in child datasets,
    # since those are not handled by python/linkml inheritance
    assert "d" in [attr.name for attr in child.datasets[0].attributes]
    # overrides set values in child datasets while preserving unset
    c_attr = [attr for attr in child.datasets[0].attributes if attr.name == "c"][0]
    assert c_attr.value == "z"
    assert c_attr.dtype == FlatDtype.int32
    # preserves new attrs
    assert "e" in [attr.name for attr in child.datasets[0].attributes]

    # neurodata_type_def is not included in untyped children
    assert child.groups[0].neurodata_type_def is None
    # we don't set any of the attrs from the parent class here because we don't override them,
    # so we don't need to merge them, and we don't want to clutter our linkml models unnecessarily
    assert child.groups[0].attributes is None
