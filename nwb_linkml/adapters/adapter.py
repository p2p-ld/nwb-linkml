"""
Base class for adapters
"""
from abc import abstractmethod
import warnings
from dataclasses import dataclass, field
from typing import List, Dict, Type, Generator, Any, Tuple, Optional, TypeVar, TypeVarTuple, Unpack
from pydantic import BaseModel, Field, validator
from linkml_runtime.linkml_model import Element, SchemaDefinition, ClassDefinition, SlotDefinition, TypeDefinition

# SchemaDefClass = dataclass(SchemaDefinition).__pydantic_model__

@dataclass
class BuildResult:
    # pass
    schemas: List[SchemaDefinition] = field(default_factory=list)
    classes: List[ClassDefinition] = field(default_factory=list)
    slots: List[SlotDefinition] = field(default_factory=list)
    types: List[TypeDefinition] = field(default_factory=list)

    def __post_init__(self):
        for field in ('schemas', 'classes', 'slots', 'types'):
            attr = getattr(self, field)
            if not isinstance(attr, list):
                setattr(self, field, [attr])

    def _dedupe(self, ours, others):
        existing_names = [c.name for c in ours]
        others_dedupe = [o for o in others if o.name not in existing_names]
        return others_dedupe

    def __add__(self, other:'BuildResult') -> 'BuildResult':
        # if not isinstance(other, 'BuildResult'):
        #     raise TypeError('Can only add two build results together')

        self.schemas.extend(self._dedupe(self.schemas, other.schemas))
        self.classes.extend(self._dedupe(self.classes, other.classes))
        # existing_names = [c.name for c in self.classes]
        # for newc in other.classes:
        #     if newc.name in existing_names:
        #         warnings.warn(f'Not creating duplicate class for {newc.name}')
        #         continue
        #     self.classes.append(newc)
        # self.classes.extend(other.classes)
        self.slots.extend(other.slots)
        self.types.extend(other.types)
        return self

T = TypeVar
Ts = TypeVarTuple('Ts')

class Adapter(BaseModel):
    @abstractmethod
    def build(self) -> 'BuildResult':
        """
        Generate the corresponding linkML element for this adapter
        """

    def walk(self, input: BaseModel | list | dict):
        yield input
        if isinstance(input, BaseModel):
            for key in input.__fields__.keys():
                val = getattr(input, key)
                yield (key, val)
                if isinstance(val, (BaseModel, dict, list)):
                    yield from self.walk(val)

        elif isinstance(input, dict):
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

    def walk_fields(self, input: BaseModel | list | dict, field: str | Tuple[str, ...]):
        if isinstance(field, str):
            field = (field,)
        for item in self.walk(input):
            if isinstance(item, tuple) and item[0] in field and item[1] is not None:
                yield item[1]


    def walk_types(self, input: BaseModel | list | dict, get_type: T | List[Unpack[Ts]] | Tuple[Unpack[T]]) -> Generator[T, None, None]:
        if not isinstance(get_type, (list, tuple)):
            get_type = [get_type]

        for item in self.walk(input):
            if any([type(item) == atype for atype in get_type]):
                yield item

    #
    #
    # if isinstance(input, BaseModel):
    #     for key in input.__fields__.keys():
    #         val = getattr(input, key)
    #         if key == field:
    #             yield val
    #         if isinstance(val, (BaseModel, dict, list)):
    #             yield from self.walk(val, field)
    #
    # elif isinstance(input, dict):
    #     for key, val in input.items():
    #         if key == field:
    #             yield val
    #         if isinstance(val, (BaseModel, dict, list)):
    #             yield from self.walk(val, field)
    #
    # elif isinstance(input, (list, tuple)):
    #     for val in input:
    #         yield from self.walk(val, field)
    #
    # else:
    #     # do nothing, is a string or whatever
    #     pass
