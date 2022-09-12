import numpy as np
from numpy.testing import assert_allclose
from pint import Quantity
import pytest

from ansys.geometry.core.math import ZERO_VECTOR3D, Plane, Point, UnitVector, Vector
from ansys.geometry.core.misc import UNIT_LENGTH, UNITS
from ansys.geometry.core.shapes import Circle, Ellipse, Line, Segment
from ansys.geometry.core.sketch import Sketch

DOUBLE_EPS = np.finfo(float).eps


def test_create_circle():
    """Test circle shape creation in a sketch."""

    # Create a Sketch instance
    sketch = Sketch()

    # Draw a circle in previous sketch
    center, radius = (
        Point([0, 0, 0], UNITS.m),
        (1 * UNITS.m),
    )
    circle = sketch.draw_circle(center, radius)

    # Check attributes are expected ones
    assert circle.center == center
    assert circle.radius == radius
    assert circle.diameter == 2 * radius
    assert circle.area == np.pi * radius**2
    assert circle.perimeter == 2 * np.pi * radius

    # Check points are expected ones
    local_points = circle.local_points(num_points=5)
    assert abs(all(local_points[0] - Point([1, 0, 0]))) <= DOUBLE_EPS
    assert abs(all(local_points[2] - Point([-1, 0, 0]))) <= DOUBLE_EPS

    # Use the class method to build a circle
    center_2, radius_2 = Point([10, 20, 0], UNITS.mm), (10 * UNITS.mm)
    circle_from_center_and_radius = Circle.from_center_and_radius(center_2, radius_2)
    assert circle_from_center_and_radius.center == center_2
    assert circle_from_center_and_radius.radius == radius_2
    assert circle_from_center_and_radius.diameter == 2 * radius_2
    assert circle_from_center_and_radius.area == np.pi * radius_2**2
    assert circle_from_center_and_radius.perimeter == 2 * np.pi * radius_2

    local_points_2 = circle_from_center_and_radius.local_points(num_points=5)
    assert abs(all(local_points_2[0] - Point([10, 20, 0], UNITS.mm))) <= DOUBLE_EPS
    assert abs(all(local_points_2[2] - Point([-10, 20, 0], UNITS.mm))) <= DOUBLE_EPS


def test_circle_errors():
    """Test various circle instantiation errors."""
    xy_plane = Plane()

    with pytest.raises(ValueError, match="Center must be contained in the plane."):
        Circle(xy_plane, Point([0, 0, 1]), 1 * UNITS.fahrenheit)

    with pytest.raises(
        TypeError, match=r"The pint.Unit provided as input should be a \[length\] quantity."
    ):
        Circle(xy_plane, Point([10, 20, 0]), 1 * UNITS.fahrenheit)

    with pytest.raises(ValueError, match="Radius must be a real positive value."):
        Circle(xy_plane, Point([10, 20, 0]), -10 * UNITS.mm)


def test_create_ellipse():
    """Test ellipse shape creation in a sketch."""

    # Create a Sketch instance
    sketch = Sketch()

    # Draw a circle in previous sketch
    semi_major, semi_minor, origin = 2 * UNITS.m, 1 * UNITS.m, Point([0, 0, 0], UNITS.m)
    ecc = np.sqrt(1 - (semi_minor / semi_major) ** 2)
    ellipse = sketch.draw_ellipse(origin, semi_major, semi_minor)

    # Check attributes are expected ones
    assert ellipse.semi_major_axis == semi_major
    assert ellipse.semi_minor_axis == semi_minor
    assert abs(ellipse.eccentricity - ecc.m) <= DOUBLE_EPS
    assert ellipse.linear_eccentricity == np.sqrt(semi_major**2 - semi_minor**2)
    assert ellipse.semi_latus_rectum == semi_minor**2 / semi_major
    assert abs((ellipse.perimeter - 9.6884482205477 * UNITS.m).m) <= 5e-14
    assert abs((ellipse.area - 6.28318530717959 * UNITS.m * UNITS.m).m) <= 5e-14

    # Check points are expected ones
    local_points = ellipse.local_points(num_points=5)
    assert abs(all(local_points[0] - Point([2, 0, 0]))) <= DOUBLE_EPS
    assert abs(all(local_points[2] - Point([-2, 0, 0]))) <= DOUBLE_EPS

    # Use the class method to build an ellipse
    semi_major_2, semi_minor_2, center_2 = 5 * UNITS.mm, 4 * UNITS.mm, Point([10, 20, 0], UNITS.mm)
    ecc_2 = np.sqrt(1 - (semi_minor_2 / semi_major_2) ** 2)
    ellipse_from_axes = Ellipse.from_axes(center_2, semi_major_2, semi_minor_2)
    assert ellipse_from_axes.semi_major_axis == semi_major_2
    assert ellipse_from_axes.semi_minor_axis == semi_minor_2
    assert abs(ellipse_from_axes.eccentricity - ecc_2.m) <= DOUBLE_EPS
    assert ellipse_from_axes.linear_eccentricity == np.sqrt(semi_major_2**2 - semi_minor_2**2)
    assert ellipse_from_axes.semi_latus_rectum == semi_minor_2**2 / semi_major_2
    assert abs((ellipse_from_axes.perimeter - 28.36166788897449 * UNITS.mm).m) <= 5e-14
    assert abs((ellipse_from_axes.area - 62.8318530717959 * UNITS.mm * UNITS.mm).m) <= 5e-14

    local_points_2 = ellipse_from_axes.local_points(num_points=5)
    assert abs(all(local_points_2[0] - Point([10, 20, 0], UNITS.mm))) <= DOUBLE_EPS
    assert abs(all(local_points_2[2] - Point([-10, 20, 0], UNITS.mm))) <= DOUBLE_EPS


