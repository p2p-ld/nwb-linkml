"""
Dtype mappings
"""

from datetime import datetime
from typing import Any, Optional

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

linkml_reprs = {"numeric": "float | int"}
"""
``repr`` fields used in the nwb language elements injected in every namespace
that give the nwb type a specific representation in the generated pydantic models
"""

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

integer_types = {
    "long",
    "int64",
    "int",
    "int32",
    "int16",
    "short",
    "int8",
    "uint",
    "uint32",
    "uint16",
    "uint8",
    "uint64",
}

float_types = {"float", "float32", "double", "float64", "numeric"}

string_types = {"text", "utf", "utf8", "utf_8", "ascii"}


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
        )
    },
    **{n: str for n in (np.character, np.str_)},
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
        # Compound Dtypes are handled by the MapCompoundDtype dataset map,
        # but this function is also used within ``check`` methods, so we should always
        # return something from it rather than raise
        return "AnyType"

    else:
        # flat dtype
        return dtype


def inlined(dtype: DTypeType | None) -> Optional[bool]:
    """
    Check if a slot should be inlined based on its dtype

    for now that is equivalent to checking whether that dtype is another a reference dtype,
    but the function remains semantically reserved for answering this question w.r.t. dtype.

    Returns ``None`` if not inlined to not clutter generated models with unnecessary props
    """
    return (
        True
        if isinstance(dtype, ReferenceDtype)
        or (isinstance(dtype, CompoundDtype) and isinstance(dtype.dtype, ReferenceDtype))
        else None
    )
