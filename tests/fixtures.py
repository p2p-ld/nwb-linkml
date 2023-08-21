import pytest
from typing import Dict


from nwb_linkml import io
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
def nwb_core_fixture() -> Dict[str, io.NamespaceBundle]:
    nwb_core = io.load_nwb_core()
    return nwb_core