import re
import textwrap
from doctest import NORMALIZE_WHITESPACE, ELLIPSIS
from sybil import Document
from sybil import Sybil, Region
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser
import yaml
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


def test_adapter_block(example):
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


def parse_adapter_blocks(document: Document):
    for start_match, end_match, source in document.find_region_sources(ADAPTER_START, ADAPTER_END):
        # parse
        sections = re.split(r":\w+?:", source, re.MULTILINE)
        sections = [textwrap.dedent(section).strip() for section in sections]

        sections[1] = _strip_nwb(sections[1])

        yield Region(start_match.start(), end_match.end(), sections, test_adapter_block)


adapter_parser = Sybil(
    parsers=[
        parse_adapter_blocks
    ],
    patterns=["adapters/*.py"],
)

doctest_parser = Sybil(
    parsers=[DocTestParser(optionflags=ELLIPSIS + NORMALIZE_WHITESPACE), PythonCodeBlockParser()],
    patterns=["*.py"],
)

pytest_collect_file = (adapter_parser + doctest_parser).pytest()
