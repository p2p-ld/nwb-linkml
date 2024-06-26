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
import sys
import warnings
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional, Tuple, Type

from jinja2 import Template
from linkml.generators import PydanticGenerator
from linkml.generators.common.type_designators import (
    get_type_designator_value,
)
from linkml.utils.ifabsent_functions import ifabsent_value_declaration
from linkml_runtime.linkml_model.meta import (
    Annotation,
    ClassDefinition,
    ClassDefinitionName,
    ElementName,
    SchemaDefinition,
    SlotDefinition,
    SlotDefinitionName,
)
from linkml_runtime.utils.compile_python import file_text
from linkml_runtime.utils.formatutils import camelcase, underscore
from linkml_runtime.utils.schemaview import SchemaView
from pydantic import BaseModel

from nwb_linkml.maps import flat_to_nptyping
from nwb_linkml.maps.naming import module_case, version_module_case


class LinkML_Meta(BaseModel):
    """Extra LinkML Metadata stored as a class attribute"""

    tree_root: bool = False


def default_template(
    pydantic_ver: str = "2", extra_classes: Optional[List[Type[BaseModel]]] = None
) -> str:
    """Constructs a default template for pydantic classes based on the version of pydantic"""
    ### HEADER ###
    template = """
{#-

  Jinja2 Template for a pydantic classes
-#}
from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import Dict, Optional, Any, Union, ClassVar, Annotated, TypeVar, List, TYPE_CHECKING
from pydantic import BaseModel as BaseModel, Field"""
    if pydantic_ver == "2":
        template += """
from pydantic import ConfigDict, BeforeValidator
        """
    template += """
from nptyping import Shape, Float, Float32, Double, Float64, LongLong, Int64, Int, Int32, Int16, Short, Int8, UInt, UInt32, UInt16, UInt8, UInt64, Number, String, Unicode, Unicode, Unicode, String, Bool, Datetime64
from nwb_linkml.types import NDArray
import sys
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal
if TYPE_CHECKING:
    import numpy as np

{% for import_module, import_classes in imports.items() %}
from {{ import_module }} import (
    {{ import_classes | join(',\n    ') }}
)
{% endfor %}

metamodel_version = "{{metamodel_version}}"
version = "{{version if version else None}}"
"""
    ### BASE MODEL ###
    if pydantic_ver == "1":  # pragma: no cover
        template += """
List = BaseList
        
class WeakRefShimBaseModel(BaseModel):
   __slots__ = '__weakref__'

class ConfiguredBaseModel(WeakRefShimBaseModel,
                validate_assignment = False,
                validate_all = True,
                underscore_attrs_are_private = True,
                extra = {% if allow_extra %}'allow'{% else %}'forbid'{% endif %},
                arbitrary_types_allowed = True,
                use_enum_values = True):
"""
    else:
        template += """
class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = {% if allow_extra %}'allow'{% else %}'forbid'{% endif %},
        arbitrary_types_allowed = True,
        use_enum_values = True
    )
"""
    ### Injected Fields
    template += """
{%- if injected_fields != None -%}
    {% for field in injected_fields %}
    {{ field }}
    {% endfor %}
{%- else -%}
    pass
{%- endif -%}
    """
    ### Getitem
    template += """
    
    def __getitem__(self, i: slice|int) -> 'np.ndarray':
        if hasattr(self, 'array'):
            return self.array[i]
        else:
            return super().__getitem__(i)
            
    def __setitem__(self, i: slice|int, value: Any):
        if hasattr(self, 'array'):
            self.array[i] = value
        else:
            super().__setitem__(i, value)
    """

    ### Extra classes
    if extra_classes is not None:
        template += """{{ '\n\n' }}"""
        for cls in extra_classes:
            template += inspect.getsource(cls) + "\n\n"

    ### ENUMS ###
    template += """
{% for e in enums.values() %}
class {{ e.name }}(str, Enum):
    {% if e.description -%}
    \"\"\"
    {{ e.description }}
    \"\"\"
    {%- endif %}
    {% for _, pv in e['values'].items() -%}
    {% if pv.description -%}
    # {{pv.description}}
    {%- endif %}
    {{pv.label}} = "{{pv.value}}"
    {% endfor %}
    {% if not e['values'] -%}
    dummy = "dummy"
    {% endif %}
{% endfor %}
"""
    ### CLASSES ###
    template += """
{%- for c in schema.classes.values() %}
class {{ c.name }}
    {%- if class_isa_plus_mixins[c.name] -%}
        ({{class_isa_plus_mixins[c.name]|join(', ')}})
    {%- else -%}
        (ConfiguredBaseModel)
    {%- endif -%}
                  :
    {% if c.description -%}
    \"\"\"
    {{ c.description }}
    \"\"\"
    {%- endif %}
    {% for attr in c.attributes.values() if c.attributes -%}
    {{attr.name}}:{{ ' ' }}{%- if attr.equals_string -%}
        Literal[{{ predefined_slot_values[c.name][attr.name] }}]
        {%- else -%}
        {{ attr.annotations['python_range'].value }}
        {%- endif -%}
        {%- if attr.annotations['fixed_field'] -%}
        {{ ' ' }}= {{ attr.annotations['fixed_field'].value }}
        {%- else -%}
        {{ ' ' }}= Field(
    {%- if predefined_slot_values[c.name][attr.name] is string -%}
        {{ predefined_slot_values[c.name][attr.name] }}
    {%- elif attr.required -%}
        ...
    {%- else -%}
        None
    {%- endif -%}
    {%- if attr.title != None %}, title="{{attr.title}}"{% endif -%}
    {%- if attr.description %}, description=\"\"\"{{attr.description}}\"\"\"{% endif -%}
    {%- if attr.minimum_value != None %}, ge={{attr.minimum_value}}{% endif -%}
    {%- if attr.maximum_value != None %}, le={{attr.maximum_value}}{% endif -%}
    )
    {%- endif %}
    {% else -%}
    None
    {% endfor %}
{% endfor %}
"""
    ### FWD REFS / REBUILD MODEL ###
    if pydantic_ver == "1":  # pragma: no cover
        template += """
# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
{% for c in schema.classes.values() -%}
{{ c.name }}.update_forward_refs()
{% endfor %}
"""
    else:
        template += """
# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
{% for c in schema.classes.values() -%}
{{ c.name }}.model_rebuild()
{% endfor %}    
"""
    return template


