"""
Base I/O class for loading and saving hdf5 files
"""
from typing import List

from linkml_runtime.linkml_model import SchemaDefinition

class H5File:
    pass

    # --------------------------------------------------
    # Hooks
    # --------------------------------------------------
    def load_embedded_schema(self, h5f) -> List[dict]:
        """
        Load schema that are embedded within the hdf5 file
        Returns:

        """
        pass

    def translate_schema(self, dict) -> SchemaDefinition:
        """
        Optionally translate schema from source language into LinkML

        Args:
            dict:

        Returns:

        """