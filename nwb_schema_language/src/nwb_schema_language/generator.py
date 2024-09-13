"""
Customization of linkml pydantic generator
"""

from dataclasses import dataclass
from pathlib import Path

from linkml.generators.pydanticgen import PydanticGenerator
from linkml.generators.pydanticgen.build import ClassResult
from linkml.generators.pydanticgen.template import Import, ObjectImport
from linkml_runtime import SchemaView
from pydantic import BaseModel, model_validator


class ParentizeMixin(BaseModel):
    """Mixin to populate the parent field for nested datasets and groups"""

    @model_validator(mode="after")
    def parentize(self) -> BaseModel:
        """Set the parent attribute for all our fields they have one"""
        for field_name in self.model_fields:
            if field_name == "parent":
                continue
            field = getattr(self, field_name)
            if not isinstance(field, list):
                field = [field]
            for item in field:
                if hasattr(item, "parent"):
                    item.parent = self

        return self


@dataclass
class NWBSchemaLangGenerator(PydanticGenerator):
    """
    Customization of linkml pydantic generator
    """

    def __init__(self, *args, **kwargs):
        kwargs["injected_classes"] = [ParentizeMixin]
        kwargs["imports"] = [
            Import(module="pydantic", objects=[ObjectImport(name="model_validator")])
        ]
        kwargs["black"] = True
        super().__init__(*args, **kwargs)

    def after_generate_class(self, cls: ClassResult, sv: SchemaView) -> ClassResult:
        """
        Add the ParentizeMixin to the bases of Dataset and Group
        """
        if cls.cls.name in ("Dataset", "Group"):
            cls.cls.bases = ["ConfiguredBaseModel", "ParentizeMixin"]
        return cls


def generate() -> None:
    """
    Generate pydantic models for nwb_schema_language
    """
    schema = Path(__file__).parent / "schema" / "nwb_schema_language.yaml"
    output = Path(__file__).parent / "datamodel" / "nwb_schema_pydantic.py"
    generator = NWBSchemaLangGenerator(schema=schema)
    generated = generator.serialize()
    with open(output, "w") as ofile:
        ofile.write(generated)
