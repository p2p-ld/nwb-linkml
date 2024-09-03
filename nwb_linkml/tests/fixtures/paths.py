import shutil
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def tmp_output_dir(request: pytest.FixtureRequest) -> Path:
    path = Path(__file__).parents[1].resolve() / "__tmp__"
    if path.exists():
        if request.config.getoption("--clean"):
            shutil.rmtree(path)
        else:
            for subdir in path.iterdir():
                if subdir.name == "git":
                    # don't wipe out git repos every time, they don't rly change
                    continue
                elif subdir.is_file() and subdir.parent != path:
                    continue
                elif subdir.is_file():
                    subdir.unlink(missing_ok=True)
                else:
                    shutil.rmtree(str(subdir))
    path.mkdir(exist_ok=True)

    return path


@pytest.fixture(scope="function")
def tmp_output_dir_func(tmp_output_dir) -> Path:
    """
    tmp output dir that gets cleared between every function
    cleans at the start rather than at cleanup in case the output is to be inspected
    """
    subpath = tmp_output_dir / "__tmpfunc__"
    if subpath.exists():
        shutil.rmtree(str(subpath))
    subpath.mkdir()
    return subpath


@pytest.fixture(scope="module")
def tmp_output_dir_mod(tmp_output_dir) -> Path:
    """
    tmp output dir that gets cleared between every function
    cleans at the start rather than at cleanup in case the output is to be inspected
    """
    subpath = tmp_output_dir / "__tmpmod__"
    if subpath.exists():
        shutil.rmtree(str(subpath))
    subpath.mkdir()
    return subpath


@pytest.fixture(scope="session")
def data_dir() -> Path:
    path = Path(__file__).parent.resolve() / "data"
    return path
