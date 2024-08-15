from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import re
import sys
from ...hdmf_common.v1_2_1.hdmf_common_base import Data, Container
import pandas as pd
from typing import (
    Any,
    ClassVar,
    List,
    Literal,
    Dict,
    Optional,
    Union,
    Generic,
    Iterable,
    Tuple,
    TypeVar,
    overload,
)
from numpydantic import NDArray, Shape
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator,
    model_validator,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    ValidationError,
)
import numpy as np

metamodel_version = "None"
version = "1.2.1"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=False,
    )
    hdf5_path: Optional[str] = Field(
        None, description="The absolute path that this object is stored in an NWB file"
    )
    object_id: Optional[str] = Field(None, description="Unique UUID for each object")

    def __getitem__(self, val: Union[int, slice]) -> Any:
        """Try and get a value from value or "data" if we have it"""
        if hasattr(self, "value") and self.value is not None:
            return self.value[val]
        elif hasattr(self, "data") and self.data is not None:
            return self.data[val]
        else:
            raise KeyError("No value or data field to index from")


class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key: str):
        return getattr(self.root, key)

    def __getitem__(self, key: str):
        return self.root[key]

    def __setitem__(self, key: str, value):
        self.root[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.root


NUMPYDANTIC_VERSION = "1.2.1"

T = TypeVar("T", bound=NDArray)


class VectorDataMixin(BaseModel, Generic[T]):
    """
    Mixin class to give VectorData indexing abilities
    """

    _index: Optional["VectorIndex"] = None

    # redefined in `VectorData`, but included here for testing and type checking
    value: Optional[T] = None

    def __init__(self, value: Optional[NDArray] = None, **kwargs):
        if value is not None and "value" not in kwargs:
            kwargs["value"] = value
        super().__init__(**kwargs)

    def __getitem__(self, item: Union[str, int, slice, Tuple[Union[str, int, slice], ...]]) -> Any:
        if self._index:
            # Following hdmf, VectorIndex is the thing that knows how to do the slicing
            return self._index[item]
        else:
            return self.value[item]

    def __setitem__(self, key: Union[int, str, slice], value: Any) -> None:
        if self._index:
            # Following hdmf, VectorIndex is the thing that knows how to do the slicing
            self._index[key] = value
        else:
            self.value[key] = value

    def __getattr__(self, item: str) -> Any:
        """
        Forward getattr to ``value``
        """
        try:
            return BaseModel.__getattr__(self, item)
        except AttributeError as e:
            try:
                return getattr(self.value, item)
            except AttributeError:
                raise e from None

    def __len__(self) -> int:
        """
        Use index as length, if present
        """
        if self._index:
            return len(self._index)
        else:
            return len(self.value)


class VectorIndexMixin(BaseModel, Generic[T]):
    """
    Mixin class to give VectorIndex indexing abilities
    """

    # redefined in `VectorData`, but included here for testing and type checking
    value: Optional[T] = None
    target: Optional["VectorData"] = None

    def __init__(self, value: Optional[NDArray] = None, **kwargs):
        if value is not None and "value" not in kwargs:
            kwargs["value"] = value
        super().__init__(**kwargs)

    def _slice(self, arg: int) -> slice:
        """
        Mimicking :func:`hdmf.common.table.VectorIndex.__getitem_helper`
        """
        start = 0 if arg == 0 else self.value[arg - 1]
        end = self.value[arg]
        return slice(start, end)

    def __getitem__(self, item: Union[int, slice, Iterable]) -> Any:
        if self.target is None:
            return self.value[item]
        else:
            if isinstance(item, (int, np.integer)):
                return self.target.value[self._slice(item)]
            elif isinstance(item, (slice, Iterable)):
                if isinstance(item, slice):
                    item = range(*item.indices(len(self.value)))
                return [self.target.value[self._slice(i)] for i in item]
            else:  # pragma: no cover
                raise AttributeError(f"Could not index with {item}")

    def __setitem__(self, key: Union[int, slice], value: Any) -> None:
        """
        Set a value on the :attr:`.target` .

        .. note::

            Even though we correct the indexing logic from HDMF where the
            _data_ is the thing that is provided by the API when one accesses
            table.data (rather than table.data_index as hdmf does),
            we will set to the target here (rather than to the index)
            to be consistent. To modify the index, modify `self.value` directly

        """
        if self.target:
            if isinstance(key, (int, np.integer)):
                self.target.value[self._slice(key)] = value
            elif isinstance(key, (slice, Iterable)):
                if isinstance(key, slice):
                    key = range(*key.indices(len(self.value)))

                if isinstance(value, Iterable):
                    if len(key) != len(value):
                        raise ValueError(
                            "Can only assign equal-length iterable to a slice, manually index the"
                            " ragged values of of the target VectorData object if you need more"
                            " control"
                        )
                    for i, subval in zip(key, value):
                        self.target.value[self._slice(i)] = subval
                else:
                    for i in key:
                        self.target.value[self._slice(i)] = value
            else:  # pragma: no cover
                raise AttributeError(f"Could not index with {key}")

        else:
            self.value[key] = value

    def __getattr__(self, item: str) -> Any:
        """
        Forward getattr to ``value``
        """
        try:
            return BaseModel.__getattr__(self, item)
        except AttributeError as e:
            try:
                return getattr(self.value, item)
            except AttributeError:
                raise e from None

    def __len__(self) -> int:
        """
        Get length from value
        """
        return len(self.value)


class DynamicTableRegionMixin(BaseModel):
    """
    Mixin to allow indexing references to regions of dynamictables
    """

    _index: Optional["VectorIndex"] = None

    table: "DynamicTableMixin"
    value: Optional[NDArray[Shape["*"], int]] = None

    @overload
    def __getitem__(self, item: int) -> pd.DataFrame: ...

    @overload
    def __getitem__(self, item: Union[slice, Iterable]) -> List[pd.DataFrame]: ...

    def __getitem__(
        self, item: Union[int, slice, Iterable]
    ) -> Union[pd.DataFrame, List[pd.DataFrame]]:
        """
        Use ``value`` to index the table. Works analogously to ``VectorIndex`` despite
        this being a subclass of ``VectorData``
        """
        if self._index:
            if isinstance(item, (int, np.integer)):
                # index returns an array of indices,
                # and indexing table with an array returns a list of rows
                return self.table[self._index[item]]
            elif isinstance(item, slice):
                # index returns a list of arrays of indices,
                # so we index table with an array to construct
                # a list of lists of rows
                return [self.table[idx] for idx in self._index[item]]
            else:  # pragma: no cover
                raise ValueError(f"Dont know how to index with {item}, need an int or a slice")
        else:
            if isinstance(item, (int, np.integer)):
                return self.table[self.value[item]]
            elif isinstance(item, (slice, Iterable)):
                # Return a list of dataframe rows because this is most often used
                # as a column in a DynamicTable, so while it would normally be
                # ideal to just return the slice as above as a single df,
                # we need each row to be separate to fill the column
                if isinstance(item, slice):
                    item = range(*item.indices(len(self.value)))
                return [self.table[self.value[i]] for i in item]
            else:  # pragma: no cover
                raise ValueError(f"Dont know how to index with {item}, need an int or a slice")

    def __setitem__(self, key: Union[int, str, slice], value: Any) -> None:
        # self.table[self.value[key]] = value
        raise NotImplementedError(
            "Assigning values to tables is not implemented yet!"
        )  # pragma: no cover


class DynamicTableMixin(BaseModel):
    """
    Mixin to make DynamicTable subclasses behave like tables/dataframes

    Mimicking some of the behavior from :class:`hdmf.common.table.DynamicTable`
    but simplifying along the way :)
    """

    model_config = ConfigDict(extra="allow", validate_assignment=True)
    __pydantic_extra__: Dict[str, Union["VectorDataMixin", "VectorIndexMixin", "NDArray", list]]
    NON_COLUMN_FIELDS: ClassVar[tuple[str]] = (
        "id",
        "name",
        "colnames",
        "description",
    )

    # overridden by subclass but implemented here for testing and typechecking purposes :)
    colnames: List[str] = Field(default_factory=list)
    id: Optional[NDArray[Shape["* num_rows"], int]] = None

    @property
    def _columns(self) -> Dict[str, Union[list, "NDArray", "VectorDataMixin"]]:
        return {k: getattr(self, k) for i, k in enumerate(self.colnames)}

    @overload
    def __getitem__(self, item: str) -> Union[list, "NDArray", "VectorDataMixin"]: ...

    @overload
    def __getitem__(self, item: int) -> pd.DataFrame: ...

    @overload
    def __getitem__(self, item: Tuple[int, Union[int, str]]) -> Any: ...

    @overload
    def __getitem__(self, item: Tuple[Union[int, slice], ...]) -> Union[
        pd.DataFrame,
        list,
        "NDArray",
        "VectorDataMixin",
    ]: ...

    @overload
    def __getitem__(self, item: Union[slice, "NDArray"]) -> pd.DataFrame: ...

    def __getitem__(
        self,
        item: Union[
            str,
            int,
            slice,
            "NDArray",
            Tuple[int, Union[int, str]],
            Tuple[Union[int, slice], ...],
        ],
    ) -> Any:
        """
        Get an item from the table

        If item is...

        - ``str`` : get the column with this name
        - ``int`` : get the row at this index
        - ``tuple[int, int]`` : get a specific cell value eg. (0,1) gets the 0th row and 1st column
        - ``tuple[int, str]`` : get a specific cell value eg. (0, 'colname')
          gets the 0th row from ``colname``
        - ``tuple[int | slice, int | slice]`` : get a range of cells from a range of columns.
          returns as a :class:`pandas.DataFrame`
        """
        if isinstance(item, str):
            return self._columns[item]
        if isinstance(item, (int, slice, np.integer, np.ndarray)):
            data = self._slice_range(item)
            index = self.id[item]
        elif isinstance(item, tuple):
            if len(item) != 2:
                raise ValueError(
                    "DynamicTables are 2-dimensional, can't index with more than 2 indices like"
                    f" {item}"
                )

            # all other cases are tuples of (rows, cols)
            rows, cols = item
            if isinstance(cols, (int, slice, np.integer)):
                cols = self.colnames[cols]

            if isinstance(rows, int) and isinstance(cols, str):
                # single scalar value
                return self._columns[cols][rows]

            data = self._slice_range(rows, cols)
            index = self.id[rows]
        else:
            raise ValueError(f"Unsure how to get item with key {item}")

        # cast to DF
        if not isinstance(index, Iterable):
            index = [index]
        index = pd.Index(data=index)
        return pd.DataFrame(data, index=index)

    def _slice_range(
        self, rows: Union[int, slice, np.ndarray], cols: Optional[Union[str, List[str]]] = None
    ) -> Dict[str, Union[list, "NDArray", "VectorData"]]:
        if cols is None:
            cols = self.colnames
        elif isinstance(cols, str):
            cols = [cols]
        data = {}
        for k in cols:
            if isinstance(rows, np.ndarray):
                # help wanted - this is probably cr*zy slow
                val = [self._columns[k][i] for i in rows]
            else:
                val = self._columns[k][rows]

            # scalars need to be wrapped in series for pandas
            # do this by the iterability of the rows index not the value because
            # we want all lengths from this method to be equal, and if the rows are
            # scalar, that means length == 1
            if not isinstance(rows, (Iterable, slice)):
                val = [val]

            data[k] = val
        return data

    def __setitem__(self, key: str, value: Any) -> None:
        raise NotImplementedError("TODO")  # pragma: no cover

    def __setattr__(self, key: str, value: Union[list, "NDArray", "VectorData"]):
        """
        Add a column, appending it to ``colnames``
        """
        # don't use this while building the model
        if not getattr(self, "__pydantic_complete__", False):  # pragma: no cover
            return super().__setattr__(key, value)

        if key not in self.model_fields_set and not key.endswith("_index"):
            self.colnames.append(key)

        # we get a recursion error if we setattr without having first added to
        # extras if we need it to be there
        if key not in self.model_fields and key not in self.__pydantic_extra__:
            self.__pydantic_extra__[key] = value

        return super().__setattr__(key, value)

    def __getattr__(self, item: str) -> Any:
        """Try and use pandas df attrs if we don't have them"""
        try:
            return BaseModel.__getattr__(self, item)
        except AttributeError as e:
            try:
                return getattr(self[:, :], item)
            except AttributeError:
                raise e from None

    def __len__(self) -> int:
        """
        Use the id column to determine length.

        If the id column doesn't represent length accurately, it's a bug
        """
        return len(self.id)

    @model_validator(mode="before")
    @classmethod
    def create_id(cls, model: Dict[str, Any]) -> Dict:
        """
        Create ID column if not provided
        """
        if not isinstance(model, dict):
            return model
        if "id" not in model:
            lengths = []
            for key, val in model.items():
                # don't get lengths of columns with an index
                if (
                    f"{key}_index" in model
                    or (isinstance(val, VectorData) and val._index)
                    or key in cls.NON_COLUMN_FIELDS
                ):
                    continue
                lengths.append(len(val))
            model["id"] = np.arange(np.max(lengths))

        return model

    @model_validator(mode="before")
    @classmethod
    def create_colnames(cls, model: Dict[str, Any]) -> Dict:
        """
        Construct colnames from arguments.

        the model dict is ordered after python3.6, so we can use that minus
        anything in :attr:`.NON_COLUMN_FIELDS` to determine order implied from passage order
        """
        if not isinstance(model, dict):
            return model
        if "colnames" not in model:
            colnames = [
                k
                for k in model
                if k not in cls.NON_COLUMN_FIELDS
                and not k.endswith("_index")
                and not isinstance(model[k], VectorIndexMixin)
            ]
            model["colnames"] = colnames
        else:
            # add any columns not explicitly given an order at the end
            colnames = model["colnames"].copy()
            colnames.extend(
                [
                    k
                    for k in model
                    if k not in cls.NON_COLUMN_FIELDS
                    and not k.endswith("_index")
                    and k not in model["colnames"]
                    and not isinstance(model[k], VectorIndexMixin)
                ]
            )
            model["colnames"] = colnames
        return model

    @model_validator(mode="before")
    @classmethod
    def cast_extra_columns(cls, model: Dict[str, Any]) -> Dict:
        """
        If extra columns are passed as just lists or arrays, cast to VectorData
        before we resolve targets for VectorData and VectorIndex pairs.

        See :meth:`.cast_specified_columns` for handling columns in the class specification
        """
        # if columns are not in the specification, cast to a generic VectorData

        if isinstance(model, dict):
            for key, val in model.items():
                if key in cls.model_fields:
                    continue
                if not isinstance(val, (VectorData, VectorIndex)):
                    try:
                        if key.endswith("_index"):
                            model[key] = VectorIndex(name=key, description="", value=val)
                        else:
                            model[key] = VectorData(name=key, description="", value=val)
                    except ValidationError as e:  # pragma: no cover
                        raise ValidationError(
                            f"field {key} cannot be cast to VectorData from {val}"
                        ) from e
        return model

    @model_validator(mode="after")
    def resolve_targets(self) -> "DynamicTableMixin":
        """
        Ensure that any implicitly indexed columns are linked, and create backlinks
        """
        for key, col in self._columns.items():
            if isinstance(col, VectorData):
                # find an index
                idx = None
                for field_name in self.model_fields_set:
                    if field_name in self.NON_COLUMN_FIELDS or field_name == key:
                        continue
                    # implicit name-based index
                    field = getattr(self, field_name)
                    if isinstance(field, VectorIndex) and (
                        field_name == f"{key}_index" or field.target is col
                    ):
                        idx = field
                        break
                if idx is not None:
                    col._index = idx
                    idx.target = col
        return self

    @model_validator(mode="after")
    def ensure_equal_length_cols(self) -> "DynamicTableMixin":
        """
        Ensure that all columns are equal length
        """
        lengths = [len(v) for v in self._columns.values()] + [len(self.id)]
        assert all([length == lengths[0] for length in lengths]), (
            "Columns are not of equal length! "
            f"Got colnames:\n{self.colnames}\nand lengths: {lengths}"
        )
        return self

    @field_validator("*", mode="wrap")
    @classmethod
    def cast_specified_columns(
        cls, val: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
    ) -> Any:
        """
        If columns *in* the model specification are supplied as arrays,
        try casting them to the type before validating.

        Columns that are not in the spec are handled separately in
        :meth:`.cast_extra_columns`
        """
        try:
            return handler(val)
        except ValidationError as e:
            annotation = cls.model_fields[info.field_name].annotation
            if type(annotation).__name__ == "_UnionGenericAlias":
                annotation = annotation.__args__[0]
            try:
                # should pass if we're supposed to be a VectorData column
                # don't want to override intention here by insisting that it is
                # *actually* a VectorData column in case an NDArray has been specified for now
                return handler(
                    annotation(
                        val,
                        name=info.field_name,
                        description=cls.model_fields[info.field_name].description,
                    )
                )
            except Exception:
                raise e from None


class AlignedDynamicTableMixin(BaseModel):
    """
    Mixin to allow indexing multiple tables that are aligned on a common ID

    A great deal of code duplication because we need to avoid diamond inheritance
    and also it's not so easy to copy a pydantic validator method.
    """

    model_config = ConfigDict(extra="allow", validate_assignment=True)
    __pydantic_extra__: Dict[str, Union["DynamicTableMixin", "VectorDataMixin", "VectorIndexMixin"]]

    NON_CATEGORY_FIELDS: ClassVar[tuple[str]] = (
        "name",
        "categories",
        "colnames",
        "description",
    )

    name: str = "aligned_table"
    categories: List[str] = Field(default_factory=list)
    id: Optional[NDArray[Shape["* num_rows"], int]] = None

    @property
    def _categories(self) -> Dict[str, "DynamicTableMixin"]:
        return {k: getattr(self, k) for i, k in enumerate(self.categories)}

    def __getitem__(
        self, item: Union[int, str, slice, NDArray[Shape["*"], int], Tuple[Union[int, slice], str]]
    ) -> pd.DataFrame:
        """
        Mimic hdmf:

        https://github.com/hdmf-dev/hdmf/blob/dev/src/hdmf/common/alignedtable.py#L261
        Args:
            item:

        Returns:

        """
        if isinstance(item, str):
            # get a single table
            return self._categories[item][:]
        elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], str):
            # get a slice of a single table
            return self._categories[item[1]][item[0]]
        elif isinstance(item, (int, slice, Iterable)):
            # get a slice of all the tables
            ids = self.id[item]
            if not isinstance(ids, Iterable):
                ids = pd.Series([ids])
            ids = pd.DataFrame({"id": ids})
            tables = [ids]
            for category_name, category in self._categories.items():
                table = category[item]
                if isinstance(table, pd.DataFrame):
                    table = table.reset_index()
                elif isinstance(table, np.ndarray):
                    table = pd.DataFrame({category_name: [table]})
                elif isinstance(table, Iterable):
                    table = pd.DataFrame({category_name: table})
                else:
                    raise ValueError(
                        f"Don't know how to construct category table for {category_name}"
                    )
                tables.append(table)

            names = [self.name] + self.categories
            # construct below in case we need to support array indexing in the future
        else:
            raise ValueError(
                f"Dont know how to index with {item}, "
                "need an int, string, slice, ndarray, or tuple[int | slice, str]"
            )

        df = pd.concat(tables, axis=1, keys=names)
        df.set_index((self.name, "id"), drop=True, inplace=True)
        return df

    def __getattr__(self, item: str) -> Any:
        """Try and use pandas df attrs if we don't have them"""
        try:
            return BaseModel.__getattr__(self, item)
        except AttributeError as e:
            try:
                return getattr(self[:], item)
            except AttributeError:
                raise e from None

    def __len__(self) -> int:
        """
        Use the id column to determine length.

        If the id column doesn't represent length accurately, it's a bug
        """
        return len(self.id)

    @model_validator(mode="before")
    @classmethod
    def create_id(cls, model: Dict[str, Any]) -> Dict:
        """
        Create ID column if not provided
        """
        if "id" not in model:
            lengths = []
            for key, val in model.items():
                # don't get lengths of columns with an index
                if (
                    f"{key}_index" in model
                    or (isinstance(val, VectorData) and val._index)
                    or key in cls.NON_CATEGORY_FIELDS
                ):
                    continue
                lengths.append(len(val))
            model["id"] = np.arange(np.max(lengths))

        return model

    @model_validator(mode="before")
    @classmethod
    def create_categories(cls, model: Dict[str, Any]) -> Dict:
        """
        Construct categories from arguments.

        the model dict is ordered after python3.6, so we can use that minus
        anything in :attr:`.NON_COLUMN_FIELDS` to determine order implied from passage order
        """
        if "categories" not in model:
            categories = [
                k for k in model if k not in cls.NON_CATEGORY_FIELDS and not k.endswith("_index")
            ]
            model["categories"] = categories
        else:
            # add any columns not explicitly given an order at the end
            categories = [
                k
                for k in model
                if k not in cls.NON_COLUMN_FIELDS
                and not k.endswith("_index")
                and k not in model["categories"]
            ]
            model["categories"].extend(categories)
        return model

    @model_validator(mode="after")
    def resolve_targets(self) -> "DynamicTableMixin":
        """
        Ensure that any implicitly indexed columns are linked, and create backlinks
        """
        for key, col in self._categories.items():
            if isinstance(col, VectorData):
                # find an index
                idx = None
                for field_name in self.model_fields_set:
                    if field_name in self.NON_CATEGORY_FIELDS or field_name == key:
                        continue
                    # implicit name-based index
                    field = getattr(self, field_name)
                    if isinstance(field, VectorIndex) and (
                        field_name == f"{key}_index" or field.target is col
                    ):
                        idx = field
                        break
                if idx is not None:
                    col._index = idx
                    idx.target = col
        return self

    @model_validator(mode="after")
    def ensure_equal_length_cols(self) -> "DynamicTableMixin":
        """
        Ensure that all columns are equal length
        """
        lengths = [len(v) for v in self._categories.values()] + [len(self.id)]
        assert all([length == lengths[0] for length in lengths]), (
            "Columns are not of equal length! "
            f"Got colnames:\n{self.categories}\nand lengths: {lengths}"
        )
        return self


