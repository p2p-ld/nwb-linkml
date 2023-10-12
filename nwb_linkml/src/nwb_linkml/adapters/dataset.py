"""
Adapter for NWB datasets to linkml Classes
"""
import pdb
from typing import Optional, List
import warnings
from abc import abstractmethod

from linkml_runtime.linkml_model import ClassDefinition, SlotDefinition
from pydantic import PrivateAttr

from nwb_schema_language import Dataset, ReferenceDtype, CompoundDtype, DTypeType
from nwb_linkml.adapters.classes import ClassAdapter
from nwb_linkml.maps.naming import camel_to_snake
from nwb_linkml.maps.dtype import flat_to_linkml
from nwb_linkml.adapters.adapter import BuildResult
from nwb_linkml.maps import QUANTITY_MAP, Map

class DatasetMap(Map):

    @classmethod
    @abstractmethod
    def check(c, cls:Dataset) -> bool:
        pass # pragma: no cover

    @classmethod
    @abstractmethod
    def apply(c, res: BuildResult, cls:Dataset, name:Optional[str] = None) -> BuildResult:
        pass # pragma: no cover

class MapScalar(DatasetMap):
    """
    Datasets that are just a single value should just be a scalar value, not an array with size 1

    Replace the built class with
    """

    @classmethod
    def check(c, cls:Dataset) -> bool:
        if cls.neurodata_type_inc != 'VectorData' and \
                not cls.neurodata_type_inc and \
                not cls.attributes and \
                not cls.dims and \
                not cls.shape and \
                cls.name:
            return True
        else:
            return False

    @classmethod
    def apply(c, res: BuildResult, cls:Dataset, name:Optional[str] = None) -> BuildResult:
        this_slot = SlotDefinition(
            name=cls.name,
            description=cls.doc,
            range=ClassAdapter.handle_dtype(cls.dtype),
            **QUANTITY_MAP[cls.quantity]
        )
        res = BuildResult(slots=[this_slot])
        return res

class MapScalarAttributes(DatasetMap):
    """
    A scalar with attributes gets an additional slot "value" that contains the actual scalar
    value of this field
    """
    @classmethod
    def check(c, cls:Dataset) -> bool:
        if cls.neurodata_type_inc != 'VectorData' and \
             not cls.neurodata_type_inc and \
             cls.attributes and \
             not cls.dims and \
             not cls.shape and \
             cls.name:
            return True
        else:
            return False

    @classmethod
    def apply(c, res: BuildResult, cls:Dataset, name:Optional[str] = None) -> BuildResult:
        value_slot = SlotDefinition(
            name='value',
            range=ClassAdapter.handle_dtype(cls.dtype),
            required=True
        )
        res.classes[0].attributes['value'] = value_slot
        return res

