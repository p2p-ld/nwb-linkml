import pdb

import numpy as np
import pytest
from ..fixtures import nwb_core_fixture

from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition, SlotDefinition, TypeDefinition
from nwb_schema_language import Dataset, Group, Schema, CompoundDtype, Attribute

from nwb_linkml.adapters import BuildResult

from ..fixtures import linkml_schema_bare

def test_walk(nwb_core_fixture):
    """
    Not sure exactly what should be tested here, for now just testing that we get an expected value
    """
    everything = nwb_core_fixture.walk(nwb_core_fixture)

    # number of items obviously changes based on what version we're talking about
    # this is configured as a test matrix on the nwb_core_fixture, currently only testing the latest version
    if nwb_core_fixture.versions['core'] == '2.6.0-alpha' and nwb_core_fixture.versions['hdmf-common'] == '1.5.0':

        assert len(list(everything)) == 9908

@pytest.mark.parametrize(
    ['walk_class', 'known_number'],
    [
        (Dataset, 210),
        (Group, 144),
        ((Dataset, Group), 354),
        (Schema, 19)
    ]
)
def test_walk_types(nwb_core_fixture, walk_class, known_number):
    classes = nwb_core_fixture.walk_types(nwb_core_fixture, walk_class)
    class_list = list(classes)
    assert len(class_list) == known_number

def test_walk_fields(nwb_core_fixture):
    # should get same number of dtype fields as there are datasets and attributes + compound dtypes
    dtype = list(nwb_core_fixture.walk_fields(nwb_core_fixture, 'dtype'))

    dtype_havers = list(nwb_core_fixture.walk_types(nwb_core_fixture, (Dataset, Attribute)))
    compound_dtypes = [len(d.dtype) for d in dtype_havers if isinstance(d.dtype, list)]
    expected_dtypes = np.sum(compound_dtypes) + len(dtype_havers)
    assert expected_dtypes == len(dtype)


def test_walk_field_values(nwb_core_fixture):
    dtype_models = list(nwb_core_fixture.walk_field_values(nwb_core_fixture, 'dtype', value=None))
    assert all([hasattr(d, 'dtype') for d in dtype_models])
    text_models = list(nwb_core_fixture.walk_field_values(nwb_core_fixture, 'dtype', value='text'))
    assert all([d.dtype == 'text' for d in text_models])
    # 135 known value from regex search
    assert len(text_models) == len([d for d in dtype_models if d.dtype == 'text']) == 134


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




