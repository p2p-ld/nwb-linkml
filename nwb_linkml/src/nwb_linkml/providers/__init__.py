"""
Classes used for acquiring things from elsewhere, managing build processes, and caching
results.[^recall]

Each provider class handles gathering the inputs and caching and providing the desired outputs
for its domain.

- {mod}`.git` providers faithfully yield to us the state of some code or schema somewhere
- {mod}`~.providers.linkml` providers nobly convert NWB schema language to linkml
- {mod}`~.providers.pydantic` providers courageously generate pydantic models from that linkml
- {mod}`~.providers.schema` providers sit around on their ass all day and wrap the other kinds of
  providers for a simpler interface

[^recall]: Recall that
    - {mod}`.adapters` are for converting nwb schema language to linkml
    - {mod}`.generators` (or rather the pydanticgen) are for converting linkml into concrete
        representations like pydantic models
    - so **providers** are the things that manage the multistage build process given some cache of
      the stages so that you can go like "gimme model i want my model" and you will probably get it.
"""

# ruff: noqa: I001 - import order necessary to avoid circular imports :)
from nwb_linkml.providers.provider import Provider
from nwb_linkml.providers.linkml import LinkMLProvider
from nwb_linkml.providers.pydantic import PydanticProvider
from nwb_linkml.providers.schema import SchemaProvider

__all__ = ["Provider", "LinkMLProvider", "PydanticProvider", "SchemaProvider"]
