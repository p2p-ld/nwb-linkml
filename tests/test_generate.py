import pytest
import warnings

from .fixtures import nwb_core_fixture, tmp_output_dir
from linkml_runtime.dumpers import yaml_dumper

from nwb_linkml.lang_elements import NwbLangSchema

def test_generate_nwblang(tmp_output_dir):
    output_file = (tmp_output_dir / NwbLangSchema.name).with_suffix('.yml')
    yaml_dumper.dump(NwbLangSchema, output_file)

def test_generate_base(nwb_core_fixture, tmp_output_dir):
    schema = nwb_core_fixture.schemas[0].build()
    output_file = (tmp_output_dir / schema.name).with_suffix('.yml')
    warnings.warn(output_file)
    yaml_dumper.dump(schema, output_file)
