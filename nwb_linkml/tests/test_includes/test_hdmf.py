import numpy as np
import pandas as pd

# FIXME: Make this just be the output of the provider by patching into import machinery
from nwb_linkml.models.pydantic.core.v2_7_0.namespace import (
    DynamicTable,
    DynamicTableRegion,
    ElectrodeGroup,
    VectorIndex,
    VoltageClampStimulusSeries,
)

from .conftest import _ragged_array


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


def test_dynamictable_ragged(units):
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


def test_dynamictable_region_basic(electrical_series):
    """
    DynamicTableRegion should be able to refer to a row or rows of another table
    itself as a column within a table
    """
    series, electrodes = electrical_series
    row = series.electrodes[0]
    # check that we correctly got the 4th row instead of the 0th row,
    # since the indexed table was constructed with inverted indexes because it's a test, ya dummy.
    # we will only vaguely check the basic functionality here bc
    # a) the indexing behavior of the indexed objects is tested above, and
    # b) every other object in the chain is strictly validated,
    # so we assume if we got a right shaped df that it is the correct one.
    # feel free to @ me when i am wrong about this
    assert all(row.id == 4)
    assert row.shape == (1, 7)
    # and we should still be preserving the model that is the contents of the cell of this row
    # so this is a dataframe row with a column "group" that contains an array of ElectrodeGroup
    # objects and that's as far as we are going to chase the recursion in this basic indexing test
    # ElectrodeGroup is strictly validating so an instance check is all we need.
    assert isinstance(row.group.values[0], ElectrodeGroup)

    # getting a list of table rows is actually correct behavior here because
    # this list of table rows is actually the cell of another table
    rows = series.electrodes[0:3]
    assert all([all(row.id == idx) for row, idx in zip(rows, [4, 3, 2])])


def test_dynamictable_region_ragged():
    """
    Dynamictables can also have indexes so that they are ragged arrays of column rows
    """
    spike_times, spike_idx = _ragged_array(24)
    spike_times_flat = np.concatenate(spike_times)

    # construct a secondary index that selects overlapping segments of the first table
    value = np.array([0, 1, 2, 1, 2, 3, 2, 3, 4])
    idx = np.array([3, 6, 9])

    table = DynamicTable(
        name="table",
        description="a table what else would it be",
        id=np.arange(len(spike_idx)),
        timeseries=spike_times_flat,
        timeseries_index=spike_idx,
    )
    region = DynamicTableRegion(
        name="dynamictableregion",
        description="this field should be optional",
        table=table,
        value=value,
    )
    index = VectorIndex(name="index", description="hgggggggjjjj", target=region, value=idx)
    region._index = index
    rows = region[1]
    # i guess this is right?
    # the region should be a set of three rows of the table, with a ragged array column timeseries
    # like...
    #
    #    id                                         timeseries
    # 0   1  [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, ...
    # 1   2  [2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, ...
    # 2   3  [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, ...
    assert rows.shape == (3, 2)
    assert all(rows.id == [1, 2, 3])
    assert all([all(row[1].timeseries == i) for i, row in zip([1, 2, 3], rows.iterrows())])


def test_dynamictable_append_column():
    pass


def test_dynamictable_append_row():
    pass


def test_dynamictable_extra_coercion():
    """
    Extra fields should be coerced to VectorData and have their
    indexing relationships handled when passed as plain arrays.
    """


def test_aligned_dynamictable(intracellular_recordings_table):
    """
    Multiple aligned dynamictables should be indexable with a multiindex
    """
    # can get a single row.. (check correctness below)
    row = intracellular_recordings_table[0]
    # can get a single table with its name
    stimuli = intracellular_recordings_table["stimuli"]
    assert stimuli.shape == (10, 1)

    # nab a few rows to make the dataframe
    rows = intracellular_recordings_table[0:3]
    assert all(
        rows.columns
        == pd.MultiIndex.from_tuples(
            [
                ("electrodes", "index"),
                ("electrodes", "electrode"),
                ("stimuli", "index"),
                ("stimuli", "stimulus"),
                ("responses", "index"),
                ("responses", "response"),
            ]
        )
    )

    # ensure that we get the actual values from the TimeSeriesReferenceVectorData
    # also tested separately
    # each individual cell should be an array of VoltageClampStimulusSeries...
    # and then we should be able to index within that as well
    stims = rows["stimuli", "stimulus"][0]
    for i in range(len(stims)):
        assert isinstance(stims[i], VoltageClampStimulusSeries)
        assert all([i == val for val in stims[i][:]])
