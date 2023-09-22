"""
Just saving a scratch file temporarily where i was trying a different strategy,
rather than doing one big recursive pass through, try and solve subsections
of the tree and then piece them together once you have the others done.

sort of working. I think what i need to do is populate the 'depends'
field more so that at each pass i can work through the items whose dependencies
have been solved from the bottom up.
"""

from nwb_linkml.io.hdf5 import HDF5IO, flatten_hdf
import h5py
from typing import NamedTuple, Tuple, Optional
from nwb_linkml.io.hdf5 import H5SourceItem, FlatH5, ReadQueue, HDF5IO
from nwb_linkml.providers.schema import SchemaProvider
from rich import print
from pydantic import BaseModel


class Rank(NamedTuple):
    has_depends: bool
    not_leaf: bool
    not_dataset: bool
    has_type: bool

def sort_flat(item:Tuple[str, H5SourceItem]):

    return Rank(
        has_depends=len(item[1].depends)>0,
        not_leaf = ~item[1].leaf,
        not_dataset = item[1].h5_type != 'dataset',
        has_type = 'neurodata_type' in item[1].attrs
    )

def prune_empty(flat: FlatH5) -> FlatH5:
    """
    Groups without children or attrs can be removed
    """
    deletes = []
    for k,v in flat.items():
        if v.leaf and v.h5_type == 'group' and len(v.attrs) == 0:
            deletes.append(k)

    for k in deletes:
        del flat[k]

    return flat

def resolve_scalars(res: ReadQueue) -> ReadQueue:
    for path, item in res.queue.copy().items():
        if item.h5_type == 'group':
            continue
        dset = res.h5f.get(path)
        if dset.shape == ():
            res.completed[path] = dset[()]
            res.queue.pop(path)
    return res

def resolve_terminal_arrays(res:ReadQueue) -> ReadQueue:
    """Terminal arrays can just get loaded as a dict"""
    for path, item in res.queue.copy().items():
        if item.h5_type != 'dataset' or not item.leaf or len(item.depends) > 0:
            continue
        h5_object = res.h5f.get(path)
        item_dict = {
            'name': path.split('/')[-1],
            'array': h5_object[:],
            **h5_object.attrs,
        }
        res.completed[path] = item_dict
        res.queue.pop(path)
    return res

def attempt_parentless(res:ReadQueue, provider:SchemaProvider) -> ReadQueue:
    """Try the groups whose parents have no neurodata type (ie. acquisition)"""
    for path, item in res.queue.copy().items():
        if item.h5_type == 'dataset':
            continue
        group = res.h5f.get(path)
        if 'neurodata_type' in group.parent.attrs.keys() or 'neurodata_type' not in group.attrs.keys():
            continue
        model = provider.get_class(group.attrs['namespace'], group.attrs['neurodata_type'])
        res = naive_instantiation(group, model, res)
    return res



def naive_instantiation(element: h5py.Group|h5py.Dataset, model:BaseModel, res:ReadQueue) -> Optional[BaseModel]:
    """
    Try to instantiate model with just the attrs and any resolved children
    """
    print(element)
    kwargs = {}
    kwargs['name'] = element.name.split('/')[-1]
    for k in element.attrs.keys():
        try:
            kwargs[k] = element.attrs[k]
        except Exception as e:
            print(f'couldnt load attr: {e}')
    for key, child in element.items():
        if child.name in res.completed:
            kwargs[child.name] = res.completed[child.name]

    kwargs = {k:v for k,v in kwargs.items() if k in model.model_fields.keys()}

    try:
        instance = model(**kwargs)
        res.queue.pop(element.name)
        res.completed[element.name] = instance
        print('succeeded')
        return res
    except Exception as e:
        print(f'failed: {e}')
        return res


# --------------------------------------------------
path = '/Users/jonny/Dropbox/lab/p2p_ld/data/nwb/sub-738651046_ses-760693773_probe-769322820_ecephys.nwb'

h5io = HDF5IO(path)
provider = h5io.make_provider()

h5f = h5py.File(path)
flat = flatten_hdf(h5f)

flat = prune_empty(flat)
flat_sorted = dict(sorted(flat.items(), key=sort_flat))

res = ReadQueue(h5f=h5f, queue=flat_sorted.copy())

res = resolve_scalars(res)
res = resolve_terminal_arrays(res)
res = attempt_parentless(res, provider)

