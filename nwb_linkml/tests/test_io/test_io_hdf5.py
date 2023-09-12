import pytest
from pathlib import Path

from nwb_linkml.io.hdf5 import HDF5IO
@pytest.mark.skip()
def test_hdf_read():
    NWBFILE = Path('/Users/jonny/Dropbox/lab/p2p_ld/data/nwb/sub-738651046_ses-760693773.nwb')
    if not NWBFILE.exists():
        return
    io = HDF5IO(path=NWBFILE)
    model = io.read('/general')
