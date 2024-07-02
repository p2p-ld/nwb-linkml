"""
Utility functions for introspection on python annotations
"""

import typing
from typing import Any, List, Optional, Type, TypeVar

T = TypeVar("T")


def unwrap_optional(annotation: Type[Optional[T]]) -> Type[T]:
    """
    Get the inner type of an `Optional[T]` type
    """
    if typing.get_origin(annotation) == typing.Union:
        args = typing.get_args(annotation)

        if len(args) == 2 and args[1].__name__ == "NoneType":
            annotation = args[0]
    return annotation


def get_inner_types(annotation: Type) -> List[Any]:
    """
    Get the inner types in some nested type, recursively
    """
    types = []
    args = typing.get_args(annotation)
    for arg in args:
        # try and get inner types to see if we're a terminal type
        inner_args = typing.get_args(arg)
        if len(inner_args) == 0:
            types.append(arg)
        else:
            types.extend(get_inner_types(arg))
    return types
