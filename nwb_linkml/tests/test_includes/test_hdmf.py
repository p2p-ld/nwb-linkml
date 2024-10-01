from typing import Optional, Type

import numpy as np
import pandas as pd
import pytest
from numpydantic import NDArray, Shape
from pydantic import ValidationError

from nwb_linkml.includes import hdmf
from nwb_linkml.includes.hdmf import (
    AlignedDynamicTableMixin,
    DynamicTableMixin,
    VectorDataMixin,
    VectorIndexMixin,
)

# FIXME: Make this just be the output of the provider by patching into import machinery
from nwb_models.models.pydantic.core.v2_7_0.namespace import (
    ElectrodeGroup,
)

from .conftest import _ragged_array

# --------------------------------------------------
# Unit tests on mixins directly (model tests below)
# --------------------------------------------------


@pytest.fixture()
def basic_table() -> tuple[DynamicTableMixin, dict[str, NDArray[Shape["10"], int]]]:
    class MyData(DynamicTableMixin):
        col_1: hdmf.VectorData[NDArray[Shape["*"], int]]
        col_2: hdmf.VectorData[NDArray[Shape["*"], int]]
        col_3: hdmf.VectorData[NDArray[Shape["*"], int]]

    cols = {
        "col_1": np.arange(10),
        "col_2": np.arange(10),
        "col_3": np.arange(10),
        "col_4": np.arange(10),
        "col_5": np.arange(10),
    }
    return MyData, cols


@pytest.fixture()
def aligned_table() -> tuple[Type[AlignedDynamicTableMixin], dict[str, DynamicTableMixin]]:
    class Table1(DynamicTableMixin):
        col1: hdmf.VectorData[NDArray[Shape["*"], int]]
        col2: hdmf.VectorData[NDArray[Shape["*"], int]]

    class Table2(DynamicTableMixin):
        col3: hdmf.VectorData[NDArray[Shape["*"], int]]
        col4: hdmf.VectorData[NDArray[Shape["*"], int]]

    class Table3(DynamicTableMixin):
        col5: hdmf.VectorData[NDArray[Shape["*"], int]]
        col6: hdmf.VectorData[NDArray[Shape["*"], int]]

    array = np.arange(10)

    table1 = Table1(col1=array, col2=array)
    table2 = Table2(col3=array, col4=array)
    table3 = Table3(col5=array, col6=array)

    class AlignedTable(AlignedDynamicTableMixin):
        table1: Table1
        table2: Table2

    return AlignedTable, {"table1": table1, "table2": table2, "table3": table3}


def test_dynamictable_mixin_indexing(basic_table):
    """
    Can index values from a dynamictable
    """
    MyData, cols = basic_table

    colnames = [c for c in cols]
    inst = MyData(**cols)
    assert len(inst) == 10

    row = inst[0]
    # successfully get a single row :)
    assert row.shape == (1, 5)
    assert row.columns.tolist() == colnames

    # slice a range of rows
    rows = inst[0:3]
    assert rows.shape == (3, 5)

    # get a single column
    col = inst["col_1"]
    assert all(col.value == np.arange(10))

    # get a single cell
    val = inst[5, "col_2"]
    assert val == 5
    val = inst[5, 1]
    assert val == 5

    # get a slice of rows and columns
    val = inst[0:3, 0:3]
    assert val.shape == (3, 3)
    assert val.columns.tolist() == colnames[0:3]

    # slice of rows with string colname
    val = inst[0:2, "col_1"]
    assert val.shape == (2, 1)
    assert val.columns.tolist() == ["col_1"]

    # array of rows
    # crazy slow but we'll work on perf later
    val = inst[np.arange(2), "col_1"]
    assert val.shape == (2, 1)
    assert val.columns.tolist() == ["col_1"]

    # should raise an error on a 3d index
    with pytest.raises(ValueError, match=".*2-dimensional.*"):
        _ = inst[1, 1, 1]

    # error on unhandled indexing type
    with pytest.raises(ValueError, match="Unsure how to get item with key.*"):
        _ = inst[5.5]


