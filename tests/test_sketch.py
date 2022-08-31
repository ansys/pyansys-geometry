from ansys.geometry.core.primitives import Point
from ansys.geometry.core.sketch import LineSketch, Sketch


def test_create_line():
    """Simple test to create a ``LineSketch`` using a
    ``Sketch`` object."""

    # Create a Sketch object
    sketch = Sketch()

    # Create a LineSketch from two Point objects
    p_1 = Point(0, 1, 3)
    p_2 = Point(0, 4, 7)
    line = sketch.line(p_1, p_2)

    # Check that the line has been created properly
    assert line.point_1.x == p_1.x
    assert line.point_1.y == p_1.y
    assert line.point_1.z == p_1.z
    assert line.point_2.x == p_2.x
    assert line.point_2.y == p_2.y
    assert line.point_2.z == p_2.z

    # Check also against the sketch_curves property
    assert len(sketch.sketch_curves) == 1
    assert isinstance(sketch.sketch_curves[-1], LineSketch)
    assert sketch.sketch_curves[-1].point_1 == p_1
    assert sketch.sketch_curves[-1].point_2 == p_2
