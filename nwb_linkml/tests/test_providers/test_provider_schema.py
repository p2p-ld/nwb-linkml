import pdb
import shutil
import os
import sys
from pathlib import Path

from typing import Optional, Union, List
from ..fixtures import tmp_output_dir, set_config_vars

import pytest

from nwb_linkml.providers.schema import LinkMLProvider, PydanticProvider
import nwb_linkml
from nwb_linkml.maps.naming import version_module_case


CORE_MODULES = (
"core.nwb.base",
"core.nwb.device",
"core.nwb.epoch",
"core.nwb.image",
"core.nwb.file",
"core.nwb.misc",
"core.nwb.behavior",
"core.nwb.ecephys",
"core.nwb.icephys",
"core.nwb.ogen",
"core.nwb.ophys",
"core.nwb.retinotopy",
"core.nwb.language"
)
@pytest.mark.parametrize(
    ["repo_version", "schema_version", "schema_dir"],
    [
        ('2.6.0', '2.6.0-alpha', 'v2_6_0_alpha')
    ]
)
def test_linkml_provider(tmp_output_dir, repo_version, schema_version, schema_dir):

    provider = LinkMLProvider(path=tmp_output_dir)
    # clear any prior output
    shutil.rmtree(provider.path, ignore_errors=True)
    assert not provider.path.exists()

    # end to end, check that we can get the 'core' repo at the latest version
    # in the gitrepo
    core = provider.get('core', version=repo_version)

    assert core.schema.version == schema_version
    assert all([mod in core.schema.imports for mod in CORE_MODULES])
    assert schema_dir in [path.name for path in (provider.path / 'core').iterdir()]



@pytest.mark.depends(on=['test_linkml_provider'])
@pytest.mark.parametrize(
    ['class_name', 'test_fields'],
    [
        ('TimeSeries', {
            'name':str,
            'description': Optional[str],
            'comments': Optional[str],
            'data': 'TimeSeriesData',
            'timestamps': Optional[List[float]],
            'control': Optional[List[int]],
        })
    ]
)
def test_pydantic_provider_core(tmp_output_dir, class_name, test_fields):
    provider = PydanticProvider(path=tmp_output_dir)
    # clear any prior output
    assert provider.path.parent == tmp_output_dir
    shutil.rmtree(provider.path, ignore_errors=True)
    assert not provider.path.exists()

    # first, we should not build if we're allowed to get core from repo
    core = provider.get('core', allow_repo=True)
    assert Path(nwb_linkml.__file__).parent in Path(core.__file__).parents
    assert not (provider.path / 'core').exists()

    # then, if we're not allowed to get repo versions, we build!
    del sys.modules[core.__name__]
    core = provider.get('core', allow_repo=False)
    # ensure we didn't get the builtin one
    assert Path(nwb_linkml.__file__).parent not in Path(core.__file__).parents
    assert (tmp_output_dir / 'pydantic' / 'core' / version_module_case(core.version) / 'namespace.py').exists()

    test_class = getattr(core, class_name)
    assert test_class == provider.get_class('core', class_name)

    for k, v in test_fields.items():
        if isinstance(v, str):
            assert test_class.model_fields[k].annotation.__name__ == v
        else:
            assert test_class.model_fields[k].annotation == v