@dataclass
class NWBPydanticGenerator(PydanticGenerator):

    SKIP_ENUM: Tuple[str] = ("FlatDType",)
    # SKIP_SLOTS=('VectorData',)
    SKIP_SLOTS: Tuple[str] = ("",)
    SKIP_CLASSES: Tuple[str] = ("",)
    INJECTED_FIELDS: Tuple[str] = (
        (
            'hdf5_path: Optional[str] = Field(None, description="The absolute path that this object'
            ' is stored in an NWB file")'
        ),
        'object_id: Optional[str] = Field(None, description="Unique UUID for each object")',
    )
    # SKIP_CLASSES=('VectorData','VectorIndex')
    split: bool = True
    schema_map: Optional[Dict[str, SchemaDefinition]] = None
    versions: dict = None
    """See :meth:`.LinkMLProvider.build` for usage - a list of specific versions to import from"""
    pydantic_version = "2"

    def _locate_imports(self, needed_classes: List[str], sv: SchemaView) -> Dict[str, List[str]]:
        """
        Given a list of class names, find the python modules that need to be imported
        """
        imports = {}

        # These classes are not generated by pydantic!
        skips = ("AnyType",)

        for cls in needed_classes:
            if cls in skips:  # pragma: no cover
                continue
            # Find module that contains class
            module_name = sv.element_by_schema_map()[ElementName(cls)]
            # Don't get classes that are defined in this schema!
            if module_name == self.schema.name:
                continue
            schema_name = module_name.split(".")[0]
            if (
                self.versions
                and schema_name != self.schema.name.split(".")[0]
                and schema_name in self.versions
            ):
                version = version_module_case(self.versions[schema_name])
                if self.split:
                    local_mod_name = (
                        "..."
                        + module_case(schema_name)
                        + "."
                        + version
                        + "."
                        + module_case(module_name)
                    )
                else:  # pragma: no cover
                    local_mod_name = (
                        "..." + module_case(schema_name) + "." + version + "." + "namespace"
                    )

            else:

                local_mod_name = "." + module_case(module_name)
            if local_mod_name not in imports:
                imports[local_mod_name] = [camelcase(cls)]
            else:
                imports[local_mod_name].append(camelcase(cls))
        return imports

    def _get_namespace_imports(self, sv: SchemaView) -> Dict[str, List[str]]:
        """
        Get imports for namespace packages. For these we import all
        the tree_root classes, ie. all the classes that are top-level classes
        rather than nested classes
        """
        all_classes = sv.all_classes(imports=True)
        needed_classes = []
        for clsname, cls in all_classes.items():
            if cls.is_a != "Arraylike":
                needed_classes.append(clsname)

        imports = self._locate_imports(needed_classes, sv)
        return imports

    def _get_class_imports(
        self,
        cls: ClassDefinition,
        sv: SchemaView,
        all_classes: dict[ClassDefinitionName, ClassDefinition],
        class_slots: dict[str, List[SlotDefinition]],
    ) -> List[str]:
        """Get the imports needed for a single class"""
        needed_classes = []
        needed_classes.append(cls.is_a)
        # get needed classes used as ranges in class attributes
        for slot in class_slots[cls.name]:
            if slot.name in self.SKIP_SLOTS:  # pragma: no cover
                continue
            if slot.range in all_classes:
                needed_classes.append(slot.range)
            # handle when a range is a union of classes
            if slot.any_of:
                for any_slot_range in slot.any_of:
                    if any_slot_range.range in all_classes:
                        needed_classes.append(any_slot_range.range)

        return needed_classes

    def _get_imports(
        self,
        sv: SchemaView,
        local_classes: List[ClassDefinition],
        class_slots: Dict[str, List[SlotDefinition]],
    ) -> Dict[str, List[str]]:
        # import from local references, rather than serializing every class in every file
        if not self.split:
            # we are compiling this whole thing in one big file so we don't import anything
            return {}
        if "is_namespace" in sv.schema.annotations.keys() and sv.schema.annotations["is_namespace"][
            "value"
        ] in ("True", True):
            return self._get_namespace_imports(sv)

        all_classes = sv.all_classes(imports=True)
        # local_classes = sv.all_classes(imports=False)
        needed_classes = []
        # find needed classes - is_a and slot ranges

        for cls in local_classes:
            # get imports for this class
            needed_classes.extend(self._get_class_imports(cls, sv, all_classes, class_slots))

        # remove duplicates and arraylikes
        needed_classes = [
            cls for cls in set(needed_classes) if cls is not None and cls != "Arraylike"
        ]
        needed_classes = [cls for cls in needed_classes if sv.get_class(cls).is_a != "Arraylike"]

        imports = self._locate_imports(needed_classes, sv)

        return imports

    def _get_classes(self, sv: SchemaView) -> List[ClassDefinition]:
        if self.split:
            classes = sv.all_classes(imports=False).values()
        else:
            classes = sv.all_classes(imports=True).values()

        # Don't want to generate classes when class_uri is linkml:Any, will
        # just swap in typing.Any instead down below
        classes = [
            c for c in list(classes) if c.is_a != "Arraylike" and c.class_uri != "linkml:Any"
        ]

        return classes

    def _get_class_slots(self, sv: SchemaView, cls: ClassDefinition) -> List[SlotDefinition]:
        slots = []
        for slot_name in sv.class_slots(cls.name):
            if slot_name in self.SKIP_SLOTS:
                continue
            slots.append(sv.induced_slot(slot_name, cls.name))
        return slots

    def _build_class(self, class_original: ClassDefinition) -> ClassDefinition:
        class_def: ClassDefinition
        class_def = copy(class_original)
        class_def.name = camelcase(class_original.name)
        if class_def.is_a:
            class_def.is_a = camelcase(class_def.is_a)
        class_def.mixins = [camelcase(p) for p in class_def.mixins]
        if class_def.description:
            class_def.description = class_def.description.replace('"', '\\"')
        return class_def

    def _check_anyof(
        self, s: SlotDefinition, sn: SlotDefinitionName, sv: SchemaView
    ):  # pragma: no cover
        # Confirm that the original slot range (ignoring the default that comes in from
        # induced_slot) isn't in addition to setting any_of
        if len(s.any_of) > 0 and sv.get_slot(sn).range is not None:
            base_range_subsumes_any_of = False
            base_range = sv.get_slot(sn).range
            base_range_cls = sv.get_class(base_range, strict=False)
            if base_range_cls is not None and base_range_cls.class_uri == "linkml:Any":
                base_range_subsumes_any_of = True
            if not base_range_subsumes_any_of:
                raise ValueError("Slot cannot have both range and any_of defined")

    def _make_npytyping_range(self, attrs: Dict[str, SlotDefinition]) -> str:
        # slot always starts with...
        prefix = "NDArray["

        # and then we specify the shape:
        shape_prefix = 'Shape["'

        # using the cardinality from the attributes
        dim_pieces = []
        for attr in attrs.values():

            if attr.maximum_cardinality:
                shape_part = str(attr.maximum_cardinality)
            else:
                shape_part = "*"

            # do this with the most heinous chain of string replacements rather than regex
            # because i am still figuring out what needs to be subbed lol
            name_part = (
                attr.name.replace(",", "_")
                .replace(" ", "_")
                .replace("__", "_")
                .replace("|", "_")
                .replace("-", "_")
                .replace("+", "plus")
            )

            dim_pieces.append(" ".join([shape_part, name_part]))

        dimension = ", ".join(dim_pieces)

        shape_suffix = '"], '

        # all dimensions should be the same dtype
        try:
            dtype = flat_to_nptyping[list(attrs.values())[0].range]
        except KeyError as e:  # pragma: no cover
            warnings.warn(str(e))
            range = list(attrs.values())[0].range
            return f"List[{range}] | {range}"
        suffix = "]"

        slot = "".join([prefix, shape_prefix, dimension, shape_suffix, dtype, suffix])
        return slot

    def _get_numpy_slot_range(self, cls: ClassDefinition) -> str:
        # if none of the dimensions are optional, we just have one possible array shape
        if all([s.required for s in cls.attributes.values()]):  # pragma: no cover
            return self._make_npytyping_range(cls.attributes)
        # otherwise we need to make permutations
        # but not all permutations, because we typically just want to be able to exclude the last possible dimensions
        # the array classes should always be well-defined where the optional dimensions are at the end, so
        requireds = {k: v for k, v in cls.attributes.items() if v.required}
        optionals = [(k, v) for k, v in cls.attributes.items() if not v.required]

        annotations = []
        if len(requireds) > 0:
            # first the base case
            annotations.append(self._make_npytyping_range(requireds))
        # then add back each optional dimension
        for i in range(len(optionals)):
            attrs = {**requireds, **{k: v for k, v in optionals[0 : i + 1]}}
            annotations.append(self._make_npytyping_range(attrs))

        # now combine with a union:
        union = "Union[\n" + " " * 8
        union += (",\n" + " " * 8).join(annotations)
        union += "\n" + " " * 4 + "]"
        return union

    def _get_linkml_classvar(self, cls: ClassDefinition) -> SlotDefinition:
        """A class variable that holds additional linkml attrs"""
        slot = SlotDefinition(name="linkml_meta")
        slot.annotations["python_range"] = Annotation("python_range", "ClassVar[LinkML_Meta]")
        meta_fields = {k: getattr(cls, k, None) for k in LinkML_Meta.model_fields.keys()}
        meta_field_strings = [f"{k}={v}" for k, v in meta_fields.items() if v is not None]
        meta_field_string = ", ".join(meta_field_strings)
        slot.annotations["fixed_field"] = Annotation(
            "fixed_field", f"Field(LinkML_Meta({meta_field_string}), frozen=True)"
        )

        return slot

    def sort_classes(
        self, clist: List[ClassDefinition], imports: Dict[str, List[str]]
    ) -> List[ClassDefinition]:
        """
        sort classes such that if C is a child of P then C appears after P in the list

        Overridden method include mixin classes

        Modified from original to allow for imported classes
        """
        # unnest imports
        imported_classes = []
        for i in imports.values():
            imported_classes.extend(i)

        clist = list(clist)
        clist = [c for c in clist if c.name not in self.SKIP_CLASSES]
        slist = []  # type: List[ClassDefinition]
        while len(clist) > 0:
            can_add = False
            for i in range(len(clist)):
                candidate = clist[i]
                can_add = False
                if candidate.is_a:
                    candidates = [candidate.is_a] + candidate.mixins
                else:
                    candidates = candidate.mixins
                if not candidates:
                    can_add = True

                else:
                    if set(candidates) <= set([p.name for p in slist] + imported_classes):
                        can_add = True

                if can_add:
                    slist = slist + [candidate]
                    del clist[i]
                    break
            if not can_add:  # pragma: no cover
                raise ValueError(
                    f"could not find suitable element in {clist} that does not ref {slist}"
                )

        self.sorted_class_names = [camelcase(cname) for cname in imported_classes]
        self.sorted_class_names += [camelcase(c.name) for c in slist]
        return slist

    def get_class_slot_range(self, slot_range: str, inlined: bool, inlined_as_list: bool) -> str:
        """
        Monkeypatch to convert Array typed slots and classes into npytyped hints
        """
        sv = self.schemaview
        range_cls = sv.get_class(slot_range)
        if range_cls.is_a == "Arraylike":
            return self._get_numpy_slot_range(range_cls)
        else:
            return self._get_class_slot_range_origin(slot_range, inlined, inlined_as_list)

    def _get_class_slot_range_origin(
        self, slot_range: str, inlined: bool, inlined_as_list: bool
    ) -> str:
        """
        Parent class get class range

        Overriding to not use strings in the type hint when a class has an identifier value

        Not testing this method except for what we changes
        """
        sv = self.schemaview
        range_cls = sv.get_class(slot_range)

        # Hardcoded handling for Any
        if range_cls.class_uri == "linkml:Any":  # pragma: no cover
            return "Any"

        # Inline the class itself only if the class is defined as inline, or if the class has no
        # identifier slot and also isn't a mixin.
        if (
            inlined
            or inlined_as_list
            or (
                # sv.get_identifier_slot(range_cls.name, use_key=True) is None and
                not sv.is_mixin(range_cls.name)
            )
        ):
            if (
                len([x for x in sv.class_induced_slots(slot_range) if x.designates_type]) > 0
                and len(sv.class_descendants(slot_range)) > 1
            ):  # pragma: no cover
                return (
                    "Union["
                    + ",".join([camelcase(c) for c in sv.class_descendants(slot_range)])
                    + "]"
                )
            else:
                return f"{camelcase(slot_range)}"

        # For the more difficult cases, set string as the default and attempt to improve it
        range_cls_identifier_slot_range = "str"  # pragma: no cover

        # For mixins, try to use the identifier slot of descendant classes
        if (
            self.gen_mixin_inheritance
            and sv.is_mixin(range_cls.name)
            and sv.get_identifier_slot(range_cls.name)
        ):  # pragma: no cover
            range_cls_identifier_slot_range = self.get_mixin_identifier_range(range_cls)

        return range_cls_identifier_slot_range  # pragma: no cover

    def get_class_isa_plus_mixins(
        self, classes: Optional[List[ClassDefinition]] = None
    ) -> Dict[str, List[str]]:
        """
        Generate the inheritance list for each class from is_a plus mixins

        Patched to only get local classes

        :return:
        """
        sv = self.schemaview
        if classes is None:  # pragma: no cover
            classes = sv.all_classes(imports=False).values()

        parents = {}
        for class_def in classes:
            class_parents = []
            if class_def.is_a:
                class_parents.append(camelcase(class_def.is_a))
            if self.gen_mixin_inheritance and class_def.mixins:  # pragma: no cover
                class_parents.extend([camelcase(mixin) for mixin in class_def.mixins])
            if len(class_parents) > 0:
                # Use the sorted list of classes to order the parent classes, but reversed to match MRO needs
                class_parents.sort(key=lambda x: self.sorted_class_names.index(x))
                class_parents.reverse()
                parents[camelcase(class_def.name)] = class_parents
        return parents

    def get_predefined_slot_value(
        self, slot: SlotDefinition, class_def: ClassDefinition
    ) -> Optional[str]:
        """
        Modified from base pydantic generator to use already grabbed induced_slot from
        already-grabbed and modified classes rather than doing a fresh iteration to
        save time and respect changes already made elsewhere in the serialization routine

        :return: Dictionary of dictionaries with predefined slot values for each class
        """
        sv = self.schemaview
        slot_value: Optional[str] = None
        # for class_def in sv.all_classes().values():
        #     for slot_name in sv.class_slots(class_def.name):
        #        slot = sv.induced_slot(slot_name, class_def.name)
        if slot.designates_type:  # pragma: no cover
            target_value = get_type_designator_value(sv, slot, class_def)
            slot_value = f'"{target_value}"'
            if slot.multivalued:
                slot_value = "[" + slot_value + "]"
        elif slot.ifabsent is not None:
            value = ifabsent_value_declaration(slot.ifabsent, sv, class_def, slot)
            slot_value = value
        # Multivalued slots that are either not inlined (just an identifier) or are
        # inlined as lists should get default_factory list, if they're inlined but
        # not as a list, that means a dictionary
        elif slot.multivalued:
            # this is slow, needs to do additional induced slot calls
            # has_identifier_slot = self.range_class_has_identifier_slot(slot)

            if slot.inlined and not slot.inlined_as_list:  # and has_identifier_slot:
                slot_value = "default_factory=dict"
            else:  # pragma: no cover
                slot_value = "default_factory=list"

        return slot_value

    def serialize(self) -> str:
        predefined_slot_values = {}
        """splitting up parent class :meth:`.get_predefined_slot_values`"""

        if self.template_file is not None:  # pragma: no cover
            with open(self.template_file) as template_file:
                template_obj = Template(template_file.read())
        else:
            template_obj = Template(
                default_template(self.pydantic_version, extra_classes=[LinkML_Meta])
            )

        sv: SchemaView
        sv = self.schemaview
        if self.schema_map is not None:  # pragma: no cover
            sv.schema_map = self.schema_map
        schema = sv.schema
        pyschema = SchemaDefinition(
            id=schema.id,
            name=schema.name,
            description=schema.description.replace('"', '\\"') if schema.description else None,
        )
        # test caching if import closure
        enums = self.generate_enums(sv.all_enums())
        # filter skipped enums
        enums = {k: v for k, v in enums.items() if k not in self.SKIP_ENUM}

        classes = self._get_classes(sv)
        # just induce slots once because that turns out to be expensive
        class_slots = {}  # type: Dict[str, List[SlotDefinition]]
        for aclass in classes:
            class_slots[aclass.name] = self._get_class_slots(sv, aclass)

        # figure out what classes we need to imports
        imports = self._get_imports(sv, classes, class_slots)

        sorted_classes = self.sort_classes(classes, imports)

        for class_original in sorted_classes:
            # Generate class definition
            class_def = self._build_class(class_original)

            if class_def.is_a != "Arraylike":
                # skip actually generating arraylike classes, just use them to generate
                # the npytyping annotations
                pyschema.classes[class_def.name] = class_def
            else:  # pragma: no cover
                continue

            # Not sure why this happens
            for attribute in list(class_def.attributes.keys()):
                del class_def.attributes[attribute]

            # make class attr that stores extra linkml attrs
            class_def.attributes["linkml_meta"] = self._get_linkml_classvar(class_def)

            class_name = class_original.name
            predefined_slot_values[camelcase(class_name)] = {}
            for s in class_slots[class_name]:
                sn = SlotDefinitionName(s.name)
                predefined_slot_value = self.get_predefined_slot_value(s, class_def)
                if predefined_slot_value is not None:
                    predefined_slot_values[camelcase(class_name)][s.name] = predefined_slot_value
                # logging.error(f'Induced slot {class_name}.{sn} == {s.name} {s.range}')
                s.name = underscore(s.name)
                if s.description:
                    s.description = s.description.replace('"', '\\"')
                class_def.attributes[s.name] = s

                slot_ranges: List[str] = []

                self._check_anyof(s, sn, sv)

                if s.any_of is not None and len(s.any_of) > 0:
                    # list comprehension here is pulling ranges from within AnonymousSlotExpression
                    slot_ranges.extend([r.range for r in s.any_of])
                else:
                    slot_ranges.append(s.range)

                pyranges = [
                    self.generate_python_range(slot_range, s, class_def)
                    for slot_range in slot_ranges
                ]
                # --------------------------------------------------
                # Special Case - since we get abstract classes from
                # potentially multiple versions (which are then different)
                # model classes, we allow container classes to also
                # be generic descendants of BaseModel
                # --------------------------------------------------
                if "DynamicTable" in pyranges:  # pragma: no cover
                    pyranges.append("BaseModel")

                pyranges = list(set(pyranges))  # remove duplicates
                pyranges.sort()

                if len(pyranges) == 1:
                    pyrange = pyranges[0]
                elif len(pyranges) > 1:
                    pyrange = f"Union[{', '.join(pyranges)}]"
                else:  # pragma: no cover
                    raise Exception(f"Could not generate python range for {class_name}.{s.name}")

                if s.multivalued:
                    if s.inlined or s.inlined_as_list:
                        collection_key = self.generate_collection_key(slot_ranges, s, class_def)
                    else:  # pragma: no cover
                        collection_key = None
                    if (
                        s.inlined is False or collection_key is None or s.inlined_as_list is True
                    ):  # pragma: no cover
                        pyrange = f"List[{pyrange}] | {pyrange}"
                    else:
                        pyrange = f"Dict[{collection_key}, {pyrange}]"
                if not s.required and not s.designates_type:
                    pyrange = f"Optional[{pyrange}]"
                ann = Annotation("python_range", pyrange)
                s.annotations[ann.tag] = ann

        code = template_obj.render(
            imports=imports,
            schema=pyschema,
            underscore=underscore,
            enums=enums,
            predefined_slot_values=predefined_slot_values,
            allow_extra=self.extra_fields,
            metamodel_version=self.schema.metamodel_version,
            version=self.schema.version,
            class_isa_plus_mixins=self.get_class_isa_plus_mixins(sorted_classes),
            injected_fields=self.INJECTED_FIELDS,
        )
        return code

    def compile_module(
        self, module_path: Path = None, module_name: str = "test"
    ) -> ModuleType:  # pragma: no cover - replaced with provider
        """
        Compiles generated python code to a module
        :return:
        """
        pycode = self.serialize()
        if module_path is not None:
            module_path = Path(module_path)
            init_file = module_path / "__init__.py"
            with open(init_file, "w") as ifile:
                ifile.write(" ")

        try:
            return compile_python(pycode, module_path, module_name)
        except NameError as e:
            raise e


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
