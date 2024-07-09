"""
Adapter for NWB datasets to linkml Classes
"""
from abc import abstractmethod
from typing import Optional, Type

from linkml_runtime.linkml_model.meta import (
    SlotDefinition,
)

from nwb_linkml.adapters.adapter import BuildResult
from nwb_linkml.adapters.array import ArrayAdapter
from nwb_linkml.adapters.classes import ClassAdapter
from nwb_linkml.maps import QUANTITY_MAP, Map
from nwb_linkml.maps.dtype import flat_to_linkml
from nwb_linkml.maps.naming import camel_to_snake
from nwb_schema_language import Dataset, CompoundDtype


class DatasetMap(Map):
    """
    Abstract builder class for dataset elements
    """

    @classmethod
    @abstractmethod
    def check(c, cls: Dataset) -> bool:
        """
        Check if this map applies
        """
        pass  # pragma: no cover

    @classmethod
    @abstractmethod
    def apply(
        c, cls: Dataset, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Apply this mapping
        """
        pass  # pragma: no cover


class MapScalar(DatasetMap):
    """
    Datasets that are just a single value should just be a scalar value, not an array with size 1

    Replaces the built class with a slot.

    Examples:

        .. adapter:: DatasetAdapter
            :nwb:
                datasets:
                - name: MyScalar
                  doc: A scalar
                  dtype: int32
                  quantity: '?'
            :linkml:
                attributes:
                - name: MyScalar
                  description: A scalar
                  multivalued: false
                  range: int32
                  required: false





    """

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        .. list-table::
            :header-rows: 1
            :align: left

            * - Attr
              - Value
            * - ``neurodata_type_inc``
              - ``None``
            * - ``attributes``
              - ``None``
            * - ``dims``
              - ``None``
            * - ``shape``
              - ``None``
            * - ``name``
              - ``str``

        """
        return (
            cls.neurodata_type_inc != "VectorData"
            and not cls.neurodata_type_inc
            and not cls.attributes
            and not cls.dims
            and not cls.shape
            and not is_compound(cls)
            and cls.name
        )

    @classmethod
    def apply(
        c, cls: Dataset, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Map to a scalar value
        """
        this_slot = SlotDefinition(
            name=cls.name,
            description=cls.doc,
            range=ClassAdapter.handle_dtype(cls.dtype),
            **QUANTITY_MAP[cls.quantity],
        )
        res = BuildResult(slots=[this_slot])
        return res


class MapScalarAttributes(DatasetMap):
    """
    A scalar with attributes gets an additional slot "value" that contains the actual scalar
    value of this field
    """

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        .. list-table::
            :header-rows: 1
            :align: left

            * - Attr
              - Value
            * - ``neurodata_type_inc``
              - ``None``
            * - ``attributes``
              - Truthy
            * - ``dims``
              - ``None``
            * - ``shape``
              - ``None``
            * - ``name``
              - ``str``

        """
        return (
            cls.neurodata_type_inc != "VectorData"
            and not cls.neurodata_type_inc
            and cls.attributes
            and not cls.dims
            and not cls.shape
            and cls.name
        )

    @classmethod
    def apply(
        c, cls: Dataset, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Map to a scalar attribute with an adjoining "value" slot
        """
        value_slot = SlotDefinition(
            name="value", range=ClassAdapter.handle_dtype(cls.dtype), required=True
        )
        res.classes[0].attributes["value"] = value_slot
        return res


class MapListlike(DatasetMap):
    """
    Datasets that refer to other datasets (that handle their own arrays)
    """

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        Check if we are a 1D dataset that isn't a normal datatype
        """
        dtype = ClassAdapter.handle_dtype(cls.dtype)
        return is_1d(cls) and dtype != "AnyType" and dtype not in flat_to_linkml

    @classmethod
    def apply(
        c, cls: Dataset, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Map to a list of the given class
        """
        dtype = camel_to_snake(ClassAdapter.handle_dtype(cls.dtype))
        slot = SlotDefinition(
            name=dtype,
            multivalued=True,
            range=ClassAdapter.handle_dtype(cls.dtype),
            description=cls.doc,
            required=cls.quantity not in ("*", "?"),
        )
        res.classes[0].attributes[dtype] = slot
        return res


class MapArraylike(DatasetMap):
    """
    Datasets without any additional attributes don't create their own subclass,
    they're just an array :).

    Replace the base class with the array class, and make a slot that refers to it.
    """

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        Check if we're a plain array
        """
        return cls.name and all([cls.dims, cls.shape]) and not has_attrs(cls) and not is_compound(cls)

    @classmethod
    def apply(
        c, cls: Dataset, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Map to an array class and the adjoining slot
        """
        array_adapter = ArrayAdapter(cls.dims, cls.shape)
        expressions = array_adapter.make_slot()
        name = camel_to_snake(cls.name)
        res = BuildResult(
            slots=[
                SlotDefinition(
                    name=name,
                    multivalued=False,
                    range=ClassAdapter.handle_dtype(cls.dtype),
                    description=cls.doc,
                    required=cls.quantity not in ("*", "?"),
                    **expressions,
                )
            ]
        )
        return res


class MapArrayLikeAttributes(DatasetMap):
    """
    The most general case - treat everything that isn't handled by one of the special cases
    as an array!
    """

    NEEDS_NAME = True

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        Check that we're an array with some additional metadata
        """
        dtype = ClassAdapter.handle_dtype(cls.dtype)
        return (
            all([cls.dims, cls.shape])
            and cls.neurodata_type_inc != "VectorData"
            and has_attrs(cls)
            and not is_compound(cls)
            and (dtype == "AnyType" or dtype in flat_to_linkml)
        )

    @classmethod
    def apply(
        c, cls: Dataset, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Map to an arraylike class
        """
        array_adapter = ArrayAdapter(cls.dims, cls.shape)
        expressions = array_adapter.make_slot()
        # make a slot for the arraylike class
        array_slot = SlotDefinition(
            name="array", range=ClassAdapter.handle_dtype(cls.dtype), **expressions
        )
        res.classes[0].attributes.update({"array": array_slot})
        return res


# --------------------------------------------------
# DynamicTable special cases
# --------------------------------------------------


class Map1DVector(DatasetMap):
    """
    ``VectorData`` is subclassed with a name but without dims or attributes,
    treat this as a normal 1D array slot that replaces any class that would be built for this

    eg. all the datasets in epoch.TimeIntervals:

    .. code-block:: yaml

        groups:
        - neurodata_type_def: TimeIntervals
          neurodata_type_inc: DynamicTable
          doc: A container for aggregating epoch data and the TimeSeries that each epoch applies
            to.
          datasets:
          - name: start_time
            neurodata_type_inc: VectorData
            dtype: float32
            doc: Start time of epoch, in seconds.

    """

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        Check that we're a 1d VectorData class
        """
        return (
            cls.neurodata_type_inc == "VectorData"
            and not cls.dims
            and not cls.shape
            and not cls.attributes
            and not cls.neurodata_type_def
            and not is_compound(cls)
            and cls.name
        )

    @classmethod
    def apply(
        c, cls: Dataset, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Return a simple multivalued slot
        """
        this_slot = SlotDefinition(
            name=cls.name,
            description=cls.doc,
            range=ClassAdapter.handle_dtype(cls.dtype),
            multivalued=True,
        )
        # No need to make a class for us, so we replace the existing build results
        res = BuildResult(slots=[this_slot])
        return res


class MapNVectors(DatasetMap):
    """
    An unnamed container that indicates an arbitrary quantity of some other neurodata type.

    Most commonly: ``VectorData`` is subclassed without a name and with a '*' quantity to indicate
    arbitrary columns.
    """

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        Check for being an unnamed multivalued vector class
        """
        return (
            cls.name is None
            and cls.neurodata_type_def is None
            and cls.neurodata_type_inc
            and cls.quantity in ("*", "+")
        )

    @classmethod
    def apply(
        c, cls: Dataset, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Return a slot mapping to multiple values of the type
        """
        this_slot = SlotDefinition(
            name=camel_to_snake(cls.neurodata_type_inc),
            description=cls.doc,
            range=cls.neurodata_type_inc,
            **QUANTITY_MAP[cls.quantity],
        )
        # No need to make a class for us, so we replace the existing build results
        res = BuildResult(slots=[this_slot])
        return res

class MapCompoundDtype(DatasetMap):
    """
    A ``dtype`` declared as an array of types that function effectively as a row in a table.

    We render them just as a class with each of the dtypes as slots - they are
    typically used by other datasets to create a table.

    Eg. ``base.TimeSeriesReferenceVectorData``

    .. code-block:: yaml

        datasets:
        - neurodata_type_def: TimeSeriesReferenceVectorData
          neurodata_type_inc: VectorData
          default_name: timeseries
          dtype:
          - name: idx_start
            dtype: int32
            doc: Start index into the TimeSeries 'data' and 'timestamp' datasets of the referenced
              TimeSeries. The first dimension of those arrays is always time.
          - name: count
            dtype: int32
            doc: Number of data samples available in this time series, during this epoch
          - name: timeseries
            dtype:
              target_type: TimeSeries
              reftype: object
            doc: The TimeSeries that this index applies to
          doc: Column storing references to a TimeSeries (rows). For each TimeSeries this
            VectorData column stores the start_index and count to indicate the range in time
            to be selected as well as an object reference to the TimeSeries.

    """

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        Check that we're a dataset with a compound dtype
        """
        return is_compound(cls)

    @classmethod
    def apply(
        c, cls: Dataset, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Make a new class for this dtype, using its sub-dtypes as fields,
        and use it as the range for the parent class
        """
        slots = {}
        for a_dtype in cls.dtype:
            slots[a_dtype.name] = SlotDefinition(
                name=a_dtype.name,
                description=a_dtype.doc,
                range=ClassAdapter.handle_dtype(a_dtype.dtype),
                **QUANTITY_MAP[cls.quantity]
            )
        res.classes[0].attributes.update(slots)
        return res








class DatasetAdapter(ClassAdapter):
    """
    Orchestrator class for datasets - calls the set of applicable mapping classes
    """
    TYPE: Type = Dataset

    cls: Dataset

    def build(self) -> BuildResult:
        """
        Build the base result, and then apply the applicable mappings.
        """
        res = self.build_base()

        # find a map to use
        map = self.match()

        # apply matching maps
        if map is not None:
            res = map.apply(self.cls, res, self._get_full_name())

        return res

    def match(self) -> Optional[Type[DatasetMap]]:
        """
        Find the map class that applies to this class

        Returns:
            :class:`.DatasetMap`

        Raises:
            RuntimeError - if more than one map matches
        """
        # find a map to use
        matches = [m for m in DatasetMap.__subclasses__() if m.check(self.cls)]

        if len(matches) > 1:  # pragma: no cover
            raise RuntimeError(
                "Only one map should apply to a dataset, you need to refactor the maps! Got maps:"
                f" {matches}"
            )
        elif len(matches) == 0:
            return None
        else:
            return matches[0]


def is_1d(cls: Dataset) -> bool:
    """
    Check if the values of a dataset are 1-dimensional
    """
    return (
        not any([isinstance(dim, list) for dim in cls.dims]) and len(cls.dims) == 1
    ) or (  # nested list
        all([isinstance(dim, list) for dim in cls.dims])
        and len(cls.dims) == 1
        and len(cls.dims[0]) == 1
    )

def is_compound(cls: Dataset) -> bool:
    return isinstance(cls.dtype, list) and len(cls.dtype)>0 and isinstance(cls.dtype[0], CompoundDtype)

def has_attrs(cls: Dataset) -> bool:
    """
    Check if a dataset has any attributes at all without defaults
    """
    return len(cls.attributes) > 0 and all([not a.value for a in cls.attributes])
