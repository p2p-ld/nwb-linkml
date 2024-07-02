"""
Placeholder end-to-end tests for generating linkml translations and pydantic models.

Should be replaced with more specific unit and integration tests, but in place for now
to ensure that the basics of the whole thing operate -- not doing any actual data validation
here.
"""

import pdb
from pathlib import Path
from typing import Dict

import pytest
import warnings

from .fixtures import nwb_core_fixture, tmp_output_dir
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SchemaDefinition
from nwb_linkml.generators.pydantic import NWBPydanticGenerator
from linkml_runtime.loaders.yaml_loader import YAMLLoader

from nwb_linkml.lang_elements import NwbLangSchema


def test_generate_nwblang(tmp_output_dir):
    output_file = (tmp_output_dir / NwbLangSchema.name).with_suffix(".yml")
    yaml_dumper.dump(NwbLangSchema, output_file)


def test_generate_core(nwb_core_fixture, tmp_output_dir):
    schemas = nwb_core_fixture.build().schemas

    (tmp_output_dir / "schema").mkdir(exist_ok=True)

    for schema in schemas:
        output_file = tmp_output_dir / "schema" / (schema.name + ".yaml")
        yaml_dumper.dump(schema, output_file)


def load_schema_files(path: Path) -> Dict[str, SchemaDefinition]:
    yaml_loader = YAMLLoader()
    sch: SchemaDefinition
    preloaded_schema = {}
    for schema_path in (path / "schema").glob("*.yaml"):
        sch = yaml_loader.load(str(schema_path), target_class=SchemaDefinition)
        preloaded_schema[sch.name] = sch
    return preloaded_schema


@pytest.mark.depends(on=["test_generate_core"])
def test_generate_pydantic(tmp_output_dir):

    (tmp_output_dir / "models").mkdir(exist_ok=True)

    preloaded_schema = load_schema_files(tmp_output_dir)

    for schema_path in (tmp_output_dir / "schema").glob("*.yaml"):
        if not schema_path.exists():
            continue
        # python friendly name
        python_name = schema_path.stem.replace(".", "_").replace("-", "_")

        pydantic_file = (schema_path.parent.parent / "models" / python_name).with_suffix(".py")

        generator = NWBPydanticGenerator(
            str(schema_path),
            pydantic_version="2",
            emit_metadata=True,
            gen_classvars=True,
            gen_slots=True,
            schema_map=preloaded_schema,
        )
        gen_pydantic = generator.serialize()

        with open(pydantic_file, "w") as pfile:
            pfile.write(gen_pydantic)

    # make __init__.py
    with open(tmp_output_dir / "models" / "__init__.py", "w") as initfile:
        initfile.write("# Autogenerated module indicator")
