import numpy as np
from numpy.testing import assert_allclose

from ansys.geometry.core import UNITS as u
from ansys.geometry.core.math import Point3D
from ansys.geometry.core.sketch import Sketch


def test_create_cirlce():
    """Test circle shape creation in a sketch."""

    # Create a Sketch instance
    sketch = Sketch()

    # Draw a circle in previous sketch
    radius, origin = 1 * u.m, Point3D([0, 0, 0], u.m)
    circle = sketch.draw_circle(radius, origin)

    # Check attributes are expected ones
    assert_allclose(circle.r, radius)
    assert_allclose(circle.d, 2 * radius)
    assert_allclose(circle.area, np.pi * radius**2)
    assert_allclose(circle.perimeter, 2 * np.pi * radius)

    # Check points are expected ones
    five_local_points = [
        [1, 0, -1, 0, 1],
        [0, 1, 0, -1, 0],
        [0, 0, 0, 0, 0],
    ]
    assert_allclose(circle.local_points(num_points=5), five_local_points, atol=1e-5, rtol=1e-7)


def test_create_ellipse():
    """Test ellipse shape creation in a sketch."""

    # Create a Sketch instance
    sketch = Sketch()

    # Draw a circle in previous sketch
    a, b, origin = 2 * u.m, 1 * u.m, Point3D([0, 0, 0], u.m)
    ecc = np.sqrt(1 - (b / a) ** 2)
    ellipse = sketch.draw_ellipse(a, b, origin)

    # Check attributes are expected ones
    assert_allclose(ellipse.a, a)
    assert_allclose(ellipse.b, b)
    assert_allclose(ellipse.ecc, ecc)
    assert_allclose(ellipse.c, np.sqrt(a**2 - b**2))
    assert_allclose(ellipse.l, b**2 / a)
    assert_allclose(ellipse.perimeter, 9.6884482205477 * u.m)

    # Check points are expected ones
    five_local_points = [
        [2, 0, -2, 0, 2],
        [0, 1, 0, -1, 0],
        [0, 0, 0, 0, 0],
    ]
    assert_allclose(ellipse.local_points(num_points=5), five_local_points, atol=1e-5, rtol=1e-7)


def test_create_line():
    """Test line shape creation in a sketch."""

    # Create a Sketch object
    sketch = Sketch()

    # Draw a line in previous sketch
    start_point = Point3D([0, 1, 3], u.m)
    end_point = Point3D([0, 4, 7], u.m)
    line = sketch.draw_line(start_point, end_point)

    # Check that the line has been created properly
    assert_allclose(line.start_point.x, start_point.x)
    assert_allclose(line.start_point.y, start_point.y)
    assert_allclose(line.start_point.z, start_point.z)
    assert_allclose(line.end_point.x, end_point.x)
    assert_allclose(line.end_point.y, end_point.y)
    assert_allclose(line.end_point.z, end_point.z)
