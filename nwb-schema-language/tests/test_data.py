"""Data test."""
import os
import glob
import unittest

from linkml_runtime.loaders import yaml_loader
from nwb_schema_language.datamodel.nwb_schema_language import Namespaces

ROOT = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(ROOT, "src", "data", "tests")

EXAMPLE_FILES = glob.glob(os.path.join(DATA_DIR, '*.yaml'))


class TestData(unittest.TestCase):
    """Test data and datamodel."""

    def test_namespaces(self):
        """Date test."""
        namespace_file = [f for f in EXAMPLE_FILES if 'namespace.yaml' in f][0]
        obj = yaml_loader.load(namespace_file, target_class=Namespaces)
        assert obj
