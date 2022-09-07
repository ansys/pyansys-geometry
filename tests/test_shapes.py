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


def test_create_polygon():
    """Test polygon shape creation in a sketch."""

    # Create a Sketch instance
    sketch = Sketch()

    # Draw a polygon in previous sketch
    radius, sides, origin = 1 * u.m, 5, Point3D([0, 0, 0], u.m)
    pentagon = sketch.draw_polygon(radius, sides, origin)

    # Check attributes are expected ones
    side_length = 2 * radius * np.tan(180 / sides)
    assert_allclose(pentagon.r, radius)
    assert pentagon.n == 5
    assert_allclose(pentagon.length, side_length)
    assert_allclose(pentagon.perimeter, sides * side_length)

    # Check points are expected ones
    five_local_points = [
        [1, 0, -1, 0, 1],
        [0, 1, 0, -1, 0],
        [0, 0, 0, 0, 0],
    ]
    assert_allclose(pentagon.local_points(num_points=5), five_local_points, atol=1e-5, rtol=1e-7)
