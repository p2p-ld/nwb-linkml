from typing import Any
from abc import ABC, abstractmethod


class Map(ABC):
    """
    The generic top-level mapping class is just a classmethod for checking if the map applies and a
    method for applying the check if it does
    """

    @classmethod
    @abstractmethod
    def check(cls, *args, **kwargs) -> bool:
        """Check if this map applies to the given item to read"""

    @classmethod
    @abstractmethod
    def apply(cls, *args, **kwargs) -> Any:
        """Actually apply the map!"""


