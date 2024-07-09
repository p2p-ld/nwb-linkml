"""
Generator for array ranges from nwb dims/ranges
"""

import warnings
from typing import Dict, List, Literal, NamedTuple, Optional, Union

from linkml_runtime.linkml_model.meta import (
    ArrayExpression,
    DimensionExpression,
)

from nwb_linkml.maps.naming import snake_case
from nwb_linkml.types.nwb import DIMS_TYPE, SHAPE_TYPE


class Dimension(NamedTuple):
    """A single dimension/shape pair"""

    dims: Optional[str] = None
    shape: [Optional[int]] = None


class Shape(tuple[Dimension]):
    """
    A collection of :class:`.Dimension` tuples representing one of the nested layers in
    a dims/shape spec
    """


class ArrayAdapter:
    """
    Adapter that generates a :class:`.ArrayExpression` (or set of them)
    from a NWB dims/shape declaration
    """

    def __init__(self, dims: DIMS_TYPE, shape: SHAPE_TYPE):
        self.dims = dims
        self.shape = shape

    def pivot_dims(
        self, dims: Optional[DIMS_TYPE] = None, shape: Optional[SHAPE_TYPE] = None
    ) -> List[Shape]:
        """
        Pivot from a list of dims and a list of shape to a list of (dim, shape) tuples
        """
        if dims is None:
            dims = self.dims
        if shape is None:
            shape = self.shape

        if len(dims) != len(shape):
            warnings.warn(
                f"dims ({len(dims)} and shape ({len(shape)}) are not the same length!!! "
                "Your schema is formatted badly",
                stacklevel=1,
            )

        def _iter_dims(dims: DIMS_TYPE, shape: SHAPE_TYPE) -> List[Shape] | Shape:
            shapes = []
            for inner_dim, inner_shape in zip(dims, shape):
                if isinstance(inner_shape, list):
                    # list of lists

                    # some badly formatted schema will have shape be a LoL but only provide a single
                    # set of names at the top level. Best we can do is repeat it and pray
                    # that it is the same size as the longest dims
                    if not isinstance(inner_dim, list):
                        inner_dim = dims

                    shapes.append(_iter_dims(inner_dim, inner_shape))
                else:
                    # single-layer list
                    shapes.append(Dimension(inner_dim, inner_shape))
            if all([isinstance(x, Dimension) for x in shapes]):
                shapes = Shape(shapes)
            return shapes

        shapes = _iter_dims(dims, shape)

        if not all([isinstance(x, Shape) for x in shapes]):
            # single-layered spec, wrap it
            shapes = [shapes]

        return shapes

    def make_expression(self, shape: Shape) -> ArrayExpression:
        """
        Create the corresponding array specification from a shape
        """
        dims = [
            DimensionExpression(alias=snake_case(dim.dims), exact_cardinality=dim.shape)
            for dim in shape
        ]
        return ArrayExpression(dimensions=dims)

    def make(self) -> List[ArrayExpression]:
        """Create an array specification from self.dims and self.shape"""
        shapes = self.pivot_dims()
        expressions = [self.make_expression(shape) for shape in shapes]
        return expressions

    def make_slot(
        self,
    ) -> Union[
        Dict[Literal["array"], ArrayExpression],
        Dict[Literal["any_of"], Dict[Literal["array"], List[ArrayExpression]]],
    ]:
        """
        Make the array expressions in a dict form that can be **kwarg'd into a SlotDefinition,
        taking into account needing to use ``any_of`` for multiple array range specifications.
        """
        expressions = self.make()
        if len(expressions) == 1:
            return {"array": expressions[0]}
        else:
            return {"any_of": [{"array": expression} for expression in expressions]}
