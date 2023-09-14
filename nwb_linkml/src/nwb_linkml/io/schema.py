"""
Loading/saving NWB Schema yaml files
"""
from pathlib import Path
from typing import Optional
from pprint import pprint

from linkml_runtime.loaders import yaml_loader
import yaml

from nwb_schema_language import Namespaces,  Group, Dataset
from nwb_linkml.providers.git import NamespaceRepo, NWB_CORE_REPO, HDMF_COMMON_REPO
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

def _load_namespaces(path:Path|NamespaceRepo) -> Namespaces:
    """Loads the NWB SCHEMA LANGUAGE namespaces (not the namespacesadapter)"""
    if isinstance(path, NamespaceRepo):
        path = path.provide_from_git()

    ns_dict = load_yaml(path)

    namespaces = yaml_loader.load(ns_dict, target_class=Namespaces)
    return namespaces

def load_schema_file(path:Path, yaml:Optional[dict] = None) -> SchemaAdapter:
    if yaml is not None:
        source = yaml
        # apply maps
        maps = [m for m in Map.instances if m.phase == PHASES.postload]
        for amap in maps:
            source = amap.apply(source)
    else:
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

def load_namespace_adapter(namespace: Path | NamespaceRepo | Namespaces, path:Optional[Path]=None) -> NamespacesAdapter:
    """
    Load all schema referenced by a namespace file

    Args:
        namespace (:class:`:class:`.Namespace`):
        path (:class:`pathlib.Path`): Location of the namespace file - all relative paths are interpreted relative to this

    Returns:
        :class:`.NamespacesAdapter`
    """
    if path is None:
        path = Path('..')

    if isinstance(namespace, Path):
        path = namespace
        namespaces = _load_namespaces(path)
    elif isinstance(namespace, NamespaceRepo):
        path = namespace.provide_from_git()
        namespaces = _load_namespaces(namespace)

    elif isinstance(namespace, Namespaces):
        namespaces = namespace
    else:
        raise ValueError(f"Namespace must be a path, namespace repo, or already loaded namespaces")


    if path.is_file():
        # given the namespace file itself, so find paths relative to its directory
        path = path.parent

    sch = []
    for ns in namespaces.namespaces:
        for schema in ns.schema_:
            if schema.source is None:
                # this is normal, we'll resolve later
                continue
            yml_file = (path / schema.source).resolve()
            sch.append(load_schema_file(yml_file))

    adapter = NamespacesAdapter(
        namespaces=namespaces,
        schemas=sch
    )

    return adapter

def load_nwb_core() -> NamespacesAdapter:
    # First get hdmf-common:
    hdmf_schema = load_namespace_adapter(HDMF_COMMON_REPO)
    schema = load_namespace_adapter(NWB_CORE_REPO)

    schema.imported.append(hdmf_schema)

    return schema














