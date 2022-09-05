import pytest

from ansys.geometry.core import UNIT_LENGTH, UNITS
from ansys.geometry.core.primitives import Point3D, UnitVector3D, Vector3D
from ansys.geometry.core.sketch.line import Line, Segment

DOUBLE_EPS = 1e-14
"""Numerical accuracy for ``test_line`` module"""


def test_create_line():
    """Simple test to create a ``Line``."""
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

    # Test line_3 - Modify the direction
    direction_y = UnitVector3D([0, 1, 0])
    direction_y_vector3D = Vector3D([0, 45, 0])  # Equivalent (as a UnitVector3D) to "direction_y"
    line_3 = Line(origin=origin, direction=direction_x)
    line_3.direction = direction_y_vector3D
    assert line_3.direction == direction_y
    assert line_3.origin == origin

    # Test line_4 - Modify the origin
    origin_4 = Point3D([3, 2, 1], unit=UNITS.mm)
    line_4 = Line(origin=origin, direction=direction_x)
    line_4.origin = origin_4
    assert line_4.direction == direction_x
    assert line_4.origin != origin
    assert line_4.origin == origin_4


def test_create_segment():
    """Simple test to create a ``Segment``."""

    # Test segment - Create a segment using two Point3D objects
    start = Point3D([1, 2, 3], unit=UNITS.mm)
    end = Point3D([1, 5, 9], unit=UNITS.mm)
    unit_vector = UnitVector3D(end - start)
    segment = Segment(start, end)
    assert segment.start == start
    assert segment.end == end
    assert segment.direction == unit_vector
    assert abs(segment.start.x - 1) <= DOUBLE_EPS
    assert abs(segment.start.y - 2) <= DOUBLE_EPS
    assert abs(segment.start.z - 3) <= DOUBLE_EPS
    assert segment.start.unit == UNITS.mm
    assert abs(segment.end.x - 1) <= DOUBLE_EPS
    assert abs(segment.end.y - 5) <= DOUBLE_EPS
    assert abs(segment.end.z - 9) <= DOUBLE_EPS
    assert segment.end.unit == UNITS.mm

    # Test segment_2 - Create a segment using a Point3D and a vector
    start_2 = Point3D([1, 2, 3], unit=UNITS.mm)
    end_2 = Point3D([1, 5, 9], unit=UNITS.mm)
    vector_2 = Vector3D(end_2 - start_2)
    segment_2 = Segment.from_origin_and_vector(start_2, vector_2, vector_units=UNITS.meter)
    assert segment_2.start == start
    assert segment_2.end == end
    assert segment_2.direction == unit_vector
    assert abs(segment_2.start.x - 0.001) <= DOUBLE_EPS
    assert abs(segment_2.start.y - 0.002) <= DOUBLE_EPS
    assert abs(segment_2.start.z - 0.003) <= DOUBLE_EPS
    assert segment_2.start.unit == UNIT_LENGTH
    assert abs(segment_2.end.x - 0.001) <= DOUBLE_EPS
    assert abs(segment_2.end.y - 0.005) <= DOUBLE_EPS
    assert abs(segment_2.end.z - 0.009) <= DOUBLE_EPS
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
    assert abs(segment_2b.start.x - 1) <= DOUBLE_EPS
    assert abs(segment_2b.start.y - 2) <= DOUBLE_EPS
    assert abs(segment_2b.start.z - 3) <= DOUBLE_EPS
    assert segment_2b.start.unit == UNITS.mm
    assert abs(segment_2b.end.x - 1) <= DOUBLE_EPS
    assert abs(segment_2b.end.y - 5) <= DOUBLE_EPS
    assert abs(segment_2b.end.z - 9) <= DOUBLE_EPS
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
    assert abs(segment_3.start.x - 0.001) <= DOUBLE_EPS
    assert abs(segment_3.start.y - 0.002) <= DOUBLE_EPS
    assert abs(segment_3.start.z - 0.003) <= DOUBLE_EPS
    assert segment_3.start.unit == UNIT_LENGTH
    assert abs(segment_3.end.x - 0.01) <= DOUBLE_EPS
    assert abs(segment_3.end.y - 0.05) <= DOUBLE_EPS
    assert abs(segment_3.end.z - 0.09) <= DOUBLE_EPS
    assert segment_3.end.unit == UNIT_LENGTH

    # Test segment_4 - Modify the origin
    start_4 = Point3D([10, 20, 30], unit=UNITS.mm)
    end_4 = Point3D([10, 50, 90], unit=UNITS.mm)
    unit_vector_4 = UnitVector3D(end_4 - start_4)
    new_start_4 = Point3D([-1, 2, 3], unit=UNITS.cm)
    new_unit_vector_4 = UnitVector3D(end_4 - new_start_4)

    segment_4 = Segment(start_4, end_4)
    assert segment_4.start == start_4
    assert segment_4.end == end_4
    assert segment_4.direction == unit_vector_4

    segment_4.start = new_start_4
    assert segment_4.start == new_start_4
    assert segment_4.end == end_4
    assert segment_4.direction == new_unit_vector_4

    # Test segment_5 - Modify the end
    start_5 = Point3D([10, 20, 30], unit=UNITS.mm)
    end_5 = Point3D([10, 50, 90], unit=UNITS.mm)
    unit_vector_5 = UnitVector3D(end_5 - start_5)
    new_end_5 = Point3D([-1, 5, 9], unit=UNITS.cm)
    new_unit_vector_5 = UnitVector3D(new_end_5 - start_5)

    segment_5 = Segment(start_5, end_5)
    assert segment_5.start == start_5
    assert segment_5.end == end_5
    assert segment_5.direction == unit_vector_5

    segment_5.end = new_end_5
    assert segment_5.start == start_5
    assert segment_5.end == new_end_5
    assert segment_5.direction == new_unit_vector_5


