"""
Monkeypatches to external modules
"""

# ruff: noqa: ANN001 - not well defined types for this module


def patch_schemaview() -> None:
    """
    Patch schemaview to correctly resolve multiple layers of relative imports.

    References:

    Returns:

    """
    from functools import lru_cache
    from typing import List

    from linkml_runtime.linkml_model import SchemaDefinitionName
    from linkml_runtime.utils.schemaview import SchemaView

    @lru_cache
    def imports_closure(
        self, imports: bool = True, traverse=True, inject_metadata=True
    ) -> List[SchemaDefinitionName]:
        """
        Return all imports

        :param traverse: if true, traverse recursively
        :return: all schema names in the transitive reflexive imports closure
        """
        if not imports:
            return [self.schema.name]
        if self.schema_map is None:
            self.schema_map = {self.schema.name: self.schema}
        closure = []
        visited = set()
        todo = [self.schema.name]
        if not traverse:
            return todo
        while len(todo) > 0:
            sn = todo.pop()
            visited.add(sn)
            if sn not in self.schema_map:
                imported_schema = self.load_import(sn)
                self.schema_map[sn] = imported_schema
            s = self.schema_map[sn]
            if sn not in closure:
                closure.append(sn)
            for i in s.imports:
                if sn.startswith(".") and ":" not in i:
                    # prepend the relative part
                    i = "/".join(sn.split("/")[:-1]) + "/" + i
                if i not in visited:
                    todo.append(i)
        if inject_metadata:
            for s in self.schema_map.values():
                for x in {**s.classes, **s.enums, **s.slots, **s.subsets, **s.types}.values():
                    x.from_schema = s.id
                for c in s.classes.values():
                    for a in c.attributes.values():
                        a.from_schema = s.id
        return closure

    SchemaView.imports_closure = imports_closure


def patch_array_expression() -> None:
    """
    Allow SlotDefinitions to use `any_of` with `array`

    see: https://github.com/linkml/linkml-model/issues/199
    """
    from dataclasses import field, make_dataclass
    from typing import Optional

    from linkml_runtime.linkml_model import meta

    new_dataclass = make_dataclass(
        "AnonymousSlotExpression",
        fields=[("array", Optional[meta.ArrayExpression], field(default=None))],
        bases=(meta.AnonymousSlotExpression,),
    )
    meta.AnonymousSlotExpression = new_dataclass


def patch_pretty_print() -> None:
    """
    Fix the godforsaken linkml dataclass reprs

    See: https://github.com/linkml/linkml-runtime/pull/314
    """
    import re
    import textwrap
    from dataclasses import field, is_dataclass, make_dataclass
    from pprint import pformat
    from typing import Any

    from linkml_runtime.linkml_model import meta
    from linkml_runtime.utils.formatutils import items

    def _pformat(fields: dict, cls_name: str, indent: str = "  ") -> str:
        """
        pretty format the fields of the items of a ``YAMLRoot`` object without the wonky
        indentation of pformat.
        see ``YAMLRoot.__repr__``.
        formatting is similar to black - items at similar levels of nesting have similar levels
        of indentation,
        rather than getting placed at essentially random levels of indentation depending on what
        came before them.
        """
        res = []
        total_len = 0
        for key, val in fields:
            if val == [] or val == {} or val is None:
                continue
            # pformat handles everything else that isn't a YAMLRoot object,
            # but it sure does look ugly
            # use it to split lines and as the thing of last resort, but otherwise indent = 0,
            # we'll do that
            val_str = pformat(val, indent=0, compact=True, sort_dicts=False)
            # now we indent everything except the first line by indenting
            # and then using regex to remove just the first indent
            val_str = re.sub(rf"\A{re.escape(indent)}", "", textwrap.indent(val_str, indent))
            # now recombine with the key in a format that can be re-eval'd
            # into an object if indent is just whitespace
            val_str = f"'{key}': " + val_str

            # count the total length of this string so we know if we need to linebreak or not later
            total_len += len(val_str)
            res.append(val_str)

        if total_len > 80:
            inside = ",\n".join(res)
            # we indent twice - once for the inner contents of every inner object, and one to
            # offset from the root element.
            # that keeps us from needing to be recursive except for the
            # single pformat call
            inside = textwrap.indent(inside, indent)
            return cls_name + "({\n" + inside + "\n})"
        else:
            return cls_name + "({" + ", ".join(res) + "})"

    def __repr__(self) -> str:
        return _pformat(items(self), self.__class__.__name__)

    for cls_name in dir(meta):
        cls = getattr(meta, cls_name)
        if is_dataclass(cls):
            new_dataclass = make_dataclass(
                cls.__name__,
                fields=[("__dummy__", Any, field(default=None))],
                bases=(cls,),
                repr=False,
            )
            new_dataclass.__repr__ = __repr__
            new_dataclass.__str__ = __repr__
            setattr(meta, cls.__name__, new_dataclass)


def apply_patches() -> None:
    """Apply all monkeypatches"""
    patch_schemaview()
    patch_array_expression()
    patch_pretty_print()
