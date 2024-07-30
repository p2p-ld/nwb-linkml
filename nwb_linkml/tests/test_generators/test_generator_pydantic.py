"""
Test custom features of the pydantic generator

Note that since this is largely a subclass, we don't test all of the functionality of the generator
because it's tested in the base linkml package.
"""

import re
import sys
import typing
from types import ModuleType
from typing import Optional, TypedDict

import numpy as np
import pytest
from numpydantic.ndarray import NDArrayMeta
from pydantic import BaseModel

from nwb_linkml.generators.pydantic import NWBPydanticGenerator, compile_python

from ..fixtures import (
    TestSchemas,
)


class TestModules(TypedDict):
    core: ModuleType
    imported: ModuleType
    namespace: ModuleType
    split: bool


TestModules.__test__ = False


@pytest.mark.xfail()
def generate_and_import(
    linkml_schema: TestSchemas, split: bool, generator_kwargs: Optional[dict] = None
) -> TestModules:
    if generator_kwargs is None:
        generator_kwargs = {}
    default_kwargs = {
        "split": split,
        "emit_metadata": True,
        "gen_slots": True,
        "pydantic_version": "2",
        **generator_kwargs,
    }

    core_str = NWBPydanticGenerator(str(linkml_schema.core_path), **default_kwargs).serialize()
    imported_str = NWBPydanticGenerator(
        str(linkml_schema.imported_path), **default_kwargs
    ).serialize()
    namespace_str = NWBPydanticGenerator(
        str(linkml_schema.namespace_path), **default_kwargs
    ).serialize()

    with open(linkml_schema.core_path.with_suffix(".py"), "w") as pfile:
        pfile.write(core_str)
    with open(linkml_schema.imported_path.with_suffix(".py"), "w") as pfile:
        pfile.write(imported_str)
    with open(linkml_schema.namespace_path.with_suffix(".py"), "w") as pfile:
        pfile.write(namespace_str)
    with open(linkml_schema.core_path.parent / "__init__.py", "w") as pfile:
        pfile.write(" ")

    sys.path.append(str(linkml_schema.core_path.parents[1]))

    core = compile_python(
        str(linkml_schema.core_path.with_suffix(".py")), module_name="test_schema.core"
    )
    imported = compile_python(
        str(linkml_schema.imported_path.with_suffix(".py")), module_name="test_schema.imported"
    )
    namespace = compile_python(
        str(linkml_schema.namespace_path.with_suffix(".py")), module_name="test_schema.namespace"
    )

    return TestModules(core=core, imported=imported, namespace=namespace, split=split)


@pytest.mark.xfail()
@pytest.fixture(scope="module", params=["split", "unsplit"])
def imported_schema(linkml_schema, request) -> TestModules:
    """
    Convenience fixture for testing non-core generator features without needing to re-generate and
    import every time.
    """
    split = request.param == "split"

    yield generate_and_import(linkml_schema, split)

    del sys.modules["test_schema.core"]
    del sys.modules["test_schema.imported"]
    del sys.modules["test_schema.namespace"]


def _model_correctness(modules: TestModules):
    """
    Shared assertions for model correctness.
    Only tests very basic things like type and existence,
    more specific tests are in their own test functions!
    """
    assert issubclass(modules["core"].MainTopLevel, BaseModel)
    assert issubclass(modules["core"].Skippable, BaseModel)
    assert issubclass(modules["core"].OtherClass, BaseModel)
    assert issubclass(modules["core"].StillAnotherClass, BaseModel)
    assert issubclass(modules["imported"].MainThing, BaseModel)


@pytest.mark.xfail()
def test_generate(linkml_schema):
    """
    Base case, we can generate pydantic models from linkml schema

    Tests basic functionality of serializer including

    - serialization
    - compilation (loading as a python model)
    - existence and correctness of attributes
    """
    modules = generate_and_import(linkml_schema, split=False)

    assert isinstance(modules["core"], ModuleType)
    assert isinstance(modules["imported"], ModuleType)
    assert isinstance(modules["namespace"], ModuleType)
    _model_correctness(modules)

    # unsplit modules should have all the classes present, even if they aren't defined in it
    assert modules["core"].MainThing.__module__ == "test_schema.core"
    assert issubclass(modules["core"].MainTopLevel, modules["core"].MainThing)
    del sys.modules["test_schema.core"]
    del sys.modules["test_schema.imported"]
    del sys.modules["test_schema.namespace"]


@pytest.mark.xfail()
def test_generate_split(linkml_schema):
    """
    We can generate schema split into separate files
    """
    modules = generate_and_import(linkml_schema, split=True)

    assert isinstance(modules["core"], ModuleType)
    assert isinstance(modules["imported"], ModuleType)
    assert isinstance(modules["namespace"], ModuleType)
    _model_correctness(modules)

    # split modules have classes defined once and imported
    assert modules["core"].MainThing.__module__ == "test_schema.imported"
    # can't assert subclass here because of the weird way relative imports work
    # when we don't actually import using normal python import machinery
    assert modules["core"].MainTopLevel.__mro__[1].__module__ == "test_schema.imported"
    del sys.modules["test_schema.core"]
    del sys.modules["test_schema.imported"]
    del sys.modules["test_schema.namespace"]


