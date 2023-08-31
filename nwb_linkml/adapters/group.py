"""
Adapter for NWB groups to linkml Classes
"""
import pdb
from typing import List
from linkml_runtime.linkml_model import ClassDefinition, SlotDefinition

from nwb_schema_language import Dataset, Group, ReferenceDtype, CompoundDtype, DTypeType
from nwb_linkml.adapters.classes import ClassAdapter
from nwb_linkml.adapters.dataset import DatasetAdapter
from nwb_linkml.adapters.adapter import BuildResult
from nwb_linkml.maps import QUANTITY_MAP

class GroupAdapter(ClassAdapter):
    cls: Group

    def build(self) -> BuildResult:


        nested_res = self.build_subclasses()
        # we don't propagate slots up to the next level since they are meant for this
        # level (ie. a way to refer to our children)
        res = self.build_base(extra_attrs=nested_res.slots)
        # we do propagate classes tho
        res.classes.extend(nested_res.classes)

        return res

    def handle_children(self, children: List[Group]) -> BuildResult:
        """
        Make a special LinkML `children` slot that can
        have any number of the objects that are of `neurodata_type_inc` class

        Args:
            children (List[:class:`.Group`]): Child groups

        """
        child_slot = SlotDefinition(
            name='children',
            multivalued=True,
            any_of=[{'range': cls.neurodata_type_inc} for cls in children]
        )
        return BuildResult(slots=[child_slot])

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

        # group_res = BuildResult()
        # children = []
        # for group in self.cls.groups:
        #     if not group.name and \
        #         group.quantity == '*' and \
        #         group.neurodata_type_inc:
        #         children.append(group)
        #     else:
        #         group_adapter = GroupAdapter(cls=group, parent=self)
        #         group_res += group_adapter.build()
        #
        # group_res += self.handle_children(children)

        group_res = BuildResult()
        for group in self.cls.groups:
            group_adapter = GroupAdapter(cls=group, parent=self)
            group_res += group_adapter.build()

        res = dataset_res + group_res

        return res