def test_ellipse_errors():
    """Test various circle instantiation errors."""
    xy_plane = Plane()

    with pytest.raises(
        TypeError, match=r"The pint.Unit provided as input should be a \[length\] quantity."
    ):
        Ellipse(
            xy_plane,
            Point([10, 20, 0]),
            Quantity(1, UNITS.fahrenheit),
            Quantity(56, UNITS.fahrenheit),
        )

    with pytest.raises(
        TypeError, match=r"The pint.Unit provided as input should be a \[length\] quantity."
    ):
        Ellipse(xy_plane, Point([10, 20, 0]), 1 * UNITS.m, Quantity(56, UNITS.fahrenheit))

    with pytest.raises(ValueError, match="Center must be contained in the plane."):
        Ellipse(xy_plane, Point([0, 0, 1]), -1 * UNITS.m, -3 * UNITS.m)

    with pytest.raises(ValueError, match="Semi-major axis must be a real positive value."):
        Ellipse(
            xy_plane,
            Point([10, 20, 0]),
            -1 * UNITS.m,
            -3 * UNITS.m,
        )

    with pytest.raises(ValueError, match="Semi-minor axis must be a real positive value."):
        Ellipse(
            xy_plane,
            Point([10, 20, 0]),
            1 * UNITS.m,
            -3 * UNITS.m,
        )

    with pytest.raises(ValueError, match="Semi-major axis cannot be shorter than semi-minor axis."):
        Ellipse(
            xy_plane,
            Point([10, 20, 0]),
            1 * UNITS.m,
            3 * UNITS.m,
        )

    ellipse = Ellipse(
        xy_plane,
        Point([10, 20, 0]),
        3 * UNITS.m,
        100 * UNITS.cm,
    )


def test_create_polygon():
    """Test polygon shape creation in a sketch."""

    # Create a Sketch instance
    sketch = Sketch()

    # Draw a pentagon in previous sketch
    radius, sides, center = (1 * UNITS.m), 5, Point([0, 0, 0], UNITS.m)
    pentagon = sketch.draw_polygon(center, radius, sides)

    # Check attributes are expected ones
    side_length = 2 * radius * np.tan(np.pi / sides)
    assert_allclose(pentagon.inner_radius, radius)
    assert pentagon.n_sides == 5
    assert_allclose(pentagon.length, side_length)
    assert_allclose(pentagon.perimeter, sides * side_length)

    # Draw a square in previous sketch
    radius, sides, center = (1 * UNITS.m), 4, Point([0, 0, 0], UNITS.m)
    square = sketch.draw_polygon(center, radius, sides)

    # Check attributes are expected ones
    side_length = 2 * radius * np.tan(np.pi / sides)  # 2.0 m
    assert_allclose(square.inner_radius, radius)
    assert square.n_sides == 4
    assert_allclose(square.length, side_length)
    assert_allclose(square.perimeter, sides * side_length)
    assert_allclose(square.area, 4.0 * UNITS.m**2)

    # Check points are expected ones
    local_points = square.local_points()
    assert abs(all(local_points[0] - Point([1.41421356, 0, 0]))) <= DOUBLE_EPS
    assert abs(all(local_points[2] - Point([-1.41421356, 0, 0]))) <= DOUBLE_EPS

    with pytest.raises(
        ValueError, match="The minimum number of sides to construct a polygon should be 3."
    ):
        radius, sides, center = (1 * UNITS.m), 2, Point([0, 0, 0], UNITS.m)
        sketch.draw_polygon(center, radius, sides)

    with pytest.raises(ValueError, match="Radius must be a real positive value."):
        radius, sides, center = (-1 * UNITS.m), 6, Point([0, 0, 0], UNITS.m)
        sketch.draw_polygon(center, radius, sides)


