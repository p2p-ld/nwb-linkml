"""
Placeholder test module to test reading from pynwb-generated NWB file
"""

from nwb_linkml.io.hdf5 import HDF5IO


def test_read_from_nwbfile(nwb_file):
    """
    Read data from a pynwb HDF5 NWB file
    """
    res = HDF5IO(nwb_file).read()


def test_read_from_yaml(nwb_file):
    """
    Read data from a yaml-fied NWB file
    """
    pass
