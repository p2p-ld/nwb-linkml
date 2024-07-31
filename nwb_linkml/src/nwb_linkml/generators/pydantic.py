"""
Subclass of :class:`linkml.generators.PydanticGenerator`

The pydantic generator is a subclass of
- :class:`linkml.utils.generator.Generator`
- :class:`linkml.generators.oocodegen.OOCodeGenerator`

The default `__main__` method
- Instantiates the class
- Calls :meth:`~linkml.generators.PydanticGenerator.serialize`

The `serialize` method:

- Accepts an optional jinja-style template, otherwise it uses the default template
- Uses :class:`linkml_runtime.utils.schemaview.SchemaView` to interact with the schema
- Generates linkML Classes
    - `generate_enums` runs first

.. note::

    This module is heinous. We have mostly copied and pasted the existing :class:`linkml.generators.PydanticGenerator`
    and overridden what we need to make this work for NWB, but the source is...
    a little messy. We will be tidying this up and trying to pull changes upstream,
    but for now this is just our hacky little secret.

"""

# FIXME: Remove this after we refactor this generator
# ruff: noqa

import inspect
import pdb
import re
import sys
import warnings
from copy import copy
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import ClassVar, Dict, List, Optional, Tuple, Type, Union

from linkml.generators import PydanticGenerator
from linkml.generators.pydanticgen.build import SlotResult, ClassResult
from linkml.generators.pydanticgen.array import ArrayRepresentation, NumpydanticArray
from linkml.generators.pydanticgen.template import PydanticModule, Import, Imports
from linkml_runtime.linkml_model.meta import (
    Annotation,
    AnonymousSlotExpression,
    ArrayExpression,
    ClassDefinition,
    ClassDefinitionName,
    ElementName,
    SchemaDefinition,
    SlotDefinition,
    SlotDefinitionName,
)
from linkml_runtime.utils.compile_python import file_text
from linkml_runtime.utils.formatutils import camelcase, underscore, remove_empty_items
from linkml_runtime.utils.schemaview import SchemaView

from pydantic import BaseModel

from nwb_linkml.maps import flat_to_nptyping
from nwb_linkml.maps.naming import module_case, version_module_case
from nwb_linkml.includes.types import ModelTypeString, _get_name, NamedString, NamedImports
from nwb_linkml.includes.hdmf import DYNAMIC_TABLE_IMPORTS, DYNAMIC_TABLE_INJECTS

OPTIONAL_PATTERN = re.compile(r"Optional\[([\w\.]*)\]")


@dataclass
class NWBPydanticGenerator(PydanticGenerator):

    injected_fields: List[str] = (
        (
            'hdf5_path: Optional[str] = Field(None, description="The absolute path that this object'
            ' is stored in an NWB file")'
        ),
        'object_id: Optional[str] = Field(None, description="Unique UUID for each object")',
    )
    split: bool = True
    imports: list[Import] = field(default_factory=lambda: [Import(module="numpy", alias="np")])

    schema_map: Optional[Dict[str, SchemaDefinition]] = None
    """See :meth:`.LinkMLProvider.build` for usage - a list of specific versions to import from"""
    array_representations: List[ArrayRepresentation] = field(
        default_factory=lambda: [ArrayRepresentation.NUMPYDANTIC]
    )
    black: bool = True
    inlined: bool = True
    emit_metadata: bool = True
    gen_classvars: bool = True
    gen_slots: bool = True

    skip_meta: ClassVar[Tuple[str]] = ("domain_of", "alias")

    def _check_anyof(
        self, s: SlotDefinition, sn: SlotDefinitionName, sv: SchemaView
    ):  # pragma: no cover
        """
        Overridden to allow `array` in any_of
        """
        # Confirm that the original slot range (ignoring the default that comes in from
        # induced_slot) isn't in addition to setting any_of
        allowed_keys = ("array",)

        if len(s.any_of) > 0 and sv.get_slot(sn).range is not None:
            allowed = True
            for option in s.any_of:
                items = remove_empty_items(option)
                if not all([key in allowed_keys for key in items.keys()]):
                    allowed = False
            if allowed:
                return
            base_range_subsumes_any_of = False
            base_range = sv.get_slot(sn).range
            base_range_cls = sv.get_class(base_range, strict=False)
            if base_range_cls is not None and base_range_cls.class_uri == "linkml:Any":
                base_range_subsumes_any_of = True
            if not base_range_subsumes_any_of:
                raise ValueError("Slot cannot have both range and any_of defined")

    def after_generate_slot(self, slot: SlotResult, sv: SchemaView) -> SlotResult:
        """
        - strip unwanted metadata
        - generate range with any_of
        """
        slot = AfterGenerateSlot.skip_meta(slot, self.skip_meta)
        slot = AfterGenerateSlot.make_array_anyofs(slot)
        slot = AfterGenerateSlot.make_named_class_range(slot)

        return slot

    def after_generate_class(self, cls: ClassResult, sv: SchemaView) -> ClassResult:
        cls = AfterGenerateClass.inject_dynamictable(cls)
        return cls

    def before_render_template(self, template: PydanticModule, sv: SchemaView) -> PydanticModule:
        if "source_file" in template.meta:
            del template.meta["source_file"]
        return template

    def compile_module(
        self, module_path: Path = None, module_name: str = "test", **kwargs
    ) -> ModuleType:  # pragma: no cover - replaced with provider
        """
        Compiles generated python code to a module
        :return:
        """
        pycode = self.serialize(**kwargs)
        if module_path is not None:
            module_path = Path(module_path)
            init_file = module_path / "__init__.py"
            with open(init_file, "w") as ifile:
                ifile.write(" ")

        try:
            return compile_python(pycode, module_path, module_name)
        except NameError as e:
            raise e


