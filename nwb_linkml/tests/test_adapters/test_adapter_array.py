import pytest

from nwb_linkml.adapters.array import ArrayAdapter, Dimension, Shape
from nwb_linkml.types.nwb import DIMS_TYPE, SHAPE_TYPE

# pytest.param([['dim1'], ['dim1', 'dim2'], ['dim1', 'dim3']], [[1], [1, 2], [1, 2]], [],
#              id='multi shape inconsistent dims'),
# pytest.param([['dim1'], ['dim1', 'dim2'], ['dim1', 'dim2']], [[1], [1, 2], [1, 3]], [],
#              id='multi shape inconsistent shape'),
# pytest.param([['dim1'], ['dim1', 'dim2'], ['dim1', 'dim3']], [[1], [1, 2], [1, 3]], [],
#              id='multi shape inconsistent both'),


@pytest.mark.parametrize(
    "dims,shape,expected",
    [
        pytest.param(
            ["dim1", "dim2", "dim3"],
            [1, 2, 3],
            [
                Shape(
                    [
                        Dimension(dims="dim1", shape=1),
                        Dimension(dims="dim2", shape=2),
                        Dimension(dims="dim3", shape=3),
                    ]
                )
            ],
            id="single shape",
        ),
        pytest.param(
            [["dim1"], ["dim1", "dim2"], ["dim1", "dim2", "dim3"]],
            [[1], [1, 2], [1, 2, 3]],
            [
                Shape(
                    [Dimension(dims="dim1", shape=1)],
                ),
                Shape((Dimension(dims="dim1", shape=1), Dimension(dims="dim2", shape=2))),
                Shape(
                    (
                        Dimension(dims="dim1", shape=1),
                        Dimension(dims="dim2", shape=2),
                        Dimension(dims="dim3", shape=3),
                    )
                ),
            ],
            id="multi shape",
        ),
        pytest.param(
            ["dim1", "dim2", "dim3"],
            [[1], [1, 2], [1, 2, 3]],
            [
                Shape([Dimension(dims="dim1", shape=1)]),
                Shape((Dimension(dims="dim1", shape=1), Dimension(dims="dim2", shape=2))),
                Shape(
                    (
                        Dimension(dims="dim1", shape=1),
                        Dimension(dims="dim2", shape=2),
                        Dimension(dims="dim3", shape=3),
                    )
                ),
            ],
            id="malformed abbreviated dims spec",
        ),
    ],
)
def test_pivot_dims(dims: DIMS_TYPE, shape: SHAPE_TYPE, expected):
    adapter = ArrayAdapter(dims, shape)
    pivoted = adapter.pivot_dims()
    assert pivoted == expected
