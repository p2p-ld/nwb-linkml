"""
Pydantic representation of the NWB Schema Language specification
"""

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


except (NameError, RecursionError) as e:
    warnings.warn(
        "Error importing pydantic classes, passing because we might be in the process of patching"
        f" them, but it is likely they are broken and you will be unable to use them!\n{e}",
        stacklevel=1,
    )

__all__ = [
    "Attribute",
    "CompoundDtype",
    "Dataset",
    "DTypeType",
    "FlatDtype",
    "Group",
    "Link",
    "Namespace",
    "Namespaces",
    "ReferenceDtype",
    "Schema",
]
