import os
import pytest

from .fixtures import tmp_output_dir

@pytest.fixture(autouse=True, scope='session')
def set_config_vars(tmp_output_dir):
    os.environ['NWB_LINKML_CACHE_DIR'] = str(tmp_output_dir)
