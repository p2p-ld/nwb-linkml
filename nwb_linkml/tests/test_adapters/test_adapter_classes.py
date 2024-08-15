import pytest
from linkml_runtime.linkml_model import SlotDefinition

from nwb_linkml.adapters import DatasetAdapter, GroupAdapter
from nwb_linkml.maps.dtype import handle_dtype
from nwb_schema_language import CompoundDtype, Dataset, Group, ReferenceDtype


@pytest.mark.xfail()
def test_build_base(nwb_schema):
    # simplest case, nothing special here. Should be same behavior between dataset and group
    dset = DatasetAdapter(cls=nwb_schema.datasets["image"])
    base = dset.build_base()
    assert len(base.slots) == 0
    assert len(base.classes) == 1
    img = base.classes[0]
    assert img.name == "Image"
    # no parent class, tree_root should be true
    assert img.tree_root
    assert len(img.attributes) == 3

    # now with parent class
    groups = GroupAdapter(cls=nwb_schema.groups["images"])
    dset.parent = groups
    base = dset.build_base()
    # we made a self-slot (will be tested elsewhere)
    assert len(base.slots) == 1
    assert len(base.classes) == 1
    img = base.classes[0]
    assert not img.tree_root
    assert len(img.attributes) == 3

    # now try adding an extra attribute
    slot = SlotDefinition(name="newslot", range="string")
    # should coerce single slot to a list within the method
    base = dset.build_base(extra_attrs=slot)
    assert len(base.slots) == 1
    assert len(base.classes) == 1
    img = base.classes[0]
    assert len(img.attributes) == 4
    assert img.attributes["newslot"] == slot


def test_get_attr_name():
    """Name method used by parentless classes"""
    cls = Dataset(neurodata_type_def="MyClass", doc="a class")
    adapter = DatasetAdapter(cls=cls)
    # type_defs get their original name
    assert adapter._get_attr_name() == "MyClass"

    # explicit names get that name, but only if there is no type_def
    adapter.cls.name = "MyClassName"
    assert adapter._get_attr_name() == "MyClass"
    adapter.cls.neurodata_type_def = None
    assert adapter._get_attr_name() == "MyClassName"

    # if neither, use the type inc
    adapter.cls.neurodata_type_inc = "MyThirdName"
    assert adapter._get_attr_name() == "MyClassName"
    adapter.cls.name = None
    assert adapter._get_attr_name() == "MyThirdName"

    # if none are present, raise a value error
    adapter.cls.neurodata_type_inc = None
    with pytest.raises(ValueError):
        adapter._get_attr_name()


def test_get_full_name():
    """Name used by child classes"""
    cls = Dataset(neurodata_type_def="Child", doc="a class")
    parent = GroupAdapter(cls=Group(neurodata_type_def="Parent", doc="a class"))
    adapter = DatasetAdapter(cls=cls, parent=parent)

    # if child has its own type_def, use that
    assert adapter._get_full_name() == "Child"

    # same thing with type_inc
    adapter.cls.neurodata_type_def = None
    adapter.cls.neurodata_type_inc = "ChildInc"
    assert adapter._get_full_name() == "ChildInc"

    # if it just has a name, it gets concatenated with its parents
    adapter.cls.neurodata_type_inc = None
    adapter.cls.name = "ChildName"
    assert adapter._get_full_name() == "Parent__ChildName"

    # this should work at any depth of nesting if the parent is not an independently defined class
    grandparent = GroupAdapter(cls=Group(neurodata_type_def="Grandparent", doc="a class"))
    parent.cls.neurodata_type_def = None
    parent.cls.name = "ParentName"
    parent.parent = grandparent
    assert adapter._get_full_name() == "ParentName__ChildName"

    # if it has none, raise value error
    adapter.cls.name = None
    with pytest.raises(ValueError):
        adapter._get_full_name()


def test_self_slot():
    """
    Slot that represents ourselves to our parent

    Quantity map is tested elsewhere
    """
    cls = Dataset(neurodata_type_def="ChildClass", doc="a class", quantity="?")
    parent = GroupAdapter(cls=Group(neurodata_type_def="Parent", doc="a class"))
    adapter = DatasetAdapter(cls=cls, parent=parent)

    # base case - snake case a type def
    slot = adapter.build_self_slot()
    assert slot.name == "child_class"
    assert slot.range == "ChildClass" == adapter._get_full_name()

    # this should be the slot that gets build with the build_base method
    base = adapter.build_base()
    assert len(base.slots) == 1
    assert base.slots[0] == slot

    # if class has a unique name, use that without changing, but only if no type_def

    adapter.cls.name = "FixedName"
    slot = adapter.build_self_slot()
    assert slot.name == "child_class"
    adapter.cls.neurodata_type_def = None
    slot = adapter.build_self_slot()
    assert slot.name == "FixedName"
    assert slot.range == adapter._get_full_name()

    # type_inc works the same as type_def, but only if name and type_def are None
    adapter.cls.neurodata_type_inc = "IncName"
    slot = adapter.build_self_slot()
    assert slot.name == "FixedName"
    adapter.cls.name = None
    slot = adapter.build_self_slot()
    assert slot.name == "inc_name"
    assert slot.range == adapter._get_full_name()

    # if we have nothing, raise value error
    adapter.cls.neurodata_type_inc = None
    with pytest.raises(ValueError):
        adapter.build_self_slot()


def test_name_slot():
    """Classes with a fixed name should name slot with a fixed value"""
    # no name
    cls = DatasetAdapter(cls=Dataset(neurodata_type_def="MyClass", doc="a class"))
    slot = cls.build_name_slot()
    assert slot.name == "name"
    assert slot.required
    assert slot.range == "string"
    assert slot.identifier is None
    assert slot.ifabsent is None
    assert slot.equals_string is None

    cls.cls.name = "FixedName"
    slot = cls.build_name_slot()
    assert slot.name == "name"
    assert slot.required
    assert slot.range == "string"
    assert slot.identifier is None
    assert slot.ifabsent == "string(FixedName)"
    assert slot.equals_string == "FixedName"


def test_handle_dtype(nwb_schema):
    """
    Dtypes should be translated from nwb schema language to linkml

    Dtypes are validated by the nwb_schema_language classes, so we don't do that here
    """
    cls = DatasetAdapter(cls=Dataset(neurodata_type_def="MyClass", doc="a class"))

    reftype = ReferenceDtype(target_type="TargetClass", reftype="reference")
    compoundtype = [
        CompoundDtype(name="field_a", doc="field a!", dtype="int32"),
        CompoundDtype(name="field_b", doc="field b!", dtype="text"),
        CompoundDtype(name="reference", doc="reference!", dtype=reftype),
    ]

    assert handle_dtype(reftype) == "TargetClass"
    assert handle_dtype(None) == "AnyType"
    assert handle_dtype([]) == "AnyType"
    # handling compound types is currently TODO
    assert handle_dtype(compoundtype) == "AnyType"
    assert handle_dtype("int32") == "int32"
