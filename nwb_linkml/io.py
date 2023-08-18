"""
Loading/saving NWB Schema yaml files
"""
from pathlib import Path
from typing import TypedDict, List
from pprint import pprint

from linkml_runtime.loaders import yaml_loader
import yaml

from nwb_schema_language import Namespaces, Group, Dataset
from nwb_linkml.namespaces import GitRepo, NamespaceRepo, NWB_CORE_REPO



def load_namespaces(path:Path|NamespaceRepo) -> Namespaces:
    if isinstance(path, NamespaceRepo):
        path = path.provide_from_git()

    namespaces = yaml_loader.load(str(path), target_class=Namespaces)
    return namespaces

class SchemaFile(TypedDict):
    datasets: List[Dataset]
    groups: List[Group]

def load_schema_file(path:Path) -> List[Dataset | Group]:
    with open(path, 'r') as yfile:
        source = yaml.safe_load(yfile)

    schema = []

    for dataset in source.get('datasets', []):
        try:
            schema.append(Dataset(**dataset))
        except Exception as e:
            pprint(dataset)
            raise e

    #schema.extend([Dataset(**dataset) for dataset in source.get('datasets', [])])
    #schema.extend([Group(**group) for group in source.get('groups', [])])
    return schema

def load_nwb_core():
    namespace_file = NWB_CORE_REPO.provide_from_git()
    ns = load_namespaces(namespace_file)










