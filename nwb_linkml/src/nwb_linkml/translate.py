"""
Convenience functions for translating NWB schema

This module will be deprecated and removed in favor of :mod:`.providers`
"""
import tempfile
from typing import List, Optional, Dict
from types import ModuleType
from pathlib import Path
import json


import h5py
from linkml_runtime.dumpers import yaml_dumper

from nwb_schema_language import Namespaces
from nwb_linkml.io.schema import load_schema_file
from nwb_linkml.generators.pydantic import NWBPydanticGenerator
from nwb_linkml.maps.postload import apply_preload
from nwb_linkml.adapters import SchemaAdapter, NamespacesAdapter
#from nwb_linkml.models import core, hdmf_common

def make_namespace_adapter(schema: dict) -> NamespacesAdapter:
    """
    Create a :class:`.NamespacesAdapter` from a dictionary of loaded schema + namespace as are commonly
    serialized in nwbfiles under /specifications

    Args:
        schema: 

    Returns:

    """
    namespace = Namespaces(**schema['namespace'])
    schema_adapters = [] # type: List[SchemaAdapter]

    for schema_name, schema_dict in schema.items():
        if schema_name == 'namespace':
            continue
        path = Path(schema_name + '.yaml')
        schema_adapters.append(load_schema_file(path, schema_dict))

    ns_adapter = NamespacesAdapter(
        namespaces=namespace,
        schemas=schema_adapters
    )
    return ns_adapter

def populate_namespaces_imports(namespaces: List[NamespacesAdapter]) -> List[NamespacesAdapter]:
    """
    Given a set of :class:`.NamespacesAdapter`s, populate their imports with the other namespaces, if necessary
    """
    for ns in namespaces:
        needed_imports = []
        for imported_ns in ns.namespaces.namespaces:
            for imported_sch in imported_ns.schema_:
                if imported_sch.namespace and not imported_sch.source:
                    needed_imports.append(imported_sch.namespace)

        # find the import among the namespaces we have
        for other_ns in namespaces:
            if any([imported_ns.name in needed_imports for imported_ns in other_ns.namespaces.namespaces]):
                ns.imported.append(other_ns)
    return namespaces

def translate_namespaces(namespaces: NamespacesAdapter, base_dir: Path) -> List[Path]:
    """
    Write translated namespaces to disk
    """
    built_schemas = namespaces.build().schemas
    base_dir = Path(base_dir)

    paths = []
    for schema in built_schemas:
        output_file = base_dir / (schema.name + '.yaml')
        paths.append(output_file)
        yaml_dumper.dump(schema, output_file)
    return paths

def generate_pydantic(
        namespaces: NamespacesAdapter,
        schema_dir:Optional[Path]=None,
        pydantic_dir:Optional[Path]=None
) -> ModuleType:
    if schema_dir is None:
        temp_schema_dir = tempfile.TemporaryDirectory()
        schema_dir = Path(temp_schema_dir.name)
    if pydantic_dir is None:
        temp_pydantic_dir = tempfile.TemporaryDirectory()
        pydantic_dir = Path(temp_pydantic_dir.name)

    if any(schema_dir.glob('*.yaml')):
        # read already generated schema, do nothing here
        schema_paths = list(schema_dir.glob('*.yaml'))
    else:
        # generate schema files
        schema_paths = translate_namespaces(namespaces, base_dir=schema_dir)

    # just generate the namespace file, which should import everything

    ns_file = [s_path for s_path in schema_paths if s_path.stem == namespaces.namespaces.namespaces[0].name]
    if len(ns_file) == 0:
        raise ValueError("Could not find main namespace file")
    ns_file = ns_file[0]

    generator = NWBPydanticGenerator(
        str(ns_file),
        split=False,
        emit_metadata=True,
        gen_classvars=True,
        gen_slots=True,
        pydantic_version='2'
    )
    serialized = generator.serialize()
    with open(pydantic_dir / 'models.py', 'w') as mfile:
        mfile.write(serialized)
    module = generator.compile_module(pydantic_dir)
    return module

def generate_from_nwbfile(path:Path) -> Dict[str, ModuleType]:
    namespaces = []
    h5f = h5py.File(path, 'r')
    for ns_name, ns in h5f['specifications'].items():
        #if ns_name in ('core', 'hdmf-common'):
        #    continue
        ns_schema = {}
        for version in ns.values():
            for schema_name, schema in version.items():
                # read the source json binary string
                sch_str = schema[()]
                sch_dict = json.loads(sch_str)
                ns_schema[schema_name] = apply_preload(sch_dict)
        namespaces.append(ns_schema)

    adapters = [make_namespace_adapter(sch) for sch in namespaces]
    adapters = populate_namespaces_imports(adapters)
    pydantic_modules = {
        adapter.namespaces.namespaces[0].name: generate_pydantic(adapter)
        for adapter in adapters
    }
    #pydantic_modules.update({'core': core, 'hdmf-common': hdmf_common})
    return pydantic_modules











