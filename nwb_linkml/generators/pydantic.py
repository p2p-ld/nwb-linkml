"""
Subclass of :class:`linkml.generators.PydanticGenerator`

The pydantic generator is a subclass of
- :class:`linkml.utils.generator.Generator`
- :class:`linkml.generators.oocodegen.OOCodeGenerator`

The default `__main__` method
- Instantiates the class
- Calls :meth:`~linkml.generators.PydanticGenerator.serialize`

The `serialize` method
- Accepts an optional jinja-style template, otherwise it uses the default template
- Uses :class:`linkml_runtime.utils.schemaview.SchemaView` to interact with the schema
- Generates linkML Classes
    - `generate_enums` runs first

"""
import pdb
from typing import List, Dict, Set, Tuple, Optional
from copy import deepcopy
import warnings

from nwb_linkml.maps.dtype import flat_to_npytyping
from linkml.generators import PydanticGenerator
from linkml_runtime.linkml_model.meta import (
    Annotation,
    ClassDefinition,
    SchemaDefinition,
    SlotDefinition,
SlotDefinitionName,
    TypeDefinition,
ElementName
)
from linkml_runtime.utils.formatutils import camelcase, underscore
from linkml_runtime.utils.schemaview import SchemaView
from jinja2 import Template



def default_template(pydantic_ver: str = "1") -> str:
    """Constructs a default template for pydantic classes based on the version of pydantic"""
    ### HEADER ###
    template = """
{#-

  Jinja2 Template for a pydantic classes
-#}
from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel as BaseModel, Field
from nptyping import NDArray, Shape, Float, Float32, Double, Float64, LongLong, Int64, Int, Int32, Int16, Short, Int8, UInt, UInt32, UInt16, UInt8, UInt64, Number, String, Unicode, Unicode, Unicode, String, Bool, Datetime64
import sys
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

{% for import_module, import_classes in imports.items() %}
from {{ import_module }} import (
    {{ import_classes | join(',\n    ') }}
)
{% endfor %}

metamodel_version = "{{metamodel_version}}"
version = "{{version if version else None}}"
"""
    ### BASE MODEL ###
    if pydantic_ver == "1":
        template += """
class WeakRefShimBaseModel(BaseModel):
   __slots__ = '__weakref__'

class ConfiguredBaseModel(WeakRefShimBaseModel,
                validate_assignment = True,
                validate_all = True,
                underscore_attrs_are_private = True,
                extra = {% if allow_extra %}'allow'{% else %}'forbid'{% endif %},
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass
"""
    else:
        template += """
class ConfiguredBaseModel(BaseModel,
                validate_assignment = True,
                validate_default = True,
                extra = {% if allow_extra %}'allow'{% else %}'forbid'{% endif %},
                arbitrary_types_allowed = True,
                use_enum_values = True):
    pass
"""
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
    {{attr.name}}: {{ attr.annotations['python_range'].value }} = Field(
    {%- if predefined_slot_values[c.name][attr.name] -%}
        {{ predefined_slot_values[c.name][attr.name] }}
        {%- if attr.equals_string -%}
        , const=True
        {%- endif -%} 
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
    {% else -%}
    None
    {% endfor %}
{% endfor %}
"""
    ### FWD REFS / REBUILD MODEL ###
    if pydantic_ver == "1":
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



class NWBPydanticGenerator(PydanticGenerator):

    SKIP_ENUM=('FlatDType',)

    def _locate_imports(
            self,
            needed_classes:List[str],
            sv:SchemaView
    ) -> Dict[str, List[str]]:
        """
        Given a list of class names, find the python modules that need to be imported
        """
        imports = {}

        # These classes are not generated by pydantic!
        skips = ('AnyType',)

        for cls in needed_classes:
            if cls in skips:
                continue
            # Find module that contains class
            module_name = sv.element_by_schema_map()[ElementName(cls)]
            # Don't get classes that are defined in this schema!
            if module_name == self.schema.name:
                continue

            local_mod_name = '.' + module_name.replace('.', '_').replace('-', '_')
            if local_mod_name not in imports:
                imports[local_mod_name] = [camelcase(cls)]
            else:
                imports[local_mod_name].append(camelcase(cls))
        return imports

    def _get_namespace_imports(self, sv:SchemaView) -> Dict[str, List[str]]:
        """
        Get imports for namespace packages. For these we import all
        the tree_root classes, ie. all the classes that are top-level classes rather than
        rather than nested classes
        """
        all_classes = sv.all_classes(imports=True)
        needed_classes = []
        for clsname, cls in all_classes.items():
            if cls.tree_root:
                needed_classes.append(clsname)

        imports = self._locate_imports(needed_classes, sv)
        return imports



    def _get_imports(self, sv:SchemaView) -> Dict[str, List[str]]:
        all_classes = sv.all_classes(imports=True)
        local_classes = sv.all_classes(imports=False)
        needed_classes = []
        # find needed classes - is_a and slot ranges

        for clsname, cls in local_classes.items():
            needed_classes.append(cls.is_a)
            for slot_name, slot in cls.attributes.items():
                if slot.range in all_classes:
                    needed_classes.append(slot.range)
                if slot.any_of:
                    for any_slot_range in slot.any_of:
                        if any_slot_range.range in all_classes:
                            needed_classes.append(any_slot_range.range)

        needed_classes = [cls for cls in set(needed_classes) if cls is not None and cls != 'Arraylike']
        needed_classes = [cls for cls in needed_classes if sv.get_class(cls).is_a != 'Arraylike']

        imports = self._locate_imports(needed_classes, sv)

        return imports


    def _get_classes(self, sv:SchemaView, imports: Dict[str, List[str]]) -> List[ClassDefinition]:
        module_classes = sv.all_classes(imports=False).values()
        imported_classes = []
        for classes in imports.values():
            imported_classes.extend(classes)

        module_classes = [c for c in list(module_classes) if c.is_a != 'Arraylike']
        imported_classes = [c for c in imported_classes if sv.get_class(c).is_a != 'Arraylike']

        sorted_classes = self.sort_classes(module_classes, imported_classes)
        self.sorted_class_names = [camelcase(cname) for cname in imported_classes]
        self.sorted_class_names += [camelcase(c.name) for c in sorted_classes]

        # Don't want to generate classes when class_uri is linkml:Any, will
        # just swap in typing.Any instead down below
        sorted_classes = [c for c in sorted_classes if c.class_uri != "linkml:Any"]
        return sorted_classes

    def _build_class(self, class_original:ClassDefinition) -> ClassDefinition:
        class_def: ClassDefinition
        class_def = deepcopy(class_original)
        class_def.name = camelcase(class_original.name)
        if class_def.is_a:
            class_def.is_a = camelcase(class_def.is_a)
        class_def.mixins = [camelcase(p) for p in class_def.mixins]
        if class_def.description:
            class_def.description = class_def.description.replace('"', '\\"')
        return class_def

    def _check_anyof(self, s:SlotDefinition, sn: SlotDefinitionName, sv:SchemaView):
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
        prefix = 'NDArray['

        # and then we specify the shape:
        shape_prefix = 'Shape["'

        # using the cardinality from the attributes
        dim_pieces = []
        for attr in attrs.values():

            if attr.maximum_cardinality:
                shape_part = str(attr.maximum_cardinality)
            else:
                shape_part = "*"
            # do this cheaply instead of using regex because i want to see if this works at all first...
            name_part = attr.name.replace(',', '_').replace(' ', '_').replace('__', '_')

            dim_pieces.append(' '.join([shape_part, name_part]))

        dimension = ', '.join(dim_pieces)

        shape_suffix = '"], '

        # all dimensions should be the same dtype
        try:
            dtype = flat_to_npytyping[list(attrs.values())[0].range]
        except KeyError as e:
            warnings.warn(e)
            range = list(attrs.values())[0].range
            return f'List[{range}] | {range}'
        suffix = "]"

        slot = ''.join([prefix, shape_prefix, dimension, shape_suffix, dtype, suffix])
        return slot

    def _get_numpy_slot_range(self, cls:ClassDefinition) -> str:
        # if none of the dimensions are optional, we just have one possible array shape
        if all([s.required for s in cls.attributes.values()]):
            return self._make_npytyping_range(cls.attributes)
        # otherwise we need to make permutations
        # but not all permutations, because we typically just want to be able to exlude the last possible dimensions
        # the array classes should always be well-defined where the optional dimensions are at the end, so
        requireds = {k:v for k,v in cls.attributes.items() if v.required}
        optionals = [(k,v) for k, v in cls.attributes.items() if not v.required]

        annotations = []
        if len(requireds) > 0:
            # first the base case
            annotations.append(self._make_npytyping_range(requireds))
        # then add back each optional dimension
        for i in range(len(optionals)):
            attrs = {**requireds, **{k:v for k, v in optionals[0:i+1]}}
            annotations.append(self._make_npytyping_range(attrs))

        # now combine with a union:
        union = "Union[\n" + ' '*8
        union += (',\n' + ' '*8).join(annotations)
        union += '\n' + ' '*4 + ']'
        return union


    def sort_classes(self, clist: List[ClassDefinition], imports:List[str]) -> List[ClassDefinition]:
        """
        sort classes such that if C is a child of P then C appears after P in the list

        Overridden method include mixin classes

        Modified from original to allow for imported classes
        """
        clist = list(clist)
        slist = []  # sorted
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
                    if set(candidates) <= set([p.name for p in slist] + imports):
                        can_add = True

                if can_add:
                    slist = slist + [candidate]
                    del clist[i]
                    break
            if not can_add:
                raise ValueError(
                    f"could not find suitable element in {clist} that does not ref {slist}"
                )
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
            return super().get_class_slot_range(slot_range, inlined, inlined_as_list)

    def get_class_isa_plus_mixins(self, classes:Optional[List[ClassDefinition]] = None) -> Dict[str, List[str]]:
        """
        Generate the inheritance list for each class from is_a plus mixins

        Patched to only get local classes

        :return:
        """
        sv = self.schemaview
        if classes is None:
            classes = sv.all_classes(imports=False).values()

        parents = {}
        for class_def in classes:
            class_parents = []
            if class_def.is_a:
                class_parents.append(camelcase(class_def.is_a))
            if self.gen_mixin_inheritance and class_def.mixins:
                class_parents.extend([camelcase(mixin) for mixin in class_def.mixins])
            if len(class_parents) > 0:
                # Use the sorted list of classes to order the parent classes, but reversed to match MRO needs
                class_parents.sort(key=lambda x: self.sorted_class_names.index(x))
                class_parents.reverse()
                parents[camelcase(class_def.name)] = class_parents
        return parents

    def serialize(self) -> str:
        if self.template_file is not None:
            with open(self.template_file) as template_file:
                template_obj = Template(template_file.read())
        else:
            template_obj = Template(default_template(self.pydantic_version))

        sv: SchemaView
        sv = self.schemaview
        schema = sv.schema
        pyschema = SchemaDefinition(
            id=schema.id,
            name=schema.name,
            description=schema.description.replace('"', '\\"') if schema.description else None,
        )
        enums = self.generate_enums(sv.all_enums())
        # filter skipped enums
        enums = {k:v for k,v in enums.items() if k not in self.SKIP_ENUM}

        # import from local references, rather than serializing every class in every file
        if 'namespace' in schema.annotations.keys() and schema.annotations['namespace']['value'] == 'True':
            imports = self._get_namespace_imports(sv)
        else:
            imports = self._get_imports(sv)

        sorted_classes = self._get_classes(sv, imports)

        for class_original in sorted_classes:
            # Generate class definition
            class_def = self._build_class(class_original)

            if class_def.is_a != "Arraylike":
                # skip actually generating arraylike classes, just use them to generate
                # the npytyping annotations
                pyschema.classes[class_def.name] = class_def
            else:
                continue

            # Not sure why this happens
            for attribute in list(class_def.attributes.keys()):
                del class_def.attributes[attribute]

            class_name = class_original.name
            for sn in sv.class_slots(class_name):
                # TODO: fix runtime, copy should not be necessary
                s = deepcopy(sv.induced_slot(sn, class_name))
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

                pyranges = list(set(pyranges))  # remove duplicates
                pyranges.sort()

                if len(pyranges) == 1:
                    pyrange = pyranges[0]
                elif len(pyranges) > 1:
                    pyrange = f"Union[{', '.join(pyranges)}]"
                else:
                    raise Exception(f"Could not generate python range for {class_name}.{s.name}")

                if s.multivalued:
                    if s.inlined or s.inlined_as_list:
                        collection_key = self.generate_collection_key(slot_ranges, s, class_def)
                    else:
                        collection_key = None
                    if s.inlined is False or collection_key is None or s.inlined_as_list is True:
                        pyrange = f"List[{pyrange}]"
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
            predefined_slot_values=self.get_predefined_slot_values(),
            allow_extra=self.allow_extra,
            metamodel_version=self.schema.metamodel_version,
            version=self.schema.version,
            class_isa_plus_mixins=self.get_class_isa_plus_mixins(sorted_classes),
        )
        return code