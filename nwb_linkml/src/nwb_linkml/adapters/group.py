"""
Adapter for NWB groups to linkml Classes
"""

from typing import List, Type

from linkml_runtime.linkml_model import SlotDefinition

from nwb_linkml.adapters.adapter import BuildResult
from nwb_linkml.adapters.classes import ClassAdapter
from nwb_linkml.adapters.dataset import DatasetAdapter
from nwb_linkml.maps import QUANTITY_MAP
from nwb_linkml.maps.naming import camel_to_snake
from nwb_schema_language import Group


class GroupAdapter(ClassAdapter):
    """
    Adapt NWB Groups to LinkML Classes
    """

    TYPE: Type = Group

    cls: Group

    def build(self) -> BuildResult:
        """
        Do the translation, yielding the BuildResult
        """
        # Handle container groups with only * quantity unnamed groups
        if (
            len(self.cls.groups) > 0
            and not self.cls.links
            and all([self._check_if_container(g) for g in self.cls.groups])
        ):  # and \
            # self.parent is not None:
            return self.handle_container_group(self.cls)

        # handle if we are a terminal container group without making a new class
        if (
            len(self.cls.groups) == 0
            and len(self.cls.datasets) == 0
            and self.cls.neurodata_type_inc is not None
            and self.parent is not None
        ):
            return self.handle_container_slot(self.cls)

        nested_res = self.build_subclasses()
        # add links
        links = self.build_links()

        # we don't propagate slots up to the next level since they are meant for this
        # level (ie. a way to refer to our children)
        res = self.build_base(extra_attrs=nested_res.slots + links)
        # we do propagate classes tho
        res.classes.extend(nested_res.classes)

        return res

    def build_links(self) -> List[SlotDefinition]:
        """
        Build links specified in the ``links`` field as slots that refer to other
        classes, with an additional annotation specifying that they are in fact links.

        Link slots can take either the object itself or the path to that object in the
        file hierarchy as a string.
        """
        if not self.cls.links:
            return []

        annotations = [{"tag": "source_type", "value": "link"}]

        if self.debug:  # pragma: no cover - only used in development
            annotations.append({"tag": "group_adapter", "value": "link"})

        slots = [
            SlotDefinition(
                name=link.name,
                any_of=[{"range": link.target_type}, {"range": "string"}],
                annotations=annotations,
                inlined=True,
                **QUANTITY_MAP[link.quantity],
            )
            for link in self.cls.links
        ]
        return slots

    def handle_container_group(self, cls: Group) -> BuildResult:
        """
        Make a special LinkML `value` slot that can
        have any number of the objects that are of `neurodata_type_inc` class

        Examples:

            .. code-block:: yaml

                - name: templates
                  groups:
                  - neurodata_type_inc: TimeSeries
                    doc: TimeSeries objects containing template data of presented stimuli.
                    quantity: '*'
                  - neurodata_type_inc: Images
                    doc: Images objects containing images of presented stimuli.
                    quantity: '*'

        """

        # don't build subgroups as their own classes, just make a slot
        # that can contain them
        name = cls.name if self.cls.name else "value"

        slot = SlotDefinition(
            name=name,
            multivalued=True,
            any_of=[{"range": subcls.neurodata_type_inc} for subcls in cls.groups],
            inlined=True,
            inlined_as_list=False,
        )

        if self.debug:  # pragma: no cover - only used in development
            slot.annotations["group_adapter"] = {"tag": "group_adapter", "value": "container_group"}

        if self.parent is not None:
            # if we  have a parent,
            # just return the slot itself without the class
            slot.description = cls.doc
            return BuildResult(slots=[slot])
        else:
            # We are a top-level container class like ProcessingModule
            base = self.build_base()
            # remove all the attributes and replace with child slot
            base.classes[0].attributes = [slot]
            return base

    def handle_container_slot(self, cls: Group) -> BuildResult:
        """
        Handle subgroups that contain arbitrarily numbered classes,

        eg. *each* of the groups in

        Examples:
            - name: trials
              neurodata_type_inc: TimeIntervals
              doc: Repeated experimental events that have a logical grouping.
              quantity: '?'
            - name: invalid_times
              neurodata_type_inc: TimeIntervals
              doc: Time intervals that should be removed from analysis.
              quantity: '?'
            - neurodata_type_inc: TimeIntervals
              doc: Optional additional table(s) for describing other experimental time intervals.
              quantity: '*'
        """
        name = camel_to_snake(self.cls.neurodata_type_inc) if not self.cls.name else cls.name

        slot = SlotDefinition(
            name=name,
            range=self.cls.neurodata_type_inc,
            description=self.cls.doc,
            inlined=True,
            inlined_as_list=False,
            **QUANTITY_MAP[cls.quantity],
        )

        if self.debug:  # pragma: no cover - only used in development
            slot.annotations["group_adapter"] = {"tag": "group_adapter", "value": "container_slot"}

        return BuildResult(slots=[slot])

    def build_subclasses(self) -> BuildResult:
        """
        Build nested groups and datasets

        Create ClassDefinitions for each, but then also create SlotDefinitions that
        will be used as attributes linking the main class to the subclasses
        """
        # Datasets are simple, they are terminal classes, and all logic
        # for creating slots vs. classes is handled by the adapter class
        dataset_res = BuildResult()
        for dset in self.cls.datasets:
            dset_adapter = DatasetAdapter(cls=dset, parent=self)
            dataset_res += dset_adapter.build()

        group_res = BuildResult()

        for group in self.cls.groups:
            group_adapter = GroupAdapter(cls=group, parent=self)
            group_res += group_adapter.build()

        res = dataset_res + group_res

        return res

    def build_self_slot(self) -> SlotDefinition:
        """
        If we are a child class, we make a slot so our parent can refer to us

        Groups are a bit more complicated because they can also behave like
        range declarations:
        eg. a group can have multiple groups with `neurodata_type_inc`, no name,
        and quantity of *,
        the group can then contain any number of groups of those included types as direct children

        We make sure that we're inlined as a dict so our parent class can refer to us like::

            parent.{slot_name}[{name}] = self

        """
        slot = SlotDefinition(
            name=self._get_slot_name(),
            description=self.cls.doc,
            range=self._get_full_name(),
            inlined=True,
            inlined_as_list=True,
            **QUANTITY_MAP[self.cls.quantity],
        )
        if self.debug:  # pragma: no cover - only used in development
            slot.annotations["group_adapter"] = {"tag": "group_adapter", "value": "container_slot"}
        return slot

    def _check_if_container(self, group: Group) -> bool:
        """
        Check if a given subgroup is a container subgroup,

        ie. whether it's used to indicate a possible type for a child, as in:

        - name: templates
          groups:
          - neurodata_type_inc: TimeSeries
            doc: TimeSeries objects containing template data of presented stimuli.
            quantity: '*'
          - neurodata_type_inc: Images
            doc: Images objects containing images of presented stimuli.
            quantity: '*'
        """
        return not group.name and group.quantity in ("*", "+") and group.neurodata_type_inc
