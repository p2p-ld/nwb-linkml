"""
Adapters to linkML classes
"""

from nwb_schema_language import Dataset, Group
from nwb_linkml.adapters.adapter import Adapter
from linkml_runtime.linkml_model import ClassDefinition, SlotDefinition


class ClassAdapter(Adapter):
    """
    Adapter to class-like things in linkml, including datasets and groups
    """
    cls: Dataset | Group

    def build(self) -> ClassDefinition:
        if self.cls.neurodata_type_def:
            name = self.cls.neurodata_type_def
        else:
            name = self.cls.name

        attrs = [
            SlotDefinition(
                name=attr.name,
                description=attr.doc,

            ) for attr in self.cls.attributes
        ]

        cls = ClassDefinition(
            name = name,
            is_a = self.cls.neurodata_type_inc,
            description=self.cls.doc,
            attributes=attrs
        )
        return cls