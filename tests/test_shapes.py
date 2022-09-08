import numpy as np
from numpy.testing import assert_allclose
import pytest

from ansys.geometry.core import UNIT_LENGTH, UNITS
from ansys.geometry.core.math import ZERO_VECTOR3D, Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.shapes.line import Line, Segment
from ansys.geometry.core.sketch import Sketch


def test_create_circle():
    """Test circle shape creation in a sketch."""

    # Create a Sketch instance
    sketch = Sketch()

    # Draw a circle in previous sketch
    radius, origin = 1 * UNITS.m, Point3D([0, 0, 0], UNITS.m)
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
    a, b, origin = 2 * UNITS.m, 1 * UNITS.m, Point3D([0, 0, 0], UNITS.m)
    ecc = np.sqrt(1 - (b / a) ** 2)
    ellipse = sketch.draw_ellipse(a, b, origin)

    # Check attributes are expected ones
    assert_allclose(ellipse.a, a)
    assert_allclose(ellipse.b, b)
    assert_allclose(ellipse.ecc, ecc)
    assert_allclose(ellipse.c, np.sqrt(a**2 - b**2))
    assert_allclose(ellipse.l, b**2 / a)
    assert_allclose(ellipse.perimeter, 9.6884482205477 * UNITS.m)

    # Check points are expected ones
    five_local_points = [
        [2, 0, -2, 0, 2],
        [0, 1, 0, -1, 0],
        [0, 0, 0, 0, 0],
    ]
    assert_allclose(ellipse.local_points(num_points=5), five_local_points, atol=1e-5, rtol=1e-7)


def test_create_line_no_sketch():
    """Simple test to create a ``Line`` (w/o a Sketch object)."""
    # Test line - Create a line using a Point3D and a Vector3D
    origin = Point3D([1, 2, 3], unit=UNITS.mm)
    direction_x = UnitVector3D([1, 0, 0])
    line = Line(origin=origin, direction=direction_x)
    assert line.direction == direction_x
    assert line.origin == origin

    # Test line_2 - Create a line using a Point3D and a Vector3D
    direction_x_vector3D = Vector3D([45, 0, 0])  # Equivalent (as a UnitVector3D) to "direction_x"
    line_2 = Line(origin=origin, direction=direction_x_vector3D)
    assert line_2.direction == direction_x
    assert line_2.origin == origin

    # From test 1, get the local points
    local_points_even = line.local_points(num_points=80)
    local_points_odd = line.local_points(num_points=81)
    assert local_points_even[0] == Point3D([-39, 2, 3], unit=UNITS.mm)
    assert local_points_even[-1] == Point3D([40, 2, 3], unit=UNITS.mm)
    assert len(local_points_even) == 80
    assert local_points_odd[0] == Point3D([-39, 2, 3], unit=UNITS.mm)
    assert local_points_odd[-1] == Point3D([41, 2, 3], unit=UNITS.mm)
    assert len(local_points_odd) == 81


