"""
This is a sandbox file that should be split out to its own pydantic-hdf5 package, but just experimenting here to get our bearings
"""
import pdb
import typing
from typing import Optional, List, Dict, overload, Literal, Type, Any
from pathlib import Path
from types import ModuleType
from typing import TypeVar, TYPE_CHECKING
from abc import abstractmethod
import json

import h5py
from pydantic import BaseModel
from dataclasses import dataclass, field

from nwb_linkml.translate import generate_from_nwbfile
#from nwb_linkml.models.core_nwb_file import NWBFile
if TYPE_CHECKING:
    from nwb_linkml.models.core_nwb_file import NWBFile
from nwb_linkml.providers.schema import SchemaProvider

@dataclass
class HDF5Element():

    cls: h5py.Dataset | h5py.Group
    parent: Type[BaseModel]
    model: Optional[Any] = None

    @abstractmethod
    def read(self) -> BaseModel | List[BaseModel]:
        """
        Constructs the pydantic model from the given hdf5 element
        """

    @abstractmethod
    def write(self) -> h5py.Dataset | h5py.Group:
        """
        Create the h5py object from the in-memory pydantic model
        """

    @property
    def name(self) -> str:
        """Just the terminal group name"""
        return self.cls.name.split('/')[-1]

    def get_model(self) -> Type[BaseModel | dict | list]:
        """
        Find our model
        - If we have a neurodata_type in our attrs, use that
        - Otherwise, use our parent to resolve the type
        """
        if self.model is not None:
            return self.model

        if 'neurodata_type' in self.cls.attrs.keys():
            return get_model(self.cls)
        else:
            parent_model  = get_model(self.cls.parent)
            field = parent_model.model_fields.get(self.name)
            if issubclass(type(field.annotation), BaseModel):
                return field.annotation
            else:
                try:
                    if issubclass(field.annotation, BaseModel):
                        return field.annotation
                except TypeError:
                    pass
            # remove any optionals
            annotation = field.annotation
            annotation = unwrap_optional(annotation)

            if typing.get_origin(annotation) is list:
                return list

            else:
                return dict
                #raise NotImplementedError('Need to unpack at least listlike annotations')

def unwrap_optional(annotation):
    if typing.get_origin(annotation) == typing.Union:
        args = typing.get_args(annotation)

        if len(args) == 2 and args[1].__name__ == 'NoneType':
            annotation = args[0]
    return annotation

def take_outer_type(annotation):
    if typing.get_origin(annotation) is list:
        return list
    return annotation
@dataclass
class H5Dataset(HDF5Element):
    cls: h5py.Dataset

    def read(self) -> Any:
        model = self.get_model()

        # TODO: Handle references
        if self.cls.dtype == h5py.ref_dtype:
            return None

        if self.cls.shape == ():
            return self.cls[()]
        elif model is list:
            return self.cls[:].tolist()
        else:
            return {'array':self.cls[:], 'name': self.cls.name.split('/')[-1]}
            #raise NotImplementedError('oop')

@dataclass
class H5Group(HDF5Element):
    cls: h5py.Group

    def read(self) -> BaseModel:
        data = {}
        model = self.get_model()

        model_attrs = {
            k:v for k, v in self.cls.attrs.items() if k in model.model_fields.keys()
        }
        data.update(model_attrs)


        for k, v in self.cls.items():
            child_model = None
            if isinstance(model, type) and issubclass(model, BaseModel):
                child_field = model.model_fields.get(k, None)
                if child_field is not None:
                    child_model = unwrap_optional(child_field.annotation)
                    child_model = take_outer_type(child_model)
            if isinstance(v, h5py.Group):
                data[k] = H5Group(cls=v, parent=model, model=child_model).read()
            elif isinstance(v, h5py.Dataset):
                data[k] = H5Dataset(cls=v, parent=model, model=child_model).read()


        if issubclass(model, BaseModel):
            data['name'] = self.cls.name.split('/')[-1]
            return model(**data)
        elif model is list:
            return list(data.values())


class HDF5IO():

    def __init__(self, path:Path):
        self.path = Path(path)
        self._modules: Dict[str, ModuleType] = {}

    @property
    def modules(self) -> Dict[str, ModuleType]:
        if len(self._modules) == 0:
            self._modules = generate_from_nwbfile(self.path)
        return self._modules

    @overload
    def read(self, path:None) -> 'NWBFile': ...

    @overload
    def read(self, path:str) -> BaseModel | Dict[str, BaseModel]: ...

    def read(self, path:Optional[str] = None):
        h5f = h5py.File(str(self.path))
        schema = read_specs(h5f.get('specifications'))
        # build schema so we have them cached

        provider = SchemaProvider()
        res = provider.build_from_dicts(schema)

        if path:
            src = h5f.get(path)
            parent = get_model(src)
        else:
            src = h5f
            parent = provider.get_class('core', 'NWBFile')

        data = {}
        for k, v in src.items():
            if isinstance(v, h5py.Group):
                data[k] = H5Group(cls=v, parent=parent).read()
            elif isinstance(v, h5py.Dataset):
                data[k] = H5Dataset(cls=v, parent=parent).read()

        if path is None:
            return parent(**data)
        if 'neurodata_type' in src.attrs:
            raise NotImplementedError('Making a submodel not supported yet')
        else:
            return data



    def process_group(self, group:h5py.Group|h5py.File) -> dict | list:
        attrs = dict(group.attrs)

        # how to process the group?
        # --------------------------------------------------
        # list-like
        # --------------------------------------------------
        # a list of data classes
        if 'neurodata_type' not in attrs and \
            all([isinstance(v, h5py.Group) for v in group.values()]) and \
            all(['neurodata_type' in v.attrs for v in group.values()]):

            return [self.process_group(v) for v in group.values()]

        # --------------------------------------------------
        # dict-like
        # --------------------------------------------------

        res = {}


        for key, val in group.items():
            if isinstance(val, h5py.Group):
                res[key] = self.process_group(val)
            elif isinstance(val, h5py.Dataset):
                res[key] = self.process_dataset(val)
        return res

    def process_dataset(self, data: h5py.Dataset) -> dict | list:
        if len(data.shape) == 1:
            return list(data[:])



def read_specs(group: h5py.Group) -> dict:
    spec_dict = {}
    def _read_spec(name, node):

        if isinstance(node, h5py.Dataset):
            # make containing dict if they dont exist
            pieces = node.name.split('/')
            if pieces[-3] not in spec_dict.keys():
                spec_dict[pieces[-3]] = {}

            spec = json.loads(node[()])
            spec_dict[pieces[-3]][pieces[-1]] = spec

    group.visititems(_read_spec)
    return spec_dict


def get_model(cls: h5py.Group | h5py.Dataset) -> Type[BaseModel]:
    attrs = cls.attrs
    ns = attrs.get('namespace')
    model_name = attrs.get('neurodata_type')

    try:
        return SchemaProvider().get_class(ns, model_name)
    except:
        # try to get parent class
        mod = get_model(cls.parent)
        return mod.model_fields[cls.name.split('/')[-1]].annotation



