from ansys.geometry.core.math import Point3D
from ansys.geometry.core.shapes import LineShape
from ansys.geometry.core.sketch import Sketch


def test_create_line():
    """Test line shape creation in a sketch."""

    # Create a Sketch object
    sketch = Sketch()

    # Create a LineShape from two Point3D objects
    start_point = Point3D([0, 1, 3])
    end_point = Point3D([0, 4, 7])
    line = sketch.draw_line(start_point, end_point)

    # Check that the line has been created properly
    assert line.start_point.x == start_point.x
    assert line.start_point.y == start_point.y
    assert line.start_point.z == start_point.z
    assert line.end_point.x == end_point.x
    assert line.end_point.y == end_point.y
    assert line.end_point.z == end_point.z

    # Check also against the sketch_curves property
    assert len(sketch.shapes_list) == 1
    assert isinstance(sketch.shapes_list[-1], LineShape)
    assert sketch.shapes_list[-1].point_1 == start_point
    assert sketch.shapes_list[-1].point_2 == end_point
