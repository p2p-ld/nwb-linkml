"""
Adapters to linkML classes
"""

from abc import abstractmethod
from typing import List, Optional

from linkml_runtime.linkml_model import ClassDefinition, SlotDefinition

from nwb_linkml.adapters.adapter import Adapter, BuildResult
from nwb_linkml.maps import QUANTITY_MAP
from nwb_linkml.maps.naming import camel_to_snake
from nwb_schema_language import CompoundDtype, Dataset, DTypeType, Group, ReferenceDtype


class ClassAdapter(Adapter):
    """
    Abstract adapter to class-like things in linkml, holds methods common to
    both DatasetAdapter and GroupAdapter
    """

    cls: Dataset | Group
    parent: Optional["ClassAdapter"] = None

    @abstractmethod
    def build(self) -> BuildResult:
        """
        Make this abstract so it can't be instantiated directly.

        Subclasses call :meth:`.build_base` to get the basics true of both groups and datasets
        """

    def build_base(self, extra_attrs: Optional[List[SlotDefinition]] = None) -> BuildResult:
        """
        Build the basic class and attributes before adding any specific
        modifications for groups or datasets.

        The main distinction in behavior for this method is whether this class has a parent class -
        ie this is one of the anonymous nested child datasets or groups within another group.

        If the class has no parent, then...

        * Its name is inferred from its `neurodata_type_def`,  fixed name, or
          `neurodata_type_inc` in that order
        * It is just built as normal class!
        * It will be indicated as a ``tree_root`` (which will primarily be used to invert the
          translation for write operations)

        If the class has a parent, then...

        * If it has a `neurodata_type_def` or `inc`,  that will be used as its name,
          otherwise concatenate `parent__child`,
          eg. ``TimeSeries__TimeSeriesData``
        * A slot will also be made and returned with the BuildResult,
          which the parent will then have as one of its attributes.
        """

        # Build this class
        kwargs = {}
        if self.parent is not None:
            kwargs["name"] = self._get_full_name()
        else:
            kwargs["name"] = self._get_attr_name()
            kwargs["tree_root"] = True

        # Attributes
        name_slot = self.build_name_slot()
        kwargs["attributes"] = [name_slot]
        # Get vanilla top-level attributes
        kwargs["attributes"].extend(self.build_attrs(self.cls))

        if extra_attrs is not None:
            if isinstance(extra_attrs, SlotDefinition):
                extra_attrs = [extra_attrs]
            kwargs["attributes"].extend(extra_attrs)
        kwargs["description"] = self.cls.doc
        kwargs["is_a"] = self.cls.neurodata_type_inc

        cls = ClassDefinition(**kwargs)

        slots = []
        if self.parent is not None:
            slots.append(self.build_self_slot())

        res = BuildResult(classes=[cls], slots=slots)

        return res

    def build_attrs(self, cls: Dataset | Group) -> List[SlotDefinition]:
        """
        Pack the class attributes into a list of SlotDefinitions

        Args:
            cls: (:class:`.Dataset` | :class:`.Group`): Class to pack

        Returns:
            list[:class:`.SlotDefinition`]
        """
        attrs = [
            SlotDefinition(
                name=attr.name,
                description=attr.doc,
                range=self.handle_dtype(attr.dtype),
            )
            for attr in cls.attributes
        ]

        return attrs

    def _get_full_name(self) -> str:
        """The full name of the object in the generated linkml

        Distinct from 'name' which is the thing that's used to define position in
        a hierarchical data setting
        """
        if self.cls.neurodata_type_def:
            name = self.cls.neurodata_type_def
        elif self.cls.name is not None:
            # not necessarily a unique name, so we combine parent names
            name_parts = []
            if self.parent is not None:
                name_parts.append(self.parent._get_full_name())

            name_parts.append(self.cls.name)
            name = "__".join(name_parts)

        elif self.cls.neurodata_type_inc is not None:
            # again, this is against the schema, but is common
            name = self.cls.neurodata_type_inc
        else:
            raise ValueError("Not sure what our name is!")

        return name

    def _get_attr_name(self) -> str:
        """
        Get the name to use as the attribute name,
        again distinct from the actual name of the instantiated object
        """
        if self.cls.neurodata_type_def is not None:
            name = self.cls.neurodata_type_def
        elif self.cls.name is not None:
            name = self.cls.name
        elif self.cls.neurodata_type_inc is not None:
            name = self.cls.neurodata_type_inc
        else:
            raise ValueError(f"Class has no name!: {self.cls}")

        return name

    def _get_slot_name(self) -> str:
        """
        Get the name to use as the name when this is a subclass used as a slot,
        used to dodge name overlaps by snake-casing!
        again distinct from the actual name of the instantiated object
        """
        if self.cls.neurodata_type_def:
            name = camel_to_snake(self.cls.neurodata_type_def)
        elif self.cls.name is not None:
            name = self.cls.name
        elif self.cls.neurodata_type_inc:
            name = camel_to_snake(self.cls.neurodata_type_inc)
        else:
            raise ValueError(f"Class has no name!: {self.cls}")

        return name

    @classmethod
    def handle_dtype(cls, dtype: DTypeType | None) -> str:
        """
        Get the string form of a dtype

        Args:
            dtype (:class:`.DTypeType`): Dtype to stringify

        Returns:
            str
        """
        if isinstance(dtype, ReferenceDtype):
            return dtype.target_type
        elif dtype is None or dtype == []:
            # Some ill-defined datasets are "abstract" despite that not being in the schema language
            return "AnyType"
        elif isinstance(dtype, list) and isinstance(dtype[0], CompoundDtype):
            # there is precisely one class that uses compound dtypes:
            # TimeSeriesReferenceVectorData
            # compoundDtypes are able to define a ragged table according to the schema
            # but are used in this single case equivalently to attributes.
            # so we'll... uh... treat them as slots.
            # TODO
            return "AnyType"

        else:
            # flat dtype
            return dtype

    def build_name_slot(self) -> SlotDefinition:
        """
        If a class has a name, then that name should be a slot with a
        fixed value.

        If a class does not have a name, then name should be a required attribute

        References:
            https://github.com/NeurodataWithoutBorders/nwb-schema/issues/552#issuecomment-1700319001

        Returns:

        """
        if self.cls.name or self.cls.default_name:
            if self.cls.name:
                # name overrides default_name
                name = self.cls.name
                equals_string = name
            else:
                name = self.cls.default_name
                equals_string = None

            name_slot = SlotDefinition(
                name="name",
                required=True,
                ifabsent=f"string({name})",
                equals_string=equals_string,
                range="string",
                identifier=True,
            )
        else:
            name_slot = SlotDefinition(name="name", required=True, range="string", identifier=True)
        return name_slot

    def build_self_slot(self) -> SlotDefinition:
        """
        If we are a child class, we make a slot so our parent can refer to us
        """
        return SlotDefinition(
            name=self._get_slot_name(),
            description=self.cls.doc,
            range=self._get_full_name(),
            **QUANTITY_MAP[self.cls.quantity],
        )
