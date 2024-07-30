import codecs
import os
import sys
import warnings

from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from jinja2 import FileSystemLoader, Environment
import sphinx.util

TEMPLATE = """
.. grid:: 2
    :gutter: 1
    :margin: 0
    :padding: 0

    .. grid-item-card::
        :margin: 0
        :padding: 0

        NWB Schema
        ^^^
        .. code-block:: yaml

            {{ nwb | indent(12) }}

    .. grid-item-card::
        :margin: 0
        :padding: 0

        LinkML
        ^^^
        .. code-block:: yaml

            {{ linkml | indent(12) }}
"""

class AdapterDirective(Directive):
    """
    Directive for writing inline adapter doctests with pretty rendering :)

    Based on sphinx-jinja: https://pypi.org/project/sphinx-jinja/
    """
    has_content = True
    optional_arguments = 1
    option_spec = {
        "nwb": directives.unchanged,
        "linkml": directives.unchanged,
    }
    app = None

    def run(self):
        node = nodes.Element()
        node.document = self.state.document

        cxt = {
            'nwb': self.options.get("nwb"),
            'linkml': self.options.get("linkml")
        }
        template = Environment(
            #**conf.jinja_env_kwargs
        ).from_string(TEMPLATE)

        new_content = template.render(**cxt)
        new_content = StringList(new_content.splitlines(), source='')
        sphinx.util.nested_parse_with_titles(self.state, new_content, node)
        return node.children