"""
Maps to change the loaded .yaml from nwb schema before it's given to the nwb_schema_language models
"""

import ast
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar, List, Optional


class SCOPE_TYPES(StrEnum):
    namespace = "namespace"


class PHASES(StrEnum):
    postload = "postload"
    """After the YAML for a model has been loaded"""


@dataclass
class KeyMap:
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

    instances: ClassVar[List["KeyMap"]] = []
    """
    Maps that get defined!!!
    """

    def apply(self, input: dict) -> dict:
        """
        Change all keys from source to target in a super naive way.

        Convert the dictionary to a string. Do regex. parse ast
        """
        input_str = str(input)
        input_str = re.sub(self.source, self.target, input_str)
        out = ast.literal_eval(input_str)
        return out

    def __post_init__(self):
        self.instances.append(self)


MAP_HDMF_DATATYPE_DEF = KeyMap(
    source="'data_type_def'",
    target="'neurodata_type_def'",
    scope="hdmf-common",
    scope_type=SCOPE_TYPES.namespace,
    phase=PHASES.postload,
)

MAP_HDMF_DATATYPE_INC = KeyMap(
    source="'data_type_inc'",
    target="'neurodata_type_inc'",
    scope="hdmf-common",
    scope_type=SCOPE_TYPES.namespace,
    phase=PHASES.postload,
)


class MAP_TYPES(StrEnum):
    key = "key"
    """Mapping the name of one key to another key"""


def apply_postload(ns_dict) -> dict:
    maps = [m for m in KeyMap.instances if m.phase == PHASES.postload]
    for amap in maps:
        ns_dict = amap.apply(ns_dict)
    return ns_dict