def test_create_segment_no_sketch():
    """Simple test to create a ``Segment`` (w/o a Sketch object)."""

    # Test segment - Create a segment using two Point3D objects
    start = Point3D([1, 2, 3], unit=UNITS.mm)
    end = Point3D([1, 5, 9], unit=UNITS.mm)
    unit_vector = UnitVector3D(end - start)
    segment = Segment(start, end)
    assert segment.start == start
    assert segment.end == end
    assert segment.direction == unit_vector
    assert_allclose(segment.start.x, 1)
    assert_allclose(segment.start.y, 2)
    assert_allclose(segment.start.z, 3)
    assert segment.start.unit == UNITS.mm
    assert_allclose(segment.end.x, 1)
    assert_allclose(segment.end.y, 5)
    assert_allclose(segment.end.z, 9)
    assert segment.end.unit == UNITS.mm

    # Test segment_2 - Create a segment using a Point3D and a vector
    start_2 = Point3D([1, 2, 3], unit=UNITS.mm)
    end_2 = Point3D([1, 5, 9], unit=UNITS.mm)
    vector_2 = Vector3D(end_2 - start_2)
    segment_2 = Segment.from_origin_and_vector(start_2, vector_2, vector_units=UNITS.meter)
    assert segment_2.start == start
    assert segment_2.end == end
    assert segment_2.direction == unit_vector
    assert_allclose(segment_2.start.x, 0.001)
    assert_allclose(segment_2.start.y, 0.002)
    assert_allclose(segment_2.start.z, 0.003)
    assert segment_2.start.unit == UNIT_LENGTH
    assert_allclose(segment_2.end.x, 0.001)
    assert_allclose(segment_2.end.y, 0.005)
    assert_allclose(segment_2.end.z, 0.009)
    assert segment_2.end.unit == UNIT_LENGTH

    # Test segment_2b - Create a segment using a Point3D and a vector (same units as the point)
    start_2b = Point3D([1, 2, 3], unit=UNITS.mm)
    end_2b = Point3D([1, 5, 9], unit=UNITS.mm)
    vector_2b = Vector3D(end_2b - start_2b)
    vector_2b = vector_2b * 1e3  # The vector would be in meters --> convert to mm
    segment_2b = Segment.from_origin_and_vector(start_2b, vector_2b, vector_units=UNITS.mm)
    assert segment_2b.start == start
    assert segment_2b.end == end
    assert segment_2b.direction == unit_vector
    assert_allclose(segment_2b.start.x, 1)
    assert_allclose(segment_2b.start.y, 2)
    assert_allclose(segment_2b.start.z, 3)
    assert segment_2b.start.unit == UNITS.mm
    assert_allclose(segment_2b.end.x, 1)
    assert_allclose(segment_2b.end.y, 5)
    assert_allclose(segment_2b.end.z, 9)
    assert segment_2b.end.unit == UNITS.mm

    # Test segment_3 - Create a segment using two Point3D objects (in different units)
    start_3 = Point3D([1, 2, 3], unit=UNITS.mm)
    end_3 = Point3D([1, 5, 9], unit=UNITS.cm)  # Point3D([10, 50, 90], unit=UNITS.mm)
    unit_vector_3 = UnitVector3D(end_3 - start_3)
    segment_3 = Segment(start_3, end_3)
    assert segment_3.start == start_3
    assert segment_3.end == end_3
    assert segment_3.direction == unit_vector_3
    assert unit_vector != unit_vector_3
    assert end != end_3
    assert_allclose(segment_3.start.x, 0.001)
    assert_allclose(segment_3.start.y, 0.002)
    assert_allclose(segment_3.start.z, 0.003)
    assert segment_3.start.unit == UNIT_LENGTH
    assert_allclose(segment_3.end.x, 0.01)
    assert_allclose(segment_3.end.y, 0.05)
    assert_allclose(segment_3.end.z, 0.09)
    assert segment_3.end.unit == UNIT_LENGTH

    # From test 1, get the local points
    local_points_even = segment.local_points(num_points=80)
    local_points_odd = segment.local_points(num_points=81)
    assert local_points_even[0] == start
    assert local_points_even[-1] == end
    assert len(local_points_even) == 80
    assert local_points_odd[0] == start
    assert local_points_odd[-1] == end
    assert len(local_points_odd) == 81


def test_errors_line():
    """Check errors when handling a ``Line``."""
    with pytest.raises(TypeError, match="Provided type"):
        Line(Point3D([10, 20, 30], unit=UNITS.meter), "b")
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'direction' should not be a numpy.ndarray of zeros."
    ):
        Line(Point3D([10, 20, 30], unit=UNITS.meter), ZERO_VECTOR3D)

    with pytest.raises(TypeError, match="Provided type"):
        Line("a", Vector3D([1, 0, 0]))
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'origin' should not be a None numpy.ndarray."
    ):
        Line(Point3D(), Vector3D([1, 0, 0]))


def test_errors_segment():
    """Check errors when handling a ``Segment``."""
    with pytest.raises(TypeError, match="Provided type"):
        Segment("a", "b")
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'start' should not be a None numpy.ndarray."
    ):
        Segment(Point3D(), "b")
    with pytest.raises(TypeError, match="Provided type"):
        Segment(Point3D([10, 20, 30], unit=UNITS.meter), "b")
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'end' should not be a None numpy.ndarray."
    ):
        Segment(Point3D([10, 20, 30]), Point3D())
    with pytest.raises(
        ValueError,
        match="Parameters 'origin' and 'end' have the same values. No segment can be created.",
    ):
        Segment(Point3D([10, 20, 30]), Point3D([10, 20, 30]))
