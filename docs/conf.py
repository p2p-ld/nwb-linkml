# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import pdb

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'nwb-linkml'
copyright = '2023, Jonny Saunders'
author = 'Jonny Saunders'
release = 'v0.1.0'

import os
from sphinx.util.tags import Tags
tags: Tags

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.graphviz',
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinxcontrib.autodoc_pydantic',
    'sphinx.ext.intersphinx',
    'sphinx.ext.doctest',
    "sphinx_design",
    #'myst_parser',
    "myst_nb",
    'sphinx_togglebutton',
    'sphinx.ext.todo'
]


templates_path = ['_templates']

if os.environ.get('SPHINX_MINIMAL', None) == 'True':
    exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**/models']
    tags.add('minimal')
else:
    exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
    tags.add('full')



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_css_files = [
    'css/custom.css'
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'pydantic': ('https://docs.pydantic.dev/latest/', None),
    'h5py': ('https://docs.h5py.org/en/stable/', None),
    'dask': ('https://docs.dask.org/en/stable/', None),
    'linkml': ('https://linkml.io/linkml/', None),
    'linkml_runtime': ('https://linkml.io/linkml/', None),
    'linkml-runtime': ('https://linkml.io/linkml/', None)
}


# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# graphviz
graphviz_output_format = "svg"

autodoc_pydantic_model_show_json_error_strategy = 'coerce'
autodoc_pydantic_model_show_json = False
autodoc_mock_imports = []
autoclass_content = "both"
autodoc_member_order='bysource'
add_module_names = False

autodoc_default_options = {
    'exclude-members': 'NDArray,Shape',
}

# --------------------------------------------------
# myst-nb
nb_render_markdown_format = 'myst'
nb_append_css = False

# --------------------------------------------------
# doctest
doctest_global_setup = """
from linkml_runtime.linkml_model import ClassDefinition, SlotDefinition, SchemaDefinition
from nwb_schema_language import Namespaces, Namespace, Dataset, Group, Schema
from linkml_runtime.dumpers import yaml_dumper
import yaml
from pydantic import BaseModel, Field
import numpy as np

from nwb_linkml.adapters import BuildResult
"""

# --------------------------------------------------
# Etc one-off settings

# todo
todo_include_todos = True
todo_link_only = True

