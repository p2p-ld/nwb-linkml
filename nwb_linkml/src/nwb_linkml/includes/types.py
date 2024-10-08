"""
Classes and types that are injected in generated pydantic modules, but have no
corresponding representation in linkml (ie. that don't belong in :mod:`.lang_elements`

Used to customize behavior of pydantic classes either to match pynwb behavior or
reduce the verbosity of the generated models with convenience classes.
"""

from typing import Annotated, Type, TypeVar, Union

from linkml.generators.pydanticgen.template import Import, Imports, ObjectImport
from pydantic import BaseModel, BeforeValidator, ValidationInfo

ModelType = TypeVar("ModelType", bound=Type[BaseModel])
# inspect.getsource() doesn't work for typevars because everything in the typing module
# doesn't behave like a normal python object
ModelTypeString = """ModelType = TypeVar("ModelType", bound=Type[BaseModel])"""


def _get_name(item: ModelType | dict, info: ValidationInfo) -> Union[ModelType, dict]:
    """Get the name of the slot that refers to this object"""
    assert isinstance(item, (BaseModel, dict)), f"{item} was not a BaseModel or a dict!"
    name = info.field_name
    if isinstance(item, BaseModel):
        item.name = name
    else:
        item["name"] = name
    return item


Named = Annotated[ModelType, BeforeValidator(_get_name)]
"""
Generic annotated type that sets the ``name`` field of a model 
to the name of the field with this type.

Examples:

    class ChildModel(BaseModel):
        name: str
        value: int

    class MyModel(BaseModel):
        named_field: Named[ChildModel]
        
    instance = MyModel(named_field={'value': 1})
    instance.named_field.name == "named_field"
"""
NamedString = """Named = Annotated[ModelType, BeforeValidator(_get_name)]"""

NamedImports = Imports(
    imports=[
        Import(
            module="typing",
            objects=[
                ObjectImport(name="Annotated"),
                ObjectImport(name="Type"),
                ObjectImport(name="TypeVar"),
            ],
        ),
        Import(
            module="pydantic",
            objects=[ObjectImport(name="ValidationInfo"), ObjectImport(name="BeforeValidator")],
        ),
    ]
)
