import os
from pathlib import Path

import pytest
import requests_cache

from .fixtures import *  # noqa: F403


def pytest_addoption(parser):
    parser.addoption(
        "--with-output",
        action="store_true",
        help="dump output in compliance test for richer debugging information",
    )
    parser.addoption(
        "--without-cache", action="store_true", help="Don't use a sqlite cache for network requests"
    )


@pytest.fixture(autouse=True, scope="session")
def set_config_vars(tmp_output_dir):
    os.environ["NWB_LINKML_CACHE_DIR"] = str(tmp_output_dir)


@pytest.fixture(scope="session", autouse=True)
def patch_requests_cache(pytestconfig):
    """
    Cache network requests - for each unique network request, store it in
    an sqlite cache. only do unique requests once per session.
    """
    if pytestconfig.getoption("--without-cache"):
        yield
        return
    cache_file = Path(__file__).parent / "output" / "requests-cache.sqlite"
    requests_cache.install_cache(
        str(cache_file),
        backend="sqlite",
        urls_expire_after={"localhost": requests_cache.DO_NOT_CACHE},
    )
    requests_cache.clear()
    yield
    # delete cache file unless we have requested it to persist for inspection
    if not pytestconfig.getoption("--with-output"):
        cache_file.unlink(missing_ok=True)
