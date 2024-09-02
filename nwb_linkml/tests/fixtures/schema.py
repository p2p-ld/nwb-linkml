from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Dict, Optional

import pytest
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import (
    ClassDefinition,
    Prefix,
    SchemaDefinition,
    SlotDefinition,
    TypeDefinition,
)

from nwb_linkml.adapters import NamespacesAdapter
from nwb_linkml.io import schema as io
from nwb_linkml.providers import LinkMLProvider, PydanticProvider
from nwb_linkml.providers.linkml import LinkMLSchemaBuild
from nwb_schema_language import Attribute, Dataset, Group


@pytest.fixture(scope="session", params=[{"core_version": "2.7.0", "hdmf_version": "1.8.0"}])
def nwb_core_fixture(request) -> NamespacesAdapter:
    nwb_core = io.load_nwb_core(**request.param)
    assert (
        request.param["core_version"] in nwb_core.versions["core"]
    )  # 2.6.0 is actually 2.6.0-alpha
    assert nwb_core.versions["hdmf-common"] == request.param["hdmf_version"]

    return nwb_core


@pytest.fixture(scope="session")
def nwb_core_linkml(nwb_core_fixture, tmp_output_dir) -> LinkMLSchemaBuild:
    provider = LinkMLProvider(tmp_output_dir, allow_repo=False, verbose=False)
    result = provider.build(ns_adapter=nwb_core_fixture, force=True)
    return result["core"]


@pytest.fixture(scope="session")
def nwb_core_module(nwb_core_linkml: LinkMLSchemaBuild, tmp_output_dir) -> ModuleType:
    """
    Generated pydantic namespace from nwb core
    """
    provider = PydanticProvider(tmp_output_dir, verbose=False)
    result = provider.build(nwb_core_linkml.namespace, force=True)
    mod = provider.get("core", version=nwb_core_linkml.version, allow_repo=False)
    return mod


@dataclass
class TestSchemas:
    __test__ = False
    core: SchemaDefinition
    imported: SchemaDefinition
    namespace: SchemaDefinition
    core_path: Optional[Path] = None
    imported_path: Optional[Path] = None
    namespace_path: Optional[Path] = None


@pytest.fixture(scope="module")
def linkml_schema_bare() -> TestSchemas:

    schema = TestSchemas(
        core=SchemaDefinition(
            name="core",
            id="core",
            version="1.0.1",
            imports=["imported", "linkml:types"],
            default_prefix="core",
            prefixes={"linkml": Prefix("linkml", "https://w3id.org/linkml")},
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
                            identifier=True,
                        ),
                        SlotDefinition(name="array", range="MainTopLevel__Array"),
                        SlotDefinition(
                            name="SkippableSlot", description="A slot that was meant to be skipped!"
                        ),
                        SlotDefinition(
                            name="inline_dict",
                            description=(
                                "This should be inlined as a dictionary despite this class having"
                                " an identifier"
                            ),
                            multivalued=True,
                            inlined=True,
                            inlined_as_list=False,
                            any_of=[{"range": "OtherClass"}, {"range": "StillAnotherClass"}],
                        ),
                    ],
                ),
                ClassDefinition(
                    name="MainTopLevel__Array",
                    description="Main class's array",
                    is_a="Arraylike",
                    attributes=[
                        SlotDefinition(name="x", range="numeric", required=True),
                        SlotDefinition(name="y", range="numeric", required=True),
                        SlotDefinition(
                            name="z",
                            range="numeric",
                            required=False,
                            maximum_cardinality=3,
                            minimum_cardinality=3,
                        ),
                        SlotDefinition(
                            name="a",
                            range="numeric",
                            required=False,
                            minimum_cardinality=4,
                            maximum_cardinality=4,
                        ),
                    ],
                ),
                ClassDefinition(
                    name="skippable",
                    description="A class that lives to be skipped!",
                ),
                ClassDefinition(
                    name="OtherClass",
                    description="Another class yno!",
                    attributes=[
                        SlotDefinition(name="name", range="string", required=True, identifier=True)
                    ],
                ),
                ClassDefinition(
                    name="StillAnotherClass",
                    description="And yet another!",
                    attributes=[
                        SlotDefinition(name="name", range="string", required=True, identifier=True)
                    ],
                ),
            ],
            types=[TypeDefinition(name="numeric", typeof="float")],
        ),
        imported=SchemaDefinition(
            name="imported",
            id="imported",
            version="1.4.5",
            default_prefix="core",
            imports=["linkml:types"],
            prefixes={"linkml": Prefix("linkml", "https://w3id.org/linkml")},
            classes=[
                ClassDefinition(
                    name="MainThing",
                    description="Class imported by our main thing class!",
                    attributes=[SlotDefinition(name="meta_slot", range="string")],
                ),
                ClassDefinition(name="Arraylike", abstract=True),
            ],
        ),
        namespace=SchemaDefinition(
            name="namespace",
            id="namespace",
            version="1.1.1",
            default_prefix="namespace",
            annotations=[
                {"tag": "is_namespace", "value": "True"},
                {"tag": "namespace", "value": "core"},
            ],
            description="A namespace package that should import all other classes",
            imports=["core", "imported"],
        ),
    )
    return schema


@pytest.fixture(scope="module")
def linkml_schema(tmp_output_dir_mod, linkml_schema_bare) -> TestSchemas:
    """
    A test schema that includes

    - Two schemas, one importing from the other
    - Arraylike
    - Required/static "name" field
    - linkml metadata like tree_root
    - skipping classes
    """
    schema = linkml_schema_bare

    test_schema_path = tmp_output_dir_mod / "test_schema"
    test_schema_path.mkdir()

    core_path = test_schema_path / "core.yaml"
    imported_path = test_schema_path / "imported.yaml"
    namespace_path = test_schema_path / "namespace.yaml"

    schema.core_path = core_path
    schema.imported_path = imported_path
    schema.namespace_path = namespace_path

    yaml_dumper.dump(schema.core, schema.core_path)
    yaml_dumper.dump(schema.imported, schema.imported_path)
    yaml_dumper.dump(schema.namespace, schema.namespace_path)
    return schema


@dataclass
class NWBSchemaTest:
    datasets: Dict[str, Dataset] = field(default_factory=dict)
    groups: Dict[str, Group] = field(default_factory=dict)


@pytest.fixture()
def nwb_schema() -> NWBSchemaTest:
    """Minimal NWB schema for testing"""
    image = Dataset(
        neurodata_type_def="Image",
        dtype="numeric",
        neurodata_type_inc="NWBData",
        dims=[["x", "y"], ["x", "y", "r, g, b"], ["x", "y", "r, g, b, a"]],
        shape=[[None, None], [None, None, 3], [None, None, 4]],
        doc="An image!",
        attributes=[
            Attribute(dtype="float32", name="resolution", doc="resolution!"),
            Attribute(dtype="text", name="description", doc="Description!"),
        ],
    )
    images = Group(
        neurodata_type_def="Images",
        neurodata_type_inc="NWBDataInterface",
        default_name="Images",
        doc="Images!",
        attributes=[Attribute(dtype="text", name="description", doc="description!")],
        datasets=[
            Dataset(neurodata_type_inc="Image", quantity="+", doc="images!"),
            Dataset(
                neurodata_type_inc="ImageReferences",
                name="order_of_images",
                doc="Image references!",
                quantity="?",
            ),
        ],
    )
    return NWBSchemaTest(datasets={"image": image}, groups={"images": images})
