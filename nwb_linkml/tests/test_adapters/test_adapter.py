import pdb

import pytest
from ..fixtures import nwb_core_fixture

from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition, SlotDefinition, TypeDefinition
from nwb_schema_language import Dataset, Group, Schema, CompoundDtype

from nwb_linkml.adapters import BuildResult

from ..fixtures import linkml_schema_bare

def test_walk(nwb_core_fixture):
    """
    Not sure exactly what should be tested here, for now just testing that we get an expected value
    """
    everything = nwb_core_fixture.walk(nwb_core_fixture)
    assert len(list(everything)) == 9959

@pytest.mark.parametrize(
    ['walk_class', 'known_number'],
    [
        (Dataset, 211),
        (Group, 144),
        ((Dataset, Group), 355),
        (Schema, 19)
    ]
)
def test_walk_types(nwb_core_fixture, walk_class, known_number):
    classes = nwb_core_fixture.walk_types(nwb_core_fixture, walk_class)
    class_list = list(classes)
    assert len(class_list) == known_number

def test_walk_fields(nwb_core_fixture):
    dtype = nwb_core_fixture.walk_fields(nwb_core_fixture, 'dtype')


def test_walk_field_values(nwb_core_fixture):
    dtype_models = list(nwb_core_fixture.walk_field_values(nwb_core_fixture, 'dtype', value=None))

    compounds = [d for d in dtype_models if isinstance(d.dtype, list) and len(d.dtype) > 0 and isinstance(d.dtype[0], CompoundDtype)]


def test_build_result(linkml_schema_bare):
    """
    build results can hold lists of class, slot, and type definitions
    """
    schema = linkml_schema_bare
    sch = schema.core
    cls = sch.classes['MainTopLevel']
    slot1 = cls.attributes['name']
    typ = sch.types['numeric']

    # Build result should hold the results and coerce to list type
    res = BuildResult(
        schemas=sch,
        classes=cls,
        slots=slot1,
        types=typ
    )
    for field in ('schemas', 'classes', 'slots', 'types'):
        assert isinstance(getattr(res, field), list)
        assert len(getattr(res, field)) == 1

@pytest.mark.parametrize(
    'sch_type',
    ('schemas', 'classes', 'slots', 'types')
)
def test_build_result_add(linkml_schema_bare, sch_type):
    """
    Build results can be added together without duplicating
    """
    schema = linkml_schema_bare
    if sch_type == 'schemas':
        obj = schema.core
        other_obj = SchemaDefinition(name="othername", id="othername", version="1.0.1")
    elif sch_type == 'classes':
        obj = schema.core.classes['MainTopLevel']
        other_obj = ClassDefinition(name="othername")
    elif sch_type == 'slots':
        obj = schema.core.classes['MainTopLevel'].attributes['name']
        other_obj = SlotDefinition(name="othername", range="string")
    elif sch_type == 'types':
        obj = schema.core.types['numeric']
        other_obj = TypeDefinition(name="othername", typeof="float")
    else:
        raise ValueError(f"Dont know how to test type {sch_type}")

    res1 = BuildResult(**{sch_type: [obj]})
    res2 = BuildResult(**{sch_type: [obj]})
    assert len(getattr(res1, sch_type)) == 1
    assert len(getattr(res2, sch_type)) == 1

    assert len(getattr(res1 + res2, sch_type)) == 1
    assert len(getattr(res2 + res1, sch_type)) == 1

    # and then addition works as normal for not same named items
    res3 = BuildResult(**{sch_type: [other_obj]})
    assert len(getattr(res1 + res3, sch_type)) == 2
    assert len(getattr(res2 + res3, sch_type)) == 2

    res_combined_2 = res1 + res3
    assert getattr(res_combined_2, sch_type)[-1] is other_obj




