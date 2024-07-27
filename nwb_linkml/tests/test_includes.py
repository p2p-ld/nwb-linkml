from pydantic import BaseModel
from nwb_linkml.includes import Named

def test_named_generic():
    """
    the Named type should fill in the ``name`` field in a model from the field name
    """
    class Child(BaseModel):
        name: str
        value: int

    class Parent(BaseModel):
        field_name: Named[Child]

    # should instantiate correctly and have name set
    instance = Parent(field_name={'value': 1})
    assert instance.field_name.name == 'field_name'