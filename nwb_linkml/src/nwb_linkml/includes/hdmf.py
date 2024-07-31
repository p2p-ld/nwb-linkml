"""
Special types for mimicking HDMF special case behavior
"""

from typing import Any, ClassVar, Dict, List, Optional, Union, Tuple, overload, TYPE_CHECKING


from linkml.generators.pydanticgen.template import Imports, Import, ObjectImport
from numpydantic import NDArray
from pandas import DataFrame
from pydantic import BaseModel, ConfigDict, Field, model_validator

if TYPE_CHECKING:
    from nwb_linkml.models import VectorData, VectorIndex


class DynamicTableMixin(BaseModel):
    """
    Mixin to make DynamicTable subclasses behave like tables/dataframes

    Mimicking some of the behavior from :class:`hdmf.common.table.DynamicTable`
    but simplifying along the way :)
    """

    model_config = ConfigDict(extra="allow")
    __pydantic_extra__: Dict[str, Union[list, "NDArray", "VectorData"]]
    NON_COLUMN_FIELDS: ClassVar[tuple[str]] = (
        "name",
        "colnames",
        "description",
    )

    # overridden by subclass but implemented here for testing and typechecking purposes :)
    colnames: List[str] = Field(default_factory=list)

    @property
    def _columns(self) -> Dict[str, Union[list, "NDArray", "VectorData"]]:
        return {k: getattr(self, k) for i, k in enumerate(self.colnames)}

    @property
    def _columns_list(self) -> List[Union[list, "NDArray", "VectorData"]]:
        return [getattr(self, k) for i, k in enumerate(self.colnames)]

    @overload
    def __getitem__(self, item: str) -> Union[list, "NDArray", "VectorData"]: ...

    @overload
    def __getitem__(self, item: int) -> DataFrame: ...

    @overload
    def __getitem__(self, item: Tuple[int, Union[int, str]]) -> Any: ...

    @overload
    def __getitem__(self, item: Tuple[Union[int, slice], ...]) -> Union[
        DataFrame,
        list,
        "NDArray",
        "VectorData",
    ]: ...

    @overload
    def __getitem__(self, item: slice) -> DataFrame: ...

    def __getitem__(
        self,
        item: Union[
            str,
            int,
            slice,
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
        if isinstance(item, (int, slice)):
            return DataFrame.from_dict(self._slice_range(item))
        elif isinstance(item, tuple):
            if len(item) != 2:
                raise ValueError(
                    "DynamicTables are 2-dimensional, can't index with more than 2 indices like"
                    f" {item}"
                )

            # all other cases are tuples of (rows, cols)
            rows, cols = item
            if isinstance(cols, (int, slice)):
                cols = self.colnames[cols]
            data = self._slice_range(rows, cols)
            return DataFrame.from_dict(data)
        else:
            raise ValueError(f"Unsure how to get item with key {item}")

    def _slice_range(
        self, rows: Union[int, slice], cols: Optional[Union[str, List[str]]] = None
    ) -> Dict[str, Union[list, "NDArray", "VectorData"]]:
        if cols is None:
            cols = self.colnames
        elif isinstance(cols, str):
            cols = [cols]

        data = {k: self._columns[k][rows] for k in cols}
        return data

    def __setitem__(self, key: str, value: Any) -> None:
        raise NotImplementedError("TODO")

    def __setattr__(self, key: str, value: Union[list, "NDArray", "VectorData"]):
        """
        Add a column, appending it to ``colnames``
        """
        # don't use this while building the model
        if not getattr(self, "__pydantic_complete__", False):
            return super().__setattr__(key, value)

        if key not in self.model_fields_set and not key.endswith("_index"):
            self.colnames.append(key)

        return super().__setattr__(key, value)

    @model_validator(mode="before")
    @classmethod
    def create_colnames(cls, model: Dict[str, Any]):
        """
        Construct colnames from arguments.

        the model dict is ordered after python3.6, so we can use that minus
        anything in :attr:`.NON_COLUMN_FIELDS` to determine order implied from passage order
        """
        if "colnames" not in model:
            colnames = [
                k
                for k in model.keys()
                if k not in cls.NON_COLUMN_FIELDS and not k.endswith("_index")
            ]
            model["colnames"] = colnames
        else:
            # add any columns not explicitly given an order at the end
            colnames = [
                k
                for k in model.keys()
                if k not in cls.NON_COLUMN_FIELDS
                and not k.endswith("_index")
                and k not in model["colnames"].keys()
            ]
            model["colnames"].extend(colnames)
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
                    # implicit name-based index
                    field = getattr(self, field_name)
                    if isinstance(field, VectorIndex):
                        if field_name == f"{key}_index":
                            idx = field
                            break
                        elif field.target is col:
                            idx = field
                            break
                if idx is not None:
                    col._index = idx
                    idx.target = col
        return self


class VectorDataMixin(BaseModel):
    """
    Mixin class to give VectorData indexing abilities
    """

    _index: Optional["VectorIndex"] = None

    # redefined in `VectorData`, but included here for testing and type checking
    array: Optional[NDArray] = None

    def __getitem__(self, item: Union[str, int, slice, Tuple[Union[str, int, slice], ...]]) -> Any:
        if self._index:
            # Following hdmf, VectorIndex is the thing that knows how to do the slicing
            return self._index[item]
        else:
            return self.array[item]

    def __setitem__(self, key, value) -> None:
        if self._index:
            # Following hdmf, VectorIndex is the thing that knows how to do the slicing
            self._index[key] = value
        else:
            self.array[key] = value


class VectorIndexMixin(BaseModel):
    """
    Mixin class to give VectorIndex indexing abilities
    """

    # redefined in `VectorData`, but included here for testing and type checking
    array: Optional[NDArray] = None
    target: Optional["VectorData"] = None

    def _getitem_helper(self, arg: int):
        """
        Mimicking :func:`hdmf.common.table.VectorIndex.__getitem_helper`
        """

        start = 0 if arg == 0 else self.array[arg - 1]
        end = self.array[arg]
        return self.target.array[slice(start, end)]

    def __getitem__(self, item: Union[int, slice]) -> Any:
        if self.target is None:
            return self.array[item]
        elif type(self.target).__name__ == "VectorData":
            if isinstance(item, int):
                return self._getitem_helper(item)
            else:
                idx = range(*item.indices(len(self.array)))
                return [self._getitem_helper(i) for i in idx]
        else:
            raise NotImplementedError("DynamicTableRange not supported yet")

    def __setitem__(self, key, value) -> None:
        if self._index:
            # VectorIndex is the thing that knows how to do the slicing
            self._index[key] = value
        else:
            self.array[key] = value


DYNAMIC_TABLE_IMPORTS = Imports(
    imports=[
        Import(module="pandas", objects=[ObjectImport(name="DataFrame")]),
        Import(
            module="typing",
            objects=[
                ObjectImport(name="ClassVar"),
                ObjectImport(name="overload"),
                ObjectImport(name="Tuple"),
            ],
        ),
        Import(module="numpydantic", objects=[ObjectImport(name="NDArray")]),
        Import(module="pydantic", objects=[ObjectImport(name="model_validator")]),
    ]
)
"""
Imports required for the dynamic table mixin

VectorData is purposefully excluded as an import or an inject so that it will be
resolved to the VectorData definition in the generated module
"""
DYNAMIC_TABLE_INJECTS = [VectorDataMixin, VectorIndexMixin, DynamicTableMixin]

# class VectorDataMixin(BaseModel):
#     index: Optional[BaseModel] = None
