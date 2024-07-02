"""
Types used with hdf5 io
"""

from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class HDF5_Path(str):
    """
    Trivial subclass of string to indicate that it is a reference to a location within an HDF5 file
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))