def test_dynamictable_mixin_colnames():
    """
    Should correctly infer colnames
    """

    class MyDT(DynamicTableMixin):
        existing_col: NDArray[Shape["* col"], int]

    new_col_1 = VectorDataMixin(value=np.arange(10))
    new_col_2 = VectorDataMixin(value=np.arange(10))

    inst = MyDT(existing_col=np.arange(10), new_col_1=new_col_1, new_col_2=new_col_2)
    assert inst.colnames == ["existing_col", "new_col_1", "new_col_2"]


def test_dynamictable_mixin_colnames_index():
    """
    Exclude index columns in colnames
    """

    class MyDT(DynamicTableMixin):
        existing_col: NDArray[Shape["* col"], int]

    cols = {
        "existing_col": np.arange(10),
        "new_col_1": hdmf.VectorData(name="new_col_1", description="", value=np.arange(10)),
        "new_col_2": hdmf.VectorData(name="new_col_2", description="", value=np.arange(10)),
    }
    # explicit index with mismatching name
    cols["weirdname_index"] = VectorIndexMixin(value=np.arange(10), target=cols["new_col_1"])
    # implicit index with matching name
    cols["new_col_2_index"] = VectorIndexMixin(value=np.arange(10))

    inst = MyDT(**cols)
    assert inst.colnames == ["existing_col", "new_col_1", "new_col_2"]


def test_dynamictable_mixin_colnames_ordered():
    """
    Should be able to pass explicit order to colnames
    """

    class MyDT(DynamicTableMixin):
        existing_col: NDArray[Shape["* col"], int]

    cols = {
        "existing_col": np.arange(10),
        "new_col_1": hdmf.VectorData(name="new_col_1", description="", value=np.arange(10)),
        "new_col_2": hdmf.VectorData(name="new_col_2", description="", value=np.arange(10)),
        "new_col_3": hdmf.VectorData(name="new_col_2", description="", value=np.arange(10)),
    }
    order = ["new_col_2", "existing_col", "new_col_1", "new_col_3"]

    inst = MyDT(**cols, colnames=order)
    assert inst.colnames == order

    # this should get reflected in the columns selector and the df produces
    assert all([key1 == key2 for key1, key2 in zip(order, inst._columns)])
    assert all(inst[0].columns == order)

    # partial lists should append unnamed columns at the end
    partial_order = ["new_col_3", "new_col_2"]
    inst = MyDT(**cols, colnames=partial_order)
    assert inst.colnames == [*partial_order, "existing_col", "new_col_1"]


def test_dynamictable_mixin_getattr():
    """
    Dynamictable should forward unknown getattr requests to the df
    """

    class MyDT(DynamicTableMixin):
        existing_col: hdmf.VectorData[NDArray[Shape["* col"], int]]

    col = hdmf.VectorData(name="existing_col", description="", value=np.arange(10))
    inst = MyDT(existing_col=col)

    # regular lookup for attrs that exist
    assert isinstance(inst.existing_col, hdmf.VectorData)
    assert all(inst.existing_col.value == col.value)

    # df lookup for those that don't
    assert isinstance(inst.columns, pd.Index)

    with pytest.raises(AttributeError):
        _ = inst.really_fake_name_that_pandas_and_pydantic_definitely_dont_define


def test_dynamictable_coercion():
    """
    Dynamictable should coerce arrays into vectordata objects for known and unknown cols
    """

    class MyDT(DynamicTableMixin):
        existing_col: hdmf.VectorData[NDArray[Shape["* col"], int]]
        optional_col: Optional[hdmf.VectorData[NDArray[Shape["* col"], int]]]

    cols = {
        "existing_col": np.arange(10),
        "optional_col": np.arange(10),
        "new_col_1": np.arange(10),
    }
    inst = MyDT(**cols)
    assert isinstance(inst.existing_col, hdmf.VectorData)
    assert isinstance(inst.optional_col, hdmf.VectorData)
    assert isinstance(inst.new_col_1, hdmf.VectorData)
    assert all(inst.existing_col.value == np.arange(10))
    assert all(inst.optional_col.value == np.arange(10))
    assert all(inst.new_col_1.value == np.arange(10))


