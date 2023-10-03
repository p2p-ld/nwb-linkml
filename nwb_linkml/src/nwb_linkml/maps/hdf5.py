"""
Maps for reading and writing from HDF5

We have sort of diverged from the initial idea of a generalized map as in :class:`linkml.map.Map` ,
so we will make our own mapping class here and re-evaluate whether they should be unified later
"""
import pdb
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal, List, Dict, Optional, Type, Union, Tuple

import h5py
from enum import StrEnum

from pydantic import BaseModel, Field, ConfigDict

from nwb_linkml.providers.schema import SchemaProvider
from nwb_linkml.maps.hdmf import dynamictable_to_model
from nwb_linkml.types.hdf5 import HDF5_Path
from nwb_linkml.types.ndarray import NDArrayProxy


class ReadPhases(StrEnum):
    plan = 'plan'
    """Before reading starts, building an index of objects to read"""
    read = 'read'
    """Main reading operation"""
    construct = 'construct'
    """After reading, casting the results of the read into their models"""

class H5SourceItem(BaseModel):
    """
    Descriptor of items for each element when :func:`.flatten_hdf` flattens an hdf5 file.

    Consumed by :class:`.HDF5Map` classes, orchestrated by :class:`.ReadQueue`
    """
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
    """
    Result returned by each of our mapping operations.

    Also used as the source for operations in the ``construct`` :class:`.ReadPhases`
    """
    path: str
    """absolute hdf5 path of element"""
    source: Union[H5SourceItem, 'H5ReadResult']
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
    result: Optional[dict | str | int | float | BaseModel] = None
    """
    If completed, built result. A dict that can be instantiated into the model.
    If completed is True and result is None, then remove this object
    """
    model: Optional[Type[BaseModel]] = None
    """
    The model that this item should be cast into
    """
    completes: List[HDF5_Path] = Field(default_factory=list)
    """
    If this result completes any other fields, we remove them from the build queue.
    """
    namespace: Optional[str] = None
    """
    Optional: the namespace of the neurodata type for this object
    """
    neurodata_type: Optional[str] = None
    """
    Optional: The neurodata type to use for this object
    """
    applied: List[str] = Field(default_factory=list)
    """
    Which map operations were applied to this item
    """
    errors: List[str] = Field(default_factory=list)
    """
    Problems that occurred during resolution
    """
    depends: List[HDF5_Path] = Field(default_factory=list)
    """
    Other items that the final resolution of this item depends on
    """


FlatH5 = Dict[str, H5SourceItem]