linkml_meta = LinkMLMeta(
    {
        "annotations": {
            "is_namespace": {"tag": "is_namespace", "value": False},
            "namespace": {"tag": "namespace", "value": "hdmf-common"},
        },
        "default_prefix": "hdmf-common.table/",
        "id": "hdmf-common.table",
        "imports": ["hdmf-common.base", "hdmf-common.nwb.language"],
        "name": "hdmf-common.table",
    }
)


class VectorData(VectorDataMixin):
    """
    An n-dimensional dataset representing a column of a DynamicTable. If used without an accompanying VectorIndex, first dimension is along the rows of the DynamicTable and each step along the first dimension is a cell of the larger table. VectorData can also be used to represent a ragged array if paired with a VectorIndex. This allows for storing arrays of varying length in a single cell of the DynamicTable by indexing into this VectorData. The first vector is at VectorData[0:VectorIndex[0]]. The second vector is at VectorData[VectorIndex[0]:VectorIndex[1]], and so on.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "hdmf-common.table", "tree_root": True}
    )

    name: str = Field(...)
    description: str = Field(..., description="""Description of what these vectors represent.""")
    value: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class VectorIndex(VectorIndexMixin):
    """
    Used with VectorData to encode a ragged array. An array of indices into the first dimension of the target VectorData, and forming a map between the rows of a DynamicTable and the indices of the VectorData. The name of the VectorIndex is expected to be the name of the target VectorData object followed by \"_index\".
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "hdmf-common.table", "tree_root": True}
    )

    name: str = Field(...)
    target: Optional[VectorData] = Field(
        None, description="""Reference to the target dataset that this index applies to."""
    )
    description: str = Field(..., description="""Description of what these vectors represent.""")
    value: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class ElementIdentifiers(Data):
    """
    A list of unique identifiers for values within a dataset, e.g. rows of a DynamicTable.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "hdmf-common.table", "tree_root": True}
    )

    name: str = Field(
        "element_id", json_schema_extra={"linkml_meta": {"ifabsent": "string(element_id)"}}
    )


class DynamicTableRegion(DynamicTableRegionMixin, VectorData):
    """
    DynamicTableRegion provides a link from one table to an index or region of another. The `table` attribute is a link to another `DynamicTable`, indicating which table is referenced, and the data is int(s) indicating the row(s) (0-indexed) of the target array. `DynamicTableRegion`s can be used to associate rows with repeated meta-data without data duplication. They can also be used to create hierarchical relationships between multiple `DynamicTable`s. `DynamicTableRegion` objects may be paired with a `VectorIndex` object to create ragged references, so a single cell of a `DynamicTable` can reference many rows of another `DynamicTable`.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "hdmf-common.table", "tree_root": True}
    )

    name: str = Field(...)
    table: DynamicTable = Field(
        ..., description="""Reference to the DynamicTable object that this region applies to."""
    )
    description: str = Field(
        ..., description="""Description of what this table region points to."""
    )
    value: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class VocabData(VectorData):
    """
    Data that come from a controlled vocabulary of text values. A data value of i corresponds to the i-th element in the 'vocabulary' array attribute.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "hdmf-common.table", "tree_root": True}
    )

    name: str = Field(...)
    vocabulary: NDArray[Shape["* null"], str] = Field(
        ...,
        description="""The available items in the controlled vocabulary.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "null"}]}}},
    )
    description: str = Field(..., description="""Description of what these vectors represent.""")
    value: Optional[
        Union[
            NDArray[Shape["* dim0"], Any],
            NDArray[Shape["* dim0, * dim1"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2"], Any],
            NDArray[Shape["* dim0, * dim1, * dim2, * dim3"], Any],
        ]
    ] = Field(None)


class DynamicTable(DynamicTableMixin):
    """
    A group containing multiple datasets that are aligned on the first dimension (Currently, this requirement if left up to APIs to check and enforce). These datasets represent different columns in the table. Apart from a column that contains unique identifiers for each row, there are no other required datasets. Users are free to add any number of custom VectorData objects (columns) here. DynamicTable also supports ragged array columns, where each element can be of a different size. To add a ragged array column, use a VectorIndex type to index the corresponding VectorData type. See documentation for VectorData and VectorIndex for more details. Unlike a compound data type, which is analogous to storing an array-of-structs, a DynamicTable can be thought of as a struct-of-arrays. This provides an alternative structure to choose from when optimizing storage for anticipated access patterns. Additionally, this type provides a way of creating a table without having to define a compound type up front. Although this convenience may be attractive, users should think carefully about how data will be accessed. DynamicTable is more appropriate for column-centric access, whereas a dataset with a compound type would be more appropriate for row-centric access. Finally, data size should also be taken into account. For small tables, performance loss may be an acceptable trade-off for the flexibility of a DynamicTable.
    """

    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta(
        {"from_schema": "hdmf-common.table", "tree_root": True}
    )

    name: str = Field(...)
    colnames: List[str] = Field(
        ...,
        description="""The names of the columns in this table. This should be used to specify an order to the columns.""",
    )
    description: str = Field(..., description="""Description of what is in this dynamic table.""")
    id: VectorData[NDArray[Shape["* num_rows"], int]] = Field(
        ...,
        description="""Array of unique identifiers for the rows of this dynamic table.""",
        json_schema_extra={"linkml_meta": {"array": {"dimensions": [{"alias": "num_rows"}]}}},
    )
    vector_data: Optional[List[VectorData]] = Field(
        None, description="""Vector columns, including index columns, of this dynamic table."""
    )


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
VectorData.model_rebuild()
VectorIndex.model_rebuild()
ElementIdentifiers.model_rebuild()
DynamicTableRegion.model_rebuild()
VocabData.model_rebuild()
DynamicTable.model_rebuild()
