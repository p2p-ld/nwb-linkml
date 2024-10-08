"""
Adapter for NWB datasets to linkml Classes
"""

from abc import abstractmethod
from typing import ClassVar, Optional, Type

from linkml_runtime.linkml_model.meta import ArrayExpression, SlotDefinition

from nwb_linkml.adapters.adapter import BuildResult, defaults, has_attrs, is_1d, is_compound
from nwb_linkml.adapters.array import ArrayAdapter
from nwb_linkml.adapters.classes import ClassAdapter
from nwb_linkml.maps import QUANTITY_MAP, Map
from nwb_linkml.maps.dtype import flat_to_linkml, handle_dtype, inlined
from nwb_linkml.maps.naming import camel_to_snake
from nwb_schema_language import Dataset


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
                slots:
                - name: MyScalar
                  description: A scalar
                  range: int32

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
            range=handle_dtype(cls.dtype),
            **QUANTITY_MAP[cls.quantity],
            **defaults(cls),
        )
        res = BuildResult(slots=[this_slot])
        return res


class MapScalarAttributes(DatasetMap):
    """
    A scalar with attributes gets an additional slot "value" that contains the actual scalar
    value of this field

    Examples:

        .. adapter:: DatasetAdapter
            :nwb:
                datasets:
                - name: starting_time
                  dtype: float64
                  doc: Timestamp of the first sample in seconds. When timestamps are uniformly
                    spaced, the timestamp of the first sample can be specified and all subsequent
                    ones calculated from the sampling rate attribute.
                  quantity: '?'
                  attributes:
                  - name: rate
                    dtype: float32
                    doc: Sampling rate, in Hz.
                  - name: unit
                    dtype: text
                    value: seconds
                    doc: Unit of measurement for time, which is fixed to 'seconds'.
            :linkml:
                classes:
                - name: starting_time
                  description: Timestamp of the first sample in seconds. When timestamps are
                    uniformly spaced, the timestamp of the first sample can be specified and all
                    subsequent ones calculated from the sampling rate attribute.
                  attributes:
                    name:
                      name: name
                      ifabsent: string(starting_time)
                      identifier: true
                      range: string
                      required: true
                      equals_string: starting_time
                    rate:
                      name: rate
                      description: Sampling rate, in Hz.
                      range: float32
                      required: true
                    unit:
                      name: unit
                      description: Unit of measurement for time, which is fixed to 'seconds'.
                      ifabsent: string(seconds)
                      range: text
                      required: true
                      equals_string: seconds
                    value:
                      name: value
                      range: float64
                      required: true
                  tree_root: true

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
              - ``True``
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
        # the *value slot* within the generated class is always required,
        # but the slot in the parent class referring to this one will indicate whether the whole
        # thing is optional or not. You can't provide the attributes of the optional dataset
        # without providing its value
        quantity = QUANTITY_MAP[cls.quantity].copy()
        quantity["required"] = True

        value_slot = SlotDefinition(
            name="value",
            range=handle_dtype(cls.dtype),
            **quantity,
            **defaults(cls),
        )
        res.classes[0].attributes["value"] = value_slot
        return res


class MapListlike(DatasetMap):
    """
    Datasets that refer to a list of other datasets.

    Used exactly once in the core schema, in ``ImageReferences`` -
    an array of references to other ``Image`` datasets. We ignore the
    usual array structure and unnest the implicit array into a slot named "value"
    rather than the oddly-named ``num_images`` dimension so that
    ultimately in the pydantic model we get a nicely behaved single-level list.

    Examples:

        .. adapter:: DatasetAdapter
            :nwb:
                datasets:
                - neurodata_type_def: ImageReferences
                  neurodata_type_inc: NWBData
                  dtype:
                    target_type: Image
                    reftype: object
                  dims:
                  - num_images
                  shape:
                  - null
                  doc: Ordered dataset of references to Image objects.
            :linkml:
                classes:
                - name: ImageReferences
                  description: Ordered dataset of references to Image objects.
                  is_a: NWBData
                  attributes:
                    name:
                      name: name
                      identifier: true
                      range: string
                      required: true
                    value:
                      name: value
                      annotations:
                        source_type:
                          tag: source_type
                          value: reference
                      description: Ordered dataset of references to Image objects.
                      range: Image
                      required: true
                      multivalued: true
                      inlined: true
                      inlined_as_list: true
                  tree_root: true

    """

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        Check if we are a 1D dataset that isn't a normal datatype

        .. list-table::
            :header-rows: 1
            :align: left

            * - Attr
              - Value
            * - :func:`.is_1d`
              - ``True``
            * - ``dtype``
              - ``Class``
        """
        dtype = handle_dtype(cls.dtype)
        return (
            cls.neurodata_type_inc != "VectorData"
            and is_1d(cls)
            and dtype != "AnyType"
            and dtype not in flat_to_linkml
        )

    @classmethod
    def apply(
        c, cls: Dataset, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Map to a list of the given class
        """
        slot = SlotDefinition(
            name="value",
            multivalued=True,
            range=handle_dtype(cls.dtype),
            description=cls.doc,
            required=cls.quantity not in ("*", "?"),
            annotations=[{"source_type": "reference"}],
            inlined=True,
            inlined_as_list=True,
        )
        res.classes[0].attributes["value"] = slot
        return res


class MapArraylike(DatasetMap):
    """
    Datasets without any additional attributes don't create their own subclass,
    they're just an array :).

    Replace the base class with a slot that defines the array.

    Examples:

        eg. from ``image.ImageSeries`` :

        .. adapter:: DatasetAdapter
            :nwb:
                datasets:
                - name: data
                  dtype: numeric
                  dims:
                  - - frame
                    - x
                    - y
                  - - frame
                    - x
                    - y
                    - z
                  shape:
                  - - null
                    - null
                    - null
                  - - null
                    - null
                    - null
                    - null
                  doc: Binary data representing images across frames. If data are stored in an
                    external file, this should be an empty 3D array.
            :linkml:
                slots:
                - name: data
                  description: Binary data representing images across frames. If data are stored in
                    an external file, this should be an empty 3D array.
                  multivalued: false
                  range: numeric
                  required: true
                  any_of:
                  - array:
                      dimensions:
                      - alias: frame
                      - alias: x
                      - alias: y
                  - array:
                      dimensions:
                      - alias: frame
                      - alias: x
                      - alias: y
                      - alias: z

    """

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        Check if we're a plain array

        .. list-table::
            :header-rows: 1
            :align: left

            * - Attr
              - Value
            * - ``name``
              - ``True``
            * - ``dims``
              - ``True``
            * - ``shape``
              - ``True``
            * - :func:`.has_attrs`
              - ``False``
            * - :func:`.is_compound`
              - ``False``

        """
        return (
            cls.name
            and (all([cls.dims, cls.shape]) or cls.neurodata_type_inc == "VectorData")
            and not has_attrs(cls)
            and not is_compound(cls)
        )

    @classmethod
    def apply(
        c, cls: Dataset, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Map to an array class and the adjoining slot
        """
        if cls.neurodata_type_inc == "VectorData" and not (cls.dims and cls.shape):
            expressions = {
                "array": ArrayExpression(
                    minimum_number_dimensions=1, maximum_number_dimensions=False
                )
            }
        else:
            array_adapter = ArrayAdapter(cls.dims, cls.shape)
            expressions = array_adapter.make_slot()
        name = camel_to_snake(cls.name)
        res = BuildResult(
            slots=[
                SlotDefinition(
                    name=name,
                    multivalued=False,
                    range=handle_dtype(cls.dtype),
                    description=cls.doc,
                    required=cls.quantity not in ("*", "?"),
                    inlined=inlined(cls.dtype),
                    **expressions,
                )
            ]
        )
        return res


class MapArrayLikeAttributes(DatasetMap):
    """
    The most general case - treat everything that isn't handled by one of the special cases
    as an array!

    We specifically include classes that have no attributes but also don't have a name,
    as they still require their own class (unlike :class:`.MapArrayLike` above, where we
    just generate an anonymous slot.)

    Examples:

        .. adapter:: DatasetAdapter
            :nwb:
                datasets:
                - neurodata_type_def: Image
                  neurodata_type_inc: NWBData
                  dtype: numeric
                  dims:
                  - - x
                    - y
                  - - x
                    - y
                    - r, g, b
                  - - x
                    - y
                    - r, g, b, a
                  shape:
                  - - null
                    - null
                  - - null
                    - null
                    - 3
                  - - null
                    - null
                    - 4
                  doc: An abstract data type for an image. Shape can be 2-D (x, y), or 3-D where the
                    third dimension can have three or four elements, e.g. (x, y, (r, g, b)) or
                    (x, y, (r, g, b, a)).
                  attributes:
                  - name: resolution
                    dtype: float32
                    doc: Pixel resolution of the image, in pixels per centimeter.
                    required: false
                  - name: description
                    dtype: text
                    doc: Description of the image.
                    required: false
            :linkml:
                classes:
                - name: Image
                  description: An abstract data type for an image. Shape can be 2-D (x, y), or 3-D
                    where the third dimension can have three or four elements, e.g. (x, y, (r, g,
                    b)) or (x, y, (r, g, b, a)).
                  is_a: NWBData
                  attributes:
                    name:
                      name: name
                      identifier: true
                      range: string
                      required: true
                    resolution:
                      name: resolution
                      description: Pixel resolution of the image, in pixels per centimeter.
                      range: float32
                      required: false
                    description:
                      name: description
                      description: Description of the image.
                      range: text
                      required: false
                    value:
                      name: value
                      range: numeric
                      any_of:
                      - array:
                          dimensions:
                          - alias: x
                          - alias: y
                      - array:
                          dimensions:
                          - alias: x
                          - alias: y
                          - alias: r_g_b
                            exact_cardinality: 3
                      - array:
                          dimensions:
                          - alias: x
                          - alias: y
                          - alias: r_g_b_a
                            exact_cardinality: 4
                  tree_root: true

    """

    NEEDS_NAME = True

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        Check that we're an array with some additional metadata
        """
        dtype = handle_dtype(cls.dtype)
        return (
            all([cls.dims, cls.shape])
            and cls.neurodata_type_inc != "VectorData"
            and (has_attrs(cls) or not cls.name)
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
            name="value", range=handle_dtype(cls.dtype), inlined=inlined(cls.dtype), **expressions
        )
        res.classes[0].attributes.update({"value": array_slot})
        return res


class MapClassRange(DatasetMap):
    """
    Datasets that are a simple named reference to another type without any
    additional modification to that type.
    """

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        Check that we are a dataset with a ``neurodata_type_inc`` and a name but nothing else
        """
        return (
            cls.neurodata_type_inc
            and not cls.neurodata_type_def
            and not cls.attributes
            and not cls.dims
            and not cls.shape
            and not cls.dtype
            and cls.name
        )

    @classmethod
    def apply(
        c, cls: Dataset, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Replace the base class with a slot with an annotation that indicates
        it should use the :class:`.Named` generic when generated to pydantic
        """
        this_slot = SlotDefinition(
            name=cls.name,
            description=cls.doc,
            range=f"{cls.neurodata_type_inc}",
            annotations=[{"named": True}, {"source_type": "neurodata_type_inc"}],
            inlined=True,
            **QUANTITY_MAP[cls.quantity],
        )
        res = BuildResult(slots=[this_slot])
        return res


# --------------------------------------------------
# DynamicTable special cases
# --------------------------------------------------


class MapNVectors(DatasetMap):
    """
    An unnamed container that indicates an arbitrary quantity of some other neurodata type.

    Most commonly: ``VectorData`` is subclassed without a name and with a '*' quantity to indicate
    arbitrary columns.

    Used twice:
    - Images
    - DynamicTable (and all its uses)

    DynamicTable (and the slot VectorData where this is called for)
    is handled specially and just dropped, because we handle the possibility for
    arbitrary extra VectorData in the :mod:`nwb_linkml.includes.hdmf` module mixin classes
    (see :class:`.MapNVectorData` ).

    So really this is just a handler for the `Images` case
    """

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        Check for being an unnamed multivalued vector class that isn't VectorData
        """
        return (
            cls.name is None
            and cls.neurodata_type_def is None
            and cls.neurodata_type_inc
            and cls.neurodata_type_inc not in ("VectorData", "VectorIndex")
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


class MapNVectorData(DatasetMap):
    """
    An extremely special case just for DynamicTable:
    DynamicTable indicates that all of its extra columns are ``VectorData`` with an
    unnamed, * quantity dataset similar to the case of :class:`.MapNVectors` .

    We handle this with the :mod:`.includes.hdmf` module mixin classes instead,
    and so to avoid generating a pointless slot and class,
    we just catch that case and return nothing.
    """

    @classmethod
    def check(c, cls: Dataset) -> bool:
        """
        Check for being an unnamed multivalued vector class that IS VectorData
        """
        return (
            (cls.name is None or cls.name in ("vector_data", "vector_index"))
            and cls.neurodata_type_def is None
            and cls.neurodata_type_inc
            and cls.neurodata_type_inc in ("VectorData", "VectorIndex")
            and cls.quantity in ("*", "+")
        )

    @classmethod
    def apply(
        c, cls: Dataset, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Return ... nothing
        """
        return BuildResult()


class MapCompoundDtype(DatasetMap):
    """
    A ``dtype`` declared as an array of types that function effectively as a row in a table.

    We render them just as a class with each of the dtypes as slots - they are
    typically used by other datasets to create a table.

    Since there is exactly one class (``TimeSeriesReferenceVectorData``) that uses compound dtypes
    meaningfully, we just hardcode the behavior of inheriting the array shape from the VectorData
    parent classes. Otherwise, linkml schemas correctly propagate the ``value`` property.

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
                range=handle_dtype(a_dtype.dtype),
                array=ArrayExpression(exact_number_dimensions=1),
                inlined=inlined(a_dtype.dtype),
                **QUANTITY_MAP[cls.quantity],
            )
        res.classes[0].attributes.update(slots)

        if "value" in res.classes[0].attributes:
            del res.classes[0].attributes["value"]
        return res


class DatasetAdapter(ClassAdapter):
    """
    Orchestrator class for datasets - calls the set of applicable mapping classes
    """

    TYPE: ClassVar[Type] = Dataset

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

        if self.debug:  # pragma: no cover - only used in development
            res = self._amend_debug(res, map)
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

    def _amend_debug(
        self, res: BuildResult, map: Optional[Type[DatasetMap]] = None
    ) -> BuildResult:  # pragma: no cover - only used in development
        map_name = "None" if map is None else map.__name__
        for cls in res.classes:
            cls.annotations["dataset_map"] = {"tag": "dataset_map", "value": map_name}
        for slot in res.slots:
            slot.annotations["dataset_map"] = {"tag": "dataset_map", "value": map_name}
        return res
