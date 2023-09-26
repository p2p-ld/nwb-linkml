import pytest
import os

from nwb_linkml.io import schema as io
from nwb_linkml.adapters.namespaces import NamespacesAdapter
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def tmp_output_dir() -> Path:
    path = Path(__file__).parent.resolve() / '__tmp__'
    if path.exists():
        shutil.rmtree(str(path))
    path.mkdir()

    return path

@pytest.fixture(autouse=True, scope='session')
def set_config_vars(tmp_output_dir):
    os.environ['NWB_LINKML_CACHE_DIR'] = str(tmp_output_dir)



@pytest.fixture(scope="session")
def nwb_core_fixture() -> NamespacesAdapter:
    nwb_core = io.load_nwb_core()
    nwb_core.populate_imports()
    return nwb_core


@pytest.fixture(scope="session")
def data_dir() -> Path:
    path = Path(__file__).parent.resolve() / 'data'
    return path