class HDF5Map(ABC):
    phase: ReadPhases
    priority: int = 0
    """
    Within a phase, sort mapping operations from low to high priority
    (maybe this should be renamed because highest priority last doesnt make a lot of sense)
    """

    @classmethod
    @abstractmethod
    def check(cls, src: H5SourceItem|H5ReadResult, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
        """Check if this map applies to the given item to read"""

    @classmethod
    @abstractmethod
    def apply(cls, src: H5SourceItem|H5ReadResult, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> H5ReadResult:
        """Actually apply the map!"""


# --------------------------------------------------
# Planning maps
# --------------------------------------------------

def check_empty(obj: h5py.Group) -> bool:
    """
    Check if a group has no attrs or children OR has no attrs and all its children also have no attrs and no children

    Returns:
        bool
    """
    if isinstance(obj, h5py.Dataset):
        return False

    # check if we are empty
    no_attrs = False
    if len(obj.attrs) == 0:
        no_attrs = True

    no_children = False
    if len(obj.keys()) == 0:
        no_children = True

    # check if immediate children are empty
    # handles empty groups of empty groups
    children_empty = False
    if all([isinstance(item, h5py.Group) and \
            len(item.keys()) == 0 and \
            len(item.attrs) == 0 \
            for item in obj.values()]):
        children_empty = True

    # if we have no attrs and we are a leaf OR our children are empty, remove us
    if no_attrs and (no_children or children_empty):
        return True
    else:
        return False

class PruneEmpty(HDF5Map):
    """Remove groups with no attrs """
    phase = ReadPhases.plan
    @classmethod
    def check(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
        if src.h5_type == 'group':
            with h5py.File(src.h5f_path, 'r') as h5f:
                obj = h5f.get(src.path)
                return check_empty(obj)

    @classmethod
    def apply(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> H5ReadResult:
        return H5ReadResult.model_construct(
            path = src.path,
            source=src,
            completed=True
        )


class ResolveDynamicTable(HDF5Map):
    """
    Handle loading a dynamic table!

    Dynamic tables are sort of odd in that their models don't include their fields (except as a list of
    strings in ``colnames`` ), so we need to create a new model that includes fields for each column,
    and then we include the datasets as :class:`~.nwb_linkml.types.ndarray.NDArrayProxy` objects which
    lazy load the arrays in a thread/process safe way.

    This map also resolves the child elements, indicating so by the ``completes`` field in the :class:`.ReadResult`
    """
    phase = ReadPhases.read
    priority = 1
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
            base_model = provider.get_class(src.namespace, src.neurodata_type)
            model = dynamictable_to_model(obj, base=base_model)

            completes = [HDF5_Path(child.name) for child in obj.values()]

        return H5ReadResult(
            path=src.path,
            source=src,
            result=model,
            completes=completes,
            completed = True,
            applied=['ResolveDynamicTable']
        )


class ResolveModelGroup(HDF5Map):
    """
    HDF5 Groups that have a model, as indicated by ``neurodata_type`` in their attrs.
    We use the model to determine what fields we should get, and then stash references to the children to
    process later as :class:`.HDF5_Path`

    **Special Case:** Some groups like ``ProcessingGroup`` and others that have an arbitrary
    number of named children have a special ``children`` field that is a dictionary mapping
    names to the objects themselves.

    So for example, this:

        /processing/
            eye_tracking/
                cr_ellipse_fits/
                    center_x
                    center_y
                    ...
                eye_ellipse_fits/
                    ...
                pupil_ellipse_fits/
                    ...
            eye_tracking_rig_metadata/
                ...

    would pack the ``eye_tracking`` group (a ``ProcessingModule`` ) as:

        {
            "name": "eye_tracking",
            "children": {
                "cr_ellipse_fits": HDF5_Path('/processing/eye_tracking/cr_ellipse_fits'),
                "eye_ellipse_fits" : HDF5_Path('/processing/eye_tracking/eye_ellipse_fits'),
                ...
            }
        }

    We will do some nice things in the model metaclass to make it possible to access the children like
    ``nwbfile.processing.cr_ellipse_fits.center_x`` rather than having to switch between indexing and
    attribute access :)
    """
    phase = ReadPhases.read
    priority = 10 # do this generally last

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
        depends = []
        with h5py.File(src.h5f_path, 'r') as h5f:
            obj = h5f.get(src.path)
            for key, type in model.model_fields.items():
                if key == 'children':
                    res[key] = {name: resolve_hardlink(child) for name, child in obj.items()}
                    depends.extend([resolve_hardlink(child)for child in obj.values()])
                elif key in obj.attrs:
                    res[key] = obj.attrs[key]
                    continue
                elif key in obj.keys():
                    # make sure it's not empty
                    if check_empty(obj[key]):
                        continue
                    # stash a reference to this, we'll compile it at the end
                    depends.append(resolve_hardlink(obj[key]))
                    res[key] = resolve_hardlink(obj[key])


        res['hdf5_path'] = src.path
        res['name'] = src.parts[-1]
        return H5ReadResult(
            path=src.path,
            source=src,
            completed=True,
            result = res,
            model = model,
            namespace=src.namespace,
            neurodata_type=src.neurodata_type,
            applied=['ResolveModelGroup'],
            depends=depends
        )

class ResolveDatasetAsDict(HDF5Map):
    """
    Resolve datasets that do not have a ``neurodata_type`` of their own as a dictionary
    that will be packaged into a model in the next step. Grabs the array in an :class:`~nwb_linkml.types.ndarray.NDArrayProxy`
    under an ``array`` key, and then grabs any additional ``attrs`` as well.

    Mutually exclusive with :class:`.ResolveScalars` - this only applies to datasets that are larger
    than a single entry.
    """
    phase = ReadPhases.read
    priority = 11

    @classmethod
    def check(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
        if src.h5_type == 'dataset' and 'neurodata_type' not in src.attrs:
            with h5py.File(src.h5f_path, 'r') as h5f:
                obj = h5f.get(src.path)
                if obj.shape != ():
                    return True
                else: return False
        else:
            return False

    @classmethod
    def apply(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> H5ReadResult:

        res = {
            'array': NDArrayProxy(h5f_file=src.h5f_path, path=src.path),
            'hdf5_path' : src.path,
            'name': src.parts[-1],
            **src.attrs
        }
        return H5ReadResult(
            path = src.path,
            source=src,
            completed=True,
            result=res,
            applied=['ResolveDatasetAsDict']
        )

class ResolveScalars(HDF5Map):
    phase = ReadPhases.read
    priority = 11 #catchall

    @classmethod
    def check(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
        if src.h5_type == 'dataset' and 'neurodata_type' not in src.attrs:
            with h5py.File(src.h5f_path, 'r') as h5f:
                obj = h5f.get(src.path)
                if obj.shape == ():
                    return True
                else:
                    return False
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
            result = res,
            applied=['ResolveScalars']
        )

class ResolveContainerGroups(HDF5Map):
    """
    Groups like ``/acquisition``` and others that have no ``neurodata_type``
    (and thus no model) are returned as a dictionary with :class:`.HDF5_Path` references to
    the children they contain
    """
    phase = ReadPhases.read
    priority = 9

    @classmethod
    def check(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
        if src.h5_type == 'group' and 'neurodata_type' not in src.attrs and len(src.attrs) == 0:
            with h5py.File(src.h5f_path, 'r') as h5f:
                obj = h5f.get(src.path)
                if len(obj.keys()) > 0:
                    return True
                else:
                    return False
        else:
            return False

    @classmethod
    def apply(cls, src: H5SourceItem, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> H5ReadResult:
        """Simple, just return a dict with references to its children"""
        depends = []
        with h5py.File(src.h5f_path, 'r') as h5f:
            obj = h5f.get(src.path)
            children = {}
            for k, v in obj.items():
                children[k] = HDF5_Path(v.name)
                depends.append(HDF5_Path(v.name))

        # res = {
        #     'name': src.parts[-1],
        #     'hdf5_path': src.path,
        #     **children
        # }

        return H5ReadResult(
            path=src.path,
            source=src,
            completed=True,
            result=children,
            depends=depends,
            applied=['ResolveContainerGroups']
        )


# --------------------------------------------------
# Completion Steps
# --------------------------------------------------

class CompletePassThrough(HDF5Map):
    """
    Passthrough map for the construction phase for models that don't need any more work done

    - :class:`.ResolveDynamicTable`
    - :class:`.ResolveDatasetAsDict`
    - :class:`.ResolveScalars`
    """
    phase = ReadPhases.construct
    priority = 1
    @classmethod
    def check(cls, src: H5ReadResult, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
        passthrough_ops = ('ResolveDynamicTable', 'ResolveDatasetAsDict', 'ResolveScalars')

        for op in passthrough_ops:
            if hasattr(src, 'applied') and op in src.applied:
                return True
        return False

    @classmethod
    def apply(cls, src: H5ReadResult, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> H5ReadResult:
        return src

class CompleteContainerGroups(HDF5Map):
    """
    Complete container groups (usually top-level groups like /acquisition)
    that do not have a ndueodata type of their own by resolving them as dictionaries
    of values (that will then be given to their parent model)

    """
    phase = ReadPhases.construct
    priority = 3

    @classmethod
    def check(cls, src: H5ReadResult, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
        if src.model is None and \
            src.neurodata_type is None and \
                src.source.h5_type == 'group' and \
                all([depend in completed.keys() for depend in src.depends]):
            return True
        else:
            return False

    @classmethod
    def apply(cls, src: H5ReadResult, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> H5ReadResult:
        res, errors, completes = resolve_references(src.result, completed)

        return H5ReadResult(
            result=res,
            errors=errors,
            completes=completes,
            **src.model_dump(exclude={'result', 'errors', 'completes'})
        )


class CompleteModelGroups(HDF5Map):
    phase = ReadPhases.construct
    priority = 4

    @classmethod
    def check(cls, src: H5ReadResult, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> bool:
        if src.model is not None and \
                src.source.h5_type == 'group' and \
                all([depend in completed.keys() for depend in src.depends]):
            return True
        else:
            return False

    @classmethod
    def apply(cls, src: H5ReadResult, provider:SchemaProvider, completed: Dict[str, H5ReadResult]) -> H5ReadResult:
        # gather any results that were left for completion elsewhere
        # first get all already-completed items
        res = {k:v for k,v in src.result.items() if not isinstance(v, HDF5_Path)}
        unpacked_results, errors, completes = resolve_references(src.result, completed)
        res.update(unpacked_results)

        # # final cleanups
        # for key, val in res.items():
        #     # if we're supposed to be a list, but instead we're an array, fix that!
        #

        #try:
        instance = src.model(**res)
        return H5ReadResult(
            path=src.path,
            source=src,
            result=instance,
            model=src.model,
            completed=True,
            completes=completes,
            neurodata_type=src.neurodata_type,
            namespace=src.namespace,
            applied=src.applied + ['CompleteModelGroups'],
            errors=errors
        )
        # except ValidationError:
        #     # didn't get it! try again next time
        #     return H5ReadResult(
        #         path=src.path,
        #         source=src,
        #         result=src,
        #         model=src.model,
        #         completed=True,
        #         completes=completes,
        #         neurodata_type=src.neurodata_type,
        #         namespace=src.namespace,
        #         applied=src.applied + ['CompleteModelGroups']
        #     )





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
    queue: Dict[str,H5SourceItem|H5ReadResult] = Field(
        default_factory=dict,
        description="Items left to be instantiated, keyed by hdf5 path",
    )
    completed: Dict[str, H5ReadResult] = Field(
        default_factory=dict,
        description="Items that have already been instantiated, keyed by hdf5 path"
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)
    phases_completed: List[ReadPhases] = Field(
        default_factory=list,
        description="Phases that have already been completed")

    def apply_phase(self, phase:ReadPhases, max_passes=5):
        phase_maps = [m for m in HDF5Map.__subclasses__() if m.phase == phase]
        phase_maps = sorted(phase_maps, key=lambda x: x.priority)

        results = []

        # TODO: Thread/multiprocess this
        for name, item in self.queue.items():
            for op in phase_maps:
                if op.check(item, self.provider, self.completed):
                    # Formerly there was an "exclusive" property in the maps which let potentially multiple
                    # operations be applied per stage, except if an operation was `exclusive` which would break
                    # iteration over the operations. This was removed because it was badly implemented, but
                    # if there is ever a need to do that, then we would need to decide what to do with the
                    # multiple results.
                    results.append(op.apply(item, self.provider, self.completed))
                    break # out of inner iteration

        # remake the source queue and save results
        completes = []
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
                completes.extend(res.completes)

            else:
                # if we didn't complete the item (eg. we found we needed more dependencies),
                # add the updated source to the queue again
                if phase != ReadPhases.construct:
                    self.queue[res.path] = res.source
                else:
                    self.queue[res.path] = res

        # delete the ones that were already completed but might have been
        # incorrectly added back in the pile
        for c in completes:
            try:
                del self.queue[c]
            except KeyError:
                pass

        # if we have nothing left in our queue, we have completed this phase
        # and prepare only ever has one pass
        if phase == ReadPhases.plan:
            self.phases_completed.append(phase)
            return

        if len(self.queue) == 0:
            self.phases_completed.append(phase)
            if phase != ReadPhases.construct:
                # if we're not in the last phase, move our completed to our queue
                self.queue = self.completed
                self.completed = {}
        elif max_passes>0:
            self.apply_phase(phase, max_passes=max_passes-1)










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

        if not name.startswith('/'):
           name = '/' + name

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
    # then add the root item
    _itemize(h5f.name, h5f)
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

def resolve_references(src: dict, completed: Dict[str, H5ReadResult]) -> Tuple[dict, List[str], List[HDF5_Path]]:
    """
    Recursively replace references to other completed items with their results

    """
    completes = []
    errors = []
    res = {}
    for path, item in src.items():
        if isinstance(item, HDF5_Path):
            other_item = completed.get(item, None)
            if other_item is None:
                errors.append(f"Couldnt find: {item}")
            res[path] = other_item.result
            completes.append(item)

        elif isinstance(item, dict):
            inner_res, inner_error, inner_completes = resolve_references(item, completed)
            res[path] =  inner_res
            errors.extend(inner_error)
            completes.extend(inner_completes)
        else:
            res[path] = item
    return res, errors, completes

def resolve_hardlink(obj: Union[h5py.Group, h5py.Dataset]) -> HDF5_Path:
    """
    Unhelpfully, hardlinks are pretty challenging to detect with h5py, so we have
    to do extra work to check if an item is "real" or a hardlink to another item.

    Particularly, an item will be excluded from the ``visititems`` method used by
    :func:`.flatten_hdf` if it is a hardlink rather than an "original" dataset,
    meaning that we don't even have them in our sources list when start reading.

    We basically dereference the object and return that path instead of the path
    given by the object's ``name``
    """
    return HDF5_Path(obj.file[obj.ref].name)



