import pytest

from nwb_linkml.providers.schema import LinkMLProvider

def test_linkml_provider():

    provider = LinkMLProvider()
    core = provider.get('core')