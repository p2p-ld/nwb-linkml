"""
Generate downstream output from LinkML schema

Mostly for monkeypatching the pydantic generator from linkml with
changes that are unlikely to be useful upstream
"""

from nwb_linkml.generators.pydantic import PydanticGenerator

__all__ = [
    'PydanticGenerator'
]
