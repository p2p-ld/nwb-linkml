"""
Dtype mappings
"""

from datetime import datetime
from typing import Any, Type

import nptyping
import numpy as np

from nwb_schema_language import CompoundDtype, DTypeType, FlatDtype, ReferenceDtype

flat_to_linkml = {
    "float": "float",
    "float32": "float",
    "double": "double",
    "float64": "double",
    "long": "integer",
    "int64": "integer",
    "int": "integer",
    "int32": "integer",
    "int16": "integer",
    "short": "integer",
    "int8": "integer",
    "uint": "integer",
    "uint32": "integer",
    "uint16": "integer",
    "uint8": "integer",
    "uint64": "integer",
    "numeric": "float",
    "text": "string",
    "utf": "string",
    "utf8": "string",
    "utf_8": "string",
    "ascii": "string",
    "bool": "boolean",
    "isodatetime": "datetime",
}
"""
Map between the flat data types and the simpler linkml base types
"""

flat_to_nptyping = {
    "float": "Float",
    "float32": "Float32",
    "double": "Double",
    "float64": "Float64",
    "long": "LongLong",
    "int64": "Int64",
    "int": "Int",
    "int32": "Int32",
    "int16": "Int16",
    "short": "Short",
    "int8": "Int8",
    "uint": "UInt",
    "uint32": "UInt32",
    "uint16": "UInt16",
    "uint8": "UInt8",
    "uint64": "UInt64",
    "numeric": "Number",
    "text": "String",
    "utf": "Unicode",
    "utf8": "Unicode",
    "utf_8": "Unicode",
    "string": "Unicode",
    "str": "Unicode",
    "ascii": "String",
    "bool": "Bool",
    "isodatetime": "Datetime64",
    "AnyType": "Any",
    "object": "Object",
}

flat_to_np = {
    "float": float,
    "float32": np.float32,
    "double": np.double,
    "float64": np.float64,
    "long": np.longlong,
    "int64": np.int64,
    "int": int,
    "int32": np.int32,
    "int16": np.int16,
    "short": np.short,
    "int8": np.int8,
    "uint": np.uint,
    "uint32": np.uint32,
    "uint16": np.uint16,
    "uint8": np.uint8,
    "uint64": np.uint64,
    "numeric": np.number,
    "text": str,
    "utf": str,
    "utf8": str,
    "utf_8": str,
    "ascii": str,
    "bool": bool,
    "isodatetime": np.datetime64,
}

np_to_python = {
    Any: Any,
    np.number: float,
    np.object_: Any,
    np.bool_: bool,
    np.integer: int,
    np.byte: bytes,
    np.bytes_: bytes,
    np.datetime64: datetime,
    **{
        n: int
        for n in (
            np.int8,
            np.int16,
            np.int32,
            np.int64,
            np.short,
            np.uint8,
            np.uint16,
            np.uint32,
            np.uint64,
            np.uint,
        )
    },
    **{
        n: float
        for n in (
            np.float16,
            np.float32,
            np.floating,
            np.float32,
            np.float64,
            np.single,
            np.double,
            np.float_,
        )
    },
    **{n: str for n in (np.character, np.str_, np.string_, np.unicode_)},
}

allowed_precisions = {
    "float": ["double"],
    "int8": ["short", "int", "long", "int16", "int32", "int64"],
    "short": ["int", "long"],
    "int": ["long"],
    "uint8": ["uint8", "uint16", "uint32", "uint64"],
    "uint16": ["uint16", "uint32", "uint64"],
    "uint32": ["uint32", "uint64"],
    "float16": ["float16", "float32", "float64"],
    "float32": ["float32", "float64"],
    "utf": ["ascii"],
    "number": [
        "short",
        "int",
        "long",
        "int16",
        "int32",
        "int64",
        "uint",
        "uint8",
        "uint16",
        "uint32",
        "uint64",
        "float",
        "float16",
        "float32",
        "float64",
    ],
    "datetime64": ["object"],
}
"""
Following HDMF, it turns out that specifying precision actually specifies minimum precision
https://github.com/hdmf-dev/hdmf/blob/ddc842b5c81d96e0b957b96e88533b16c137e206/src/hdmf/validate/validator.py#L22
https://github.com/hdmf-dev/hdmf/blob/ddc842b5c81d96e0b957b96e88533b16c137e206/src/hdmf/spec/spec.py#L694-L714
"""


def struct_from_dtype(dtype: np.dtype) -> Type[nptyping.Structure]:
    """
    Create a nptyping Structure from a compound numpy dtype

    nptyping structures have the form::

        Structure["name: Str, age: Int"]

    """
    struct_pieces = [f"{k}: {flat_to_nptyping[v[0].name]}" for k, v in dtype.fields.items()]
    struct_dtype = ", ".join(struct_pieces)
    return nptyping.Structure[struct_dtype]


def handle_dtype(dtype: DTypeType | None) -> str:
    """
    Get the string form of a dtype

    Args:
        dtype (:class:`.DTypeType`): Dtype to stringify

    Returns:
        str
    """
    if isinstance(dtype, ReferenceDtype):
        return dtype.target_type
    elif dtype is None or dtype == []:
        # Some ill-defined datasets are "abstract" despite that not being in the schema language
        return "AnyType"
    elif isinstance(dtype, FlatDtype):
        return dtype.value
    elif isinstance(dtype, list) and isinstance(dtype[0], CompoundDtype):
        # there is precisely one class that uses compound dtypes:
        # TimeSeriesReferenceVectorData
        # compoundDtypes are able to define a ragged table according to the schema
        # but are used in this single case equivalently to attributes.
        # so we'll... uh... treat them as slots.
        # TODO
        return "AnyType"

    else:
        # flat dtype
        return dtype