def test_dynamictable_create_id():
    class MyDT(DynamicTableMixin):
        existing_col: hdmf.VectorData[NDArray[Shape["* col"], int]]

    cols = {
        "existing_col": np.arange(10),
    }
    inst = MyDT(**cols)

    assert all(inst.id == np.arange(10))


def test_dynamictable_resolve_index():
    """
    Dynamictable should resolve and connect data to indices, explicit and implicit
    """

    class MyDT(DynamicTableMixin):
        existing_col: hdmf.VectorData[NDArray[Shape["* col"], int]]

    cols = {
        "existing_col": np.arange(10),
        "new_col_1": hdmf.VectorData(name="new_col_1", description="", value=np.arange(10)),
        "new_col_2": hdmf.VectorData(name="new_col_2", description="", value=np.arange(10)),
    }
    # explicit index with mismatching name
    cols["weirdname_index"] = hdmf.VectorIndex(
        name="weirdname_index", description="", value=np.arange(10), target=cols["new_col_1"]
    )
    # implicit index with matching name
    cols["new_col_2_index"] = hdmf.VectorIndex(
        name="new_col_2_index", description="", value=np.arange(10)
    )

    inst = MyDT(**cols)
    assert inst.weirdname_index.target is inst.new_col_1
    assert inst.new_col_2_index.target is inst.new_col_2
    assert inst.new_col_1._index is inst.weirdname_index
    assert inst.new_col_2._index is inst.new_col_2_index


def test_dynamictable_assert_equal_length():
    """
    Dynamictable validates that columns are of equal length
    """

    class MyDT(DynamicTableMixin):
        existing_col: NDArray[Shape["* col"], int]

    cols = {
        "existing_col": np.arange(10),
        "new_col_1": hdmf.VectorData(name="new_col_1", description="", value=np.arange(11)),
    }
    with pytest.raises(ValidationError, match="columns are not of equal length"):
        _ = MyDT(**cols)

    cols = {
        "existing_col": np.arange(11),
        "new_col_1": hdmf.VectorData(name="new_col_1", description="", value=np.arange(10)),
    }
    with pytest.raises(ValidationError, match="columns are not of equal length"):
        _ = MyDT(**cols)

    # wrong lengths are fine as long as the index is good
    cols = {
        "existing_col": np.arange(10),
        "new_col_1": hdmf.VectorData(name="new_col_1", description="", value=np.arange(100)),
        "new_col_1_index": hdmf.VectorIndex(
            name="new_col_1_index", description="", value=np.arange(0, 100, 10) + 10
        ),
    }
    _ = MyDT(**cols)

    # but not fine if the index is not good
    cols = {
        "existing_col": np.arange(10),
        "new_col_1": hdmf.VectorData(name="new_col_1", description="", value=np.arange(100)),
        "new_col_1_index": hdmf.VectorIndex(
            name="new_col_1_index", description="", value=np.arange(0, 100, 5) + 5
        ),
    }
    with pytest.raises(ValidationError, match="columns are not of equal length"):
        _ = MyDT(**cols)


def test_dynamictable_setattr():
    """
    Setting a new column as an attribute adds it to colnames and reruns validations
    """

    class MyDT(DynamicTableMixin):
        existing_col: hdmf.VectorData[NDArray[Shape["* col"], int]]

    cols = {
        "existing_col": hdmf.VectorData(name="existing_col", description="", value=np.arange(10)),
        "new_col_1": hdmf.VectorData(name="new_col_1", description="", value=np.arange(10)),
    }
    inst = MyDT(existing_col=cols["existing_col"])
    assert inst.colnames == ["existing_col"]

    inst.new_col_1 = cols["new_col_1"]
    assert inst.colnames == ["existing_col", "new_col_1"]
    assert inst[:].columns.tolist() == ["existing_col", "new_col_1"]
    # length unchanged because id should be the same
    assert len(inst) == 10

    # model validators should be called to ensure equal length
    with pytest.raises(ValidationError):
        inst.new_col_2 = hdmf.VectorData(name="new_col_2", description="", value=np.arange(11))


