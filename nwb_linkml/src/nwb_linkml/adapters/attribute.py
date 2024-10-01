"""
Adapters for attribute types
"""

from abc import abstractmethod
from typing import ClassVar, Optional, Type, TypedDict

from linkml_runtime.linkml_model.meta import SlotDefinition

from nwb_linkml.adapters.adapter import Adapter, BuildResult, defaults, is_1d
from nwb_linkml.adapters.array import ArrayAdapter
from nwb_linkml.maps import Map
from nwb_linkml.maps.dtype import handle_dtype, inlined
from nwb_schema_language import Attribute


class AttrDefaults(TypedDict):
    """Default fields for an attribute"""

    equals_string: str | None
    equals_number: float | int | None
    ifabsent: str | None


class AttributeMap(Map):
    """Base class for attribute mapping transformations :)"""

    @classmethod
    @abstractmethod
    def check(cls, attr: Attribute) -> bool:
        """
        Check if this map applies
        """
        pass  # pragma: no cover

    @classmethod
    @abstractmethod
    def apply(
        cls, attr: Attribute, res: Optional[BuildResult] = None, name: Optional[str] = None
    ) -> BuildResult:
        """
        Apply this mapping
        """
        pass  # pragma: no cover


class MapScalar(AttributeMap):
    """
    Map a simple scalar value
    """

    @classmethod
    def check(cls, attr: Attribute) -> bool:
        """
        Check if we are a scalar value!
        """
        return not attr.dims and not attr.shape

    @classmethod
    def apply(cls, attr: Attribute, res: Optional[BuildResult] = None) -> BuildResult:
        """
        Make a slot for us!
        """
        slot = SlotDefinition(
            name=attr.name,
            range=handle_dtype(attr.dtype),
            description=attr.doc,
            required=attr.required,
            inlined=inlined(attr.dtype),
            **defaults(attr),
        )
        return BuildResult(slots=[slot])


class MapArray(AttributeMap):
    """
    Map an array value!
    """

    @classmethod
    def check(cls, attr: Attribute) -> bool:
        """
        Check that we have some array specification!
        """
        return bool(attr.dims) or attr.shape

    @classmethod
    def apply(cls, attr: Attribute, res: Optional[BuildResult] = None) -> BuildResult:
        """
        Make a slot with an array expression!

        If we're just a 1D array, use a list (set multivalued: true).
        If more than that, make an array descriptor
        """
        expressions = {}
        multivalued = False
        if is_1d(attr):
            multivalued = True
        else:
            # ---------------------------------
            # SPECIAL CASE: Some old versions of HDMF don't have ``dims``, only shape
            # ---------------------------------
            shape = attr.shape
            dims = attr.dims
            if shape and not dims:
                dims = ["null"] * len(shape)

            array_adapter = ArrayAdapter(dims, shape)
            expressions = array_adapter.make_slot()

        slot = SlotDefinition(
            name=attr.name,
            range=handle_dtype(attr.dtype),
            multivalued=multivalued,
            description=attr.doc,
            required=attr.required,
            inlined=inlined(attr.dtype),
            **expressions,
            **defaults(attr),
        )
        return BuildResult(slots=[slot])


class AttributeAdapter(Adapter):
    """
    Create slot definitions from nwb schema language attributes
    """

    TYPE: ClassVar[Type] = Attribute

    cls: Attribute

    def build(self) -> "BuildResult":
        """
        Build the slot definitions, every attribute should have a map.
        """
        map = self.match()
        res = map.apply(self.cls)
        if self.debug:  # pragma: no cover - only used in development
            res = self._amend_debug(res, map)
        return res

    def match(self) -> Optional[Type[AttributeMap]]:
        """
        Find the map class that applies to this attribute

        Returns:
            :class:`.AttributeMap`

        Raises:
            RuntimeError - if more than one map matches
        """
        # find a map to use
        matches = [m for m in AttributeMap.__subclasses__() if m.check(self.cls)]

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
        self, res: BuildResult, map: Optional[Type[AttributeMap]] = None
    ) -> BuildResult:  # pragma: no cover - only used in development
        map_name = "None" if map is None else map.__name__
        for cls in res.classes:
            cls.annotations["attribute_map"] = {"tag": "attribute_map", "value": map_name}
        for slot in res.slots:
            slot.annotations["attribute_map"] = {"tag": "attribute_map", "value": map_name}
        return res
