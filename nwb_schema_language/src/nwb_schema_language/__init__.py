import warnings
from typing import List, Union

try:
    from .datamodel.nwb_schema_pydantic import (
        Attribute,
        CompoundDtype,
        Dataset,
        FlatDtype,
        Group,
        Link,
        Namespace,
        Namespaces,
        ReferenceDtype,
        Schema,
    )

    DTypeType = Union[List[CompoundDtype], FlatDtype, ReferenceDtype]
except (NameError, RecursionError):
    warnings.warn(
        "Error importing pydantic classes, passing because we might be in the process of patching"
        " them, but it is likely they are broken and you will be unable to use them!"
    )