@pytest.mark.xfail()
def test_versions(linkml_schema):
    """
    We can use explicit versions that import from relative paths generated by
    SchemaProvider
    """
    # here all we do is check that we have the correct relative import, since we test
    # the actual generation of these path structures elsewhere in the provider tests

    core_str = NWBPydanticGenerator(
        str(linkml_schema.core_path), versions={"imported": "v4.2.0"}, split=True
    ).serialize()

    # the import should be like
    # from ...imported.v4_2_0.imported import (
    #     MainThing
    # )
    match = re.findall(r"from \.\.\.imported\.v4_2_0.*?MainThing.*?\)", core_str, flags=re.DOTALL)
    assert len(match) == 1


@pytest.mark.xfail()
def test_arraylike(imported_schema):
    """
    Arraylike classes are converted to slots that specify nptyping arrays

    array: Optional[Union[
        NDArray[Shape["* x, * y"], Number],
        NDArray[Shape["* x, * y, 3 z"], Number],
        NDArray[Shape["* x, * y, 3 z, 4 a"], Number]
    ]] = Field(None)
    """
    # check that we have gotten an NDArray annotation and its shape is correct
    array = imported_schema["core"].MainTopLevel.model_fields["array"].annotation
    args = typing.get_args(array)
    for i, _ in enumerate(("* x, * y", "* x, * y, 3 z", "* x, * y, 3 z, 4 a")):
        assert isinstance(args[i], NDArrayMeta)
        assert args[i].__args__[0].__args__
        assert args[i].__args__[1] == np.number

    # we shouldn't have an actual class for the array
    assert not hasattr(imported_schema["core"], "MainTopLevel__Array")
    assert not hasattr(imported_schema["core"], "MainTopLevelArray")


@pytest.mark.xfail()
def test_inject_fields(imported_schema):
    """
    Our root model should have the special fields we injected
    """
    base = imported_schema["core"].ConfiguredBaseModel
    assert "hdf5_path" in base.model_fields
    assert "object_id" in base.model_fields


@pytest.mark.xfail()
def test_linkml_meta(imported_schema):
    """
    We should be able to store some linkml metadata with our classes
    """
    meta = imported_schema["core"].LinkML_Meta
    assert "tree_root" in meta.model_fields
    assert imported_schema["core"].MainTopLevel.linkml_meta.default.tree_root
    assert not imported_schema["core"].OtherClass.linkml_meta.default.tree_root


@pytest.mark.xfail()
def test_skip(linkml_schema):
    """
    We can skip slots and classes
    """
    modules = generate_and_import(
        linkml_schema,
        split=False,
        generator_kwargs={
            "SKIP_SLOTS": ("SkippableSlot",),
            "SKIP_CLASSES": ("Skippable", "skippable"),
        },
    )
    assert not hasattr(modules["core"], "Skippable")
    assert "SkippableSlot" not in modules["core"].MainTopLevel.model_fields


@pytest.mark.xfail()
def test_inline_with_identifier(imported_schema):
    """
    By default, if a class has an identifier attribute, it is inlined
    as a string rather than its class. We overrode that to be able to make dictionaries of collections
    """
    main = imported_schema["core"].MainTopLevel
    inline = main.model_fields["inline_dict"].annotation
    assert typing.get_origin(typing.get_args(inline)[0]) is dict
    # god i hate pythons typing interface
    otherclass, stillanother = typing.get_args(typing.get_args(typing.get_args(inline)[0])[1])
    assert otherclass is imported_schema["core"].OtherClass
    assert stillanother is imported_schema["core"].StillAnotherClass


@pytest.mark.xfail()
def test_namespace(imported_schema):
    """
    Namespace schema import all classes from the other schema
    Returns:

    """
    ns = imported_schema["namespace"]

    for classname, modname in (
        ("MainThing", "test_schema.imported"),
        ("Arraylike", "test_schema.imported"),
        ("MainTopLevel", "test_schema.core"),
        ("Skippable", "test_schema.core"),
        ("OtherClass", "test_schema.core"),
        ("StillAnotherClass", "test_schema.core"),
    ):
        assert hasattr(ns, classname)
        if imported_schema["split"]:
            assert getattr(ns, classname).__module__ == modname


@pytest.mark.xfail()
def test_get_set_item(imported_schema):
    """We can get and set without explicitly addressing array"""
    cls = imported_schema["core"].MainTopLevel(array=np.array([[1, 2, 3], [4, 5, 6]]))
    cls[0] = 50
    assert (cls[0] == 50).all()
    assert (cls.array[0] == 50).all()

    cls[1, 1] = 100
    assert cls[1, 1] == 100
    assert cls.array[1, 1] == 100
