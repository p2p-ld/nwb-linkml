"""
Utility functions for introspection on python annotations
"""
import typing


def unwrap_optional(annotation):
    if typing.get_origin(annotation) == typing.Union:
        args = typing.get_args(annotation)

        if len(args) == 2 and args[1].__name__ == 'NoneType':
            annotation = args[0]
    return annotation


def take_outer_type(annotation):
    if typing.get_origin(annotation) is list:
        return list
    return annotation