class AfterGenerateSlot:
    """
    Container class for slot-modification methods
    """

    @staticmethod
    def skip_meta(slot: SlotResult, skip_meta: tuple[str]) -> SlotResult:
        for key in skip_meta:
            if key in slot.attribute.meta:
                del slot.attribute.meta[key]
        return slot

    @staticmethod
    def make_array_anyofs(slot: SlotResult) -> SlotResult:
        """
        Make a Union of array ranges if multiple array types specified in ``any_of``
        """
        # make array ranges in any_of
        if "any_of" in slot.attribute.meta:
            any_ofs = slot.attribute.meta["any_of"]
            if all(["array" in expr for expr in any_ofs]):
                ranges = []
                is_optional = False
                for expr in any_ofs:
                    # remove optional from inner type
                    pyrange = slot.attribute.range
                    is_optional = OPTIONAL_PATTERN.match(pyrange)
                    if is_optional:
                        pyrange = is_optional.groups()[0]
                    range_generator = NumpydanticArray(ArrayExpression(**expr["array"]), pyrange)
                    ranges.append(range_generator.make().range)

                slot.attribute.range = "Union[" + ", ".join(ranges) + "]"
                if is_optional:
                    slot.attribute.range = "Optional[" + slot.attribute.range + "]"
                del slot.attribute.meta["any_of"]

                # merge injects/imports from the numpydantic array without using the merge method
                if slot.injected_classes is None:
                    slot.injected_classes = NumpydanticArray.INJECTS.copy()
                else:
                    slot.injected_classes.extend(NumpydanticArray.INJECTS.copy())
                if isinstance(slot.imports, list):
                    slot.imports = (
                        Imports(imports=slot.imports) + NumpydanticArray.IMPORTS.model_copy()
                    )
                elif isinstance(slot.imports, Imports):
                    slot.imports += NumpydanticArray.IMPORTS.model_copy()
                else:
                    slot.imports = NumpydanticArray.IMPORTS.model_copy()

        return slot

    @staticmethod
    def make_named_class_range(slot: SlotResult) -> SlotResult:
        """
        When a slot has a ``named`` annotation, wrap it in :class:`.Named`
        """

        if "named" in slot.source.annotations and slot.source.annotations["named"].value:
            slot.attribute.range = f"Named[{slot.attribute.range}]"
            named_injects = [ModelTypeString, _get_name, NamedString]
            if slot.injected_classes is None:
                slot.injected_classes = named_injects
            else:
                slot.injected_classes.extend([ModelTypeString, _get_name, NamedString])
            if isinstance(slot.imports, list):
                slot.imports = Imports(imports=slot.imports) + NamedImports
            elif isinstance(slot.imports, Imports):
                slot.imports += NamedImports
            else:
                slot.imports = NamedImports
        return slot


class AfterGenerateClass:
    """
    Container class for class-modification methods
    """

    @staticmethod
    def inject_dynamictable(cls: ClassResult) -> ClassResult:
        if cls.cls.name == "DynamicTable":
            cls.cls.bases = ["DynamicTableMixin"]

            if cls.injected_classes is None:
                cls.injected_classes = DYNAMIC_TABLE_INJECTS.copy()
            else:
                cls.injected_classes.extend(DYNAMIC_TABLE_INJECTS.copy())

            if isinstance(cls.imports, Imports):
                cls.imports += DYNAMIC_TABLE_IMPORTS
            elif isinstance(cls.imports, list):
                cls.imports = Imports(imports=cls.imports) + DYNAMIC_TABLE_IMPORTS
            else:
                cls.imports = DYNAMIC_TABLE_IMPORTS.model_copy()
        elif cls.cls.name == "VectorData":
            cls.cls.bases = ["VectorDataMixin"]
        elif cls.cls.name == "VectorIndex":
            cls.cls.bases = ["VectorIndexMixin"]
        return cls


def compile_python(
    text_or_fn: str, package_path: Path = None, module_name: str = "test"
) -> ModuleType:
    """
    Compile the text or file and return the resulting module
    @param text_or_fn: Python text or file name that references python file
    @param package_path: Root package path.  If omitted and we've got a python file, the package is the containing
    directory
    @return: Compiled module
    """
    python_txt = file_text(text_or_fn)
    if package_path is None and python_txt != text_or_fn:
        package_path = Path(text_or_fn)
    spec = compile(python_txt, "<string>", "exec")
    module = ModuleType(module_name)

    exec(spec, module.__dict__)
    sys.modules[module_name] = module
    return module
