import pdb

import pytest

from nwb_linkml.providers.schema import LinkMLProvider, PydanticProvider

def test_linkml_provider():

    provider = LinkMLProvider()
    core = provider.get('core')

@pytest.mark.depends(on=['test_linkml_provider'])
def test_pydantic_provider():
    provider = PydanticProvider()

    core = provider.get('core')

