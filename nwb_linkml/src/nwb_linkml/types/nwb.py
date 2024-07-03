"""
Type annotations for NWB schema language types
"""

from typing import List, Union, TypeAlias

DIMS_LIST: TypeAlias = List[Union[str, None]]
"""A single-dimension dims specification"""

DIMS_TYPE: TypeAlias = Union[DIMS_LIST, List[DIMS_LIST]]
"""``dims`` in the nwb schema language"""

SHAPE_LIST: TypeAlias = List[Union[str, None]]
"""A single-dimension shape specification"""

SHAPE_TYPE: TypeAlias = Union[SHAPE_LIST, List[SHAPE_LIST]]
"""``shape`` in the nwb schema language"""