def test_vectordata_indexing():
    """
    Vectordata/VectorIndex pairs should know how to index off each other
    """
    n_rows = 50
    value_array, index_array = _ragged_array(n_rows)
    value_array = np.concatenate(value_array)

    data = hdmf.VectorData(name="data", description="", value=value_array)

    # before we have an index, things should work as normal, indexing a 1D array
    assert data[0] == 0
    # and setting values
    data[0] = 1
    assert data[0] == 1
    data[0] = 0

    # indexes by themselves are the same
    index_notarget = hdmf.VectorIndex(name="no_target_index", description="", value=index_array)
    assert index_notarget[0] == index_array[0]
    assert all(index_notarget[0:3] == index_array[0:3])
    oldval = index_array[0]
    index_notarget[0] = 5
    assert index_notarget[0] == 5
    index_notarget[0] = oldval

    index = hdmf.VectorIndex(name="data_index", description="", value=index_array, target=data)
    data._index = index

    # after an index, both objects should index raggedly
    for i in range(len(index)):
        assert all(data[i] == i)
        assert all(index[i] == i)

    for item in (data, index):
        section = item[0:3]
        for i, subitem in enumerate(section):
            assert all(subitem == i)

    # setting uses the same indexing logic
    data[0] = 5
    assert all(data[0] == 5)
    data[0:3] = [5, 4, 3]
    assert all(data[0] == 5)
    assert all(data[1] == 4)
    assert all(data[2] == 3)
    data[0:3] = 6
    assert all(data[0] == 6)
    assert all(data[1] == 6)
    assert all(data[2] == 6)
    with pytest.raises(ValueError, match=".*equal-length.*"):
        data[0:3] = [5, 4]


def test_vectordata_getattr():
    """
    VectorData and VectorIndex both forward getattr to ``value``
    """
    data = hdmf.VectorData(name="data", description="", value=np.arange(100))
    index = hdmf.VectorIndex(
        name="data_index", description="", value=np.arange(10, 101, 10), target=data
    )

    # get attrs that we defined on the models
    # i.e. no attribute errors here
    _ = data.model_fields
    _ = index.model_fields

    # but for things that aren't defined, get the numpy method
    # note that index should not try and get the sum from the target -
    # that would be hella confusing. we only refer to the target when indexing.
    assert data.sum() == np.sum(np.arange(100))
    assert index.sum() == np.sum(np.arange(10, 101, 10))

    # and also raise attribute errors when nothing is found
    with pytest.raises(AttributeError):
        _ = data.super_fake_attr_name
    with pytest.raises(AttributeError):
        _ = index.super_fake_attr_name


def test_vectordata_generic_numpydantic_validation():
    """
    Using VectorData as a generic with a numpydantic array annotation should still validate

    Simple test here because numpydantic validation is tested in numpydantic itself,
    we just want to check that the annotations work as validation and it doesn't just
    """

    class MyDT(DynamicTableMixin):
        existing_col: NDArray[Shape["3 col"], int]

    with pytest.raises(ValidationError):
        _ = MyDT(existing_col=np.zeros((4, 5, 6), dtype=int))


@pytest.mark.xfail
def test_dynamictable_append_row():
    raise NotImplementedError("Reminder to implement row appending")


def test_dynamictable_region_indexing(basic_table):
    """
    Without an index, DynamicTableRegion should just be a single-row index into
    another table
    """
    model, cols = basic_table
    inst = model(**cols)

    index = np.array([9, 4, 8, 3, 7, 2, 6, 1, 5, 0])

    table_region = hdmf.DynamicTableRegion(
        name="table_region", description="", value=index, table=inst
    )

    row = table_region[1]
    assert all(row.iloc[0] == index[1])

    # slices
    rows = table_region[3:5]
    assert all(rows[0].iloc[0] == index[3])
    assert all(rows[1].iloc[0] == index[4])
    assert len(rows) == 2
    assert all([row.shape == (1, 5) for row in rows])

    # out of order fine too
    oorder = [2, 5, 4]
    rows = table_region[oorder]
    assert len(rows) == 3
    assert all([row.shape == (1, 5) for row in rows])
    for i, idx in enumerate(oorder):
        assert all(rows[i].iloc[0] == index[idx])

    # also works when used as a column in a table
    class AnotherTable(DynamicTableMixin):
        region: hdmf.DynamicTableRegion
        another_col: hdmf.VectorData[NDArray[Shape["*"], int]]

    inst2 = AnotherTable(region=table_region, another_col=np.arange(10))
    rows = inst2[0:3]
    col = rows.region
    for i in range(3):
        assert all(col[i].iloc[0] == index[i])


