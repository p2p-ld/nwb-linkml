import pdb
from collections import defaultdict

from linkml.generators.sqltablegen import SQLTableGenerator
from linkml.transformers.relmodel_transformer import ForeignKeyPolicy, RelationalModelTransformer
from linkml.utils.generator import Generator, shared_arguments
from linkml_runtime.utils.schemaview import SchemaView
from linkml_runtime.linkml_model import (
    Annotation,
    ClassDefinition,
    ClassDefinitionName,
    SchemaDefinition,
)

from nwb_linkml.generators.pydantic import NWBPydanticGenerator

def default_template(pydantic_ver: str = "2") -> str:
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
from sqlmodel import SQLModel, Field
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
        ({{class_isa_plus_mixins[c.name]|join(', ')}}, table=True)
    {%- else -%}
        (ConfiguredBaseModel, table=True)
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
    {%- if 'foreign_key' in s.annotations -%}, foreign_key='{{ s.annotations['foreign_key'].value }}' {%- endif -%}
    {%- if 'primary_key' in s.annotations -%}, primary_key=True {%- endif -%}
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


class SQLModelGenerator(NWBPydanticGenerator):
    """
    Generate an SQLModels-compatible model
    """

    def generate_sqla(
            self,
            foreign_key_policy: ForeignKeyPolicy = None,
            **kwargs
    ):
        """
        Adapted from :meth:`linkml.generators.sqlalchemygen.SQLAlchemyGenerator.generate_sqla`

        Need to add SQL annotations to pydantic before passing to
        the template, but original classes don't return generated values

        - Accept as arguments:
            -

        Returns:
            - mappings=tr_result.mappings
            - backrefs=backrefs
            - is_join_table

        """
        sqltr = RelationalModelTransformer(self.schemaview)
        tr_result = sqltr.transform(**kwargs)
        tgen = SQLTableGenerator(self.schemaview.schema)
        tr_schema = tr_result.schema
        pdb.set_trace()
        for c in tr_schema.classes.values():
            for a in c.attributes.values():
                sql_range = tgen.get_sql_range(a, tr_schema)
                sql_type = sql_range.__repr__()
                ann = Annotation("sql_type", sql_type)
                a.annotations[ann.tag] = ann

        backrefs = defaultdict(list)
        for m in tr_result.mappings:
            backrefs[m.source_class].append(m)
        tr_sv = SchemaView(tr_schema)

        rel_schema_classes_ordered = [
            tr_sv.get_class(cn, strict=True) for cn in tr_sv.all_classes()
        ]
        for c in rel_schema_classes_ordered:
            # For SQLA there needs to be a primary key for each class;
            # autogenerate this as a compound key if none declared
            has_pk = any(a for a in c.attributes.values() if "primary_key" in a.annotations)
            if not has_pk:
                for a in c.attributes.values():
                    ann = Annotation("primary_key", "true")
                    a.annotations[ann.tag] = ann
        return tr_sv, backrefs




