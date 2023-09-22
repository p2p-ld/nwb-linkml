"""
This is a sandbox file that should be split out to its own pydantic-hdf5 package, but just experimenting here to get our bearings

Notes:

    * Rather than a set of recursive build steps as is used elsewhere in the package,
      since we need to instantiate some models first that are referred to elsewhere, we
      flatten the hdf5 file and build each from a queue.

Mapping operations (mostly TODO atm)

* Create new models from DynamicTables
* Handle softlinks as object references and vice versa by adding a ``path`` attr



Other TODO:

* Read metadata only, don't read all arrays
* Write, obvi lol.

"""
import pdb
import typing
import warnings
from typing import Optional, List, Dict, overload, Literal, Type, Any
from pathlib import Path
from types import ModuleType
from typing import TypeVar, TYPE_CHECKING, NamedTuple
from abc import abstractmethod
import json
import subprocess
import shutil

import h5py
from pydantic import BaseModel, Field, ConfigDict
from dataclasses import dataclass, field

from nwb_linkml.translate import generate_from_nwbfile
#from nwb_linkml.models.core_nwb_file import NWBFile
if TYPE_CHECKING:
    from nwb_linkml.models import NWBFile
from nwb_linkml.providers.schema import SchemaProvider



class H5SourceItem(BaseModel):
    """Tuple of items for each element when flattening an hdf5 file"""
    path: str
    """Absolute hdf5 path of element"""
    leaf: bool
    """If ``True``, this item has no children (and thus we should start instantiating it before ascending to parent classes)"""
    h5_type: Literal['group', 'dataset']
    """What kind of hdf5 element this is"""
    depends: List[str] = Field(default_factory=list)
    """Paths of other source items that this item depends on before it can be instantiated. eg. from softlinks"""
    attrs: dict = Field(default_factory=dict)
    """Any static attrs that can be had from the element"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    @property
    def parts(self) -> List[str]:
        """path split by /"""
        return self.path.split('/')

FlatH5 = Dict[str, H5SourceItem]

class ReadQueue(BaseModel):
    """Container model to store items as they are built """
    h5f: h5py.File = Field(
        description="Open hdf5 file used when resolving the queue!"
    )
    queue: Dict[str,H5SourceItem] = Field(
        default_factory=dict,
        description="Items left to be instantiated, keyed by hdf5 path",
    )
    completed: Dict[str, Any] = Field(
        default_factory=dict,
        description="Items that have already been instantiated, keyed by hdf5 path"
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)


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
        provider = self.make_provider()

        h5f = h5py.File(str(self.path))
        if path:
            src = h5f.get(path)
        else:
            src = h5f

        # get all children of selected item
        if isinstance(src, (h5py.File, h5py.Group)):
            children = self._flatten_hdf(src)
        else:
            raise NotImplementedError('directly read individual datasets')





        data = {}
        for k, v in src.items():
            if isinstance(v, h5py.Group):
                data[k] = H5Group(cls=v, parent=parent, root_model=parent).read()
            elif isinstance(v, h5py.Dataset):
                data[k] = H5Dataset(cls=v, parent=parent).read()

        if path is None:
            return parent(**data)
        if 'neurodata_type' in src.attrs:
            raise NotImplementedError('Making a submodel not supported yet')
        else:
            return data





    def make_provider(self) -> SchemaProvider:
        """
        Create a :class:`~.providers.schema.SchemaProvider` by
        reading specifications from the NWBFile ``/specification`` group and translating
        them to LinkML and generating pydantic models

        Returns:
            :class:`~.providers.schema.SchemaProvider` : Schema Provider with correct versions
                specified as defaults
        """
        h5f = h5py.File(str(self.path))
        schema = read_specs_as_dicts(h5f.get('specifications'))

        # get versions for each namespace
        versions = {}
        for ns_schema in schema.values():
            # each "namespace" can actually contain multiple namespaces which actually contain the version info
            for inner_ns in ns_schema['namespace']['namespaces']:
                versions[inner_ns['name']] = inner_ns['version']

        provider = SchemaProvider(versions=versions)

        # build schema so we have them cached
        provider.build_from_dicts(schema)
        h5f.close()
        return provider




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



def read_specs_as_dicts(group: h5py.Group) -> dict:
    """
    Utility function to iterate through the `/specifications` group and
    load

    Args:
        group:

    Returns:

    """
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


def truncate_file(source: Path, target: Optional[Path] = None, n:int=10) -> Path:
    """
    Create a truncated HDF5 file where only the first few samples are kept.

    Used primarily to create testing data from real data without it being so damn bit

    Args:
        source (:class:`pathlib.Path`): Source hdf5 file
        target (:class:`pathlib.Path`): Optional - target hdf5 file to write to. If ``None``, use ``{source}_truncated.hdf5``
        n (int): The number of items from datasets (samples along the 0th dimension of a dataset) to include

    Returns:
        :class:`pathlib.Path` path of the truncated file
    """
    if target is None:
        target = source.parent / (source.stem + '_truncated.hdf5')
    else:
        target = Path(target)

    source = Path(source)

    # and also a temporary file that we'll make with h5repack
    target_tmp = target.parent / (target.stem + '_tmp.hdf5')


    # copy the whole thing
    if target.exists():
        target.unlink()
    shutil.copy(source, target)

    h5f_target = h5py.File(str(target), 'r+')
    def _prune_dataset(name:str, obj: h5py.Dataset | h5py.Group):

        if isinstance(obj, h5py.Dataset):
            if obj.size > 10:
                try:
                    obj.resize(n, axis=0)
                except TypeError:
                    # contiguous arrays cant be resized directly
                    # so we have to jank our way through it
                    tmp_name = obj.name + '__tmp'
                    original_name = obj.name
                    obj.parent.move(obj.name, tmp_name)
                    old_obj = obj.parent.get(tmp_name)
                    new_obj = obj.parent.create_dataset(original_name, data=old_obj[0:n])
                    for k, v in old_obj.attrs.items():
                        new_obj.attrs[k] = v
                    del new_obj.parent[tmp_name]


    h5f_target.visititems(_prune_dataset)
    h5f_target.flush()
    h5f_target.close()

    # use h5repack to actually remove the items from the dataset
    if shutil.which('h5repack') is None:
        warnings.warn('Truncated file made, but since h5repack not found in path, file wont be any smaller')
        return target

    res = subprocess.run(
        ['h5repack', '-f', 'GZIP=9', str(target), str(target_tmp)],
        capture_output=True
    )
    if res.returncode != 0:
        warnings.warn(f'h5repack did not return 0: {res.stderr} {res.stdout}')
        # remove the attempt at the repack
        target_tmp.unlink()
        return target

    target.unlink()
    target_tmp.rename(target)

    return target

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



def submodel_by_path(model: BaseModel, path:str) -> Type[BaseModel | dict | list]:
    """
    Given a pydantic model and an absolute HDF5 path, get the type annotation
    """
    parts = path.split('/')
    for part in parts:
        ann = model.model_fields[part].annotation


def flatten_hdf(h5f:h5py.File | h5py.Group, skip='specifications') -> Dict[str, H5SourceItem]:
    """
    Flatten all child elements of hdf element into a dict of :class:`.H5SourceItem` s keyed by their path

    Args:
        h5f (:class:`h5py.File` | :class:`h5py.Group`): HDF file or group to flatten!
    """
    items = {}
    def _itemize(name: str, obj: h5py.Dataset | h5py.Group):
        if skip in name:
            return
        leaf = isinstance(obj, h5py.Dataset) or len(obj.keys()) == 0
        # get references in attrs and datasets
        refs = [ref for ref in obj.attrs.values() if isinstance(ref, h5py.h5r.Reference)]
        if isinstance(obj, h5py.Dataset):
            h5_type = 'dataset'
            if obj.shape == ():
                if isinstance(obj[()], h5py.h5r.Reference):
                    refs.append(obj[()])
            elif isinstance(obj[0], h5py.h5r.Reference):
                refs.extend(obj[:].tolist())
        else:
            h5_type = 'group'
        # dereference and get name of reference
        depends = list(set([h5f[i].name for i in refs]))
        if not name.startswith('/'):
            name = '/' + name
        items[name] = H5SourceItem.model_construct(
            path = name,
            leaf = leaf,
            depends = depends,
            h5_type=h5_type,
            attrs = dict(obj.attrs.items())
        )

    h5f.visititems(_itemize)
    return items

def sort_flat_hdf(flat: Dict[str, H5SourceItem]) -> Dict[str, H5SourceItem]:
    """
    Sort flat hdf5 file in a rough order of solvability

    * First process any leaf items

    * Put any items with dependencies at the end

    Args:
        flat:

    Returns:

    """
    class Rank(NamedTuple):
        has_depends: bool
        not_leaf: bool



