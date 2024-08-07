from typing import Tuple

import numpy as np
import pytest

# FIXME: Make this just be the output of the provider by patching into import machinery
from nwb_linkml.models.pydantic.core.v2_7_0.namespace import (
    Device,
    DynamicTableRegion,
    ElectricalSeries,
    ElectrodeGroup,
    ExtracellularEphysElectrodes,
    Units,
)


@pytest.fixture()
def electrical_series() -> Tuple["ElectricalSeries", "ExtracellularEphysElectrodes"]:
    """
    Demo electrical series with adjoining electrodes
    """
    n_electrodes = 5
    n_times = 100
    data = np.arange(0, n_electrodes * n_times).reshape(n_times, n_electrodes).astype(float)
    timestamps = np.linspace(0, 1, n_times)

    device = Device(name="my electrode")

    # electrode group is the physical description of the electrodes
    electrode_group = ElectrodeGroup(
        name="GroupA",
        device=device,
        description="an electrode group",
        location="you know where it is",
    )

    # make electrodes tables
    electrodes = ExtracellularEphysElectrodes(
        description="idk these are also electrodes",
        id=np.arange(0, n_electrodes),
        x=np.arange(0, n_electrodes).astype(float),
        y=np.arange(n_electrodes, n_electrodes * 2).astype(float),
        group=[electrode_group] * n_electrodes,
        group_name=[electrode_group.name] * n_electrodes,
        location=[str(i) for i in range(n_electrodes)],
        extra_column=["sup"] * n_electrodes,
    )

    electrical_series = ElectricalSeries(
        name="my recording!",
        electrodes=DynamicTableRegion(
            table=electrodes, value=np.arange(0, n_electrodes), name="electrodes", description="hey"
        ),
        timestamps=timestamps,
        data=data,
    )
    return electrical_series, electrodes


@pytest.fixture(params=[True, False])
def units(request) -> Tuple[Units, list[np.ndarray], np.ndarray]:
    """
    Test case for units

    Parameterized by extra_column because pandas likes to pivot dataframes
    to long when there is only one column and it's not len() == 1
    """

    n_units = 24
    generator = np.random.default_rng()
    spike_times = [
        np.full(shape=generator.integers(10, 50), fill_value=i, dtype=float) for i in range(n_units)
    ]
    spike_idx = []
    for i in range(n_units):
        if i == 0:
            spike_idx.append(len(spike_times[0]))
        else:
            spike_idx.append(len(spike_times[i]) + spike_idx[i - 1])
    spike_idx = np.array(spike_idx)

    spike_times_flat = np.concatenate(spike_times)

    kwargs = {
        "description": "units!!!!",
        "spike_times": spike_times_flat,
        "spike_times_index": spike_idx,
    }
    if request.param:
        kwargs["extra_column"] = ["hey!"] * n_units
    units = Units(**kwargs)
    return units, spike_times, spike_idx


def test_dynamictable_indexing(electrical_series):
    """
    Can index values from a dynamictable
    """
    series, electrodes = electrical_series

    colnames = [
        "id",
        "x",
        "y",
        "group",
        "group_name",
        "location",
        "extra_column",
    ]
    dtypes = [
        np.dtype("int64"),
        np.dtype("float64"),
        np.dtype("float64"),
    ] + ([np.dtype("O")] * 4)

    row = electrodes[0]
    # successfully get a single row :)
    assert row.shape == (1, 7)
    assert row.dtypes.values.tolist() == dtypes
    assert row.columns.tolist() == colnames

    # slice a range of rows
    rows = electrodes[0:3]
    assert rows.shape == (3, 7)
    assert rows.dtypes.values.tolist() == dtypes
    assert rows.columns.tolist() == colnames

    # get a single column
    col = electrodes["y"]
    assert all(col == [5, 6, 7, 8, 9])

    # get a single cell
    val = electrodes[0, "y"]
    assert val == 5
    val = electrodes[0, 2]
    assert val == 5

    # get a slice of rows and columns
    subsection = electrodes[0:3, 0:3]
    assert subsection.shape == (3, 3)
    assert subsection.columns.tolist() == colnames[0:3]
    assert subsection.dtypes.values.tolist() == dtypes[0:3]


def test_dynamictable_region(electrical_series):
    """
    Dynamictableregion should
    Args:
        electrical_series:

    Returns:

    """
    series, electrodes = electrical_series
    


def test_dynamictable_ragged_arrays(units):
    """
    Should be able to index ragged arrays using an implicit _index column

    Also tests:
    - passing arrays directly instead of wrapping in vectordata/index specifically,
      if the models in the fixture instantiate then this works
    """
    units, spike_times, spike_idx = units

    # ensure we don't pivot to long when indexing
    assert units[0].shape[0] == 1
    # check that we got the indexing boundaries corrunect
    # (and that we are forwarding attr calls to the dataframe by accessing shape
    for i in range(units.shape[0]):
        assert np.all(units.iloc[i, 0] == spike_times[i])


def test_dynamictable_append_column():
    pass


def test_dynamictable_append_row():
    pass
