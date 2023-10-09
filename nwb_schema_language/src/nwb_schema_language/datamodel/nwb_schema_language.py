# Auto generated from nwb_schema_language.yaml by pythongen.py version: 0.0.1
# Generation date: 2023-10-09T15:03:09
# Schema: nwb-schema-language
#
# id: https://w3id.org/p2p_ld/nwb-schema-language
# description: Translation of the nwb-schema-language to LinkML
# license: GNU GPL v3.0

import dataclasses
import re
from jsonasobj2 import JsonObj, as_dict
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from linkml_runtime.linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml_runtime.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.formatutils import camelcase, underscore, sfx
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.linkml_model.types import Boolean, Datetime, String
from linkml_runtime.utils.metamodelcore import Bool, XSDDateTime

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
NWB_SCHEMA_LANGUAGE = CurieNamespace('nwb_schema_language', 'https://w3id.org/p2p_ld/nwb-schema-language/')
SCHEMA = CurieNamespace('schema', 'http://schema.org/')
DEFAULT_ = NWB_SCHEMA_LANGUAGE


# Types

# Class references



@dataclass
class Namespace(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Namespace
    class_class_curie: ClassVar[str] = "nwb_schema_language:Namespace"
    class_name: ClassVar[str] = "Namespace"
    class_model_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Namespace

    doc: str = None
    name: str = None
    version: str = None
    author: Union[str, List[str]] = None
    contact: Union[str, List[str]] = None
    full_name: Optional[str] = None
    date: Optional[Union[str, XSDDateTime]] = None
    schema_: Optional[Union[Union[dict, "Schema"], List[Union[dict, "Schema"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.doc):
            self.MissingRequiredField("doc")
        if not isinstance(self.doc, str):
            self.doc = str(self.doc)

        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, str):
            self.name = str(self.name)

        if self._is_empty(self.version):
            self.MissingRequiredField("version")
        if not isinstance(self.version, str):
            self.version = str(self.version)

        if self._is_empty(self.author):
            self.MissingRequiredField("author")
        if not isinstance(self.author, list):
            self.author = [self.author] if self.author is not None else []
        self.author = [v if isinstance(v, str) else str(v) for v in self.author]

        if self._is_empty(self.contact):
            self.MissingRequiredField("contact")
        if not isinstance(self.contact, list):
            self.contact = [self.contact] if self.contact is not None else []
        self.contact = [v if isinstance(v, str) else str(v) for v in self.contact]

        if self.full_name is not None and not isinstance(self.full_name, str):
            self.full_name = str(self.full_name)

        if self.date is not None and not isinstance(self.date, XSDDateTime):
            self.date = XSDDateTime(self.date)

        if not isinstance(self.schema_, list):
            self.schema_ = [self.schema_] if self.schema_ is not None else []
        self.schema_ = [v if isinstance(v, Schema) else Schema(**as_dict(v)) for v in self.schema_]

        super().__post_init__(**kwargs)


@dataclass
class Namespaces(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Namespaces
    class_class_curie: ClassVar[str] = "nwb_schema_language:Namespaces"
    class_name: ClassVar[str] = "Namespaces"
    class_model_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Namespaces

    namespaces: Optional[Union[Union[dict, Namespace], List[Union[dict, Namespace]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.namespaces, list):
            self.namespaces = [self.namespaces] if self.namespaces is not None else []
        self.namespaces = [v if isinstance(v, Namespace) else Namespace(**as_dict(v)) for v in self.namespaces]

        super().__post_init__(**kwargs)


@dataclass
class Schema(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Schema
    class_class_curie: ClassVar[str] = "nwb_schema_language:Schema"
    class_name: ClassVar[str] = "Schema"
    class_model_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Schema

    source: Optional[str] = None
    namespace: Optional[str] = None
    title: Optional[str] = None
    neurodata_types: Optional[Union[str, List[str]]] = empty_list()
    doc: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.source is not None and not isinstance(self.source, str):
            self.source = str(self.source)

        if self.namespace is not None and not isinstance(self.namespace, str):
            self.namespace = str(self.namespace)

        if self.title is not None and not isinstance(self.title, str):
            self.title = str(self.title)

        if not isinstance(self.neurodata_types, list):
            self.neurodata_types = [self.neurodata_types] if self.neurodata_types is not None else []
        self.neurodata_types = [v if isinstance(v, str) else str(v) for v in self.neurodata_types]

        if self.doc is not None and not isinstance(self.doc, str):
            self.doc = str(self.doc)

        super().__post_init__(**kwargs)


@dataclass
class Group(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Group
    class_class_curie: ClassVar[str] = "nwb_schema_language:Group"
    class_name: ClassVar[str] = "Group"
    class_model_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Group

    doc: str = None
    neurodata_type_def: Optional[str] = None
    neurodata_type_inc: Optional[str] = None
    name: Optional[str] = None
    default_name: Optional[str] = None
    quantity: Optional[str] = 1
    linkable: Optional[Union[bool, Bool]] = None
    attributes: Optional[Union[Union[dict, "Attribute"], List[Union[dict, "Attribute"]]]] = empty_list()
    datasets: Optional[Union[Union[dict, "Dataset"], List[Union[dict, "Dataset"]]]] = empty_list()
    groups: Optional[Union[Union[dict, "Group"], List[Union[dict, "Group"]]]] = empty_list()
    links: Optional[Union[Union[dict, "Link"], List[Union[dict, "Link"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.doc):
            self.MissingRequiredField("doc")
        if not isinstance(self.doc, str):
            self.doc = str(self.doc)

        if self.neurodata_type_def is not None and not isinstance(self.neurodata_type_def, str):
            self.neurodata_type_def = str(self.neurodata_type_def)

        if self.neurodata_type_inc is not None and not isinstance(self.neurodata_type_inc, str):
            self.neurodata_type_inc = str(self.neurodata_type_inc)

        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.default_name is not None and not isinstance(self.default_name, str):
            self.default_name = str(self.default_name)

        if self.quantity is not None and not isinstance(self.quantity, str):
            self.quantity = str(self.quantity)

        if self.linkable is not None and not isinstance(self.linkable, Bool):
            self.linkable = Bool(self.linkable)

        self._normalize_inlined_as_dict(slot_name="attributes", slot_type=Attribute, key_name="name", keyed=False)

        if not isinstance(self.datasets, list):
            self.datasets = [self.datasets] if self.datasets is not None else []
        self.datasets = [v if isinstance(v, Dataset) else Dataset(**as_dict(v)) for v in self.datasets]

        if not isinstance(self.groups, list):
            self.groups = [self.groups] if self.groups is not None else []
        self.groups = [v if isinstance(v, Group) else Group(**as_dict(v)) for v in self.groups]

        self._normalize_inlined_as_dict(slot_name="links", slot_type=Link, key_name="doc", keyed=False)

        super().__post_init__(**kwargs)


@dataclass
class Groups(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Groups
    class_class_curie: ClassVar[str] = "nwb_schema_language:Groups"
    class_name: ClassVar[str] = "Groups"
    class_model_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Groups

    groups: Optional[Union[Union[dict, Group], List[Union[dict, Group]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.groups, list):
            self.groups = [self.groups] if self.groups is not None else []
        self.groups = [v if isinstance(v, Group) else Group(**as_dict(v)) for v in self.groups]

        super().__post_init__(**kwargs)


@dataclass
class Attribute(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Attribute
    class_class_curie: ClassVar[str] = "nwb_schema_language:Attribute"
    class_name: ClassVar[str] = "Attribute"
    class_model_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Attribute

    name: str = None
    doc: str = None
    dims: Optional[Union[str, List[str]]] = empty_list()
    shape: Optional[Union[str, List[str]]] = empty_list()
    value: Optional[Union[dict, "AnyType"]] = None
    default_value: Optional[Union[dict, "AnyType"]] = None
    required: Optional[Union[bool, Bool]] = True
    dtype: Optional[Union[str, List[str]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, str):
            self.name = str(self.name)

        if self._is_empty(self.doc):
            self.MissingRequiredField("doc")
        if not isinstance(self.doc, str):
            self.doc = str(self.doc)

        if not isinstance(self.dims, list):
            self.dims = [self.dims] if self.dims is not None else []
        self.dims = [v if isinstance(v, str) else str(v) for v in self.dims]

        if not isinstance(self.shape, list):
            self.shape = [self.shape] if self.shape is not None else []
        self.shape = [v if isinstance(v, str) else str(v) for v in self.shape]

        if self.required is not None and not isinstance(self.required, Bool):
            self.required = Bool(self.required)

        if not isinstance(self.dtype, list):
            self.dtype = [self.dtype] if self.dtype is not None else []
        self.dtype = [v if isinstance(v, str) else str(v) for v in self.dtype]

        super().__post_init__(**kwargs)


@dataclass
class Link(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Link
    class_class_curie: ClassVar[str] = "nwb_schema_language:Link"
    class_name: ClassVar[str] = "Link"
    class_model_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Link

    doc: str = None
    target_type: str = None
    name: Optional[str] = None
    quantity: Optional[str] = 1

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.doc):
            self.MissingRequiredField("doc")
        if not isinstance(self.doc, str):
            self.doc = str(self.doc)

        if self._is_empty(self.target_type):
            self.MissingRequiredField("target_type")
        if not isinstance(self.target_type, str):
            self.target_type = str(self.target_type)

        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.quantity is not None and not isinstance(self.quantity, str):
            self.quantity = str(self.quantity)

        super().__post_init__(**kwargs)


@dataclass
class Dataset(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Dataset
    class_class_curie: ClassVar[str] = "nwb_schema_language:Dataset"
    class_name: ClassVar[str] = "Dataset"
    class_model_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Dataset

    doc: str = None
    neurodata_type_def: Optional[str] = None
    neurodata_type_inc: Optional[str] = None
    name: Optional[str] = None
    default_name: Optional[str] = None
    dims: Optional[Union[str, List[str]]] = empty_list()
    shape: Optional[Union[str, List[str]]] = empty_list()
    value: Optional[Union[dict, "AnyType"]] = None
    default_value: Optional[Union[dict, "AnyType"]] = None
    quantity: Optional[str] = 1
    linkable: Optional[Union[bool, Bool]] = None
    attributes: Optional[Union[Union[dict, Attribute], List[Union[dict, Attribute]]]] = empty_list()
    dtype: Optional[Union[str, List[str]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.doc):
            self.MissingRequiredField("doc")
        if not isinstance(self.doc, str):
            self.doc = str(self.doc)

        if self.neurodata_type_def is not None and not isinstance(self.neurodata_type_def, str):
            self.neurodata_type_def = str(self.neurodata_type_def)

        if self.neurodata_type_inc is not None and not isinstance(self.neurodata_type_inc, str):
            self.neurodata_type_inc = str(self.neurodata_type_inc)

        if self.name is not None and not isinstance(self.name, str):
            self.name = str(self.name)

        if self.default_name is not None and not isinstance(self.default_name, str):
            self.default_name = str(self.default_name)

        if not isinstance(self.dims, list):
            self.dims = [self.dims] if self.dims is not None else []
        self.dims = [v if isinstance(v, str) else str(v) for v in self.dims]

        if not isinstance(self.shape, list):
            self.shape = [self.shape] if self.shape is not None else []
        self.shape = [v if isinstance(v, str) else str(v) for v in self.shape]

        if self.quantity is not None and not isinstance(self.quantity, str):
            self.quantity = str(self.quantity)

        if self.linkable is not None and not isinstance(self.linkable, Bool):
            self.linkable = Bool(self.linkable)

        self._normalize_inlined_as_dict(slot_name="attributes", slot_type=Attribute, key_name="name", keyed=False)

        if not isinstance(self.dtype, list):
            self.dtype = [self.dtype] if self.dtype is not None else []
        self.dtype = [v if isinstance(v, str) else str(v) for v in self.dtype]

        super().__post_init__(**kwargs)


@dataclass
class Datasets(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Datasets
    class_class_curie: ClassVar[str] = "nwb_schema_language:Datasets"
    class_name: ClassVar[str] = "Datasets"
    class_model_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.Datasets

    datasets: Optional[Union[Union[dict, Dataset], List[Union[dict, Dataset]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.datasets, list):
            self.datasets = [self.datasets] if self.datasets is not None else []
        self.datasets = [v if isinstance(v, Dataset) else Dataset(**as_dict(v)) for v in self.datasets]

        super().__post_init__(**kwargs)


@dataclass
class ReferenceDtype(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.ReferenceDtype
    class_class_curie: ClassVar[str] = "nwb_schema_language:ReferenceDtype"
    class_name: ClassVar[str] = "ReferenceDtype"
    class_model_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.ReferenceDtype

    target_type: str = None
    reftype: Optional[Union[str, "ReftypeOptions"]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.target_type):
            self.MissingRequiredField("target_type")
        if not isinstance(self.target_type, str):
            self.target_type = str(self.target_type)

        if self.reftype is not None and not isinstance(self.reftype, ReftypeOptions):
            self.reftype = ReftypeOptions(self.reftype)

        super().__post_init__(**kwargs)


@dataclass
class CompoundDtype(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.CompoundDtype
    class_class_curie: ClassVar[str] = "nwb_schema_language:CompoundDtype"
    class_name: ClassVar[str] = "CompoundDtype"
    class_model_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.CompoundDtype

    name: str = None
    doc: str = None
    dtype: Union[str, List[str]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.name):
            self.MissingRequiredField("name")
        if not isinstance(self.name, str):
            self.name = str(self.name)

        if self._is_empty(self.doc):
            self.MissingRequiredField("doc")
        if not isinstance(self.doc, str):
            self.doc = str(self.doc)

        if self._is_empty(self.dtype):
            self.MissingRequiredField("dtype")
        if not isinstance(self.dtype, list):
            self.dtype = [self.dtype] if self.dtype is not None else []
        self.dtype = [v if isinstance(v, str) else str(v) for v in self.dtype]

        super().__post_init__(**kwargs)


@dataclass
class DtypeMixin(YAMLRoot):
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.DtypeMixin
    class_class_curie: ClassVar[str] = "nwb_schema_language:DtypeMixin"
    class_name: ClassVar[str] = "DtypeMixin"
    class_model_uri: ClassVar[URIRef] = NWB_SCHEMA_LANGUAGE.DtypeMixin

    dtype: Optional[Union[str, List[str]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.dtype, list):
            self.dtype = [self.dtype] if self.dtype is not None else []
        self.dtype = [v if isinstance(v, str) else str(v) for v in self.dtype]

        super().__post_init__(**kwargs)


AnyType = Any

# Enumerations
class ReftypeOptions(EnumDefinitionImpl):

    ref = PermissibleValue(
        text="ref",
        description="Reference to another group or dataset of the given target_type")
    reference = PermissibleValue(
        text="reference",
        description="Reference to another group or dataset of the given target_type")
    object = PermissibleValue(
        text="object",
        description="Reference to another group or dataset of the given target_type")
    region = PermissibleValue(
        text="region",
        description="Reference to a region (i.e. subset) of another dataset of the given target_type")

    _defn = EnumDefinition(
        name="ReftypeOptions",
    )

class QuantityEnum(EnumDefinitionImpl):

    zero_or_many = PermissibleValue(
        text="zero_or_many",
        description="Zero or more instances, equivalent to *")
    one_or_many = PermissibleValue(
        text="one_or_many",
        description="One or more instances, equivalent to +")
    zero_or_one = PermissibleValue(
        text="zero_or_one",
        description="Zero or one instances, equivalent to ?")

    _defn = EnumDefinition(
        name="QuantityEnum",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "*",
            PermissibleValue(
                text="*",
                description="Zero or more instances, equivalent to zero_or_many"))
        setattr(cls, "?",
            PermissibleValue(
                text="?",
                description="Zero or one instances, equivalent to zero_or_one"))
        setattr(cls, "+",
            PermissibleValue(
                text="+",
                description="One or more instances, equivalent to one_or_many"))

class FlatDtype(EnumDefinitionImpl):

    float = PermissibleValue(
        text="float",
        description="single precision floating point (32 bit)")
    float32 = PermissibleValue(
        text="float32",
        description="single precision floating point (32 bit)")
    double = PermissibleValue(
        text="double",
        description="double precision floating point (64 bit)")
    float64 = PermissibleValue(
        text="float64",
        description="double precision floating point (64 bit)")
    long = PermissibleValue(
        text="long",
        description="signed 64 bit integer")
    int64 = PermissibleValue(
        text="int64",
        description="signed 64 bit integer")
    int = PermissibleValue(
        text="int",
        description="signed 32 bit integer")
    int32 = PermissibleValue(
        text="int32",
        description="signed 32 bit integer")
    int16 = PermissibleValue(
        text="int16",
        description="signed 16 bit integer")
    short = PermissibleValue(
        text="short",
        description="signed 16 bit integer")
    int8 = PermissibleValue(
        text="int8",
        description="signed 8 bit integer")
    uint = PermissibleValue(
        text="uint",
        description="unsigned 32 bit integer")
    uint32 = PermissibleValue(
        text="uint32",
        description="unsigned 32 bit integer")
    uint16 = PermissibleValue(
        text="uint16",
        description="unsigned 16 bit integer")
    uint8 = PermissibleValue(
        text="uint8",
        description="unsigned 8 bit integer")
    uint64 = PermissibleValue(
        text="uint64",
        description="unsigned 64 bit integer")
    numeric = PermissibleValue(
        text="numeric",
        description="any numeric type (i.e., any int, uint, float)")
    text = PermissibleValue(
        text="text",
        description="8-bit Unicode")
    utf = PermissibleValue(
        text="utf",
        description="8-bit Unicode")
    utf8 = PermissibleValue(
        text="utf8",
        description="8-bit Unicode")
    ascii = PermissibleValue(
        text="ascii",
        description="ASCII text")
    bool = PermissibleValue(
        text="bool",
        description="8 bit integer with valid values 0 or 1")
    isodatetime = PermissibleValue(
        text="isodatetime",
        description="ISO 8601 datetime string")

    _defn = EnumDefinition(
        name="FlatDtype",
    )

    @classmethod
    def _addvals(cls):
        setattr(cls, "utf-8",
            PermissibleValue(
                text="utf-8",
                description="8-bit Unicode"))

# Slots
class slots:
    pass

slots.doc = Slot(uri=NWB_SCHEMA_LANGUAGE.doc, name="doc", curie=NWB_SCHEMA_LANGUAGE.curie('doc'),
                   model_uri=NWB_SCHEMA_LANGUAGE.doc, domain=None, range=str)

slots.name = Slot(uri=NWB_SCHEMA_LANGUAGE.name, name="name", curie=NWB_SCHEMA_LANGUAGE.curie('name'),
                   model_uri=NWB_SCHEMA_LANGUAGE.name, domain=None, range=Optional[str])

slots.full_name = Slot(uri=NWB_SCHEMA_LANGUAGE.full_name, name="full_name", curie=NWB_SCHEMA_LANGUAGE.curie('full_name'),
                   model_uri=NWB_SCHEMA_LANGUAGE.full_name, domain=None, range=Optional[str])

slots.version = Slot(uri=NWB_SCHEMA_LANGUAGE.version, name="version", curie=NWB_SCHEMA_LANGUAGE.curie('version'),
                   model_uri=NWB_SCHEMA_LANGUAGE.version, domain=None, range=str,
                   pattern=re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'))

slots.date = Slot(uri=SCHEMA.dateModified, name="date", curie=SCHEMA.curie('dateModified'),
                   model_uri=NWB_SCHEMA_LANGUAGE.date, domain=None, range=Optional[Union[str, XSDDateTime]])

slots.author = Slot(uri=SCHEMA.author, name="author", curie=SCHEMA.curie('author'),
                   model_uri=NWB_SCHEMA_LANGUAGE.author, domain=None, range=Union[str, List[str]])

slots.contact = Slot(uri=SCHEMA.email, name="contact", curie=SCHEMA.curie('email'),
                   model_uri=NWB_SCHEMA_LANGUAGE.contact, domain=None, range=Union[str, List[str]])

slots.schema = Slot(uri=NWB_SCHEMA_LANGUAGE.schema_, name="schema", curie=NWB_SCHEMA_LANGUAGE.curie('schema_'),
                   model_uri=NWB_SCHEMA_LANGUAGE.schema, domain=None, range=Optional[Union[Union[dict, Schema], List[Union[dict, Schema]]]])

slots.source = Slot(uri=NWB_SCHEMA_LANGUAGE.source, name="source", curie=NWB_SCHEMA_LANGUAGE.curie('source'),
                   model_uri=NWB_SCHEMA_LANGUAGE.source, domain=None, range=Optional[str],
                   pattern=re.compile(r'.*\.(yml|yaml|json)'))

slots.namespace = Slot(uri=NWB_SCHEMA_LANGUAGE.namespace, name="namespace", curie=NWB_SCHEMA_LANGUAGE.curie('namespace'),
                   model_uri=NWB_SCHEMA_LANGUAGE.namespace, domain=None, range=Optional[str])

slots.namespaces = Slot(uri=NWB_SCHEMA_LANGUAGE.namespaces, name="namespaces", curie=NWB_SCHEMA_LANGUAGE.curie('namespaces'),
                   model_uri=NWB_SCHEMA_LANGUAGE.namespaces, domain=None, range=Optional[Union[Union[dict, Namespace], List[Union[dict, Namespace]]]])

slots.neurodata_types = Slot(uri=NWB_SCHEMA_LANGUAGE.neurodata_types, name="neurodata_types", curie=NWB_SCHEMA_LANGUAGE.curie('neurodata_types'),
                   model_uri=NWB_SCHEMA_LANGUAGE.neurodata_types, domain=None, range=Optional[Union[str, List[str]]])

slots.title = Slot(uri=NWB_SCHEMA_LANGUAGE.title, name="title", curie=NWB_SCHEMA_LANGUAGE.curie('title'),
                   model_uri=NWB_SCHEMA_LANGUAGE.title, domain=None, range=Optional[str])

slots.neurodata_type_def = Slot(uri=NWB_SCHEMA_LANGUAGE.neurodata_type_def, name="neurodata_type_def", curie=NWB_SCHEMA_LANGUAGE.curie('neurodata_type_def'),
                   model_uri=NWB_SCHEMA_LANGUAGE.neurodata_type_def, domain=None, range=Optional[str])

slots.neurodata_type_inc = Slot(uri=NWB_SCHEMA_LANGUAGE.neurodata_type_inc, name="neurodata_type_inc", curie=NWB_SCHEMA_LANGUAGE.curie('neurodata_type_inc'),
                   model_uri=NWB_SCHEMA_LANGUAGE.neurodata_type_inc, domain=None, range=Optional[str])

slots.default_name = Slot(uri=NWB_SCHEMA_LANGUAGE.default_name, name="default_name", curie=NWB_SCHEMA_LANGUAGE.curie('default_name'),
                   model_uri=NWB_SCHEMA_LANGUAGE.default_name, domain=None, range=Optional[str])

slots.quantity = Slot(uri=NWB_SCHEMA_LANGUAGE.quantity, name="quantity", curie=NWB_SCHEMA_LANGUAGE.curie('quantity'),
                   model_uri=NWB_SCHEMA_LANGUAGE.quantity, domain=None, range=Optional[str])

slots.linkable = Slot(uri=NWB_SCHEMA_LANGUAGE.linkable, name="linkable", curie=NWB_SCHEMA_LANGUAGE.curie('linkable'),
                   model_uri=NWB_SCHEMA_LANGUAGE.linkable, domain=None, range=Optional[Union[bool, Bool]])

slots.attributes = Slot(uri=NWB_SCHEMA_LANGUAGE.attributes, name="attributes", curie=NWB_SCHEMA_LANGUAGE.curie('attributes'),
                   model_uri=NWB_SCHEMA_LANGUAGE.attributes, domain=None, range=Optional[Union[Union[dict, Attribute], List[Union[dict, Attribute]]]])

slots.datasets = Slot(uri=NWB_SCHEMA_LANGUAGE.datasets, name="datasets", curie=NWB_SCHEMA_LANGUAGE.curie('datasets'),
                   model_uri=NWB_SCHEMA_LANGUAGE.datasets, domain=None, range=Optional[Union[Union[dict, Dataset], List[Union[dict, Dataset]]]])

slots.groups = Slot(uri=NWB_SCHEMA_LANGUAGE.groups, name="groups", curie=NWB_SCHEMA_LANGUAGE.curie('groups'),
                   model_uri=NWB_SCHEMA_LANGUAGE.groups, domain=None, range=Optional[Union[Union[dict, Group], List[Union[dict, Group]]]])

slots.links = Slot(uri=NWB_SCHEMA_LANGUAGE.links, name="links", curie=NWB_SCHEMA_LANGUAGE.curie('links'),
                   model_uri=NWB_SCHEMA_LANGUAGE.links, domain=None, range=Optional[Union[Union[dict, Link], List[Union[dict, Link]]]])

slots.dtype = Slot(uri=NWB_SCHEMA_LANGUAGE.dtype, name="dtype", curie=NWB_SCHEMA_LANGUAGE.curie('dtype'),
                   model_uri=NWB_SCHEMA_LANGUAGE.dtype, domain=None, range=Optional[Union[str, List[str]]])

slots.dims = Slot(uri=NWB_SCHEMA_LANGUAGE.dims, name="dims", curie=NWB_SCHEMA_LANGUAGE.curie('dims'),
                   model_uri=NWB_SCHEMA_LANGUAGE.dims, domain=None, range=Optional[Union[str, List[str]]])

slots.shape = Slot(uri=NWB_SCHEMA_LANGUAGE.shape, name="shape", curie=NWB_SCHEMA_LANGUAGE.curie('shape'),
                   model_uri=NWB_SCHEMA_LANGUAGE.shape, domain=None, range=Optional[Union[str, List[str]]])

slots.value = Slot(uri=NWB_SCHEMA_LANGUAGE.value, name="value", curie=NWB_SCHEMA_LANGUAGE.curie('value'),
                   model_uri=NWB_SCHEMA_LANGUAGE.value, domain=None, range=Optional[Union[dict, AnyType]])

slots.default_value = Slot(uri=NWB_SCHEMA_LANGUAGE.default_value, name="default_value", curie=NWB_SCHEMA_LANGUAGE.curie('default_value'),
                   model_uri=NWB_SCHEMA_LANGUAGE.default_value, domain=None, range=Optional[Union[dict, AnyType]])

slots.required = Slot(uri=NWB_SCHEMA_LANGUAGE.required, name="required", curie=NWB_SCHEMA_LANGUAGE.curie('required'),
                   model_uri=NWB_SCHEMA_LANGUAGE.required, domain=None, range=Optional[Union[bool, Bool]])

slots.target_type = Slot(uri=NWB_SCHEMA_LANGUAGE.target_type, name="target_type", curie=NWB_SCHEMA_LANGUAGE.curie('target_type'),
                   model_uri=NWB_SCHEMA_LANGUAGE.target_type, domain=None, range=str)

slots.reftype = Slot(uri=NWB_SCHEMA_LANGUAGE.reftype, name="reftype", curie=NWB_SCHEMA_LANGUAGE.curie('reftype'),
                   model_uri=NWB_SCHEMA_LANGUAGE.reftype, domain=None, range=Optional[Union[str, "ReftypeOptions"]])

slots.schema__doc = Slot(uri=NWB_SCHEMA_LANGUAGE.doc, name="schema__doc", curie=NWB_SCHEMA_LANGUAGE.curie('doc'),
                   model_uri=NWB_SCHEMA_LANGUAGE.schema__doc, domain=None, range=Optional[str])

slots.Namespace_name = Slot(uri=NWB_SCHEMA_LANGUAGE.name, name="Namespace_name", curie=NWB_SCHEMA_LANGUAGE.curie('name'),
                   model_uri=NWB_SCHEMA_LANGUAGE.Namespace_name, domain=Namespace, range=str)

slots.Attribute_name = Slot(uri=NWB_SCHEMA_LANGUAGE.name, name="Attribute_name", curie=NWB_SCHEMA_LANGUAGE.curie('name'),
                   model_uri=NWB_SCHEMA_LANGUAGE.Attribute_name, domain=Attribute, range=str)

slots.CompoundDtype_name = Slot(uri=NWB_SCHEMA_LANGUAGE.name, name="CompoundDtype_name", curie=NWB_SCHEMA_LANGUAGE.curie('name'),
                   model_uri=NWB_SCHEMA_LANGUAGE.CompoundDtype_name, domain=CompoundDtype, range=str)

slots.CompoundDtype_dtype = Slot(uri=NWB_SCHEMA_LANGUAGE.dtype, name="CompoundDtype_dtype", curie=NWB_SCHEMA_LANGUAGE.curie('dtype'),
                   model_uri=NWB_SCHEMA_LANGUAGE.CompoundDtype_dtype, domain=CompoundDtype, range=Union[str, List[str]])