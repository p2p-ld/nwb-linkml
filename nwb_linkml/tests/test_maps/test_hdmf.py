
import time

import h5py
import pytest

from nwb_linkml.maps.hdmf import dynamictable_to_model, model_from_dynamictable

NWBFILE = "/Users/jonny/Dropbox/lab/p2p_ld/data/nwb/sub-738651046_ses-760693773.nwb"


@pytest.mark.parametrize("dataset", ["aibs.nwb"])
def test_make_dynamictable(data_dir, dataset):
    nwbfile = data_dir / dataset
    h5f = h5py.File(nwbfile, "r")
    group = h5f["units"]

    start_time = time.time()
    model = model_from_dynamictable(group)
    data = dynamictable_to_model(group, model)

    _ = data.model_dump_json()
    end_time = time.time()
    total_time = end_time - start_time
