"""
Abstract base classes for Map types

.. todo::
    Make this consistent or don't call them all maps lmao
"""

from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence


class Map(ABC):
    """
    The generic top-level mapping class is just a classmethod for checking if the map applies and a
    method for applying the check if it does
    """

    @classmethod
    @abstractmethod
    def check(cls, *args: Sequence, **kwargs: Mapping) -> bool:
        """Check if this map applies to the given item to read"""

    @classmethod
    @abstractmethod
    def apply(cls, *args: Sequence, **kwargs: Mapping) -> Any:
        """Actually apply the map!"""
