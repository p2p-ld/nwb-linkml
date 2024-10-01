"""
Various visualization routines, mostly to help development for now
"""

import random
from typing import TYPE_CHECKING, List, Optional, TypedDict

import dash_cytoscape as cyto
from dash import Dash, html
from rich import print

from nwb_linkml.io.schema import load_nwb_core
from nwb_schema_language import Dataset, Group, Namespace

if TYPE_CHECKING:
    from nwb_linkml.adapters import NamespacesAdapter

# ruff: noqa: D101
# ruff: noqa: D102
# ruff: noqa: D103

cyto.load_extra_layouts()


class _CytoNode(TypedDict):
    id: str
    label: str


class _CytoEdge(TypedDict):
    source: str
    target: str


class CytoElement(TypedDict):
    data: _CytoEdge | _CytoNode
    classes: Optional[str]


class Node:
    def __init__(self, id: str, label: str, klass: str, parent: Optional[str] = None):
        self.id = id
        self.label = label
        self.parent = parent
        self.klass = klass

    def make(self) -> List[CytoElement]:

        node = [CytoElement(data=_CytoNode(id=self.id, label=self.label), classes=self.klass)]
        if self.parent:
            edge = [CytoElement(data=_CytoEdge(source=self.parent, target=self.id))]
            node += edge

        return node


def make_node(
    element: Group | Dataset, parent: Optional[str] = None, recurse: bool = True
) -> List[Node]:
    if element.neurodata_type_def is None:
        if element.name is None:
            name = "anonymous" if element.neurodata_type_inc is None else element.neurodata_type_inc
        else:
            name = element.name
        id = name + "-" + str(random.randint(0, 1000))
        label = id
        classname = str(type(element).__name__).lower() + "-child"
    else:
        id = element.neurodata_type_def
        label = element.neurodata_type_def
        classname = str(type(element).__name__).lower()

    if parent is None:
        parent = element.neurodata_type_inc

    node = Node(id=id, label=label, parent=parent, klass=classname)
    nodes = [node]

    if isinstance(element, Group) and recurse:
        for group in element.groups:
            nodes += make_node(group, parent=id)
        for dataset in element.datasets:
            nodes += make_node(dataset, parent=id)
    return nodes


def make_graph(namespaces: "NamespacesAdapter", recurse: bool = True) -> List[CytoElement]:
    namespaces.complete_namespaces()
    nodes = []
    element: Namespace | Group | Dataset
    print("walking graph")
    for element in namespaces.walk_types(namespaces, (Group, Dataset)):
        if element.neurodata_type_def is None:
            # skip child nodes at top level, we'll get them in recursion
            continue
        if any([element.neurodata_type_def == node.id for node in nodes]):
            continue
        nodes.extend(make_node(element, recurse=recurse))

    print("making elements")
    cytoelements = []
    for node in nodes:
        cytoelements += node.make()
    print(cytoelements)
    return cytoelements


def plot_dependency_graph(namespaces: "NamespacesAdapter", recurse: bool = True) -> Dash:
    graph = make_graph(namespaces, recurse=recurse)

    app = Dash(__name__)

    styles = [
        {"selector": "node", "style": {"content": "data(label)"}},
        {"selector": ".dataset", "style": {"background-color": "red", "shape": "rectangle"}},
        {"selector": ".group", "style": {"background-color": "blue", "shape": "rectangle"}},
        {"selector": ".dataset-child", "style": {"background-color": "red"}},
        {"selector": ".group-child", "style": {"background-color": "blue"}},
    ]

    app.layout = html.Div(
        [
            cyto.Cytoscape(
                id="nwb_graph",
                elements=graph,
                style={"width": "100%", "height": "100vh"},
                layout={"name": "klay", "rankDir": "LR"},
                stylesheet=styles,
            )
        ]
    )
    return app


if __name__ == "__main__":
    core = load_nwb_core()
    app = plot_dependency_graph(core, recurse=True)
    print("opening dash")
    app.run(debug=True)
