"""
Base class for adapters
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any,
    Generator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    TypeVarTuple,
    Union,
    Unpack,
)

from linkml_runtime.linkml_model import (
    ClassDefinition,
    Definition,
    SchemaDefinition,
    SlotDefinition,
    TypeDefinition,
)
from pydantic import BaseModel

from nwb_schema_language import Attribute, Dataset, Group, Schema

T = TypeVar("T", Dataset, Attribute, Schema, Group, BaseModel)
Ts = TypeVarTuple("Ts")
Td = TypeVar("Td", bound=Union[Definition, SchemaDefinition, TypeDefinition])


@dataclass
class BuildResult:
    """
    Container class for propagating nested build results back up to caller
    """

    schemas: List[SchemaDefinition] = field(default_factory=list)
    classes: List[ClassDefinition] = field(default_factory=list)
    slots: List[SlotDefinition] = field(default_factory=list)
    types: List[TypeDefinition] = field(default_factory=list)

    def __post_init__(self):
        for a_field in ("schemas", "classes", "slots", "types"):
            attr = getattr(self, a_field)
            if not isinstance(attr, list):
                setattr(self, a_field, [attr])

    def _dedupe(self, ours: List[Td], others: List[Td]) -> List[Td]:
        existing_names = [c.name for c in ours]
        others_dedupe = [o for o in others if o.name not in existing_names]
        return others_dedupe

    def __add__(self, other: "BuildResult") -> "BuildResult":
        # if not isinstance(other, 'BuildResult'):
        #     raise TypeError('Can only add two build results together')

        self.schemas.extend(self._dedupe(self.schemas, other.schemas))
        self.classes.extend(self._dedupe(self.classes, other.classes))
        self.slots.extend(self._dedupe(self.slots, other.slots))
        self.types.extend(self._dedupe(self.types, other.types))
        return self

    def __repr__(self):  # pragma: no cover
        out_str = "\nBuild Result:\n"
        out_str += "-" * len(out_str)

        for label, alist in (
            ("Schemas", self.schemas),
            ("Classes", self.classes),
            ("Slots", self.slots),
            ("Types", self.types),
        ):
            if len(alist) == 0:
                continue

            name_str = "\n\n" + label + ":"
            name_str += "\n" + "-" * len(name_str) + "\n"
            name_list = sorted([i.name for i in alist])
            item_str = "\n ".join(name_list)
            out_str += name_str + item_str

        return out_str


class Adapter(BaseModel):
    """Abstract base class for adapters"""

    @abstractmethod
    def build(self) -> "BuildResult":
        """
        Generate the corresponding linkML element for this adapter
        """

    def walk(self, input: BaseModel | list | dict) -> Generator[BaseModel | Any | None, None, None]:
        """
        Iterate through all items in the given model.

        Could be a staticmethod or a function, but bound to adapters to make it available to them :)
        """

        yield input
        if isinstance(input, BaseModel):

            for key in input.model_fields:
                # Special case where SchemaAdapter Imports are themselves
                # SchemaAdapters that should be located under the same
                # NamespacesAdapter when it's important to query across SchemaAdapters,
                # so skip to avoid combinatoric walking
                if key == "imports" and type(input).__name__ == "SchemaAdapter":
                    continue
                val = getattr(input, key)
                yield (key, val)
                if isinstance(val, (BaseModel, dict, list)):
                    yield from self.walk(val)

        elif isinstance(
            input, dict
        ):  # pragma: no cover - not used in our adapters, but necessary for logical completeness
            for key, val in input.items():
                yield (key, val)
                if isinstance(val, (BaseModel, dict, list)):
                    yield from self.walk(val)

        elif isinstance(input, (list, tuple)):
            yield input
            for val in input:
                yield from self.walk(val)

        else:
            # do nothing, is a string or whatever
            pass

    def walk_fields(
        self, input: BaseModel | list | dict, field: str | Tuple[str, ...]
    ) -> Generator[Any, None, None]:
        """
        Recursively walk input for fields that match ``field``

        Args:
            input (:class:`pydantic.BaseModel`) : Model to walk (or a list or dictionary
                to walk too)
            field (str, Tuple[str, ...]):

        Returns:

        """
        if isinstance(field, str):
            field = (field,)
        for item in self.walk(input):
            if isinstance(item, tuple) and item[0] in field and item[1] is not None:
                yield item[1]

    def walk_field_values(
        self, input: BaseModel | list | dict, field: str, value: Optional[Any] = None
    ) -> Generator[BaseModel, None, None]:
        """
        Recursively walk input for **models** that contain a ``field`` as a direct child
        with a value matching ``value``

        Args:
            input (:class:`pydantic.BaseModel`): Model to walk
            field (str): Name of field - unlike :meth:`.walk_fields`, only one field can be given
            value (Any): Value to match for given field. If ``None`` ,
                return models that have the field

        Returns:
            :class:`pydantic.BaseModel` the matching model
        """
        for item in self.walk(input):
            if isinstance(item, BaseModel) and field in item.model_fields:
                if value is None:
                    yield item
                field_value = item.model_dump().get(field, None)
                if value == field_value:
                    yield item

    def walk_types(
        self, input: BaseModel | list | dict, get_type: Type[T] | Tuple[Type[T], Type[Unpack[Ts]]]
    ) -> Generator[T | Ts, None, None]:
        """
        Walk a model, yielding items that are the same type as the given type

        Args:
            input (:class:`pydantic.BaseModel`, list, dict): Object to yield from
            get_type (:class:`~typing.Type`, tuple[:class:`~typing.Type`]): Type to match
        """
        if not isinstance(get_type, (list, tuple)):
            get_type = [get_type]

        for item in self.walk(input):
            if any([type(item) == atype for atype in get_type]):
                yield item