def test_dynamictable_region_ragged():
    """
    Dynamictables can also have indexes so that they are ragged arrays of column rows
    """
    spike_times, spike_idx = _ragged_array(24)
    spike_times_flat = np.concatenate(spike_times)

    # construct a secondary index that selects overlapping segments of the first table
    value = np.array([0, 1, 2, 1, 2, 3, 2, 3, 4])
    idx = np.array([3, 6, 9])

    table = DynamicTableMixin(
        name="table",
        description="a table what else would it be",
        id=np.arange(len(spike_idx)),
        another_column=np.arange(len(spike_idx) - 1, -1, -1),
        timeseries=spike_times_flat,
        timeseries_index=spike_idx,
    )
    region = hdmf.DynamicTableRegion(
        name="region",
        description="a table region what else would it be",
        table=table,
        value=value,
    )
    index = hdmf.VectorIndex(
        name="region_index", description="hgggggggjjjj", target=region, value=idx
    )
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
    assert all(rows.index.to_numpy() == [1, 2, 3])
    assert all([all(row[1].timeseries == i) for i, row in zip([1, 2, 3], rows.iterrows())])

    rows = region[0:2]
    for i in range(2):
        assert all(
            [all(row[1].timeseries == i) for i, row in zip(range(i, i + 3), rows[i].iterrows())]
        )

    # also works when used as a column in a table
    class AnotherTable(DynamicTableMixin):
        region: hdmf.DynamicTableRegion
        yet_another_col: hdmf.VectorData[NDArray[Shape["*"], int]]

    inst2 = AnotherTable(region=region, yet_another_col=np.arange(len(idx)))
    row = inst2[0]
    assert row.shape == (1, 2)
    assert row.iloc[0, 0].equals(region[0])

    rows = inst2[0:3]
    for i, df in enumerate(rows.iloc[:, 0]):
        assert df.equals(region[i])


def test_aligned_dynamictable_indexing(aligned_table):
    """
    Should be able to index aligned dynamic tables to yield a multi-index df
    """
    AlignedTable, tables = aligned_table
    atable = AlignedTable(**tables)

    row = atable[0]
    assert all(
        row.columns
        == pd.MultiIndex.from_tuples(
            [
                ("table1", "id"),
                ("table1", "col1"),
                ("table1", "col2"),
                ("table2", "id"),
                ("table2", "col3"),
                ("table2", "col4"),
                ("table3", "id"),
                ("table3", "col5"),
                ("table3", "col6"),
            ]
        )
    )
    for i in range(len(atable)):
        vals = atable[i]
        assert vals.shape == (1, 9)
        assert all(vals == i)

    # mildly different, indexing with a slice.
    rows = atable[0:3]
    for i, row in enumerate(rows.iterrows()):
        vals = row[1]
        assert len(vals) == 9
        assert all(vals == i)

    # index just a single table
    row = atable[0:3, "table3"]
    assert all(row.columns.to_numpy() == ["col5", "col6"])
    assert row.shape == (3, 2)

    # index out of order
    rows = atable[np.array([0, 2, 1])]
    assert all(rows.iloc[:, 0] == [0, 2, 1])


def test_mixed_aligned_dynamictable(aligned_table):
    """
    Aligned dynamictable should also accept vectordata/vector index pairs
    """

    AlignedTable, cols = aligned_table
    value_array, index_array = _ragged_array(10)
    value_array = np.concatenate(value_array)

    data = hdmf.VectorData(name="data", description="", value=value_array)
    index = hdmf.VectorIndex(name="data_index", description="", value=index_array)

    atable = AlignedTable(**cols, extra_col=data, extra_col_index=index)
    atable[0]
    assert atable[0].columns[-1] == ("extra_col", "extra_col")

    for i, row in enumerate(atable[:].extra_col.iterrows()):
        array = row[1].iloc[0]
        assert all(array == i)
        if i > 0:
            assert len(array) == index_array[i] - index_array[i - 1]
        else:
            assert len(array) == index_array[i]


