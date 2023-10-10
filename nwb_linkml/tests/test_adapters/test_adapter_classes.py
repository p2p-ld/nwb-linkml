import pdb

import pytest

from ..fixtures import linkml_schema_bare, linkml_schema, nwb_schema

from nwb_linkml.adapters import DatasetAdapter, ClassAdapter

def test_build_base(nwb_schema):
    # simplest case, nothing special here
    dset = DatasetAdapter(cls=nwb_schema.datasets['image'])

    #pdb.set_trace()
    pass