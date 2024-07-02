import pdb
import h5py

import pytest
from pathlib import Path
import numpy as np

from ..fixtures import tmp_output_dir, data_dir

from nwb_linkml.io.hdf5 import HDF5IO
from nwb_linkml.io.hdf5 import truncate_file


@pytest.mark.xfail()
@pytest.mark.parametrize("dset", ["aibs.nwb", "aibs_ecephys.nwb"])
def test_hdf_read(data_dir, dset):
    NWBFILE = data_dir / dset
    io = HDF5IO(path=NWBFILE)
    # the test for now is just whether we can read it lol
    model = io.read()


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


@pytest.mark.skip()
def test_flatten_hdf():
    from nwb_linkml.io.hdf5 import HDF5IO
    from nwb_linkml.maps.hdf5 import flatten_hdf

    path = "/Users/jonny/Dropbox/lab/p2p_ld/data/nwb/sub-738651046_ses-760693773.nwb"
    import h5py

    h5f = h5py.File(path)
    flat = flatten_hdf(h5f)
    assert not any(["specifications" in v.path for v in flat.values()])
    pdb.set_trace()
    raise NotImplementedError("Just a stub for local testing for now, finish me!")
