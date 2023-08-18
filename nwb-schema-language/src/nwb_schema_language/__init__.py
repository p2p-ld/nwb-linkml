import warnings
try:
    from .datamodel.nwb_schema_pydantic import Namespace, \
        Namespaces, \
        Schema, \
        Group, \
        Attribute, \
        Link, \
        Dataset, \
        ReferenceDtype, \
        CompoundDtype
except NameError:
    warnings.warn('Error importing pydantic classes, passing because we might be in the process of patching them, but it is likely they are broken and you will be unable to use them!')