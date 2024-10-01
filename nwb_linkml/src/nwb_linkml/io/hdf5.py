"""
This is a sandbox file that should be split out to its own pydantic-hdf5 package,
but just experimenting here to get our bearings

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

import json
import os
import re
import shutil
import subprocess
import sys
import warnings
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Dict, List, Optional, Union, overload

import h5py
import networkx as nx
import numpy as np
from numpydantic.interface.hdf5 import H5ArrayPath
from pydantic import BaseModel
from tqdm import tqdm

from nwb_linkml.maps.hdf5 import (
    get_attr_references,
    get_dataset_references,
    get_references,
    resolve_hardlink,
)

if TYPE_CHECKING:
    from nwb_linkml.providers.schema import SchemaProvider
    from nwb_models.models import NWBFile

if sys.version_info.minor >= 11:
    from typing import Never
else:
    from typing_extensions import Never


SKIP_PATTERN = re.compile("(^/specifications.*)|(\.specloc)")
"""Nodes to always skip in reading e.g. because they are handled elsewhere"""


def hdf_dependency_graph(h5f: Path | h5py.File | h5py.Group) -> nx.DiGraph:
    """
    Directed dependency graph of dataset and group nodes in an NWBFile such that
    each node ``n_i`` is connected to node ``n_j`` if

    * ``n_j`` is ``n_i``'s child
    * ``n_i`` contains a reference to ``n_j``

    Resolve references in

    * Attributes
    * Dataset columns
    * Compound dtypes

    Edges are labeled with ``reference`` or ``child`` depending on the type of edge it is,
    and attributes from the hdf5 file are added as node attributes.

    Args:
        h5f (:class:`pathlib.Path` | :class:`h5py.File`): NWB file to graph

    Returns:
        :class:`networkx.DiGraph`
    """

    if isinstance(h5f, (Path, str)):
        h5f = h5py.File(h5f, "r")

    g = nx.DiGraph()

    def _visit_item(name: str, node: h5py.Dataset | h5py.Group) -> None:
        if SKIP_PATTERN.match(node.name):
            return
        # find references in attributes
        refs = get_references(node)
        # add edges from references
        edges = [(node.name, ref) for ref in refs if not SKIP_PATTERN.match(ref)]
        g.add_edges_from(edges, label="reference")

        # add children, if group
        if isinstance(node, h5py.Group):
            children = [
                resolve_hardlink(child)
                for child in node.values()
                if not SKIP_PATTERN.match(child.name)
            ]
            edges = [(node.name, ref) for ref in children if not SKIP_PATTERN.match(ref)]
            g.add_edges_from(edges, label="child")

        # ensure node added to graph
        if len(edges) == 0:
            g.add_node(node.name)

        # store attrs in node
        g.nodes[node.name].update(node.attrs)

    # apply to root
    _visit_item(h5f.name, h5f)

    h5f.visititems(_visit_item)
    return g


def filter_dependency_graph(g: nx.DiGraph) -> nx.DiGraph:
    """
    Remove nodes from a dependency graph if they

    * have no neurodata type AND
    * have no outbound edges

    OR

    * are a VectorIndex (which are handled by the dynamictable mixins)
    """
    remove_nodes = []
    node: str
    for node in g.nodes:
        ndtype = g.nodes[node].get("neurodata_type", None)
        if (ndtype is None and g.out_degree(node) == 0) or SKIP_PATTERN.match(node):
            remove_nodes.append(node)

    g.remove_nodes_from(remove_nodes)
    return g


def _load_node(
    path: str, h5f: h5py.File, provider: "SchemaProvider", context: dict
) -> dict | BaseModel:
    """
    Load an individual node in the graph, then removes it from the graph
    Args:
        path:
        g:
        context:

    Returns:

    """
    obj = h5f.get(path)

    if isinstance(obj, h5py.Dataset):
        args = _load_dataset(obj, h5f, context)
    elif isinstance(obj, h5py.Group):
        args = _load_group(obj, h5f, context)
    else:
        raise TypeError(f"Nodes can only be h5py Datasets and Groups, got {obj}")

    if "neurodata_type" in obj.attrs:
        # SPECIAL CASE: ignore `.specloc`
        if ".specloc" in args:
            del args[".specloc"]

        model = provider.get_class(obj.attrs["namespace"], obj.attrs["neurodata_type"])
        return model(**args)

    else:
        if "name" in args:
            del args["name"]
        if "hdf5_path" in args:
            del args["hdf5_path"]
        return args


def _load_dataset(
    dataset: h5py.Dataset, h5f: h5py.File, context: dict
) -> Union[dict, str, int, float]:
    """
    Resolves datasets that do not have a ``neurodata_type`` as a dictionary or a scalar.

    If the dataset is a single value without attrs, load it and return as a scalar value.
    Otherwise return a :class:`.H5ArrayPath` as a reference to the dataset in the `value` key.
    """
    res = {}
    if dataset.shape == ():
        val = dataset[()]
        if isinstance(val, h5py.h5r.Reference):
            val = context.get(h5f[val].name)
        # if this is just a scalar value, return it
        if not dataset.attrs:
            return val

        res["value"] = val
    elif len(dataset) > 0 and isinstance(dataset[0], h5py.h5r.Reference):
        # vector of references
        res["value"] = [context.get(h5f[ref].name) for ref in dataset[:]]
    elif len(dataset.dtype) > 1:
        # compound dataset - check if any of the fields are references
        for name in dataset.dtype.names:
            if isinstance(dataset[name][0], h5py.h5r.Reference):
                res[name] = [context.get(h5f[ref].name) for ref in dataset[name]]
            else:
                res[name] = H5ArrayPath(h5f.filename, dataset.name, name)
    else:
        res["value"] = H5ArrayPath(h5f.filename, dataset.name)

    res.update(dataset.attrs)
    if "namespace" in res:
        del res["namespace"]
    if "neurodata_type" in res:
        del res["neurodata_type"]
    res["name"] = dataset.name.split("/")[-1]
    res["hdf5_path"] = dataset.name

    # resolve attr references
    for k, v in res.items():
        if isinstance(v, h5py.h5r.Reference):
            ref_path = h5f[v].name
            if SKIP_PATTERN.match(ref_path):
                res[k] = ref_path
            else:
                res[k] = context[ref_path]

    if len(res) == 1:
        return res["value"]
    else:
        return res


def _load_group(group: h5py.Group, h5f: h5py.File, context: dict) -> dict:
    """
    Load a group!
    """
    res = {}
    res.update(group.attrs)
    for child_name, child in group.items():
        if child.name in context:
            res[child_name] = context[child.name]
        elif isinstance(child, h5py.Dataset):
            res[child_name] = _load_dataset(child, h5f, context)
        elif isinstance(child, h5py.Group):
            res[child_name] = _load_group(child, h5f, context)
        else:
            raise TypeError(
                "Can only handle preinstantiated child objects in context, datasets, and group,"
                f" got {child} for {child_name}"
            )
    if "namespace" in res:
        del res["namespace"]
    if "neurodata_type" in res:
        del res["neurodata_type"]
        name = group.name.split("/")[-1]
        if name:
            res["name"] = name
        res["hdf5_path"] = group.name

    # resolve attr references
    for k, v in res.items():
        if isinstance(v, h5py.h5r.Reference):
            ref_path = h5f[v].name
            if SKIP_PATTERN.match(ref_path):
                res[k] = ref_path
            else:
                res[k] = context[ref_path]

    return res


class HDF5IO:
    """
    Read (and eventually write) from an NWB HDF5 file.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self._modules: Dict[str, ModuleType] = {}

    @overload
    def read(self, path: None) -> "NWBFile": ...

    @overload
    def read(self, path: str) -> BaseModel | Dict[str, BaseModel]: ...

    def read(self, path: Optional[str] = None) -> Union["NWBFile", BaseModel, Dict[str, BaseModel]]:
        """
        Read data into models from an NWB File.

        The read process is in several stages:

        * Use :meth:`.make_provider` to generate any needed LinkML Schema or Pydantic Classes
          using a :class:`.SchemaProvider`
        * :func:`flatten_hdf` file into a :class:`.ReadQueue` of nodes.
        * Apply the queue's :class:`ReadPhases` :

            * ``plan`` - trim any blank nodes, sort nodes to read, etc.
            * ``read`` - load the actual data into temporary holding objects
            * ``construct`` - cast the read data into models.

        Read is split into stages like this to handle references between objects,
        where the read result of one node
        might depend on another having already been completed.
        It also allows us to parallelize the operations
        since each mapping operation is independent of the results of all the others in that pass.

        .. todo::

            Implement reading, skipping arrays - they are fast to read with the ArrayProxy class
            and dask, but there are times when we might want to leave them out of the read entirely.
            This might be better implemented as a filter on ``model_dump`` ,
            but to investigate further how best to support reading just metadata,
            or even some specific field value, or if
            we should leave that to other implementations like eg. after we do SQL export then
            not rig up a whole query system ourselves.

        Args:
            path (Optional[str]): If ``None`` (default), read whole file.
                Otherwise, read from specific (hdf5) path and its children

        Returns:
            ``NWBFile`` if ``path`` is ``None``,
            otherwise whatever Model or dictionary of models applies to the requested ``path``
        """

        provider = self.make_provider()

        h5f = h5py.File(str(self.path))
        src = h5f.get(path) if path else h5f
        graph = hdf_dependency_graph(src)
        graph = filter_dependency_graph(graph)

        # topo sort to get read order
        # TODO: This could be parallelized using `topological_generations`,
        # but it's not clear what the perf bonus would be because there are many generations
        # with few items
        topo_order = list(reversed(list(nx.topological_sort(graph))))
        context = {}
        for node in topo_order:
            res = _load_node(node, h5f, provider, context)
            context[node] = res

        if path is None:
            path = "/"
        return context[path]

    def write(self, path: Path) -> Never:
        """
        Write to NWB file

        .. todo::

            Implement HDF5 writing.

            Need to create inverse mappings that can take pydantic models to
            hdf5 groups and datasets. If more metadata about the generation process
            needs to be preserved (eg. explicitly notating that something is an attribute,
            dataset, group, then we can make use of the
            :class:`~nwb_linkml.generators.pydantic.LinkML_Meta`
            model. If the model to edit has been loaded from an HDF5 file (rather than
            freshly created), then the ``hdf5_path`` should be populated making
            mapping straightforward, but we probably want to generalize that to deterministically
            get hdf5_path from position in the NWBFile object -- I think that might
            require us to explicitly annotate when something is supposed to be a reference
            vs. the original in the model representation, or else it's ambiguous.

            Otherwise, it should be a matter of detecting changes from file if it exists already,
            and then write them.

        """
        raise NotImplementedError("Writing to HDF5 is not implemented yet!")

    def make_provider(self) -> "SchemaProvider":
        """
        Create a :class:`~.providers.schema.SchemaProvider` by
        reading specifications from the NWBFile ``/specification`` group and translating
        them to LinkML and generating pydantic models

        Returns:
            :class:`~.providers.schema.SchemaProvider` : Schema Provider with correct versions
                specified as defaults
        """
        from nwb_linkml.providers.schema import SchemaProvider

        h5f = h5py.File(str(self.path), "r")
        schema = read_specs_as_dicts(h5f.get("specifications"))

        # get versions for each namespace
        versions = {}
        for ns_schema in schema.values():
            # each "namespace" can actually contain multiple namespaces
            # which actually contain the version info
            for inner_ns in ns_schema["namespace"]["namespaces"]:
                versions[inner_ns["name"]] = inner_ns["version"]

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

    def _read_spec(name: str, node: h5py.Dataset) -> None:

        if isinstance(node, h5py.Dataset):
            # make containing dict if they don't exist
            pieces = node.name.split("/")
            if pieces[-3] not in spec_dict:
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

    def _find_references(name: str, obj: h5py.Group | h5py.Dataset) -> None:
        pbar.update()
        refs = [attr for attr in obj.attrs.values() if isinstance(attr, h5py.h5r.Reference)]

        if isinstance(obj, h5py.Dataset):
            # dataset is all references
            if obj.dtype.metadata is not None and isinstance(
                obj.dtype.metadata.get("ref", None), h5py.h5r.Reference
            ):
                refs.extend(obj[:].tolist())
            # compound dtype
            elif isinstance(obj.dtype, np.dtypes.VoidDType):
                for name in obj.dtype.names:
                    if isinstance(obj[name][0], h5py.h5r.Reference):
                        refs.extend(obj[name].tolist())

        for ref in refs:
            assert isinstance(ref, h5py.h5r.Reference)
            if name == path:
                references.append(name)
                return

    pbar = tqdm()
    try:
        h5f.visititems(_find_references)
    finally:
        pbar.close()
    return references


