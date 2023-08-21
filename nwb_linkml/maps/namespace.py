"""
Practice translation of namespaces to linkml just as a warmup to
see what kind of operations we'll need

Notes:
    - Handling "namespace" imports within namespaces separately as prefixes
"""
from typing import List
from dataclasses import dataclass


from nwb_schema_language import Namespace
from linkml.utils.schema_builder import SchemaBuilder

from linkml_runtime.linkml_model import SchemaDefinition



# top-level attributes
def build_schema(namespace: Namespace) -> SchemaDefinition:
    return SchemaDefinition(
        id=namespace.name,
        name=namespace.name,
        title=namespace.full_name,
        version=namespace.version,
        imports=[schema.source for schema in namespace.schema_ if schema.source is not None]
    )


