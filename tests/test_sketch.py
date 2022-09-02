import numpy as np

from ansys.geometry.core.primitives import Point3D
from ansys.geometry.core.sketch import CircleSketch, EllipseSketch, LineSketch, Sketch


def test_ellipse_from_axes():
    """Verify constructor for ``EllipseSketch``."""
    expected_a, expected_b = 9, 7
    ellipse = EllipseSketch.from_axes(expected_a, expected_b)
    np.testing.assert_allclose(ellipse.a, expected_a)
    np.testing.assert_allclose(ellipse.b, expected_b)


def test_ellipse_with_same_axes_is_circle_like():
    """Verify an ellipse with zero eccentricity has same points as a circle."""
    ellipse = EllipseSketch.from_axes(1, 1)
    circle = CircleSketch.from_radius(1)
    for ellipse_point, circle_point in zip(ellipse.points, circle.points):
        np.testing.assert_allclose(ellipse_point[0], circle_point[0])
        np.testing.assert_allclose(ellipse_point[1], circle_point[1])


def test_create_line():
    """Simple test to create a ``LineSketch`` using a
    ``Sketch`` object."""

    # Create a Sketch object
    sketch = Sketch()

    # Create a LineSketch from two Point3D objects
    p_1 = Point3D([0, 1, 3])
    p_2 = Point3D([0, 4, 7])
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
