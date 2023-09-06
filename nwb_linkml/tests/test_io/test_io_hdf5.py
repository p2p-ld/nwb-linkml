import pytest
from pathlib import Path

from nwb_linkml.io.hdf5 import HDF5IO

def test_hdf_read():
    NWBFILE = Path('/Users/jonny/Dropbox/lab/p2p_ld/data/nwb/sub-738651046_ses-760693773.nwb')

    io = HDF5IO(path=NWBFILE)
    model = io.read('/general')
