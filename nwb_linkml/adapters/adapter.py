"""
Base class for adapters
"""
from typing import List, Dict, Type, Generator, Any, Tuple
from pydantic import BaseModel

class Adapter(BaseModel):
    pass

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

    def walk_fields(self, input: BaseModel | list | dict, field: str):
        for item in self.walk(input):
            if isinstance(item, tuple) and item[0] == field and item[1] is not None:
                yield item[1]


    def walk_types(self, input: BaseModel | list | dict, get_type: Type | List[Type] | Tuple[Type]):
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
