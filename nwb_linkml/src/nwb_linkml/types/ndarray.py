"""
Extension of nptyping NDArray for pydantic that allows for JSON-Schema serialization

* Order to store data in (row first)
"""
import base64
import pdb
from pathlib import Path
from typing import (
    Any,
    Callable,
    Tuple
)
import sys
from copy import copy

from pydantic_core import core_schema
from pydantic import (
    BaseModel,
    GetJsonSchemaHandler,
    ValidationError,
    GetCoreSchemaHandler
)
from pydantic.json_schema import JsonSchemaValue

import numpy as np
import h5py
from dask.array.core import Array as DaskArray
import blosc2

from nptyping import NDArray as _NDArray
from nptyping.ndarray import NDArrayMeta as _NDArrayMeta
from nptyping import Shape, Number
from nptyping.nptyping_type import NPTypingType
from nptyping.shape_expression import check_shape

from nwb_linkml.maps.dtype import np_to_python, allowed_precisions


class NDArrayMeta(_NDArrayMeta, implementation="NDArray"):
    """
    Kept here to allow for hooking into metaclass, which has
    been necessary on and off as we work this class into a stable
    state"""

class NDArray(NPTypingType, metaclass=NDArrayMeta):
    """
    Following the example here: https://docs.pydantic.dev/latest/usage/types/custom/#handling-third-party-types
    """
    __args__ = (Any, Any)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: 'NDArray',
        _handler: Callable[[Any], core_schema.CoreSchema],

    ) -> core_schema.CoreSchema:

        shape, dtype = _source_type.__args__
        # get pydantic core schema for the given specified type
        array_type_handler = _handler.generate_schema(
            np_to_python[dtype])

        def validate_dtype(value: np.ndarray) -> np.ndarray:
            if dtype is Any:
                return value

            assert value.dtype == dtype or value.dtype.name in allowed_precisions[dtype.__name__], f"Invalid dtype! expected {dtype}, got {value.dtype}"
            return value
            
        def validate_shape(value: Any) -> np.ndarray:
            assert shape is Any or check_shape(value.shape, shape), f'Invalid shape! expected shape {shape.prepared_args}, got shape {value.shape}'
            return value

        def coerce_list(value: Any) -> np.ndarray:
            if isinstance(value, list):
                value = np.array(value)
            return value

        # get the names of the shape constraints, if any
        if shape is Any:
            list_schema = core_schema.list_schema(core_schema.any_schema())
        else:
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


        def array_to_list(instance: np.ndarray | DaskArray) -> list|dict:
            if isinstance(instance, DaskArray):
                arr = instance.__array__()
            elif isinstance(instance, NDArrayProxy):
                arr = instance[:]
            else:
                arr = instance

            # If we're larger than 16kB then compress array!
            if sys.getsizeof(arr) > 16 * 1024:
                packed = blosc2.pack_array2(arr)
                packed = base64.b64encode(packed)
                ret= {
                    'array': packed,
                    'shape': copy(arr.shape),
                    'dtype': copy(arr.dtype.name),
                    'unpack_fns': ['base64.b64decode', 'blosc2.unpack_array2']
                }
                return ret
            else:
                return arr.tolist()




        return core_schema.json_or_python_schema(
            json_schema=list_schema,
            python_schema=core_schema.chain_schema(
                [
                    core_schema.no_info_plain_validator_function(coerce_list),
                    core_schema.union_schema([
                        core_schema.is_instance_schema(cls=np.ndarray),
                        core_schema.is_instance_schema(cls=DaskArray),
                        core_schema.is_instance_schema(cls=NDArrayProxy)
                        ]),
                    core_schema.no_info_plain_validator_function(validate_dtype),
                    core_schema.no_info_plain_validator_function(validate_shape)
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                array_to_list,
                when_used='json'
            )
        )

class NDArrayProxy():
    """
    Thin proxy to numpy arrays stored within hdf5 files,
    only read into memory when accessed, but otherwise
    passthrough all attempts to access attributes.
    """
    def __init__(self, h5f_file: Path|str, path: str):
        """
        Args:
            h5f_file (:class:`pathlib.Path`): Path to source HDF5 file
            path (str): Location within HDF5 file where this array is located
        """
        self.h5f_file = Path(h5f_file)
        self.path = path

    def __getattr__(self, item):
        with h5py.File(self.h5f_file, 'r') as h5f:
            obj = h5f.get(self.path)
            return getattr(obj, item)
    def __getitem__(self, slice) -> np.ndarray:
        with h5py.File(self.h5f_file, 'r') as h5f:
            obj = h5f.get(self.path)
            return obj[slice]
    def __setitem__(self, slice, value):
        raise NotImplementedError(f"Cant write into an arrayproxy yet!")


    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: _NDArray,
        _handler: Callable[[Any], core_schema.CoreSchema],

    ) -> core_schema.CoreSchema:
        # return core_schema.no_info_after_validator_function(
        #     serialization=core_schema.plain_serializer_function_ser_schema(
        #         lambda instance: instance.tolist(),
        #         when_used='json'
        #     )
        # )

        return NDArray_.__get_pydantic_core_schema__(cls, _source_type, _handler)
