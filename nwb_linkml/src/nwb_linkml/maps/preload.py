"""
Maps to change the loaded .yaml from nwb schema before it's given to the nwb_schema_language models
"""

from nwb_linkml.src.nwb_linkml.map import KeyMap, SCOPE_TYPES, PHASES

MAP_HDMF_DATATYPE_DEF = KeyMap(
    source="\'data_type_def\'",
    target="\'neurodata_type_def\'",
    scope='hdmf-common',
    scope_type=SCOPE_TYPES.namespace,
    phase=PHASES.postload
)

MAP_HDMF_DATATYPE_INC = KeyMap(
    source="\'data_type_inc\'",
    target="\'neurodata_type_inc\'",
    scope='hdmf-common',
    scope_type=SCOPE_TYPES.namespace,
    phase=PHASES.postload
)

