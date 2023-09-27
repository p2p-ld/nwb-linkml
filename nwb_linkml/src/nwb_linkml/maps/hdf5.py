"""
Maps for reading and writing from HDF5

We have sort of diverged from the initial idea of a generalized map as in :class:`linkml.map.Map` ,
so we will make our own mapping class here and re-evaluate whether they should be unified later
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal, List, Dict, Optional, Type

import h5py
from enum import StrEnum

from pydantic import BaseModel, Field, ConfigDict

from nwb_linkml.providers.schema import SchemaProvider
from nwb_linkml.maps.hdmf import dynamictable_to_model
from nwb_linkml.types.hdf5 import HDF5_Path


class ReadPhases(StrEnum):
    plan = 'plan'
    """Before reading starts, building an index of objects to read"""
    read = 'read'
    """Main reading operation"""
    construct = 'construct'
    """After reading, casting the results of the read into their models"""

class H5SourceItem(BaseModel):
    """Tuple of items for each element when flattening an hdf5 file"""
    path: str
    """Absolute hdf5 path of element"""
    h5f_path: str
    """Path to the source hdf5 file"""
    leaf: bool
    """If ``True``, this item has no children (and thus we should start instantiating it before ascending to parent classes)"""
    h5_type: Literal['group', 'dataset']
    """What kind of hdf5 element this is"""
    depends: List[str] = Field(default_factory=list)
    """Paths of other source items that this item depends on before it can be instantiated. eg. from softlinks"""
    attrs: dict = Field(default_factory=dict)
    """Any static attrs that can be had from the element"""
    namespace: Optional[str] = None
    """Optional: The namespace that the neurodata type belongs to"""
    neurodata_type: Optional[str] = None
    """Optional: the neurodata type for this dataset or group"""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    @property
    def parts(self) -> List[str]:
        """path split by /"""
        return self.path.split('/')

class H5ReadResult(BaseModel):
    """Result returned by each of our mapping operations"""
    path: str
    """absolute hdf5 path of element"""
    source: H5SourceItem
    """
    Source that this result is based on. 
    The map can modify this item, so the container should update the source
    queue on each pass
    """
    completed: bool = False
    """
    Was this item completed by this map step? False for cases where eg. 
    we still have dependencies that need to be completed before this one
    """
    result: Optional[BaseModel | dict | str | int | float] = None
    """
    If completed, built result. A dict that can be instantiated into the model.
    If completed is True and result is None, then remove this object
    """
    model: Optional[Type[BaseModel]] = None
    """
    The model that this item should be cast into
    """
    completes: List[str] = Field(default_factory=list)
    """
    If this result completes any other fields, we remove them from the build queue
    """
    namespace: Optional[str] = None
    """
    Optional: the namespace of the neurodata type for this object
    """
    neurodata_type: Optional[str] = None
    """
    Optional: The neurodata type to use for this object 
    """


FlatH5 = Dict[str, H5SourceItem]


class HDF5Map(ABC):
    phase: ReadPhases
    exclusive: bool = False
    """
    If ``True``, if the check is fulfilled, no other maps can be applied this phase
    """
    priority: int = 0

    @classmethod
    @abstractmethod
    def check(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
        """Check if this map applies to the given item to read"""

    @classmethod
    @abstractmethod
    def apply(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> H5ReadResult:
        """Actually apply the map!"""


# --------------------------------------------------
# Planning maps
# --------------------------------------------------
class PruneEmpty(HDF5Map):
    """Remove groups with no attrs """
    phase = ReadPhases.plan
    @classmethod
    def check(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
        if src.leaf and src.h5_type == 'group':
            with h5py.File(src.h5f_path, 'r') as h5f:
                obj = h5f.get(src.path)
                if len(obj.attrs) == 0:
                    return True

    @classmethod
    def apply(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> H5ReadResult:
        return H5ReadResult.model_construct(
            path = src.path,
            source=src,
            completed=True
        )

# class ResolveVectorData(HDF5Map):
#     """
#     We will load vanilla VectorData as part of :class:`.ResolveDynamicTable`
#     """
#     phase = ReadPhases.read
#
#     @classmethod
#     def check(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
#         if src.h5_type == 'group':
#             return False
#         if src.neurodata_type == 'VectorData':
#