def truncate_file(source: Path, target: Optional[Path] = None, n: int = 10) -> Path | None:
    """
    Create a truncated HDF5 file where only the first few samples are kept.

    Used primarily to create testing data from real data without it being so damn bit

    Args:
        source (:class:`pathlib.Path`): Source hdf5 file
        target (:class:`pathlib.Path`): Optional - target hdf5 file to write to.
            If ``None``, use ``{source}_truncated.hdf5``
        n (int): The number of items from datasets
            (samples along the 0th dimension of a dataset) to include

    Returns:
        :class:`pathlib.Path` path of the truncated file
    """
    if shutil.which("h5repack") is None:
        warnings.warn(
            "Truncation requires h5repack to be available, "
            "or else the truncated files will be no smaller than the originals",
            stacklevel=2,
        )
        return

    target = source.parent / (source.stem + "_truncated.hdf5") if target is None else Path(target)

    source = Path(source)

    # and also a temporary file that we'll make with h5repack
    target_tmp = target.parent / (target.stem + "_tmp.hdf5")

    # copy the whole thing
    if target.exists():
        target.unlink()
    print(f"Copying {source} to {target}...")
    shutil.copy(source, target)
    os.chmod(target, 0o774)

    to_resize = []
    attr_refs = {}
    dataset_refs = {}

    def _need_resizing(name: str, obj: h5py.Dataset | h5py.Group) -> None:
        if isinstance(obj, h5py.Dataset) and obj.size > n:
            to_resize.append(name)

    def _find_attr_refs(name: str, obj: h5py.Dataset | h5py.Group) -> None:
        """Find all references in object attrs"""
        refs = get_attr_references(obj)
        if refs:
            attr_refs[name] = refs

    def _find_dataset_refs(name: str, obj: h5py.Dataset | h5py.Group) -> None:
        """Find all references in datasets themselves"""
        refs = get_dataset_references(obj)
        if refs:
            dataset_refs[name] = refs

    # first we get the items that need to be resized and then resize them below
    # problems with writing to the file from within the visititems call
    print("Planning resize...")
    h5f_target = h5py.File(str(target), "r+")
    h5f_target.visititems(_need_resizing)
    h5f_target.visititems(_find_attr_refs)
    h5f_target.visititems(_find_dataset_refs)

    print("Resizing datasets...")
    for resize in to_resize:
        obj = h5f_target.get(resize)
        try:
            obj.resize(n, axis=0)
        except TypeError:
            # contiguous arrays can't be trivially resized,
            # so we have to copy and create a new dataset
            tmp_name = obj.name + "__tmp"
            original_name = obj.name

            obj.parent.move(obj.name, tmp_name)
            old_obj = obj.parent.get(tmp_name)
            new_obj = obj.parent.create_dataset(
                original_name, data=old_obj[0:n], dtype=old_obj.dtype
            )
            for k, v in old_obj.attrs.items():

                new_obj.attrs[k] = v
            del new_obj.parent[tmp_name]

    h5f_target.flush()
    h5f_target.close()

    # use h5repack to actually remove the items from the dataset
    print("Repacking hdf5...")
    res = subprocess.run(
        [
            "h5repack",
            "--verbose=2",
            "--enable-error-stack",
            "-f",
            "GZIP=9",
            str(target),
            str(target_tmp),
        ],
        capture_output=True,
    )
    if res.returncode != 0:
        warnings.warn(f"h5repack did not return 0: {res.stderr} {res.stdout}", stacklevel=2)
        # remove the attempt at the repack
        target_tmp.unlink()
        return target

    h5f_target = h5py.File(str(target_tmp), "r+")

    # recreate references after repacking, because repacking ruins them if they
    # are in a compound dtype
    for obj_name, obj_refs in attr_refs.items():
        obj = h5f_target.get(obj_name)
        for attr_name, ref_target in obj_refs.items():
            ref_target = h5f_target.get(ref_target)
            obj.attrs[attr_name] = ref_target.ref

    for obj_name, obj_refs in dataset_refs.items():
        obj = h5f_target.get(obj_name)
        if isinstance(obj_refs, list):
            if len(obj_refs) == 1:
                ref_target = h5f_target.get(obj_refs[0])
                obj[()] = ref_target.ref
            else:
                targets = [h5f_target.get(ref).ref for ref in obj_refs[:n]]
                obj[:] = targets
        else:
            # dict for a compound dataset
            for col_name, column_refs in obj_refs.items():
                targets = [h5f_target.get(ref).ref for ref in column_refs[:n]]
                data = obj[:]
                data[col_name] = targets
                obj[:] = data

    h5f_target.flush()
    h5f_target.close()

    target.unlink()
    target_tmp.rename(target)

    return target
