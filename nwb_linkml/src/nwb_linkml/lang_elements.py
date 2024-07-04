"""
Language elements in nwb schema language that have a fixed, alternative representation
in LinkML. These are exported as an nwb.language.yml file along with every generated namespace
"""

from linkml_runtime.linkml_model import (
    ClassDefinition,
    EnumDefinition,
    PermissibleValue,
    Prefix,
    SchemaDefinition,
    TypeDefinition,
)

from nwb_linkml.maps import flat_to_linkml
from nwb_schema_language.datamodel.nwb_schema_pydantic import FlatDtype as FlatDtype_source

FlatDType = EnumDefinition(
    name="FlatDType",
    permissible_values=[PermissibleValue(p) for p in FlatDtype_source.__members__],
)

DTypeTypes = []
for nwbtype, linkmltype in flat_to_linkml.items():
    # skip the dtypes that are the same as the builtin linkml types (which should already exist)
    # to avoid a recursion error
    if linkmltype == nwbtype:
        continue

    amin = None
    if nwbtype.startswith("uint"):
        amin = 0

    atype = TypeDefinition(name=nwbtype, minimum_value=amin, typeof=linkmltype)
    DTypeTypes.append(atype)

AnyType = ClassDefinition(
    name="AnyType",
    class_uri="linkml:Any",
    description="""Needed because some classes in hdmf-common are datasets without dtype""",
)


NwbLangSchema = SchemaDefinition(
    name="nwb.language",
    id="nwb.language",
    description="Adapter objects to mimic the behavior of elements in the nwb-schema-language",
    enums=[FlatDType],
    classes=[AnyType],
    types=DTypeTypes,
    imports=["linkml:types"],
    prefixes={"linkml": Prefix("linkml", "https://w3id.org/linkml")},
    annotations=[{"tag": "is_namespace", "value": False}, {"tag": "namespace", "value": ""}],
)