def test_create_line_no_sketch():
    """Simple test to create a ``Line`` (w/o a Sketch object)."""
    # Test line - Create a line using a Point and a Vector
    origin = Point([1, 2, 3], unit=UNITS.mm)
    direction_x = UnitVector([1, 0, 0])
    line = Line(origin=origin, direction=direction_x)
    assert line.direction == direction_x
    assert line.origin == origin

    # Test line_2 - Create a line using a Point and a Vector
    direction_x_vector3D = Vector([45, 0, 0])  # Equivalent (as a UnitVector) to "direction_x"
    line_2 = Line(origin=origin, direction=direction_x_vector3D)
    assert line_2.direction == direction_x
    assert line_2.origin == origin

    # From test 1, get the local points
    local_points_even = line.local_points(num_points=80)
    local_points_odd = line.local_points(num_points=81)
    assert local_points_even[0] == Point([-39, 2, 3], unit=UNITS.mm)
    assert local_points_even[-1] == Point([40, 2, 3], unit=UNITS.mm)
    assert len(local_points_even) == 80
    assert local_points_odd[0] == Point([-39, 2, 3], unit=UNITS.mm)
    assert local_points_odd[-1] == Point([41, 2, 3], unit=UNITS.mm)
    assert len(local_points_odd) == 81


def test_create_segment_no_sketch():
    """Simple test to create a ``Segment`` (w/o a Sketch object)."""

    # Test segment - Create a segment using two Point objects
    start = Point([1, 2, 3], unit=UNITS.mm)
    end = Point([1, 5, 9], unit=UNITS.mm)
    unit_vector = UnitVector(end - start)
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

    # Test segment_2 - Create a segment using a Point and a vector
    start_2 = Point([1, 2, 3], unit=UNITS.mm)
    end_2 = Point([1, 5, 9], unit=UNITS.mm)
    vector_2 = Vector(end_2 - start_2)
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

    # Test segment_2b - Create a segment using a Point and a vector (same units as the point)
    start_2b = Point([1, 2, 3], unit=UNITS.mm)
    end_2b = Point([1, 5, 9], unit=UNITS.mm)
    vector_2b = Vector(end_2b - start_2b)
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

    # Test segment_3 - Create a segment using two Point objects (in different units)
    start_3 = Point([1, 2, 3], unit=UNITS.mm)
    end_3 = Point([1, 5, 9], unit=UNITS.cm)  # Point([10, 50, 90], unit=UNITS.mm)
    unit_vector_3 = UnitVector(end_3 - start_3)
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
        Line(Point([10, 20, 30], unit=UNITS.meter), "b")
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'direction' should not be a numpy.ndarray of zeros."
    ):
        Line(Point([10, 20, 30], unit=UNITS.meter), ZERO_VECTOR3D)

    with pytest.raises(TypeError, match="Provided type"):
        Line("a", Vector([1, 0, 0]))
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'origin' should not be a nan numpy.ndarray."
    ):
        Line(Point(), Vector([1, 0, 0]))


def test_errors_segment():
    """Check errors when handling a ``Segment``."""
    with pytest.raises(TypeError, match="Provided type"):
        Segment("a", "b")
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'start' should not be a nan numpy.ndarray."
    ):
        Segment(Point(), "b")
    with pytest.raises(TypeError, match="Provided type"):
        Segment(Point([10, 20, 30], unit=UNITS.meter), "b")
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'end' should not be a nan numpy.ndarray."
    ):
        Segment(Point([10, 20, 30]), Point())
    with pytest.raises(
        ValueError,
        match="Parameters 'origin' and 'end' have the same values. No segment can be created.",
    ):
        Segment(Point([10, 20, 30]), Point([10, 20, 30]))
