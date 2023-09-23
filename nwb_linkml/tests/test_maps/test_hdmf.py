import pytest
import h5py

from nwb_linkml.maps.hdmf import model_from_dynamictable, dynamictable_to_df

NWBFILE = '/Users/jonny/Dropbox/lab/p2p_ld/data/nwb/sub-738651046_ses-760693773.nwb'

@pytest.mark.skip()
def test_make_dynamictable():
    h5f = h5py.File(NWBFILE, 'r')
    group = h5f['intervals']['drifting_gratings_presentations']

    model = model_from_dynamictable(group)
    data = dynamictable_to_df(group, model)


