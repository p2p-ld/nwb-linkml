from types import NoneType
from typing import List

import pytest

from nwb_linkml.annotations import get_inner_types


@pytest.mark.parametrize(("annotation", "inner_types"), [(List[str | None], (str, NoneType))])
def test_get_inner_types(annotation, inner_types):
    got_inner_types = get_inner_types(annotation)
    assert len(got_inner_types) == len(inner_types)
    for got, expected in zip(got_inner_types, inner_types):
        assert got is expected
