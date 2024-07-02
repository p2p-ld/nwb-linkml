"""
Monkeypatches to external modules
"""


def patch_npytyping_perf():
    """
    npytyping makes an expensive call to inspect.stack()
    that makes imports of pydantic models take ~200x longer than
    they should:

    References:
        - https://github.com/ramonhagenaars/nptyping/issues/110
    """
    import inspect
    from types import FrameType

    from nptyping import base_meta_classes, ndarray, recarray
    from nptyping.pandas_ import dataframe

    # make a new __module__ methods for the affected classes
    def new_module_ndarray(cls) -> str:
        return cls._get_module(inspect.currentframe(), "nptyping.ndarray")

    def new_module_recarray(cls) -> str:
        return cls._get_module(inspect.currentframe(), "nptyping.recarray")

    def new_module_dataframe(cls) -> str:
        return cls._get_module(inspect.currentframe(), "nptyping.pandas_.dataframe")

    # and a new _get_module method for the parent class
    def new_get_module(cls, stack: FrameType, module: str) -> str:
        return (
            "typing"
            if inspect.getframeinfo(stack.f_back).function == "formatannotation"
            else module
        )

    # now apply the patches
    ndarray.NDArrayMeta.__module__ = property(new_module_ndarray)
    recarray.RecArrayMeta.__module__ = property(new_module_recarray)
    dataframe.DataFrameMeta.__module__ = property(new_module_dataframe)
    base_meta_classes.SubscriptableMeta._get_module = new_get_module


def patch_nptyping_warnings():
    """
    nptyping shits out a bunch of numpy deprecation warnings from using
    olde aliases
    """
    import warnings

    warnings.filterwarnings("ignore", category=DeprecationWarning, module="nptyping.*")


def patch_schemaview():
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


def apply_patches():
    patch_npytyping_perf()
    patch_nptyping_warnings()
    patch_schemaview()
