import pytest
import warnings

def test_hold_up():
    from linkml_runtime.linkml_model import SchemaDefinition, Annotation
    schema = SchemaDefinition(
        id='myschema',
        name='myschema',
        annotations=[{'tag':'my_annotation','value':True}]
    )

    warnings.warn('TYPE OF ANNOTATION IS')
    warnings.warn(str(type(schema.annotations['my_annotation'].value)))


