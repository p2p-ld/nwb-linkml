import pytest
from ..fixtures import nwb_core_fixture

from nwb_schema_language import Dataset, Group, Schema

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

    # pdb.set_trace()


def test_build_result_add():
    """
    Build results can
    Returns:

    """