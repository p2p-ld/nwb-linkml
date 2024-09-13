from pathlib import Path
from dataclasses import dataclass

from linkml.generators.pydanticgen import PydanticGenerator
from linkml.generators.pydanticgen.build import ClassResult
from linkml.generators.pydanticgen.template import Import, ObjectImport
from linkml_runtime import SchemaView
from pydantic import BaseModel, model_validator


class ParentizeMixin(BaseModel):

    @model_validator(mode="after")
    def parentize(self):
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

    def __init__(self, *args, **kwargs):
        kwargs["injected_classes"] = [ParentizeMixin]
        kwargs["imports"] = [
            Import(module="pydantic", objects=[ObjectImport(name="model_validator")])
        ]
        kwargs["black"] = True
        super().__init__(*args, **kwargs)

    def after_generate_class(self, cls: ClassResult, sv: SchemaView) -> ClassResult:
        if cls.cls.name in ("Dataset", "Group"):
            cls.cls.bases = ["ConfiguredBaseModel", "ParentizeMixin"]
        return cls


def generate():
    schema = Path(__file__).parent / "schema" / "nwb_schema_language.yaml"
    output = Path(__file__).parent / "datamodel" / "nwb_schema_pydantic.py"
    generator = NWBSchemaLangGenerator(schema=schema)
    generated = generator.serialize()
    with open(output, "w") as ofile:
        ofile.write(generated)
