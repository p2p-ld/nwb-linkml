import os
import pytest
from doctest import ELLIPSIS, NORMALIZE_WHITESPACE

from tests.fixtures import tmp_output_dir

from sybil import Sybil
from sybil.parsers.rest import DocTestParser, PythonCodeBlockParser

pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS + NORMALIZE_WHITESPACE),
        PythonCodeBlockParser(),
    ],
    patterns=['*.py'],
).pytest()

@pytest.fixture(autouse=True, scope='session')
def set_config_vars(tmp_output_dir):
    os.environ['NWB_LINKML_CACHE_DIR'] = str(tmp_output_dir)
