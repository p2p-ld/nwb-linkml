"""
Maps for reading and writing from HDF5

We have sort of diverged from the initial idea of a generalized map as in :class:`linkml.map.Map` ,
so we will make our own mapping class here and re-evaluate whether they should be unified later
"""

# ruff: noqa: D102
# ruff: noqa: D101

from typing import List, Union

import h5py


def get_attr_references(obj: h5py.Dataset | h5py.Group) -> dict[str, str]:
    """
    Get any references in object attributes
    """
    refs = {
        k: obj.file.get(ref).name
        for k, ref in obj.attrs.items()
        if isinstance(ref, h5py.h5r.Reference)
    }
    return refs


def get_dataset_references(obj: h5py.Dataset | h5py.Group) -> list[str] | dict[str, str]:
    """
    Get references in datasets
    """
    refs = []
    # For datasets, apply checks depending on shape of data.
    if isinstance(obj, h5py.Dataset):
        if obj.shape == ():
            # scalar
            if isinstance(obj[()], h5py.h5r.Reference):
                refs = [obj.file.get(obj[()]).name]
        elif len(obj) > 0 and isinstance(obj[0], h5py.h5r.Reference):
            # single-column
            refs = [obj.file.get(ref).name for ref in obj[:]]
        elif len(obj.dtype) > 1:
            # "compound" datasets
            refs = {}
            for name in obj.dtype.names:
                if isinstance(obj[name][0], h5py.h5r.Reference):
                    refs[name] = [obj.file.get(ref).name for ref in obj[name]]
    return refs


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
    attr_refs = get_attr_references(obj)
    dataset_refs = get_dataset_references(obj)

    # flatten to list
    refs = [ref for ref in attr_refs.values()]
    if isinstance(dataset_refs, list):
        refs.extend(dataset_refs)
    else:
        for v in dataset_refs.values():
            refs.extend(v)

    return refs


def resolve_hardlink(obj: Union[h5py.Group, h5py.Dataset]) -> str:
    """
    Unhelpfully, hardlinks are pretty challenging to detect with h5py, so we have
    to do extra work to check if an item is "real" or a hardlink to another item.

    Particularly, an item will be excluded from the ``visititems`` method used by
    :func:`.flatten_hdf` if it is a hardlink rather than an "original" dataset,
    meaning that we don't even have them in our sources list when start reading.

    We basically dereference the object and return that path instead of the path
    given by the object's ``name``
    """
    return obj.file[obj.ref].name
