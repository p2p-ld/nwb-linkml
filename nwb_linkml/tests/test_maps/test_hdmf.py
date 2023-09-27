import pdb

import pytest
import h5py
import time

from nwb_linkml.maps.hdmf import model_from_dynamictable, dynamictable_to_model

NWBFILE = '/Users/jonny/Dropbox/lab/p2p_ld/data/nwb/sub-738651046_ses-760693773.nwb'

@pytest.mark.skip()
def test_make_dynamictable():
    h5f = h5py.File(NWBFILE, 'r')
    group = h5f['units']

    start_time = time.time()
    model = model_from_dynamictable(group)
    data = dynamictable_to_model(group, model)
    ser = data.model_dump_json()
    end_time = time.time()
    total_time = end_time - start_time
    pdb.set_trace()


