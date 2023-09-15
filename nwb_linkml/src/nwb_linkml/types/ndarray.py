"""
Extension of nptyping NDArray for pydantic that allows for JSON-Schema serialization

* Order to store data in (row first)
"""
import pdb
from typing import (
    Any,
    Callable,
    Annotated,
Generic,
TypeVar
)

from pydantic_core import core_schema
from pydantic import (
    BaseModel,
    GetJsonSchemaHandler,
    ValidationError,
    GetCoreSchemaHandler
)
from pydantic.json_schema import JsonSchemaValue

import numpy as np

from nptyping import NDArray as _NDArray
from nptyping.ndarray import NDArrayMeta
from nptyping import Shape, Number
from nptyping.shape_expression import check_shape

from nwb_linkml.maps.dtype import np_to_python

class NDArray(_NDArray):
    """
    Following the example here: https://docs.pydantic.dev/latest/usage/types/custom/#handling-third-party-types
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: _NDArray,
        _handler: Callable[[Any], core_schema.CoreSchema],

    ) -> core_schema.CoreSchema:

        shape, dtype = _source_type.__args__
        # get pydantic core schema for the given specified type
        array_type_handler = _handler.generate_schema(
            np_to_python[dtype])

        def validate_dtype(value: np.ndarray) -> np.ndarray:
            assert value.dtype == dtype, f"Invalid dtype! expected {dtype}, got {value.dtype}"
            return value
        def validate_array(value: Any) -> np.ndarray:
            assert cls.__instancecheck__(value), f'Invalid shape! expected shape {shape.prepared_args}, got shape {value.shape}'
            return value

        # get the names of the shape constraints, if any
        shape_parts = shape.__args__[0].split(',')
        split_parts = [p.split(' ')[1] if len(p.split(' ')) == 2 else None for p in shape_parts]


        # Construct a list of list schema
        # go in reverse order - construct list schemas such that
        # the final schema is the one that checks the first dimension
        shape_labels = reversed(split_parts)
        shape_args = reversed(shape.prepared_args)
        list_schema = None
        for arg, label in zip(shape_args, shape_labels):
            # which handler to use? for the first we use the actual type
            # handler, everywhere else we use the prior list handler
            if list_schema is None:
                inner_schema = array_type_handler
            else:
                inner_schema = list_schema

            # make a label annotation, if we have one
            if label is not None:
                metadata = {'name': label}
            else:
                metadata = None

            # make the current level list schema, accounting for shape
            if arg == '*':
                list_schema = core_schema.list_schema(inner_schema,
                                                      metadata=metadata)
            else:
                arg = int(arg)
                list_schema = core_schema.list_schema(
                    inner_schema,
                    min_length=arg,
                    max_length=arg,
                    metadata=metadata
                )


        return core_schema.json_or_python_schema(
            json_schema=list_schema,
            python_schema=core_schema.chain_schema(
                [
                    core_schema.is_instance_schema(np.ndarray),
                    core_schema.no_info_plain_validator_function(validate_dtype),
                    core_schema.no_info_plain_validator_function(validate_array)
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.tolist(),
                when_used='json'
            )
        )