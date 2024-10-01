"""
Test custom features of the pydantic generator

Note that since this is largely a subclass, we don't test all of the functionality of the generator
because it's tested in the base linkml package.
"""

# ruff: noqa: F821 - until the tests here settle down

import sys
import typing
from types import ModuleType
from typing import Optional, TypedDict

import numpy as np
import pytest
from numpydantic.ndarray import NDArrayMeta
from numpydantic.dtype import Float

from linkml_runtime.utils.compile_python import compile_python
from nwb_linkml.generators.pydantic import NWBPydanticGenerator

from ..fixtures import (
    TestSchemas,
)


class TestModules(TypedDict):
    core: ModuleType
    imported: ModuleType
    namespace: ModuleType
    split: bool


TestModules.__test__ = False


def generate_and_import(
    linkml_schema: TestSchemas, split: bool, generator_kwargs: Optional[dict] = None
) -> TestModules:
    if generator_kwargs is None:
        generator_kwargs = {}
    default_kwargs = {
        "split": split,
        "emit_metadata": True,
        "gen_slots": True,
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

    core = compile_python(str(linkml_schema.core_path.with_suffix(".py")))
    imported = compile_python(str(linkml_schema.imported_path.with_suffix(".py")))
    namespace = compile_python(str(linkml_schema.namespace_path.with_suffix(".py")))

    return TestModules(core=core, imported=imported, namespace=namespace, split=split)


@pytest.fixture(scope="module", params=["split", "unsplit"])
def imported_schema(linkml_schema, request) -> TestModules:
    """
    Convenience fixture for testing non-core generator features without needing to re-generate and
    import every time.
    """
    split = request.param == "split"

    return generate_and_import(linkml_schema, split)


def test_array(imported_schema):
    """
    Arraylike classes are converted to slots that specify nptyping arrays

    array: Optional[Union[
        NDArray[Shape["* x, * y"], Number],
        NDArray[Shape["* x, * y, 3 z"], Number],
        NDArray[Shape["* x, * y, 3 z, 4 a"], Number]
    ]] = Field(None)
    """
    # check that we have gotten an NDArray annotation and its shape is correct
    array = imported_schema["core"].MainTopLevel.model_fields["value"].annotation
    args = typing.get_args(array)
    for i, shape in enumerate(("* x, * y", "* x, * y, 3 z", "* x, * y, 3 z, 4 a")):
        assert isinstance(args[i], NDArrayMeta)
        assert args[i].__args__[0].__args__[0] == shape
        assert args[i].__args__[1] == Float

    # we shouldn't have an actual class for the array
    assert not hasattr(imported_schema["core"], "MainTopLevel__Array")
    assert not hasattr(imported_schema["core"], "MainTopLevelArray")


def test_inject_fields(imported_schema):
    """
    Our root model should have the special fields we injected
    """
    base = imported_schema["core"].ConfiguredBaseModel
    assert "hdf5_path" in base.model_fields
    assert "object_id" in base.model_fields


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
        ("OtherClass", "test_schema.core"),
        ("StillAnotherClass", "test_schema.core"),
    ):
        assert hasattr(ns, classname)
        if imported_schema["split"]:
            module_end_name = ".".join(getattr(ns, classname).__module__.split(".")[-2:])
            assert module_end_name == modname


def test_get_item(imported_schema):
    """We can get without explicitly addressing array"""
    cls = imported_schema["core"].MainTopLevel(value=np.array([[1, 2, 3], [4, 5, 6]], dtype=float))
    assert np.array_equal(cls[0], np.array([1, 2, 3], dtype=float))
    

