import os
import shutil
import tempfile
from pathlib import Path

from nwb_linkml.config import Config


def test_config_dir():
    """Ensure that the temporary directory is the same across multiple instantiations of the singleton-like config object"""
    c1 = Config()
    c2 = Config()
    assert c1.cache_dir == c2.cache_dir


def test_config_env():
    """
    Base cache dir can be overridden by environmental variable
    """

    orig_env = os.environ["NWB_LINKML_CACHE_DIR"]

    new_temp = Path(tempfile.gettempdir()) / "test_tmp_dir"
    new_temp.mkdir()

    try:
        assert Path(orig_env) != new_temp

        os.environ["NWB_LINKML_CACHE_DIR"] = str(new_temp)

        conf = Config()

        assert conf.cache_dir == new_temp
    finally:
        shutil.rmtree(new_temp)
        os.environ["NWB_LINKML_CACHE_DIR"] = orig_env
