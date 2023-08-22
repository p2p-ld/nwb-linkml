"""
Loading/saving NWB Schema yaml files
"""
from pathlib import Path
from typing import TypedDict, List, Dict
from pprint import pprint
import warnings

from linkml_runtime.loaders import yaml_loader
import yaml

from nwb_schema_language import Namespaces,  Group, Dataset
from nwb_linkml.namespaces import NamespaceRepo, NWB_CORE_REPO, HDMF_COMMON_REPO
from nwb_linkml.maps import preload
from nwb_linkml.map import PHASES, Map
from nwb_linkml.adapters.namespaces import NamespacesAdapter
from nwb_linkml.adapters.schema import SchemaAdapter


def load_yaml(path:Path) -> dict:
    with open(path, 'r') as file:
        ns_dict = yaml.safe_load(file)

    # apply maps
    maps = [m for m in Map.instances if m.phase == PHASES.postload]
    for amap in maps:
        ns_dict = amap.apply(ns_dict)
    return ns_dict

def load_namespaces(path:Path|NamespaceRepo) -> Namespaces:
    if isinstance(path, NamespaceRepo):
        path = path.provide_from_git()

    ns_dict = load_yaml(path)


    namespaces = yaml_loader.load(ns_dict, target_class=Namespaces)
    return namespaces



def load_schema_file(path:Path) -> SchemaAdapter:
    source = load_yaml(path)

    datasets = []

    for dataset in source.get('datasets', []):
        try:
            datasets.append(Dataset(**dataset))
        except Exception as e:
            pprint(dataset)
            raise e

    groups = []
    for group in source.get('groups', []):
        try:
            groups.append(Group(**group))
        except Exception as e:
            pprint(group)
            raise e

    schema = SchemaAdapter(
        path=path,
        datasets=datasets,
        groups=groups
    )
    return schema

def load_namespace_schema(namespace: Namespaces, path:Path=Path('.')) -> NamespacesAdapter:
    """
    Load all schema referenced by a namespace file

    Args:
        namespace (:class:`.Namespace`):
        path (:class:`pathlib.Path`): Location of the namespace file - all relative paths are interpreted relative to this

    Returns:
        :class:`.NamespacesAdapter`
    """

    path = Path(path).resolve()
    if path.is_file():
        # given the namespace file itself, so find paths relative to its directory
        path = path.parent

    sch = []
    for ns in namespace.namespaces:
        for schema in ns.schema_:
            if schema.source is None:
                warnings.warn(f"No source specified for {schema}")
                continue
            yml_file = (path / schema.source).resolve()
            sch.append(load_schema_file(yml_file))

    adapter = NamespacesAdapter(
        namespaces=namespace,
        schemas=sch
    )

    return adapter

def load_nwb_core() -> NamespacesAdapter:
    # First get hdmf-common:
    hdmf_ns_file = HDMF_COMMON_REPO.provide_from_git()
    hdmf_ns = load_namespaces(hdmf_ns_file)
    hdmf_schema = load_namespace_schema(hdmf_ns, hdmf_ns_file)

    namespace_file = NWB_CORE_REPO.provide_from_git()
    ns = load_namespaces(namespace_file)
    schema = load_namespace_schema(ns, namespace_file)

    schema.imported.append(hdmf_schema)

    return schema













