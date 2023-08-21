import pytest

from .fixtures import nwb_core_fixture, tmp_output_dir

from nwb_linkml.maps.namespace import build_schema
from linkml_runtime.dumpers import yaml_dumper

def test_namespace_to_linkml(nwb_core_fixture, tmp_output_dir):
    output_file = tmp_output_dir / 'nwb.namespace.yml'
    schema = build_schema(nwb_core_fixture['nwb-core']['namespace'].namespaces[0])

    yaml_dumper.dump(schema, output_file)

