import pytest
import os
from typing import NamedTuple

from linkml_runtime.dumpers import yaml_dumper

from nwb_linkml.io import schema as io
from nwb_linkml.adapters.namespaces import NamespacesAdapter
from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition, SlotDefinition, Prefix, TypeDefinition
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def tmp_output_dir() -> Path:
    path = Path(__file__).parent.resolve() / '__tmp__'
    if path.exists():
        shutil.rmtree(str(path))
    path.mkdir()

    return path

@pytest.fixture(scope="function")
def tmp_output_dir_func(tmp_output_dir) -> Path:
    """
    tmp output dir that gets cleared between every function
    cleans at the start rather than at cleanup in case the output is to be inspected
    """
    subpath = tmp_output_dir / '__tmp__'
    if subpath.exists():
        shutil.rmtree(str(subpath))
    subpath.mkdir()
    return subpath

@pytest.fixture(scope="module")
def tmp_output_dir_mod(tmp_output_dir) -> Path:
    """
    tmp output dir that gets cleared between every function
    cleans at the start rather than at cleanup in case the output is to be inspected
    """
    subpath = tmp_output_dir / '__tmp__'
    if subpath.exists():
        shutil.rmtree(str(subpath))
    subpath.mkdir()
    return subpath

@pytest.fixture(autouse=True, scope='session')
def set_config_vars(tmp_output_dir):
    os.environ['NWB_LINKML_CACHE_DIR'] = str(tmp_output_dir)



@pytest.fixture(scope="session")
def nwb_core_fixture() -> NamespacesAdapter:
    nwb_core = io.load_nwb_core()
    nwb_core.populate_imports()
    return nwb_core


@pytest.fixture(scope="session")
def data_dir() -> Path:
    path = Path(__file__).parent.resolve() / 'data'
    return path

class TestSchemas(NamedTuple):
    core: SchemaDefinition
    core_path: Path
    imported: SchemaDefinition
    imported_path: Path
    namespace: SchemaDefinition
    namespace_path: Path

@pytest.fixture(scope="module")
def linkml_schema(tmp_output_dir_mod) -> TestSchemas:
    """
    A test schema that includes

    - Two schemas, one importing from the other
    - Arraylike
    - Required/static "name" field
    - linkml metadata like tree_root
    - skipping classes
    """
    test_schema_path = tmp_output_dir_mod / 'test_schema'
    test_schema_path.mkdir()

    core_path = test_schema_path / 'core.yaml'
    imported_path = test_schema_path / 'imported.yaml'
    namespace_path = test_schema_path / 'namespace.yaml'

    schema = TestSchemas(
        core_path=core_path,
        imported_path=imported_path,
        namespace_path=namespace_path,
        core=SchemaDefinition(
            name="core",
            id="core",
            version="1.0.1",
            imports=["imported",'linkml:types'],
            default_prefix="core",
            prefixes={'linkml': Prefix('linkml','https://w3id.org/linkml')},
            description="Test core schema",
            classes=[
                ClassDefinition(
                    name="MainTopLevel",
                    description="The main class we are testing!",
                    is_a="MainThing",
                    tree_root=True,
                    attributes=[
                        SlotDefinition(
                            name="name",
                            description="A fixed property that should use Literal and be frozen",
                            range="string",
                            required=True,
                            ifabsent="string(toplevel)",
                            equals_string="toplevel",
                            identifier=True
                        ),
                        SlotDefinition(
                            name="array",
                            range="MainTopLevel__Array"
                        ),
                        SlotDefinition(
                            name="SkippableSlot",
                            description="A slot that was meant to be skipped!"
                        ),
                        SlotDefinition(
                            name="inline_dict",
                            description="This should be inlined as a dictionary despite this class having an identifier",
                            multivalued=True,
                            inlined=True,
                            inlined_as_list=False,
                            any_of=[{'range': 'OtherClass'}, {'range': 'StillAnotherClass'} ]
                        )
                    ]
                ),
                ClassDefinition(
                    name="MainTopLevel__Array",
                    description="Main class's array",
                    is_a="Arraylike",
                    attributes=[
                        SlotDefinition(
                            name="x",
                            range="numeric",
                            required=True
                        ),
                        SlotDefinition(
                            name="y",
                            range="numeric",
                            required=True
                        ),
                        SlotDefinition(
                            name="z",
                            range="numeric",
                            required=False,
                            maximum_cardinality=3,
                            minimum_cardinality=3
                        ),
                        SlotDefinition(
                            name="a",
                            range="numeric",
                            required=False,
                            minimum_cardinality=4,
                            maximum_cardinality=4
                        )
                    ]
                ),
                ClassDefinition(
                    name="skippable",
                    description="A class that lives to be skipped!",

                ),
                ClassDefinition(
                    name="OtherClass",
                    description="Another class yno!",
                    attributes=[
                        SlotDefinition(
                            name="name",
                            range="string",
                            required=True,
                            identifier=True
                        )
                    ]
                ),
                ClassDefinition(
                    name="StillAnotherClass",
                    description="And yet another!",
                    attributes=[
                        SlotDefinition(
                            name="name",
                            range="string",
                            required=True,
                            identifier=True
                        )
                    ]
                )
            ],
            types=[
                TypeDefinition(
                    name="numeric",
                    typeof="float"
                )
            ]
        ),
        imported=SchemaDefinition(
            name="imported",
            id="imported",
            version="1.4.5",
            default_prefix="core",
            imports=['linkml:types'],
            prefixes = {'linkml': Prefix('linkml', 'https://w3id.org/linkml')},
            classes = [
                ClassDefinition(
                    name="MainThing",
                    description="Class imported by our main thing class!",
                    attributes=[
                        SlotDefinition(
                            name="meta_slot",
                            range="string"
                        )
                    ]
                ),
                ClassDefinition(
                    name="Arraylike",
                    abstract=True
                )
            ]
        ),
        namespace=SchemaDefinition(
            name="namespace",
            id="namespace",
            version="1.1.1",
            default_prefix="namespace",
            annotations={'namespace': {'tag': 'namespace', 'value': 'True'}},
            description="A namespace package that should import all other classes",
            imports=['core', 'imported']
        )
    )
    yaml_dumper.dump(schema.core, schema.core_path)
    yaml_dumper.dump(schema.imported, schema.imported_path)
    yaml_dumper.dump(schema.namespace, schema.namespace_path)
    return schema

