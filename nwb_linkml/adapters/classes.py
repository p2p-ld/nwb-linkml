"""
Adapters to linkML classes
"""
import pdb
from typing import List, Optional
from nwb_schema_language import Dataset, Group, ReferenceDtype, DTypeType
from nwb_linkml.adapters.adapter import Adapter, BuildResult
from linkml_runtime.linkml_model import ClassDefinition, SlotDefinition


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

    def handle_dtype(self, dtype: DTypeType):
        if isinstance(dtype, ReferenceDtype):
            return dtype.target_type
        else:
            return dtype

    def build_attrs(self, cls: Dataset | Group) -> List[SlotDefinition]:
        attrs = [
            SlotDefinition(
                name=attr.name,
                description=attr.doc,
                range=self.handle_dtype(attr.dtype)
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
                range=subclass._get_full_name()
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
        # if name == 'TimeSeries':
        #     pdb.set_trace()

        # Get vanilla top-level attributes
        attrs = self.build_attrs(self.cls)

        # unnest and build subclasses in datasets and groups
        if isinstance(self.cls, Group):
            # only groups have sub-datasets and sub-groups
            nested_res = self.build_subclasses(self.cls)
            attrs.extend(nested_res.slots)
        else:
            nested_res = BuildResult()

        cls = ClassDefinition(
            name = name,
            is_a = self.cls.neurodata_type_inc,
            description=self.cls.doc,
            attributes=attrs
        )
        res = BuildResult(
            classes = [cls, *nested_res.classes]
        )

        return res