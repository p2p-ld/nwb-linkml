import os
import tempfile
from pathlib import Path

import yaml
from yaml import CDumper as Dumper

from nwb_linkml.io.schema import load_yaml


def test_preload_maps():
    hdmf_style_naming = {
        "groups": [
            {
                "data_type_def": "Container",
                "data_type_inc": "MainClass",
                "doc": "Demo group",
                "datasets": [{"data_type_inc": "Data"}],
            }
        ]
    }

    temp, temp_name = tempfile.mkstemp(suffix=".yaml")

    with open(temp_name, "w") as temp_f:
        yaml.dump(hdmf_style_naming, temp_f, Dumper=Dumper)
    loaded = load_yaml(Path(temp_name))

    assert "neurodata_type_def" in loaded["groups"][0]
    assert "data_type_def" not in loaded["groups"][0]
    assert "neurodata_type_inc" in loaded["groups"][0]
    assert "data_type_inc" not in loaded["groups"][0]
    assert "neurodata_type_inc" in loaded["groups"][0]["datasets"][0]
    assert "data_type_inc" not in loaded["groups"][0]["datasets"][0]

    os.remove(temp_name)
