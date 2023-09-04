import pdb

import pytest
import warnings

from .fixtures import nwb_core_fixture, tmp_output_dir
from linkml_runtime.dumpers import yaml_dumper
from linkml.generators import PydanticGenerator
from nwb_linkml.generators.pydantic import NWBPydanticGenerator
from nwb_linkml.generators.sqlmodel import SQLModelGenerator

from nwb_linkml.lang_elements import NwbLangSchema

def test_generate_nwblang(tmp_output_dir):
    output_file = (tmp_output_dir / NwbLangSchema.name).with_suffix('.yml')
    yaml_dumper.dump(NwbLangSchema, output_file)

def test_generate_core(nwb_core_fixture, tmp_output_dir):
    schemas = nwb_core_fixture.build().schemas

    (tmp_output_dir / 'schema').mkdir(exist_ok=True)

    for schema in schemas:
        output_file = tmp_output_dir / 'schema' / (schema.name + '.yaml')
        yaml_dumper.dump(schema, output_file)

@pytest.mark.depends(on=['test_generate_core'])
def test_generate_pydantic(tmp_output_dir):


    # core_file = tmp_output_dir / 'core.yaml'
    # pydantic_file = tmp_output_dir / 'core.py'

    (tmp_output_dir / 'models' / 'pydantic').mkdir(exist_ok=True, parents=True)

    for schema in (tmp_output_dir / 'schema').glob('*.yaml'):
        if not schema.exists():
            continue
        # python friendly name
        python_name = schema.stem.replace('.', '_').replace('-','_')

        pydantic_file = (schema.parent.parent / 'models' / 'pydantic' / python_name).with_suffix('.py')

        generator = NWBPydanticGenerator(
            str(schema),
            pydantic_version='2',
            emit_metadata=True,
            gen_classvars=True,
            gen_slots=True
        )
        gen_pydantic = generator.serialize()


        with open(pydantic_file, 'w') as pfile:
            pfile.write(gen_pydantic)

@pytest.mark.depends(on=['test_generate_core'])
def test_generate_sqlmodel(tmp_output_dir):

    (tmp_output_dir / 'models' / 'sqlmodel').mkdir(exist_ok=True, parents=True)

    for schema in (tmp_output_dir / 'schema').glob('*.yaml'):
        if not schema.exists():
            continue
        # python friendly name
        python_name = schema.stem.replace('.', '_').replace('-','_')

        sqlmodel_file = (schema.parent.parent / 'models' / 'sqlmodel' / python_name).with_suffix('.py')

        generator = SQLModelGenerator(
            str(schema),
            pydantic_version='2',
            emit_metadata=True,
            gen_classvars=True,
            gen_slots=True
        )
        gen_sqlmodel = generator.generate_sqla()


        with open(sqlmodel_file, 'w') as pfile:
            pfile.write(gen_sqlmodel)

