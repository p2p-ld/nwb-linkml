"""
Base includes
"""

import pytest


@pytest.mark.skip
def test_basemodel_getitem(imported_schema):
    """
    We can get a value from ``value`` if we have it
    """
    pass


@pytest.mark.skip
def test_basemodel_coerce_value(imported_schema):
    """
    We can instantiate something by trying to grab it's "value" item
    """
    pass


@pytest.mark.skip
def test_basemodel_cast_with_value(imported_schema):
    """
    Opposite of above, we try to cast **into** the ``value`` field
    """
    pass


@pytest.mark.skip
def test_basemodel_coerce_subclass(imported_schema):
    """
    We try to rescue by coercing to a child class if possible
    """
    pass


@pytest.mark.skip
def test_basemodel_extra_to_value(imported_schema):
    """
    We gather extra fields and put them into a value dict when it's present
    """
    pass
