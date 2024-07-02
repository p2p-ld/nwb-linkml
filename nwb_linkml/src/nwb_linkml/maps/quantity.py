"""
Quantity maps on to two things: required and cardinality.

Though it is technically possible to use an integer as
a quantity, that is never done in the core schema,
which is our only target for now.

We will handle cardinality of array dimensions elsewhere
"""

QUANTITY_MAP = {
    "*": {"required": False, "multivalued": True},
    "+": {"required": True, "multivalued": True},
    "?": {"required": False, "multivalued": False},
    1: {"required": True, "multivalued": False},
    # include the NoneType for indexing
    None: {"required": None, "multivalued": None},
}
