"""
NWB in LinkML
"""
from nwb_linkml.monkeypatch import apply_patches

apply_patches()

from nwb_linkml.config import Config  # noqa: E402

__all__ = [
    "Config"
]
