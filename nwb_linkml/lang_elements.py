"""
Language elements in nwb schema language that have a fixed, alternative representation
in LinkML. These are exported as an nwb.language.yml file along with every generated namespace
"""

from nwb_schema_language.datamodel.nwb_schema_pydantic import FlatDtype as FlatDtype_source
from linkml_runtime.linkml_model import \
    ClassDefinition, \
    EnumDefinition, \
    SchemaDefinition, \
    SlotDefinition, \
    TypeDefinition,\
    Prefix,\
    PermissibleValue
from nwb_linkml.maps.dtype import flat_to_linkml


FlatDType = EnumDefinition(
    name="FlatDType",
    permissible_values=[PermissibleValue(p) for p in FlatDtype_source.__members__.keys()],
)

DimNameSlot = SlotDefinition(
    name="dim_name",
    range="string",
    description="The name of a dimension"
)
DimShapeSlot = SlotDefinition(
    name="dim_shape",
    range="integer",
    required=False
)
DimClass = ClassDefinition(
    name="Dimension",
    slots=[DimNameSlot.name, DimShapeSlot.name],
    description="A single dimension within a shape"
)
DimSlot = SlotDefinition(
    name="dim",
    range=DimClass.name,
    multivalued=True,
    description="Slot representing the dimensions that a Shape can have"
)

# ShapeClass = ClassDefinition(
#     name="Shape",
#     description="A possible shape for an array-like dataset",
#     slots=[DimSlot.name]
# )

DTypeTypes = []
for nwbtype, linkmltype in flat_to_linkml.items():
    amin = None
    if nwbtype.startswith('uint'):
        amin = 0

    atype = TypeDefinition(
        name=nwbtype,
        minimum_value=amin,
        typeof=linkmltype
    )
    DTypeTypes.append(atype)


NwbLangSchema = SchemaDefinition(
    name="nwb.language",
    id='nwb.language',
    description="Adapter objects to mimic the behavior of elements in the nwb-schema-language",
    enums=[FlatDType],
    slots=[DimNameSlot, DimShapeSlot, DimSlot],
    classes=[DimClass],
    types=DTypeTypes,
    imports=['linkml:types'],
    prefixes={'linkml': Prefix('linkml','https://w3id.org/linkml')}
)

