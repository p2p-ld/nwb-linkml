"""
This is a sandbox file that should be split out to its own pydantic-hdf5 package, but just experimenting here to get our bearings
"""
from typing import Optional, List, Dict, overload, Literal, Type, Any
from pathlib import Path
from types import ModuleType
from typing import TypeVar, TYPE_CHECKING
from abc import abstractmethod

import h5py
from pydantic import BaseModel
from dataclasses import dataclass, field

from nwb_linkml.translate import generate_from_nwbfile
#from nwb_linkml.models.core_nwb_file import NWBFile
if TYPE_CHECKING:
    from nwb_linkml.models.core_nwb_file import NWBFile

@dataclass
class HDF5Element():

    cls: h5py.Dataset | h5py.Group
    models: Dict[str, ModuleType]
    parent: Type[BaseModel]

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

    def get_model(self) -> Type[BaseModel | dict]:
        """
        Find our model
        - If we have a neurodata_type in our attrs, use that
        - Otherwise, use our parent to resolve the type
        """
        if 'neurodata_type' in self.cls.attrs.keys():
            return get_model(self.cls.attrs, self.models)
        else:
            parent_model  = get_model(self.cls.parent.attrs, self.models)
            field = parent_model.model_fields.get(self.name)
            if issubclass(type(field.annotation), BaseModel):
                return field.annotation
            else:
                return dict
                #raise NotImplementedError('Need to unpack at least listlike annotations')

@dataclass
class H5Dataset(HDF5Element):
    cls: h5py.Dataset

    def read(self) -> Any:
        if self.cls.shape == ():
            return self.cls[()]
        elif len(self.cls.shape) == 1:
            return self.cls[:].tolist()
        else:
            raise NotImplementedError('oop')

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
            if isinstance(v, h5py.Group):
                data[k] = H5Group(cls=v, models=self.models, parent=model).read()
            elif isinstance(v, h5py.Dataset):
                data[k] = H5Dataset(cls=v, models=self.models, parent=model).read()


        return model(**data)


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

        if path:
            src = h5f.get(path)
            parent = get_model(src.attrs, self.modules)
        else:
            src = h5f
            parent = getattr(self.modules['core'], 'NWBFile')

        data = {}
        for k, v in src.items():
            if isinstance(v, h5py.Group):
                data[k] = H5Group(cls=v, models=self.modules, parent=parent).read()
            elif isinstance(v, h5py.Dataset):
                data[k] = H5Dataset(cls=v, models=self.modules, parent=parent).read()

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

def get_model(attrs: h5py.AttributeManager, models: Dict[str, ModuleType]) -> Type[BaseModel]:
    ns = attrs.get('namespace')
    model_name = attrs.get('neurodata_type')
    return getattr(models[ns], model_name)

# if __name__ == "__main__":
#     NWBFILE = Path('/Users/jonny/Dropbox/lab/p2p_ld/data/nwb/sub-738651046_ses-760693773.nwb')
#     h5f = HDF5IO(NWBFILE)