class ResolveDynamicTable(HDF5Map):
    """Handle loading a dynamic table!"""
    phase = ReadPhases.read
    priority = 1
    exclusive = True
    @classmethod
    def check(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
        if src.h5_type == 'dataset':
            return False
        if 'neurodata_type' in src.attrs:
            if src.attrs['neurodata_type'] == 'DynamicTable':
                return True
            # otherwise, see if it's a subclass
            model = provider.get_class(src.attrs['namespace'], src.attrs['neurodata_type'])
            # just inspect the MRO as strings rather than trying to check subclasses because
            # we might replace DynamicTable in the future, and there isn't a stable DynamicTable
            # class to inherit from anyway because of the whole multiple versions thing
            parents = [parent.__name__ for parent in model.__mro__]
            if 'DynamicTable' in parents:
                return True
            else:
                return False
        else:
            return False

    @classmethod
    def apply(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> H5ReadResult:
        with h5py.File(src.h5f_path, 'r') as h5f:
            obj = h5f.get(src.path)

            # make a populated model :)
            # TODO: use a tableproxy like NDArrayProxy to not load all these into memory
            if src.neurodata_type != 'DynamicTable':
                #base_model = provider.get_class(src.namespace, src.neurodata_type)
                base_model = None
            else:
                base_model = None

            model = dynamictable_to_model(obj, base=base_model)

            completes = ['/'.join([src.path, child]) for child in obj.keys()]

        return H5ReadResult(
            path=src.path,
            source=src,
            result=model,
            completes=completes,
            completed = True
        )


class ResolveModelGroup(HDF5Map):
    phase = ReadPhases.read
    priority = 10 # do this generally last
    exclusive = True

    @classmethod
    def check(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
        if 'neurodata_type' in src.attrs and src.h5_type == 'group':
            return True
        else:
            return False

    @classmethod
    def apply(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> H5ReadResult:
        model = provider.get_class(src.namespace, src.neurodata_type)
        res = {}
        with h5py.File(src.h5f_path, 'r') as h5f:
            obj = h5f.get(src.path)
            for key, type in model.model_fields.items():
                if key in obj.attrs:
                    res[key] = obj.attrs[key]
                    continue
                if key in obj.keys():
                    # stash a reference to this, we'll compile it at the end
                    res[key] = HDF5_Path('/'.join([src.path, key]))

        res['hdf5_path'] = src.path
        res['name'] = src.parts[-1]
        return H5ReadResult(
            path=src.path,
            source=src,
            completed=True,
            result = res,
            model = model,
            namespace=src.namespace,
            neurodata_type=src.neurodata_type
        )


#
# class ResolveModelDataset(HDF5Map):
#     phase = ReadPhases.read
#     priority = 10
#     exclusive = True
#
#     @classmethod
#     def check(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
#         if 'neurodata_type' in src.attrs and src.h5_type == 'dataset':
#             return True
#         else:
#             return False
#
#     def apply(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> H5ReadResult:
#
class ResolveScalars(HDF5Map):
    phase = ReadPhases.read
    priority = 11 #catchall
    exclusive = True

    @classmethod
    def check(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
        if src.h5_type == 'dataset' and 'neurodata_type' not in src.attrs:
            with h5py.File(src.h5f_path, 'r') as h5f:
                obj = h5f.get(src.path)
                if obj.shape == ():
                    return True
        else:
            return False
    @classmethod
    def apply(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> H5ReadResult:
        with h5py.File(src.h5f_path, 'r') as h5f:
            obj = h5f.get(src.path)
            res = obj[()]
        return H5ReadResult(
            path=src.path,
            source = src,
            completed=True,
            result = res
        )




class ReadQueue(BaseModel):
    """Container model to store items as they are built """
    h5f: Path = Field(
        description=("Path to the source hdf5 file used when resolving the queue! "
                     "Each translation step should handle opening and closing the file, "
                     "rather than passing a handle around")
    )
    provider: SchemaProvider = Field(
        description="SchemaProvider used by each of the items in the read queue"
    )
    queue: Dict[str,H5SourceItem] = Field(
        default_factory=dict,
        description="Items left to be instantiated, keyed by hdf5 path",
    )
    completed: Dict[str, H5ReadResult] = Field(
        default_factory=dict,
        description="Items that have already been instantiated, keyed by hdf5 path"
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def apply_phase(self, phase:ReadPhases):
        phase_maps = [m for m in HDF5Map.__subclasses__() if m.phase == phase]
        phase_maps = sorted(phase_maps, key=lambda x: x.priority)

        results = []

        # TODO: Thread/multiprocess this
        for name, item in self.queue.items():
            for op in phase_maps:
                if op.check(item, self.provider, self.completed):
                    results.append(op.apply(item, self.provider, self.completed))
                    if op.exclusive:
                        break # out of inner iteration

        # remake the source queue and save results
        for res in results:
            # remove the original item
            del self.queue[res.path]
            if res.completed:
                # if the item has been finished and there is some result, add it to the results
                if res.result is not None:
                    self.completed[res.path] = res
                # otherwise if the item has been completed and there was no result,
                # just drop it.

                # if we have completed other things, delete them from the queue
                for also_completed in res.completes:
                    try:
                        del self.queue[also_completed]
                    except KeyError:
                        # normal, we might have already deleted this in a previous step
                        pass
            else:
                # if we didn't complete the item (eg. we found we needed more dependencies),
                # add the updated source to the queue again
                self.queue[res.path] = res.source







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

        if isinstance(obj, h5py.Dataset):
            h5_type = 'dataset'
        elif isinstance(obj, h5py.Group):
            h5_type = 'group'
        else:
            raise ValueError(f'Object must be a dataset or group! {obj}')

        # get references in attrs and datasets to populate dependencies
        #depends = get_references(obj)

        #if not name.startswith('/'):
        #    name = '/' + name

        attrs = dict(obj.attrs.items())

        items[name] = H5SourceItem.model_construct(
            path = name,
            h5f_path=h5f.file.filename,
            leaf = leaf,
            #depends = depends,
            h5_type=h5_type,
            attrs = attrs,
            namespace = attrs.get('namespace', None),
            neurodata_type= attrs.get('neurodata_type', None)
        )

    h5f.visititems(_itemize)
    return items


def get_references(obj: h5py.Dataset | h5py.Group) -> List[str]:
    """
    Find all hdf5 object references in a dataset or group

    Locate references in

    * Attrs
    * Scalar datasets
    * Single-column datasets
    * Multi-column datasets

    Args:
        obj (:class:`h5py.Dataset` | :class:`h5py.Group`): Object to evaluate

    Returns:
        List[str]: List of paths that are referenced within this object
    """
    # Find references in attrs
    refs = [ref for ref in obj.attrs.values() if isinstance(ref, h5py.h5r.Reference)]

    # For datasets, apply checks depending on shape of data.
    if isinstance(obj, h5py.Dataset):
        if obj.shape == ():
            # scalar
            if isinstance(obj[()], h5py.h5r.Reference):
                refs.append(obj[()])
        elif isinstance(obj[0], h5py.h5r.Reference):
            # single-column
            refs.extend(obj[:].tolist())
        elif len(obj.dtype) > 1:
            # "compound" datasets
            for name in obj.dtype.names:
                if isinstance(obj[name][0], h5py.h5r.Reference):
                    refs.extend(obj[name].tolist())

    # dereference and get name of reference
    if isinstance(obj, h5py.Dataset):
        depends = list(set([obj.parent.get(i).name for i in refs]))
    else:
        depends = list(set([obj.get(i).name for i in refs]))
    return depends
