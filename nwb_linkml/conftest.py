"""
Test fixtures primarily for doctests for adapters
"""

import re
import textwrap
from doctest import ELLIPSIS, NORMALIZE_WHITESPACE
from typing import Generator

import yaml
from sybil import Document, Example, Region, Sybil
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser

from nwb_linkml import adapters

# Test adapter generation examples

ADAPTER_START = re.compile(r"\.\.\s*adapter::")
ADAPTER_END = re.compile(r"\n\s*\n")

NWB_KEYS = re.compile(r"(^\s*datasets:\s*\n)|^groups:")


def _strip_nwb(nwb: str) -> str:
    # strip 'datasets:' keys and decoration left in for readability/context
    nwb = re.sub(NWB_KEYS, "", nwb)
    nwb = re.sub(r"^-", " ", nwb)
    nwb = textwrap.dedent(nwb)
    return nwb


def test_adapter_block(example: Example) -> None:
    """
    The linkml generated from a nwb example input should match
    that provided in the docstring.

    See adapters/dataset.py for example usage of .. adapter:: directive
    """
    cls_name, nwb, linkml_expected = example.parsed

    # get adapter and generate
    adapter_cls = getattr(adapters, cls_name)
    adapter = adapter_cls(cls=nwb)
    res = adapter.build()

    # compare
    generated = yaml.safe_load(res.as_linkml())
    expected = yaml.safe_load(linkml_expected)
    assert generated == expected


def parse_adapter_blocks(document: Document) -> Generator[Region, None, None]:
    """
    Parse blocks with adapter directives, yield to test with :func:`.test_adapter_block`
    """
    for start_match, end_match, source in document.find_region_sources(ADAPTER_START, ADAPTER_END):
        # parse
        sections = re.split(r":\w+?:", source, flags=re.MULTILINE)
        sections = [textwrap.dedent(section).strip() for section in sections]

        sections[1] = _strip_nwb(sections[1])

        yield Region(start_match.start(), end_match.end(), sections, test_adapter_block)


adapter_parser = Sybil(
    parsers=[parse_adapter_blocks],
    patterns=["adapters/*.py"],
)

doctest_parser = Sybil(
    parsers=[DocTestParser(optionflags=ELLIPSIS + NORMALIZE_WHITESPACE), PythonCodeBlockParser()],
    patterns=["providers/git.py"],
)

pytest_collect_file = (adapter_parser + doctest_parser).pytest()
