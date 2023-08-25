"""
Adapters to linkML classes
"""
import pdb
from typing import List, Optional
from nwb_schema_language import Dataset, Group, ReferenceDtype, CompoundDtype, DTypeType
from nwb_linkml.adapters.adapter import Adapter, BuildResult
from linkml_runtime.linkml_model import ClassDefinition, SlotDefinition
from nwb_linkml.maps import QUANTITY_MAP
from nwb_linkml.lang_elements import Arraylike

class ClassAdapter(Adapter):
    """
    Adapter to class-like things in linkml, including datasets and groups
    """
    cls: Dataset | Group
    parent: Optional['ClassAdapter'] = None

    def _get_full_name(self) -> str:
        """The full name of the object in the generated linkml

        Distinct from 'name' which is the thing that's often used in """
        if self.cls.neurodata_type_def:
            name = self.cls.neurodata_type_def
        elif self.cls.name is not None:
            # not necessarily a unique name, so we combine parent names
            name_parts = []
            if self.parent is not None:
                name_parts.append(self.parent._get_full_name())

            name_parts.append(self.cls.name)
            name = '_'.join(name_parts)
        elif self.cls.neurodata_type_inc is not None:
            # again, this is against the schema, but is common
            name = self.cls.neurodata_type_inc
        else:
            raise ValueError('Not sure what our name is!')


        return name

    def _get_name(self) -> str:
        """
        Get the "regular" name, which is used as the name of the attr

        Returns:

        """
        # return self._get_full_name()
        name = None
        if self.cls.neurodata_type_def:
            name = self.cls.neurodata_type_def
        elif self.cls.name is not None:
            # we do have a unique name
            name = self.cls.name
        elif self.cls.neurodata_type_inc:
            # group members can be anonymous? this violates the schema but is common
            name = self.cls.neurodata_type_inc

        if name is None:
            raise ValueError(f'Class has no name!: {self.cls}')

        return name

    def handle_arraylike(self, dataset: Dataset, name:Optional[str]=None) -> Optional[ClassDefinition]:
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
            return
        elif not all((dataset.dims, dataset.shape)):
            # need to have both if one is present!
            raise ValueError(f"A dataset needs both dims and shape to define an arraylike object")

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

        # now make slots for each of them
        slots = []
        for dims, shape in dims_shape:
            # if a dim is present in all possible combinations of dims, make it required
            if all([dims in inner_dim for inner_dim in dataset.dims]):
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

        name = '_'.join([name, 'Array'])

        array_class = ClassDefinition(
            name=name,
            is_a="Arraylike",
            attributes=slots
        )
        return array_class


    def handle_dtype(self, dtype: DTypeType | None) -> str:
        if isinstance(dtype, ReferenceDtype):
            return dtype.target_type
        elif dtype is None or dtype == []:
            # Some ill-defined datasets are "abstract" despite that not being in the schema language
            return 'AnyType'
        elif isinstance(dtype, list) and isinstance(dtype[0], CompoundDtype):
            # there is precisely one class that uses compound dtypes:
            # TimeSeriesReferenceVectorData
            # compoundDtypes are able to define a ragged table according to the schema
            # but are used in this single case equivalently to attributes.
            # so we'll... uh... treat them as slots.
             # TODO
            return 'AnyType'
            #raise NotImplementedError('got distracted, need to implement')

        else:
            # flat dtype
            return dtype

    def build_attrs(self, cls: Dataset | Group) -> List[SlotDefinition]:
        attrs = [
            SlotDefinition(
                name=attr.name,
                description=attr.doc,
                range=self.handle_dtype(attr.dtype),
            ) for attr in cls.attributes
        ]

        return attrs

    def build_subclasses(self, cls: Dataset | Group) -> BuildResult:
        """
        Build nested groups and datasets

        Create ClassDefinitions for each, but then also create SlotDefinitions that
        will be used as attributes linking the main class to the subclasses
        """
        # build and flatten nested classes
        nested_classes = [ClassAdapter(cls=dset, parent=self) for dset in cls.datasets]
        nested_classes.extend([ClassAdapter(cls=grp, parent=self) for grp in cls.groups])
        nested_res = BuildResult()
        for subclass in nested_classes:
            this_slot = SlotDefinition(
                name=subclass._get_name(),
                description=subclass.cls.doc,
                range=subclass._get_full_name(),
                **QUANTITY_MAP[subclass.cls.quantity]
            )
            nested_res.slots.append(this_slot)

            if subclass.cls.name is None and subclass.cls.neurodata_type_def is None:
                # anonymous group that's just an inc, we only need the slot since the class is defined elsewhere
                continue

            this_build = subclass.build()
            nested_res += this_build
        return nested_res


    def build(self) -> BuildResult:

        # Build this class
        if self.parent is not None:
            name = self._get_full_name()
        else:
            name = self._get_name()

        # Get vanilla top-level attributes
        attrs = self.build_attrs(self.cls)

        # unnest and build subclasses in datasets and groups
        if isinstance(self.cls, Group):
            # only groups have sub-datasets and sub-groups
            # split out the recursion step rather than making purely recursive because
            # top-level datasets and groups are handled differently - they have names,
            # and so we need to split out which things we unnest and which things
            # can just be slots because they are already defined without knowing about
            # the global state of the schema build.
            nested_res = self.build_subclasses(self.cls)
            attrs.extend(nested_res.slots)
        else:
            # must be a dataset
            nested_res = BuildResult()
            arraylike = self.handle_arraylike(self.cls, self._get_full_name())
            if arraylike:
                # make a slot for the arraylike class
                attrs.append(
                    SlotDefinition(
                        name='array',
                        range=arraylike.name
                    )
                )
                nested_res.classes.append(arraylike)


        cls = ClassDefinition(
            name = name,
            is_a = self.cls.neurodata_type_inc,
            description=self.cls.doc,
            attributes=attrs,
        )
        res = BuildResult(
            classes = [cls, *nested_res.classes]
        )

        return res