def test_timeseriesreferencevectordata_index():
    """
    TimeSeriesReferenceVectorData should be able to do the thing it does
    """
    generator = np.random.default_rng()
    timeseries = np.array([np.arange(100)] * 10)

    counts = generator.integers(1, 10, (10,))
    idx_start = np.arange(0, 100, 10)

    response = hdmf.TimeSeriesReferenceVectorData(
        idx_start=idx_start,
        count=counts,
        timeseries=timeseries,
    )
    for i in range(len(counts)):
        assert len(response[i]) == counts[i]
    items = response[3:5]
    assert all(items[0] == timeseries[3][idx_start[3] : idx_start[3] + counts[3]])
    assert all(items[1] == timeseries[4][idx_start[4] : idx_start[4] + counts[4]])

    response[0] = np.zeros((counts[0],))
    assert all(response[0] == 0)

    response[1:3] = [np.zeros((counts[1],)), np.ones((counts[2],))]
    assert all(response[1] == 0)
    assert all(response[2] == 1)


# --------------------------------------------------
# Model-based tests
# --------------------------------------------------


def test_dynamictable_indexing_electricalseries(electrical_series):
    """
    Can index values from a dynamictable
    """
    series, electrodes = electrical_series

    colnames = [
        "x",
        "y",
        "group",
        "group_name",
        "location",
        "extra_column",
    ]
    dtypes = [
        np.dtype("float64"),
        np.dtype("float64"),
    ] + ([np.dtype("O")] * 4)

    row = electrodes[0]
    # successfully get a single row :)
    assert row.shape == (1, 6)
    assert row.dtypes.values.tolist() == dtypes
    assert row.columns.tolist() == colnames

    # slice a range of rows
    rows = electrodes[0:3]
    assert rows.shape == (3, 6)
    assert rows.dtypes.values.tolist() == dtypes
    assert rows.columns.tolist() == colnames

    # get a single column
    col = electrodes["y"]
    assert all(col.value == [5, 6, 7, 8, 9])

    # get a single cell
    val = electrodes[0, "y"]
    assert val == 5
    val = electrodes[0, 1]
    assert val == 5

    # get a slice of rows and columns
    subsection = electrodes[0:3, 0:3]
    assert subsection.shape == (3, 3)
    assert subsection.columns.tolist() == colnames[0:3]
    assert subsection.dtypes.values.tolist() == dtypes[0:3]


def test_dynamictable_ragged_units(units):
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


def test_dynamictable_region_basic_electricalseries(electrical_series):
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
    assert all(row.index == 4)
    assert row.shape == (1, 6)
    # and we should still be preserving the model that is the contents of the cell of this row
    # so this is a dataframe row with a column "group" that contains an array of ElectrodeGroup
    # objects and that's as far as we are going to chase the recursion in this basic indexing test
    # ElectrodeGroup is strictly validating so an instance check is all we need.
    assert isinstance(row.group.values[0], ElectrodeGroup)

    # getting a list of table rows is actually correct behavior here because
    # this list of table rows is actually the cell of another table
    rows = series.electrodes[0:3]
    assert all([all(row.index == idx) for row, idx in zip(rows, [4, 3, 2])])


def test_aligned_dynamictable_ictable(intracellular_recordings_table):
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
                ("electrodes", "id"),
                ("electrodes", "electrode"),
                ("stimuli", "id"),
                ("stimuli", "stimulus"),
                ("responses", "id"),
                ("responses", "response"),
            ]
        )
    )

    # ensure that we get the actual values from the TimeSeriesReferenceVectorData
    # also tested separately
    # each individual cell should be an array of VoltageClampStimulusSeries...
    # and then we should be able to index within that as well
    stims = rows["stimuli", "stimulus"]
    for i in range(len(stims)):
        assert all(np.array(stims[i]) == i)
