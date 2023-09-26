from dataclasses import dataclass
from typing import ClassVar, List, Optional
from enum import StrEnum
import ast
import re

class MAP_TYPES(StrEnum):
    key = 'key'
    """Mapping the name of one key to another key"""

class SCOPE_TYPES(StrEnum):
    namespace = 'namespace'

class PHASES(StrEnum):
    postload = "postload"
    """After the YAML for a model has been loaded"""



@dataclass
class Map:
    scope: str
    """The namespace that the map is relevant to"""
    scope_type: SCOPE_TYPES

    source: str
    """The path within the schema to select the element to transform"""
    target: str
    """The path where the element should end"""

    transform: Optional[callable] = None
    """
    Some transformation function, currently not implemented.
    """

    phase: Optional[PHASES] = None


    instances: ClassVar[List['Map']] = []
    """
    Maps that get defined!!!
    """

    def apply(self):
        raise NotImplementedError('do this in a subclass')

    def __post_init__(self):
        self.instances.append(self)



# def replace_keys(input: dict, source: str, target: str) -> dict:
#     """Recursively change keys in a dictionary"""


class KeyMap(Map):
    def apply(self, input: dict) -> dict:
        """
        Change all keys from source to target in a super naive way.

        Convert the dictionary to a string. Do regex. parse ast
        """
        input_str = str(input)
        input_str = re.sub(self.source, self.target, input_str)
        out = ast.literal_eval(input_str)
        return out


def apply_preload(ns_dict) -> dict:
    maps = [m for m in Map.instances if m.phase == PHASES.postload]
    for amap in maps:
        ns_dict = amap.apply(ns_dict)
    return ns_dict