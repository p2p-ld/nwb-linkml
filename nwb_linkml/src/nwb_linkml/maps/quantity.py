"""
Quantity maps on to two things: required and cardinality.

Though it is technically possible to use an integer as
a quantity, that is never done in the core schema,
which is our only target for now.

We will handle cardinality of array dimensions elsewhere
"""

QUANTITY_MAP = {
    "*": {"required": None, "multivalued": True},
    "+": {"required": True, "multivalued": True},
    "?": {"required": None, "multivalued": None},
    1: {"required": True, "multivalued": None},
    # include the NoneType for indexing
    None: {"required": None, "multivalued": None},
}
"""
Map between NWB quantity values and linkml quantity metaslot values. 

Use ``None`` for defaults (required: False, multivalued: False) rather than ``False``
to avoid adding unnecessary attributes
"""
