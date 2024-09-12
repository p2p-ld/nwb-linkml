import h5py
import networkx as nx
import numpy as np
import pytest

from nwb_linkml.io.hdf5 import HDF5IO, filter_dependency_graph, hdf_dependency_graph, truncate_file
from nwb_linkml.maps.hdf5 import resolve_hardlink


@pytest.mark.skip()
@pytest.mark.parametrize("dset", ["aibs.nwb", "aibs_ecephys.nwb"])
def test_hdf_read(data_dir, dset):
    NWBFILE = data_dir / dset
    io = HDF5IO(path=NWBFILE)
    # the test for now is just whether we can read it lol
    _ = io.read()


def test_truncate_file(tmp_output_dir):
    source = tmp_output_dir / "truncate_source.hdf5"

    # create a dang ol hdf5 file with a big dataset and some softlinks and make sure
    # we truncate the dataset and preserve softlink

    h5f = h5py.File(str(source), "w")
    data_group = h5f.create_group("data")
    dataset_contig = h5f.create_dataset(
        "/data/dataset_contig",
        data=np.zeros((1000, 30, 40), dtype=np.float64),
        compression="gzip",
        compression_opts=9,
    )
    dataset_chunked = h5f.create_dataset(
        "/data/dataset_chunked",
        data=np.zeros((1000, 40, 50), dtype=np.float64),
        compression="gzip",
        compression_opts=9,
        chunks=True,
    )
    dataset_contig.attrs["reference_other"] = dataset_chunked.ref
    dataset_chunked.attrs["reference_other"] = dataset_contig.ref
    dataset_contig.attrs["anattr"] = 1

    link_group = h5f.create_group("link/child")
    link_group.attrs["reference_contig"] = dataset_contig.ref
    link_group.attrs["reference_chunked"] = dataset_chunked.ref
    h5f.flush()
    h5f.close()

    source_size = source.stat().st_size

    # do it without providing target to check that we make filename correctly
    n = 10
    target_output = truncate_file(source, n=n)
    assert target_output == source.parent / (source.stem + "_truncated.hdf5")
    # check that we actually made it smaller
    target_size = target_output.stat().st_size
    # empirically, the source dataset is ~125KB and truncated is ~17KB
    assert target_size < source_size / 5

    # then check that we have what's expected in the file
    target_h5f = h5py.File(target_output, "r")

    # truncation happened
    assert target_h5f["data"]["dataset_contig"].shape == (n, 30, 40)
    assert target_h5f["data"]["dataset_chunked"].shape == (n, 40, 50)
    # references still work
    # can't directly assess object identity equality with "is"
    # so this tests if the referenced dereference and that they dereference to the right place
    assert (
        target_h5f[target_h5f["data"]["dataset_contig"].attrs["reference_other"]].name
        == target_h5f["data"]["dataset_chunked"].name
    )
    assert (
        target_h5f[target_h5f["data"]["dataset_chunked"].attrs["reference_other"]].name
        == target_h5f["data"]["dataset_contig"].name
    )
    assert (
        target_h5f[target_h5f["link"]["child"].attrs["reference_contig"]].name
        == target_h5f["data"]["dataset_contig"].name
    )
    assert (
        target_h5f[target_h5f["link"]["child"].attrs["reference_chunked"]].name
        == target_h5f["data"]["dataset_chunked"].name
    )
    assert target_h5f["data"]["dataset_contig"].attrs["anattr"] == 1


def test_dependencies_hardlink(nwb_file):
    """
    Test that hardlinks are resolved (eg. from /processing/ecephys/LFP/ElectricalSeries/electrodes
    to /acquisition/ElectricalSeries/electrodes
    Args:
        nwb_file:

    Returns:

    """
    parent = "/processing/ecephys/LFP/ElectricalSeries"
    source = "/processing/ecephys/LFP/ElectricalSeries/electrodes"
    target = "/acquisition/ElectricalSeries/electrodes"

    # assert that the hardlink exists in the test file
    with h5py.File(str(nwb_file), "r") as h5f:
        node = h5f.get(source)
        linked_node = resolve_hardlink(node)
        assert linked_node == target

    graph = hdf_dependency_graph(nwb_file)
    # the parent should link to the target as a child
    assert (parent, target) in graph.edges([parent])
    assert graph.edges[parent, target]["label"] == "child"


@pytest.mark.dev
def test_dependency_graph_images(nwb_file, tmp_output_dir):
    """
    Generate images of the dependency graph
    """
    graph = hdf_dependency_graph(nwb_file)
    A_unfiltered = nx.nx_agraph.to_agraph(graph)
    A_unfiltered.draw(tmp_output_dir / "test_nwb_unfiltered.png", prog="dot")
    graph = filter_dependency_graph(graph)
    A_filtered = nx.nx_agraph.to_agraph(graph)
    A_filtered.draw(tmp_output_dir / "test_nwb_filtered.png", prog="dot")


@pytest.mark.parametrize(
    "dset",
    [
        {"name": "aibs.nwb", "source": "sub-738651046_ses-760693773.nwb"},
        {
            "name": "aibs_ecephys.nwb",
            "source": "sub-738651046_ses-760693773_probe-769322820_ecephys.nwb",
        },
    ],
)
@pytest.mark.dev
def test_make_truncated_datasets(tmp_output_dir, data_dir, dset):
    input_file = tmp_output_dir / dset["source"]
    output_file = data_dir / dset["name"]
    if not input_file.exists():
        return

    truncate_file(input_file, output_file, 10)
