import pytest
from typing import Dict


from nwb_linkml import io
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


@pytest.fixture(scope="session")
def nwb_core_fixture() -> NamespacesAdapter:
    nwb_core = io.load_nwb_core()
    nwb_core.populate_imports()
    return nwb_core