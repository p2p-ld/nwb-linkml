import pdb
from pathlib import Path
import h5py
import json
from hdf5_linkml.io import H5File
from nwb_linkml.adapters import NamespacesAdapter
from nwb_linkml.io import load_schema_file
from linkml_runtime.linkml_model import SchemaDefinition

DATASET = '/Users/jonny/Dropbox/lab/p2p_ld/data/nwb/sub-738651046_ses-760693773.nwb'


class NWBH5File(H5File):

    def __init__(self, file: Path):
        self.file = Path(file)

    def read(self):
        with h5py.File(self.file, 'r') as h5f:
            embedded_schema = self.load_embedded_schema(h5f)
            translated_schema = self.translate_schema(embedded_schema)
            pdb.set_trace()

    def load_embedded_schema(self, h5f:h5py.File) -> List[dict]:
        """
        Stored in ``/specfications/{namespace}/{version}/{schema_files}``

        Args:
            h5f:

        Returns:
            [
                {
                    'namespace': "DECODED_JSON_OBJECT",
                    'nwb.base': "DECODED_JSON_OBJECT",
                    ...
                },
                {
                    'namespace': "DECODED_JSON_OBJECT",
                }
            ]

        """

        namespaces = []
        for ns_name, ns in h5f['specifications'].items():
            ns_schema = {}
            for version in ns.values():
                for schema_name, schema in version.items():
                    # read the source json binary string
                    sch_str = schema[()]
                    sch_dict = json.loads(sch_str)
                    ns_schema[schema_name] = sch_dict
            namespaces.append(ns_schema)
        return namespaces

    def translate_schema(self, schema:List[dict]) -> List[SchemaDefinition]:
        translated = []
        for ns_schema in schema:
            # find namespace
            namespace = ns_schema['namespace']
            ns_schema_adapters = [load_schema_file(sch_name, schema_dict) for sch_name, schema_dict in ns_schema.items() if sch_name != 'namespace']
            adapter = NamespacesAdapter(
                namespaces=namespace,
                schemas=ns_schema_adapters
            )
            res = adapter.build()
            translated.extend(res.schema)