def test_errors_line():
    """Check errors when handling a ``Line``."""
    with pytest.raises(TypeError, match="The parameter 'origin' should be a Point3D object."):
        Line("a", "b")
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'origin' should not be a None numpy.ndarray."
    ):
        Line(Point3D(), "b")
    with pytest.raises(TypeError, match="The parameter 'direction' should be a Vector3D object."):
        Line(Point3D([10, 20, 30], unit=UNITS.meter), "b")
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'direction' should not be a zeroes numpy.ndarray."
    ):
        Line(Point3D([10, 20, 30], unit=UNITS.meter), Vector3D([0, 0, 0]))

    # Now create a line and test the setters
    origin = Point3D([1, 2, 3], unit=UNITS.mm)
    direction_x = UnitVector3D([1, 0, 0])
    line = Line(origin=origin, direction=direction_x)
    with pytest.raises(TypeError, match="The parameter 'origin' should be a Point3D object."):
        line.origin = "a"
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'origin' should not be a None numpy.ndarray."
    ):
        line.origin = Point3D()
    with pytest.raises(TypeError, match="The parameter 'direction' should be a Vector3D object."):
        line.direction = "b"
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'direction' should not be a zeroes numpy.ndarray."
    ):
        line.direction = Vector3D([0, 0, 0])


def test_errors_segment():
    """Check errors when handling a ``Segment``."""
    with pytest.raises(TypeError, match="The parameter 'start' should be a Point3D object."):
        Segment("a", "b")
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'start' should not be a None numpy.ndarray."
    ):
        Segment(Point3D(), "b")
    with pytest.raises(TypeError, match="The parameter 'end' should be a Point3D object."):
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

    # Now create a segment and test the setters
    start = Point3D([1, 2, 3], unit=UNITS.mm)
    end = Point3D([1, 5, 9], unit=UNITS.mm)
    segment = Segment(start, end)

    with pytest.raises(TypeError, match="The parameter 'origin' should be a Point3D object."):
        segment.start = "a"
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'origin' should not be a None numpy.ndarray."
    ):
        segment.start = Point3D()
    with pytest.raises(TypeError, match="The parameter 'origin' should be a Point3D object."):
        segment.origin = "a"
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'origin' should not be a None numpy.ndarray."
    ):
        segment.origin = Point3D()
    with pytest.raises(
        ValueError,
        match="Parameters 'origin' and 'end' have the same values. No segment can be created.",
    ):
        segment.start = segment.end
    with pytest.raises(
        ValueError,
        match="Parameters 'origin' and 'end' have the same values. No segment can be created.",
    ):
        segment.origin = segment.end

    with pytest.raises(TypeError, match="The parameter 'end' should be a Point3D object."):
        segment.end = "b"
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'end' should not be a None numpy.ndarray."
    ):
        segment.end = Point3D()
    with pytest.raises(
        ValueError,
        match="Parameters 'origin' and 'end' have the same values. No segment can be created.",
    ):
        segment.end = segment.start
    with pytest.raises(ValueError, match="Segment direction is unsettable."):
        segment.direction = "a"
