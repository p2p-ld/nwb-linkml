"""
Language elements in nwb schema language that have a fixed, alternative representation
in LinkML. These are exported as an nwb.language.yml file along with every generated namespace
"""

from typing import List

from linkml_runtime.linkml_model import (
    ClassDefinition,
    Prefix,
    SchemaDefinition,
    TypeDefinition,
)

from nwb_linkml.maps import flat_to_linkml


def _make_dtypes() -> List[TypeDefinition]:
    DTypeTypes = []
    for nwbtype, linkmltype in flat_to_linkml.items():
        # skip the dtypes that are the same as the builtin linkml types (which should already exist)
        # to avoid a recursion error
        if linkmltype == nwbtype:
            continue

        amin = None
        if nwbtype.startswith("uint"):
            amin = 0

        # FIXME: Restore numpy types when we wrap them :)
        # np_type = flat_to_np[nwbtype]

        # repr_string = f"np.{np_type.__name__}" if np_type.__module__ == "numpy" else None

        atype = TypeDefinition(
            name=nwbtype,
            minimum_value=amin,
            typeof=linkmltype,  # repr=repr_string
        )
        DTypeTypes.append(atype)
    return DTypeTypes


DTypeTypes = _make_dtypes()

AnyType = ClassDefinition(
    name="AnyType",
    class_uri="linkml:Any",
    description="""Needed because some classes in hdmf-common are datasets without dtype""",
)


NwbLangSchema = SchemaDefinition(
    name="nwb.language",
    id="nwb.language",
    description="Adapter objects to mimic the behavior of elements in the nwb-schema-language",
    classes=[AnyType],
    types=DTypeTypes,
    imports=["linkml:types"],
    prefixes={"linkml": Prefix("linkml", "https://w3id.org/linkml")},
    annotations=[{"tag": "is_namespace", "value": False}, {"tag": "namespace", "value": ""}],
)