class MapListlike(DatasetMap):
    """
    Datasets that refer to other datasets (that handle their own arrays)
    """
    @classmethod
    def check(c, cls:Dataset) -> bool:
        dtype = ClassAdapter.handle_dtype(cls.dtype)
        if is_1d(cls) and dtype != 'AnyType' and dtype not in flat_to_linkml.keys():
            return True
        else:
            return False

    @classmethod
    def apply(c, res: BuildResult, cls:Dataset, name:Optional[str] = None) -> BuildResult:
        dtype = camel_to_snake(ClassAdapter.handle_dtype(cls.dtype))
        slot = SlotDefinition(
            name=dtype,
            multivalued=True,
            range=ClassAdapter.handle_dtype(cls.dtype),
            description=cls.doc,
            required=False if cls.quantity in ('*', '?') else True
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
    def check(c, cls:Dataset) -> bool:
        if cls.name and all([cls.dims, cls.shape]) and not has_attrs(cls):
            return True
        else:
            return False

    @classmethod
    def apply(c, res: BuildResult, cls:Dataset, name:Optional[str] = None) -> BuildResult:
        array_class = make_arraylike(cls, name)
        name = camel_to_snake(cls.name)
        res = BuildResult(
            slots=[
                SlotDefinition(
                    name=name,
                    multivalued=False,
                    range=array_class.name,
                    description=cls.doc,
                    required=False if cls.quantity in ('*', '?') else True
                )
            ],
            classes=[array_class]
        )
        return res

class MapArrayLikeAttributes(DatasetMap):
    """
    The most general case - treat everything that isn't handled by one of the special cases
    as an array!

    Specifically, we make an ``Arraylike`` class such that:

    - Each slot within a subclass indicates a possible dimension.
    - Only dimensions that are present in all the dimension specifiers in the
      original schema are required.
    - Shape requirements are indicated using max/min cardinalities on the slot.
    - The arraylike object should be stored in the `array` slot on the containing class
      (since there are already properties named `data`)
    """
    NEEDS_NAME = True

    @classmethod
    def check(c, cls:Dataset) -> bool:
        dtype = ClassAdapter.handle_dtype(cls.dtype)
        if all([cls.dims, cls.shape]) and \
            cls.neurodata_type_inc != 'VectorData' and \
            has_attrs(cls) and \
            (dtype == 'AnyType' or dtype in flat_to_linkml):
            return True

        else:
            return False

    @classmethod
    def apply(c, res: BuildResult, cls:Dataset, name:Optional[str] = None) -> BuildResult:
        array_class = make_arraylike(cls, name)
        # make a slot for the arraylike class
        array_slot = SlotDefinition(
            name='array',
            range=array_class.name
        )

        res.classes.append(array_class)
        res.classes[0].attributes.update({'array': array_slot})
        return res

def make_arraylike(cls:Dataset, name:Optional[str] = None) -> ClassDefinition:
    # The schema language doesn't have a way of specifying a dataset/group is "abstract"
    # and yet hdmf-common says you don't need a dtype if the dataset is "abstract"
    # so....
    dtype = ClassAdapter.handle_dtype(cls.dtype)

    # dims and shape are lists of lists. First we couple them
    # (so each dim has its corresponding shape)..
    # and then we take unique
    # (dicts are ordered by default in recent pythons,
    # while set() doesn't preserve order)
    dims_shape = []
    for inner_dim, inner_shape in zip(cls.dims, cls.shape):
        if isinstance(inner_dim, list):
            # list of lists
            dims_shape.extend([(dim, shape) for dim, shape in zip(inner_dim, inner_shape)])
        elif isinstance(inner_shape, list):
            # Some badly formatted schema will have the shape be a LoL but the dims won't be...
            dims_shape.extend([(inner_dim, shape) for shape in inner_shape])
        else:
            # single-layer list
            dims_shape.append((inner_dim, inner_shape))

    dims_shape = tuple(dict.fromkeys(dims_shape).keys())

    # --------------------------------------------------
    # SPECIAL CASE - allen institute's ndx-aibs-ecephys.extension
    # confuses "dims" with "shape" , eg shape = [None], dims = [3].
    # So we hardcode that here...
    # --------------------------------------------------
    if len(dims_shape) == 1 and isinstance(dims_shape[0][0], int) and dims_shape[0][1] is None:
        dims_shape = (('dim', dims_shape[0][0]),)

    # now make slots for each of them
    slots = []
    for dims, shape in dims_shape:
        # if there is just a single list of possible dimensions, it's required
        if not any([isinstance(inner_dim, list) for inner_dim in cls.dims]):
            required = True
        # if a dim is present in all possible combinations of dims, make it required
        elif all([dims in inner_dim for inner_dim in cls.dims]):
            required = True
        else:
            required = False

        # use cardinality to do shape
        if shape == 'null':
            cardinality = None
        else:
            cardinality = shape

        slots.append(SlotDefinition(
            name=dims,
            required=required,
            maximum_cardinality=cardinality,
            minimum_cardinality=cardinality,
            range=dtype
        ))

    # and then the class is just a subclass of `Arraylist` (which is imported by default from `nwb.language.yaml`)
    if name:
        pass
    elif cls.neurodata_type_def:
        name = cls.neurodata_type_def
    elif cls.name:
        name = cls.name
    else:
        raise ValueError(f"Dataset has no name or type definition, what do call it?")

    name = '__'.join([name, 'Array'])

    array_class = ClassDefinition(
        name=name,
        is_a="Arraylike",
        attributes=slots
    )
    return array_class

def is_1d(cls:Dataset) -> bool:
    if (
            not any([isinstance(dim, list) for dim in cls.dims]) and
            len(cls.dims) == 1
        ) or (  # nested list
            all([isinstance(dim, list) for dim in cls.dims]) and
            len(cls.dims) == 1 and
            len(cls.dims[0]) == 1
        ):
        return True
    else:
        return False

def has_attrs(cls:Dataset) -> bool:
    if len(cls.attributes) > 0 and \
        all([not a.value for a in cls.attributes]):
        return True
    else:
        return False

# --------------------------------------------------
# DynamicTable special cases
# --------------------------------------------------

class Map1DVector(DatasetMap):
    """
    ``VectorData`` is subclassed with a name but without dims or attributes, treat this as a normal 1D array
    slot that replaces any class that would be built for this
    """
    @classmethod
    def check(c, cls:Dataset) -> bool:
        if cls.neurodata_type_inc == 'VectorData' and \
                not cls.dims and \
                not cls.shape and \
                not cls.attributes \
                and cls.name:
            return True
        else:
            return False

    @classmethod
    def apply(c, res: BuildResult, cls:Dataset, name:Optional[str] = None) -> BuildResult:
        this_slot = SlotDefinition(
            name=cls.name,
            description=cls.doc,
            range=ClassAdapter.handle_dtype(cls.dtype),
            multivalued=True
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
    def check(c, cls:Dataset) -> bool:
        if cls.name is None and \
            cls.neurodata_type_def is None and \
            cls.neurodata_type_inc and \
            cls.quantity in ('*', '+'):
            #cls.neurodata_type_inc in ('VectorIndex', 'VectorData') and \
            return True
        else:
            return False

    @classmethod
    def apply(c, res: BuildResult, cls:Dataset, name:Optional[str] = None) -> BuildResult:
        this_slot = SlotDefinition(
            name=camel_to_snake(cls.neurodata_type_inc),
            description=cls.doc,
            range=cls.neurodata_type_inc,
            **QUANTITY_MAP[cls.quantity]
        )
        # No need to make a class for us, so we replace the existing build results
        res = BuildResult(slots=[this_slot])
        return res




class DatasetAdapter(ClassAdapter):
    cls: Dataset

    def build(self) -> BuildResult:
        res = self.build_base()

        # find a map to use
        matches = [m for m in DatasetMap.__subclasses__() if m.check(self.cls)]

        if len(matches) > 1: # pragma: no cover
            raise RuntimeError(f"Only one map should apply to a dataset, you need to refactor the maps! Got maps: {matches}")

        # apply matching maps
        for m in matches:
            res = m.apply(res, self.cls, self._get_full_name())

        return res

