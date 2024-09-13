from nwb_schema_language import Group, Dataset, Attribute


def test_parentize_mixin():
    """
    the parentize mixin should populate the "parent" attribute for applicable children
    """
    dset_attr = Attribute(name="dset_attr", doc="")
    dset = Dataset(
        name="dataset", doc="", attributes=[dset_attr, {"name": "dict_based_attr", "doc": ""}]
    )
    group_attr = Attribute(name="group_attr", doc="")
    group = Group(
        name="group",
        doc="",
        attributes=[group_attr, {"name": "dict_based_attr", "doc": ""}],
        datasets=[dset, {"name": "dict_based_dset", "doc": ""}],
    )

    assert dset_attr.parent is dset
    assert dset.attributes[1].name == "dict_based_attr"
    assert dset.attributes[1].parent is dset
    assert dset.parent is group
    assert group_attr.parent is group
    assert group.attributes[1].name == "dict_based_attr"
    assert group.attributes[1].parent is group
    assert group.datasets[1].name == "dict_based_dset"
    assert group.datasets[1].parent is group

    dumped = group.model_dump()
    assert "parent" not in dumped
