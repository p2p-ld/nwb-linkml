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
import warnings
from typing import Optional, Dict, overload, Type, Union, List
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, NamedTuple
import json
import subprocess
import shutil
import os

import h5py
from pydantic import BaseModel
from tqdm import tqdm
import numpy as np

from nwb_linkml.maps.hdf5 import H5SourceItem, flatten_hdf, ReadPhases, ReadQueue
#from nwb_linkml.models.core_nwb_file import NWBFile
if TYPE_CHECKING:
    from nwb_linkml.models import NWBFile
from nwb_linkml.providers.schema import SchemaProvider
from nwb_linkml.types.hdf5 import HDF5_Path



class HDF5IO():

    def __init__(self, path:Path):
        self.path = Path(path)
        self._modules: Dict[str, ModuleType] = {}

    @overload
    def read(self, path:None) -> 'NWBFile': ...

    @overload
    def read(self, path:str) -> BaseModel | Dict[str, BaseModel]: ...

    def read(self, path:Optional[str] = None) -> Union['NWBFile', BaseModel, Dict[str, BaseModel]]:
        """
        Read data into models from an NWB File.

        The read process is in several stages:

        * Use :meth:`.make_provider` to generate any needed LinkML Schema or Pydantic Classes using a :class:`.SchemaProvider`
        * :func:`flatten_hdf` file into a :class:`.ReadQueue` of nodes.
        * Apply the queue's :class:`ReadPhases` :

            * ``plan`` - trim any blank nodes, sort nodes to read, etc.
            * ``read`` - load the actual data into temporary holding objects
            * ``construct`` - cast the read data into models.

        Read is split into stages like this to handle references between objects, where the read result of one node
        might depend on another having already been completed. It also allows us to parallelize the operations
        since each mapping operation is independent of the results of all the others in that pass.

        .. todo::

            Implement reading, skipping arrays - they are fast to read with the ArrayProxy class
            and dask, but there are times when we might want to leave them out of the read entirely.
            This might be better implemented as a filter on ``model_dump`` , but to investigate further
            how best to support reading just metadata, or even some specific field value, or if
            we should leave that to other implementations like eg. after we do SQL export then
            not rig up a whole query system ourselves.

        Args:
            path (Optional[str]): If ``None`` (default), read whole file. Otherwise, read from specific (hdf5) path and its children

        Returns:
            ``NWBFile`` if ``path`` is ``None``, otherwise whatever Model or dictionary of models applies to the requested ``path``
        """

        provider = self.make_provider()

        h5f = h5py.File(str(self.path))
        if path:
            src = h5f.get(path)
        else:
            src = h5f

        # get all children of selected item
        if isinstance(src, (h5py.File, h5py.Group)):
            children = flatten_hdf(src)
        else:
            raise NotImplementedError('directly read individual datasets')

        queue = ReadQueue(
            h5f=self.path,
            queue=children,
            provider=provider
        )

        # Apply initial planning phase of reading
        queue.apply_phase(ReadPhases.plan)
        # Read operations gather the data before casting into models
        queue.apply_phase(ReadPhases.read)
        # Construction operations actually cast the models
        # this often needs to run several times as models with dependencies wait for their
        # dependents to be cast
        queue.apply_phase(ReadPhases.construct)

        if path is None:
            return queue.completed['/'].result
        else:
            return queue.completed[path].result

    def write(self, path: Path):
        """
        Write to NWB file

        .. todo::

            Implement HDF5 writing.

            Need to create inverse mappings that can take pydantic models to
            hdf5 groups and datasets. If more metadata about the generation process
            needs to be preserved (eg. explicitly notating that something is an attribute,
            dataset, group, then we can make use of the :class:`~nwb_linkml.generators.pydantic.LinkML_Meta`
            model. If the model to edit has been loaded from an HDF5 file (rather than
            freshly created), then the ``hdf5_path`` should be populated making
            mapping straightforward, but we probably want to generalize that to deterministically
            get hdf5_path from position in the NWBFile object -- I think that might
            require us to explicitly annotate when something is supposed to be a reference
            vs. the original in the model representation, or else it's ambiguous.

            Otherwise, it should be a matter of detecting changes from file if it exists already,
            and then write them.

        """
        raise NotImplementedError('Writing to HDF5 is not implemented yet!')

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


def read_specs_as_dicts(group: h5py.Group) -> dict:
    """
    Utility function to iterate through the `/specifications` group and
    load the schemas from it.

    Args:
        group ( :class:`h5py.Group` ): the ``/specifications`` group!

    Returns:
        ``dict`` of schema.
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


def find_references(h5f: h5py.File, path: str) -> List[str]:
    """
    Find all objects that make a reference to a given object in

    * Attributes
    * Dataset-level dtype (a dataset of references)
    * Compound datasets (a dataset with one "column" of references)

    Notes:
        This is extremely slow because we collect all references first,
        rather than checking them as we go and quitting early. PR if you want to make this faster!

    .. todo::

        Test :func:`.find_references` !

    Args:
        h5f (:class:`h5py.File`): Open hdf5 file
        path (str): Path to search for references to

    Returns:
        list[str]: List of paths that reference the given path
    """
    references = []

    def _find_references(name, obj: h5py.Group | h5py.Dataset):
        pbar.update()
        refs = []
        for attr in obj.attrs.values():
            if isinstance(attr, h5py.h5r.Reference):
                refs.append(attr)


        if isinstance(obj, h5py.Dataset):
            # dataset is all references
            if obj.dtype.metadata is not None and isinstance(obj.dtype.metadata.get('ref', None), h5py.h5r.Reference):
                refs.extend(obj[:].tolist())
            # compound dtype
            elif isinstance(obj.dtype, np.dtypes.VoidDType):
                for name in obj.dtype.names:
                    if isinstance(obj[name][0], h5py.h5r.Reference):
                        refs.extend(obj[name].tolist())


        for ref in refs:
            assert isinstance(ref, h5py.h5r.Reference)
            refname = h5f[ref].name
            if name == path:
                references.append(name)
                return

    pbar = tqdm()
    try:
        h5f.visititems(_find_references)
    finally:
        pbar.close()
    return references


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
    print(f'Copying {source} to {target}...')
    shutil.copy(source, target)
    os.chmod(target, 0o774)

    to_resize = []
    def _need_resizing(name:str, obj: h5py.Dataset | h5py.Group):
        if isinstance(obj, h5py.Dataset):
            if obj.size > n:
                to_resize.append(name)

    print('Resizing datasets...')
    # first we get the items that need to be resized and then resize them below
    # problems with writing to the file from within the visititems call
    h5f_target = h5py.File(str(target), 'r+')
    h5f_target.visititems(_need_resizing)


    for resize in to_resize:
        obj = h5f_target.get(resize)
        try:
            obj.resize(n, axis=0)
        except TypeError:
            # contiguous arrays can't be trivially resized, so we have to copy and create a new dataset
            tmp_name = obj.name + '__tmp'
            original_name = obj.name
            obj.parent.move(obj.name, tmp_name)
            old_obj = obj.parent.get(tmp_name)
            new_obj = obj.parent.create_dataset(original_name, data=old_obj[0:n])
            for k, v in old_obj.attrs.items():
                new_obj.attrs[k] = v
            del new_obj.parent[tmp_name]

    h5f_target.flush()
    h5f_target.close()

    # use h5repack to actually remove the items from the dataset
    if shutil.which('h5repack') is None:
        warnings.warn('Truncated file made, but since h5repack not found in path, file won't be any smaller')
        return target

    print('Repacking hdf5...')
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


