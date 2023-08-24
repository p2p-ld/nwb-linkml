import pdb

import pytest
import warnings

from .fixtures import nwb_core_fixture, tmp_output_dir
from linkml_runtime.dumpers import yaml_dumper
from linkml.generators import PydanticGenerator

from nwb_linkml.lang_elements import NwbLangSchema

def test_generate_nwblang(tmp_output_dir):
    output_file = (tmp_output_dir / NwbLangSchema.name).with_suffix('.yml')
    yaml_dumper.dump(NwbLangSchema, output_file)

def test_generate_core(nwb_core_fixture, tmp_output_dir):
    schemas = nwb_core_fixture.build().schemas
    for schema in schemas:
        output_file = tmp_output_dir / (schema.name + '.yaml')
        yaml_dumper.dump(schema, output_file)

@pytest.mark.depends(on=['test_generate_core'])
def test_generate_pydantic(tmp_output_dir):
    core_file = tmp_output_dir / 'core.yaml'
    pydantic_file = tmp_output_dir / 'core.py'

    generator = PydanticGenerator(
        str(core_file),
        pydantic_version='1',
        emit_metadata=True,
        gen_classvars=True,
        gen_slots=True

    )
    gen_pydantic = generator.serialize()
    with open(pydantic_file, 'w') as pfile:
        pfile.write(gen_pydantic)
