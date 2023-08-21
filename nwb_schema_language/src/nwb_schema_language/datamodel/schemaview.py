from pathlib import Path
from linkml_runtime.utils.schemaview import SchemaView

SCHEMA_FILE = Path(__file__).parent.parent.resolve() / 'schema' / 'nwb_schema_language.yaml'

schema_view = SchemaView(SCHEMA_FILE)

