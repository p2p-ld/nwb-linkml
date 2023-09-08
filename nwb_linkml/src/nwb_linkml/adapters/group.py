"""
Adapter for NWB groups to linkml Classes
"""
import pdb
from typing import List
from linkml_runtime.linkml_model import ClassDefinition, SlotDefinition

from nwb_schema_language import Dataset, Group, ReferenceDtype, CompoundDtype, DTypeType
from nwb_linkml.adapters.classes import ClassAdapter
from nwb_linkml.maps.naming import camel_to_snake
from nwb_linkml.adapters.dataset import DatasetAdapter
from nwb_linkml.adapters.adapter import BuildResult
from nwb_linkml.maps import QUANTITY_MAP

class GroupAdapter(ClassAdapter):
    cls: Group

    def build(self) -> BuildResult:
        # Handle container groups with only * quantity unnamed groups
        if len(self.cls.groups) > 0 and \
                all([self._check_if_container(g) for g in self.cls.groups]) and \
                self.parent is not None:
            return self.handle_container_group(self.cls)

        # handle if we are a terminal container group without making a new class
        if len(self.cls.groups) == 0 and \
            len(self.cls.datasets) == 0 and \
            self.cls.neurodata_type_inc is not None and \
            self.parent is not None:
            return self.handle_container_slot(self.cls)

        nested_res = self.build_subclasses()
        # we don't propagate slots up to the next level since they are meant for this
        # level (ie. a way to refer to our children)
        res = self.build_base(extra_attrs=nested_res.slots)
        # we do propagate classes tho
        res.classes.extend(nested_res.classes)

        return res

    def handle_container_group(self, cls: Group) -> BuildResult:
        """
        Make a special LinkML `children` slot that can
        have any number of the objects that are of `neurodata_type_inc` class

        Examples:
            - name: templates
              groups:
              - neurodata_type_inc: TimeSeries
                doc: TimeSeries objects containing template data of presented stimuli.
                quantity: '*'
              - neurodata_type_inc: Images
                doc: Images objects containing images of presented stimuli.
                quantity: '*'

        Args:
            children (List[:class:`.Group`]): Child groups

        """

        # don't build subgroups as their own classes, just make a slot
        # that can contain them
        if not self.cls.name:
            name = 'children'
        else:
            name = cls.name

        res = BuildResult(
            slots = [SlotDefinition(
                name=name,
                multivalued=True,
                description=cls.doc,
                any_of=[{'range': subcls.neurodata_type_inc} for subcls in cls.groups]
            )]
        )
        return res

    def handle_container_slot(self, cls:Group) -> BuildResult:
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
        if not self.cls.name:
            name = camel_to_snake(self.cls.neurodata_type_inc)
        else:
            name = cls.name

        return BuildResult(
            slots = [
                SlotDefinition(
                    name=name,
                    range=self.cls.neurodata_type_inc,
                    description=self.cls.doc,
                    **QUANTITY_MAP[cls.quantity]
                )
            ]
        )


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
            # if dset.name == 'timestamps':
            #     pdb.set_trace()
            dset_adapter = DatasetAdapter(cls=dset, parent=self)
            dataset_res += dset_adapter.build()

        # Actually i'm not sure we have to special case this, we could handle it in
        # i/o instead

        # Groups are a bit more complicated because they can also behave like
        # range declarations:
        # eg. a group can have multiple groups with `neurodata_type_inc`, no name, and quantity of *,
        # the group can then contain any number of groups of those included types as direct children

        group_res = BuildResult()

        for group in self.cls.groups:
            group_adapter = GroupAdapter(cls=group, parent=self)
            group_res += group_adapter.build()

        res = dataset_res + group_res

        return res

    def _check_if_container(self, group:Group) -> bool:
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
        if not group.name and \
            group.quantity in ('*','+') and \
            group.neurodata_type_inc:
            return True
        else:
            return False

