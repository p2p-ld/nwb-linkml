"""
Adapters to linkML classes
"""

from abc import abstractmethod
from typing import List, Optional, Type, TypeVar

from linkml_runtime.linkml_model import ClassDefinition, SlotDefinition
from pydantic import field_validator

from nwb_linkml.adapters.adapter import Adapter, BuildResult
from nwb_linkml.adapters.attribute import AttributeAdapter
from nwb_linkml.maps import QUANTITY_MAP
from nwb_linkml.maps.naming import camel_to_snake
from nwb_schema_language import Dataset, Group

T = TypeVar("T", bound=Type[Dataset] | Type[Group])
TI = TypeVar("TI", bound=Dataset | Group)


class ClassAdapter(Adapter):
    """
    Abstract adapter to class-like things in linkml, holds methods common to
    both DatasetAdapter and GroupAdapter
    """

    TYPE: T
    """
    The type that this adapter class handles
    """

    cls: TI
    parent: Optional["ClassAdapter"] = None

    @field_validator("cls", mode="before")
    @classmethod
    def cast_from_string(cls, value: str | TI) -> TI:
        """
        Cast from YAML string to desired class
        """
        if isinstance(value, str):
            from nwb_linkml.io.yaml import load_yaml

            value = load_yaml(value)
            value = cls.TYPE(**value)
        return value

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

        if self.debug:
            kwargs["annotations"] = {}
            kwargs["annotations"]["group_adapter"] = {
                "tag": "group_adapter",
                "value": "container_slot",
            }

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
        if cls.attributes is not None:
            results = [AttributeAdapter(cls=attr).build() for attr in cls.attributes]
            slots = [r.slots[0] for r in results]
            return slots
        else:
            return []

    def _get_full_name(self) -> str:
        """The full name of the object in the generated linkml

        Distinct from 'name' which is the thing that's used to define position in
        a hierarchical data setting.

        Combines names from ``parent``, if present, using ``"__"`` .
        Rather than concatenating the full series of names with ``__`` like

        * ``Parent``
        * ``Parent__child1``
        * ``Parent__child1__child2``

        we only keep the last parent, so

        * ``Parent``
        * ``Parent__child1``
        * ``child1__child2``

        The assumption is that a child name may not be unique, but the combination of
        a parent/child pair should be unique enough to avoid name shadowing without
        making humongous and cumbersome names.
        """
        if self.cls.neurodata_type_def:
            name = self.cls.neurodata_type_def
        elif self.cls.name is not None:
            # not necessarily a unique name, so we combine parent names
            name_parts = []
            if self.parent is not None:
                parent_name = self.parent._get_full_name().split("__")[-1]
                name_parts.append(parent_name)

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
        slot = SlotDefinition(
            name=self._get_slot_name(),
            description=self.cls.doc,
            range=self._get_full_name(),
            inlined=True,
            **QUANTITY_MAP[self.cls.quantity],
        )
        if self.debug:
            slot.annotations["group_adapter"] = {"tag": "group_adapter", "value": "self_slot"}
        return slot
