"""
Adapter for NWB datasets to linkml Classes
"""
from typing import Optional, List

from linkml_runtime.linkml_model import ClassDefinition, SlotDefinition
from pydantic import PrivateAttr

from nwb_schema_language import Dataset, ReferenceDtype, CompoundDtype, DTypeType
from nwb_linkml.adapters.classes import ClassAdapter
from nwb_linkml.adapters.adapter import BuildResult
from nwb_linkml.maps import QUANTITY_MAP

class DatasetAdapter(ClassAdapter):
    cls: Dataset

    _handlers: List[str] = PrivateAttr(default_factory=list)
    """Keep track of which handlers have been called"""


    def build(self) -> BuildResult:
        res = self.build_base()

        res = self.handle_arraylike(res, self.cls, self._get_full_name())
        res = self.handle_1d_vector(res)
        res = self.handle_listlike(res)
        res = self.handle_scalar(res)

        if len(self._handlers) > 1:
            raise RuntimeError(f"Only one handler should have been triggered, instead triggered {self._handlers}")

        return res

    def handle_scalar(self, res:BuildResult) -> BuildResult:

        # Simplify datasets that are just a single value
        if self.cls.neurodata_type_inc != 'VectorData' and \
             not self.cls.neurodata_type_inc and \
             not self.cls.attributes and \
             not self.cls.dims and \
             not self.cls.shape and \
             self.cls.name:
            self._handlers.append('scalar')
            # throw out the class that would have been made for us
            # we just need a slot
            this_slot = SlotDefinition(
                name=self.cls.name,
                description=self.cls.doc,
                range=self.handle_dtype(self.cls.dtype),
                **QUANTITY_MAP[self.cls.quantity]
            )
            res = BuildResult(slots = [this_slot])

        return res


    def handle_1d_vector(self, res: BuildResult) -> BuildResult:
        # handle the special case where `VectorData` is subclasssed without any dims or attributes
        # which just gets instantiated as a 1-d array in HDF5
        if self.cls.neurodata_type_inc == 'VectorData' and \
                not self.cls.dims and \
                not self.cls.shape and \
                not self.cls.attributes \
                and self.cls.name:
            self._handlers.append('1d_vector')
            this_slot = SlotDefinition(
                name=self.cls.name,
                description=self.cls.doc,
                range=self.handle_dtype(self.cls.dtype),
                multivalued=True
            )
            # No need to make a class for us, so we replace the existing build results
            res = BuildResult(slots=[this_slot])

        return res

    def handle_listlike(self, res:BuildResult) -> BuildResult:
        """
        Handle cases where the dataset is just a list of a specific type.

        Examples:

              datasets:
              - name: file_create_date
                dtype: isodatetime
                dims:
                - num_modifications
                shape:
                - null

        """
        if self.cls.name and ((
                # single-layer list
                not any([isinstance(dim, list) for dim in self.cls.dims]) and
                len(self.cls.dims) == 1
            ) or (
                # nested list
                all([isinstance(dim, list) for dim in self.cls.dims]) and
                len(self.cls.dims) == 1 and
                len(self.cls.dims[0]) == 1
            )):
            res = BuildResult(
                slots = [
                    SlotDefinition(
                        name = self.cls.name,
                        multivalued=True,
                        range=self.handle_dtype(self.cls.dtype),
                        description=self.cls.doc,
                        required=False if self.cls.quantity in ('*', '?') else True
                    )
                ]
            )
            return res
        else:
            return res


    def handle_arraylike(self, res: BuildResult, dataset: Dataset, name: Optional[str] = None) -> BuildResult:
        """
        Handling the

        - dims
        - shape
        - dtype

        fields as they are used in datasets. We'll use the :class:`.Arraylike` class to imitate them.

        Specifically:

        - Each slot within a subclass indicates a possible dimension.
        - Only dimensions that are present in all the dimension specifiers in the
          original schema are required.
        - Shape requirements are indicated using max/min cardinalities on the slot.
        - The arraylike object should be stored in the `array` slot on the containing class
          (since there are already properties named `data`)

        If any of `dims`, `shape`, or `dtype` are undefined, return `None`

        Args:
            dataset (:class:`nwb_schema_language.Dataset`): The dataset defining the arraylike
            name (str): If present, override the name of the class before appending _Array
                (we don't use _get_full_name here because we want to eventually decouple these functions from this adapter
                class, which is sort of a development crutch. Ideally all these methods would just work on base nwb schema language types)
        """
        if not any((dataset.dims, dataset.shape)):
            # none of the required properties are defined, that's fine.
            return res
        elif not all((dataset.dims, dataset.shape)):
            # need to have both if one is present!
            raise ValueError(f"A dataset needs both dims and shape to define an arraylike object")

        # Special cases
        if dataset.neurodata_type_inc == 'VectorData':
            # Handle this in `handle_vectorlike` instead
            return res

        # The schema language doesn't have a way of specifying a dataset/group is "abstract"
        # and yet hdmf-common says you don't need a dtype if the dataset is "abstract"
        # so....
        dtype = self.handle_dtype(dataset.dtype)

        # dims and shape are lists of lists. First we couple them
        # (so each dim has its corresponding shape)..
        # and then we take unique
        # (dicts are ordered by default in recent pythons,
        # while set() doesn't preserve order)
        dims_shape = []
        for inner_dim, inner_shape in zip(dataset.dims, dataset.shape):
            if isinstance(inner_dim, list):
                # list of lists
                dims_shape.extend([(dim, shape) for dim, shape in zip(inner_dim, inner_shape)])
            else:
                # single-layer list
                dims_shape.append((inner_dim, inner_shape))

        dims_shape = tuple(dict.fromkeys(dims_shape).keys())

        # if we only have one possible dimension, it's equivalent to a list, so we just return the slot
        if len(dims_shape) == 1 and self.parent:
            quantity = QUANTITY_MAP[dataset.quantity]
            slot = SlotDefinition(
                name=dataset.name,
                range=dtype,
                description=dataset.doc,
                required=quantity['required'],
                multivalued=True
            )
            res.classes[0].attributes.update({dataset.name: slot})
            self._handlers.append('arraylike-1d')
            return res

        # now make slots for each of them
        slots = []
        for dims, shape in dims_shape:
            # if a dim is present in all possible combinations of dims, make it required
            if all([dims in inner_dim for inner_dim in dataset.dims]):
                required = True
            # or if there is just a single list of possible dimensions
            elif not any([isinstance(inner_dim, list) for inner_dim in dataset.dims]):
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

        # and then the class is just a subclass of `Arraylike` (which is imported by default from `nwb.language.yaml`)
        if name:
            pass
        elif dataset.neurodata_type_def:
            name = dataset.neurodata_type_def
        elif dataset.name:
            name = dataset.name
        else:
            raise ValueError(f"Dataset has no name or type definition, what do call it?")

        name = '__'.join([name, 'Array'])

        array_class = ClassDefinition(
            name=name,
            is_a="Arraylike",
            attributes=slots
        )
        # make a slot for the arraylike class
        array_slot = SlotDefinition(
                name='array',
                range=array_class.name
            )

        res.classes.append(array_class)
        res.classes[0].attributes.update({'array': array_slot})
        #res.slots.append(array_slot)
        self._handlers.append('arraylike')

        return res
