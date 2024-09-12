"""
Placeholder test module to test reading from pynwb-generated NWB file
"""

from datetime import datetime

import numpy as np
import pandas as pd
import pytest
from numpydantic.interface.hdf5 import H5Proxy
from pydantic import BaseModel
from pynwb import NWBHDF5IO
from pynwb import NWBFile as PyNWBFile

from nwb_linkml.io.hdf5 import HDF5IO
from nwb_models.models import NWBFile


def test_read_from_nwbfile(nwb_file):
    """
    Read data from a pynwb HDF5 NWB file

    Placeholder that just ensures that reads work and all pydantic models validate,
    testing of correctness of read will happen elsewhere.
    """
    res = HDF5IO(nwb_file).read()


@pytest.fixture(scope="module")
def read_nwbfile(nwb_file) -> NWBFile:
    res = HDF5IO(nwb_file).read()
    return res


@pytest.fixture(scope="module")
def read_pynwb(nwb_file) -> PyNWBFile:
    nwbf = NWBHDF5IO(nwb_file, "r")
    res = nwbf.read()
    yield res
    nwbf.close()


def _compare_attrs(model: BaseModel, pymodel: object):
    for field, value in model.model_dump().items():
        if isinstance(value, (dict, H5Proxy)):
            continue
        if hasattr(pymodel, field):
            pynwb_val = getattr(pymodel, field)
            if isinstance(pynwb_val, list):
                if isinstance(pynwb_val[0], datetime):
                    # need to normalize UTC numpy.datetime64 with datetime with tz
                    continue
                assert all([val == pval for val, pval in zip(value, pynwb_val)])
            else:
                if not pynwb_val:
                    # pynwb instantiates some stuff as empty dicts where we use ``None``
                    assert bool(pynwb_val) == bool(value)
                else:
                    assert value == pynwb_val


def test_nwbfile_base(read_nwbfile, read_pynwb):
    """
    Base attributes on top-level nwbfile are correct
    """
    _compare_attrs(read_nwbfile, read_pynwb)


def test_timeseries(read_nwbfile, read_pynwb):
    py_acq = read_pynwb.get_acquisition("test_timeseries")
    acq = read_nwbfile.acquisition["test_timeseries"]
    _compare_attrs(acq, py_acq)
    # data and timeseries should be equal
    assert np.array_equal(acq.data[:], py_acq.data[:])
    assert np.array_equal(acq.timestamps[:], py_acq.timestamps[:])


def test_position(read_nwbfile, read_pynwb):
    trials = read_nwbfile.intervals.trials[:]
    py_trials = read_pynwb.trials.to_dataframe()
    pd.testing.assert_frame_equal(py_trials, trials)

    spatial = read_nwbfile.processing["behavior"].Position.SpatialSeries
    py_spatial = read_pynwb.processing["behavior"]["Position"]["SpatialSeries"]
    _compare_attrs(spatial, py_spatial)
    assert np.array_equal(spatial[:], py_spatial.data[:])
    assert np.array_equal(spatial.timestamps[:], py_spatial.timestamps[:])


def test_ecephys(read_nwbfile, read_pynwb):
    pass


def test_units(read_nwbfile, read_pynwb):
    pass


def test_icephys(read_nwbfile, read_pynwb):
    pass


def test_ca_imaging(read_nwbfile, read_pynwb):
    pass


def test_read_from_yaml(nwb_file):
    """
    Read data from a yaml-fied NWB file
    """
    pass
