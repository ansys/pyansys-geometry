# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.

from beartype.roar import BeartypeCallHintParamViolation
import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core.math import (
    ZERO_POINT2D,
    Plane,
    Point2D,
    Point3D,
    UnitVector3D,
    Vector2D,
    Vector3D,
)
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Distance
from ansys.geometry.core.sketch import (
    Arc,
    Box,
    Polygon,
    Sketch,
    SketchCircle,
    SketchEllipse,
    SketchSegment,
    Slot,
)

DOUBLE_EPS = np.finfo(float).eps


def test_errors_sketch_segment():
    """Check errors when handling a ``SketchSegment``."""
    with pytest.raises(BeartypeCallHintParamViolation):
        SketchSegment("a", "b")
    with pytest.raises(BeartypeCallHintParamViolation):
        SketchSegment(Point2D([10, 20], unit=UNITS.meter), "b")
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'start' should not be a nan numpy.ndarray."
    ):
        SketchSegment(Point2D(), Point2D())
    with pytest.raises(
        ValueError, match="The numpy.ndarray 'end' should not be a nan numpy.ndarray."
    ):
        SketchSegment(Point2D([10, 20]), Point2D())
    with pytest.raises(
        ValueError,
        match="Parameters 'start' and 'end' have the same values. No segment can be created.",
    ):
        SketchSegment(Point2D([10, 20]), Point2D([10, 20]))


def test_sketch_segment_edge():
    """Test SketchSegment SketchEdge sketching."""

    # Create a Sketch instance
    sketch = Sketch()

    # sketch api has 0, 0 origin as default start position
    assert len(sketch.edges) == 0
    sketch.segment_to_point(Point2D([2, 3]), "Segment1")
    assert len(sketch.edges) == 1
    assert sketch.edges[0].start == ZERO_POINT2D
    assert sketch.edges[0].end == Point2D([2, 3])
    assert sketch.edges[0].length.m == pytest.approx(3.60555128, rel=1e-7, abs=1e-8)

    # sketch api keeps last edge endpoint as context for new edge
    sketch.segment_to_point(Point2D([3, 3]), "Segment2").segment_to_point(
        Point2D([3, 2]), "Segment3"
    )
    assert len(sketch.edges) == 3
    assert sketch.edges[1].start == Point2D([2, 3])
    assert sketch.edges[1].end == Point2D([3, 3])
    assert sketch.edges[2].start == Point2D([3, 3])
    assert sketch.edges[2].end == Point2D([3, 2])

    # sketch api allows segment defined by two points
    sketch.segment(Point2D([3, 2]), Point2D([2, 0]), "Segment4")
    assert len(sketch.edges) == 4
    assert sketch.edges[3].start == Point2D([3, 2])
    assert sketch.edges[3].end == Point2D([2, 0])

    # sketch api allows segment defined by vector magnitude
    sketch.segment_from_point_and_vector(Point2D([2, 0]), Vector2D([-1, 1]), "Segment5")
    assert len(sketch.edges) == 5
    assert sketch.edges[4].start == Point2D([2, 0])
    assert sketch.edges[4].end == Point2D([1, 1])

    sketch.segment_from_vector(Vector2D([-1, -1]), "Segment6")
    assert len(sketch.edges) == 6
    assert sketch.edges[5].start == Point2D([1, 1])
    assert sketch.edges[5].end == Point2D([0, 0])

    segment1_retrieved = sketch.get("Segment1")
    assert len(segment1_retrieved) == 1
    assert segment1_retrieved[0] == sketch.edges[0]

    segment2_retrieved = sketch.get("Segment2")
    assert len(segment2_retrieved) == 1
    assert segment2_retrieved[0] == sketch.edges[1]

    segment3_retrieved = sketch.get("Segment3")
    assert len(segment3_retrieved) == 1
    assert segment3_retrieved[0] == sketch.edges[2]

    segment4_retrieved = sketch.get("Segment4")
    assert len(segment4_retrieved) == 1
    assert segment4_retrieved[0] == sketch.edges[3]

    segment5_retrieved = sketch.get("Segment5")
    assert len(segment5_retrieved) == 1
    assert segment5_retrieved[0] == sketch.edges[4]

    segment6_retrieved = sketch.get("Segment6")
    assert len(segment6_retrieved) == 1
    assert segment6_retrieved[0] == sketch.edges[5]

    with pytest.raises(
        ValueError,
        match="Parameters 'start' and 'end' have the same values. No segment can be created.",
    ):
        sketch.segment(Point2D([3, 2]), Point2D([3, 2]), "Segment4")


def test_sketch_arc_edge():
    """Test Arc SketchEdge sketching."""

    # Create a Sketch instance
    sketch = Sketch()

    # fluent API has (0, 0) origin as default start position
    #
    #                       ^
    #                       |
    #                       |
    #                       |        (3,3)
    #                       |---------E
    #                       |         |
    #                       |         |
    #                       |         |
    #                 (0,0) S---------O------------->
    #                                  (3,0)
    #
    #
    # Since angle is counterclockwise by default, this will lead to a 270deg
    # angle starting on S and ending on E. This is also PI * 3 / 2 in rads
    #
    assert len(sketch.edges) == 0
    sketch.arc_to_point(Point2D([3, 3]), Point2D([3, 0]), False, "Arc1")
    assert len(sketch.edges) == 1
    assert sketch.edges[0].start == ZERO_POINT2D
    assert sketch.edges[0].end == Point2D([3, 3])
    assert sketch.edges[0].angle == np.pi * 3 / 2

    # Fluent api keeps last edge endpoint as context for new edge
    #
    #
    # In this case, following the previous drawing, we are going from E to S with center
    # at 'O' again, but in clockwise direction. This will lead to 270 degs (PI * 3 / 2 in rads).
    #
    sketch.arc_to_point(Point2D([0, 0]), Point2D([3, 0]), clockwise=True, tag="Arc2")
    assert len(sketch.edges) == 2
    assert sketch.edges[1].start == Point2D([3, 3])
    assert sketch.edges[1].end == Point2D([0, 0])
    assert sketch.edges[1].angle == np.pi * 3 / 2

    sketch.arc(Point2D([10, 10]), Point2D([10, -10]), Point2D([10, 0]), tag="Arc3")
    assert len(sketch.edges) == 3
    assert sketch.edges[2].start == Point2D([10, 10])
    assert sketch.edges[2].end == Point2D([10, -10])
    assert sketch.edges[2].angle == np.pi
    assert sketch.edges[2].sector_area.m == pytest.approx(157.07963267948966, rel=1e-7, abs=1e-8)
    assert sketch.edges[2].length.m == pytest.approx(31.41592653589793, rel=1e-7, abs=1e-8)
    assert sketch.edges[2].radius.m == 10

    arc1_retrieved = sketch.get("Arc1")
    assert len(arc1_retrieved) == 1
    assert arc1_retrieved[0] == sketch.edges[0]

    arc2_retrieved = sketch.get("Arc2")
    assert len(arc2_retrieved) == 1
    assert arc2_retrieved[0] == sketch.edges[1]

    arc3_retrieved = sketch.get("Arc3")
    assert len(arc3_retrieved) == 1
    assert arc3_retrieved[0] == sketch.edges[2]


def test_sketch_triangle_face():
    """Test Triangle SketchFace sketching."""

    # Create a Sketch instance
    sketch = Sketch()

    # Create the sketch face with triangle
    sketch.triangle(Point2D([10, 10]), Point2D([2, 1]), Point2D([10, -10]), tag="triangle1")
    assert len(sketch.faces) == 1
    assert sketch.faces[0].point1 == Point2D([10, 10])
    assert sketch.faces[0].point2 == Point2D([2, 1])
    assert sketch.faces[0].point3 == Point2D([10, -10])

    sketch.triangle(Point2D([-10, 10]), Point2D([5, 6]), Point2D([-10, -10]), tag="triangle2")
    assert len(sketch.faces) == 2
    assert sketch.faces[1].point1 == Point2D([-10, 10])
    assert sketch.faces[1].point2 == Point2D([5, 6])
    assert sketch.faces[1].point3 == Point2D([-10, -10])

    triangle1_retrieved = sketch.get("triangle1")
    assert len(triangle1_retrieved) == 1
    assert triangle1_retrieved[0] == sketch.faces[0]

    triangle2_retrieved = sketch.get("triangle2")
    assert len(triangle2_retrieved) == 1
    assert triangle2_retrieved[0] == sketch.faces[1]


def test_sketch_trapezoidal_face():
    """Test Trapezoidal Sketchface sketching."""

    # Create a Sketch instance
    sketch = Sketch()

    # Create the sketch face with trapezoid
    sketch.trapezoid(10, 8, np.pi / 4, np.pi / 8, Point2D([10, -10]), tag="trapezoid1")
    assert len(sketch.faces) == 1
    assert sketch.faces[0].width.m == 10
    assert sketch.faces[0].height.m == 8
    assert sketch.faces[0].center == Point2D([10, -10])

    sketch.trapezoid(20, 10, np.pi / 8, np.pi / 16, Point2D([10, -10]), np.pi / 2, tag="trapezoid2")
    assert len(sketch.faces) == 2
    assert sketch.faces[1].width.m == 20
    assert sketch.faces[1].height.m == 10
    assert sketch.faces[1].center == Point2D([10, -10])

    trapezoid1_retrieved = sketch.get("trapezoid1")
    assert len(trapezoid1_retrieved) == 1
    assert trapezoid1_retrieved[0] == sketch.faces[0]

    trapezoid2_retrieved = sketch.get("trapezoid2")
    assert len(trapezoid2_retrieved) == 1
    assert trapezoid2_retrieved[0] == sketch.faces[1]

    # Test the trapezoid errors
    with pytest.raises(ValueError, match="Width must be a real positive value."):
        sketch.trapezoid(
            0, 10, np.pi / 8, np.pi / 16, Point2D([10, -10]), np.pi / 2, tag="trapezoid3"
        )

    with pytest.raises(ValueError, match="Height must be a real positive value."):
        sketch.trapezoid(
            10, -10, np.pi / 8, np.pi / 16, Point2D([10, -10]), np.pi / 2, tag="trapezoid3"
        )


def test_sketch_circle_instance():
    """Test circle instance."""
    center, radius = (
        Point2D([0, 0], DEFAULT_UNITS.LENGTH),
        (1 * DEFAULT_UNITS.LENGTH),
    )
    circle = SketchCircle(center, radius)
    # Check attributes are expected ones
    assert circle.center == center
    assert circle.radius == radius
    assert circle.diameter == 2 * radius
    assert circle.area == np.pi * radius**2
    assert circle.perimeter == 2 * np.pi * radius

    # Test circle on different plane
    center, radius = (
        Point2D([1, 1], DEFAULT_UNITS.LENGTH),
        (1 * DEFAULT_UNITS.LENGTH),
    )
    circle = SketchCircle(
        center, radius, Plane(Point3D([1, 1, 1]), UnitVector3D([-1, 0, 0]), UnitVector3D([0, 0, 1]))
    )

    # Check attributes are expected ones
    assert circle.origin == Point3D([0, 1, 2])
    assert circle.radius == radius
    assert circle.diameter == 2 * radius
    assert circle.area == np.pi * radius**2
    assert circle.perimeter == 2 * np.pi * radius


def test_sketch_circle_instance_errors():
    """Test various circle instantiation errors."""

    with pytest.raises(
        TypeError, match=r"The pint.Unit provided as an input should be a \[length\] quantity."
    ):
        SketchCircle(Point2D([10, 20]), 1 * UNITS.fahrenheit)

    with pytest.raises(ValueError, match="Radius must be a real positive value."):
        SketchCircle(Point2D([10, 20]), -10 * UNITS.mm)


def test_sketch_circle_face():
    """Test circle shape creation in a sketch."""

    # Create a Sketch instance
    sketch = Sketch()

    assert len(sketch.faces) == 0

    # Draw a circle in previous sketch
    center, radius = (
        Point2D([10, -10], DEFAULT_UNITS.LENGTH),
        (1 * DEFAULT_UNITS.LENGTH),
    )
    sketch.circle(center, radius, "Circle")

    # Check attributes are expected ones
    assert len(sketch.faces) == 1
    assert sketch.faces[0].radius == radius
    assert sketch.faces[0].diameter == 2 * radius
    assert sketch.faces[0].area == np.pi * radius**2
    assert sketch.faces[0].perimeter == 2 * np.pi * radius
    assert sketch.faces[0].center == Point2D([10, -10])

    circle_retrieved = sketch.get("Circle")
    assert len(circle_retrieved) == 1
    assert circle_retrieved[0] == sketch.faces[0]


def test_ellipse_instance():
    """Test ellipse instance."""

    semi_major, semi_minor, origin = 2 * UNITS.m, 1 * UNITS.m, Point2D([0, 0], UNITS.m)
    ecc = np.sqrt(1 - (semi_minor / semi_major) ** 2)
    ellipse = SketchEllipse(origin, semi_major, semi_minor)

    # Check attributes are expected ones
    assert ellipse.major_radius == semi_major
    assert ellipse.minor_radius == semi_minor
    assert abs(ellipse.eccentricity - ecc.m) <= DOUBLE_EPS
    assert ellipse.linear_eccentricity == np.sqrt(semi_major**2 - semi_minor**2)
    assert ellipse.semi_latus_rectum == semi_minor**2 / semi_major
    assert abs((ellipse.perimeter - 9.6884482205477 * UNITS.m).m) <= 5e-14
    assert abs((ellipse.area - 6.28318530717959 * UNITS.m * UNITS.m).m) <= 5e-14


def test_ellipse_instance_errors():
    """Test various ellipse instantiation errors."""
    with pytest.raises(
        TypeError, match=r"The pint.Unit provided as an input should be a \[length\] quantity."
    ):
        SketchEllipse(
            Point2D([10, 20]),
            Quantity(1, UNITS.fahrenheit),
            Quantity(56, UNITS.fahrenheit),
        )

    with pytest.raises(
        TypeError, match=r"The pint.Unit provided as an input should be a \[length\] quantity."
    ):
        SketchEllipse(Point2D([10, 20]), 1 * UNITS.m, Quantity(56, UNITS.fahrenheit))

    with pytest.raises(ValueError, match="Major radius must be a real positive value."):
        SketchEllipse(
            Point2D([10, 20]),
            -1 * UNITS.m,
            -3 * UNITS.m,
        )

    with pytest.raises(ValueError, match="Minor radius must be a real positive value."):
        SketchEllipse(
            Point2D([10, 20]),
            1 * UNITS.m,
            -3 * UNITS.m,
        )

    with pytest.raises(ValueError, match="Major radius cannot be shorter than the minor radius."):
        SketchEllipse(
            Point2D([10, 20]),
            1 * UNITS.m,
            3 * UNITS.m,
        )

    ellipse = SketchEllipse(
        Point2D([10, 20]),
        3 * UNITS.m,
        100 * UNITS.cm,
    )


def test_sketch_ellipse_face():
    """Test ellipse shape creation in a sketch."""

    # Create a Sketch instance
    sketch = Sketch()

    assert len(sketch.faces) == 0

    # Draw a circle in previous sketch
    semi_major, semi_minor, origin = 2 * UNITS.m, 1 * UNITS.m, Point2D([0, 0], UNITS.m)
    ecc = np.sqrt(1 - (semi_minor / semi_major) ** 2)
    sketch.ellipse(origin, semi_major, semi_minor, tag="Ellipse")

    # Check attributes are expected ones
    assert len(sketch.faces) == 1
    assert sketch.faces[0].major_radius == semi_major
    assert sketch.faces[0].minor_radius == semi_minor
    assert abs(sketch.faces[0].eccentricity - ecc.m) <= DOUBLE_EPS
    assert sketch.faces[0].linear_eccentricity == np.sqrt(semi_major**2 - semi_minor**2)
    assert sketch.faces[0].semi_latus_rectum == semi_minor**2 / semi_major
    assert abs((sketch.faces[0].perimeter - 9.6884482205477 * UNITS.m).m) <= 5e-14
    assert abs((sketch.faces[0].area - 6.28318530717959 * UNITS.m * UNITS.m).m) <= 5e-14

    ellipse_retrieved = sketch.get("Ellipse")
    assert len(ellipse_retrieved) == 1
    assert ellipse_retrieved[0] == sketch.faces[0]


def test_polygon_instance():
    """Test polygon instance."""

    radius, sides, center = (1 * UNITS.m), 5, Point2D([0, 0], UNITS.m)
    pentagon = Polygon(center, radius, sides)

    # Check attributes are expected ones
    side_length = 2 * radius * np.tan(np.pi / sides)
    assert pentagon.inner_radius == radius
    assert pentagon.n_sides == 5
    assert pentagon.length == side_length
    assert pentagon.perimeter == sides * side_length
    assert pentagon.outer_radius.m == pytest.approx(1.23606798, rel=1e-7, abs=1e-8)

    # Draw a square in previous sketch
    radius, sides, center = (1 * UNITS.m), 4, Point2D([0, 0], UNITS.m)
    square = Polygon(center, radius, sides)

    # Check attributes are expected ones
    side_length = 2 * radius * np.tan(np.pi / sides)  # 2.0 m
    assert square.inner_radius == radius
    assert square.n_sides == 4
    assert square.length == side_length
    assert square.perimeter == sides * side_length
    assert abs(square.area.m - 4.0) <= 1e-15

    with pytest.raises(
        ValueError, match="The minimum number of sides to construct a polygon is three."
    ):
        radius, sides, center = (1 * UNITS.m), 2, Point2D([0, 0], UNITS.m)
        Polygon(center, radius, sides)

    with pytest.raises(ValueError, match="Radius must be a real positive value."):
        radius, sides, center = (-1 * UNITS.m), 6, Point2D([0, 0], UNITS.m)
        Polygon(center, radius, sides)


def test_slot_instance():
    """Test slot instance."""

    center = Point2D([2, 3], unit=UNITS.meter)
    width = Distance(4, unit=UNITS.meter)
    height = Distance(2, unit=UNITS.meter)
    slot = Slot(center, width, height)

    # Validate Real inputs accepted
    Slot(center, 888, 88)

    # Check attributes are expected ones
    assert slot.area.m == pytest.approx(7.141592653589793, rel=1e-7, abs=1e-8)
    assert slot.area.units == UNITS.m * UNITS.m
    perimeter = slot.perimeter
    assert perimeter.m == pytest.approx(10.283185307179586, rel=1e-7, abs=1e-8)
    assert perimeter.units == UNITS.m
    assert slot.center == center
    assert slot.width == Quantity(4, DEFAULT_UNITS.LENGTH)
    assert slot.height == Quantity(2, DEFAULT_UNITS.LENGTH)

    with pytest.raises(ValueError, match="Height must be a real positive value."):
        Slot(center, width, Quantity(-4, DEFAULT_UNITS.LENGTH))

    with pytest.raises(ValueError, match="Width must be a real positive value."):
        Slot(center, Quantity(-4, DEFAULT_UNITS.LENGTH), height)

    with pytest.raises(ValueError, match="Width must be greater than height."):
        Slot(center, width, Quantity(10, DEFAULT_UNITS.LENGTH))


def test_box_instance():
    """Test box instance."""

    center = Point2D([3, 1], unit=UNITS.meter)
    width = Distance(4, unit=UNITS.meter)
    height = Distance(2, unit=UNITS.meter)
    box = Box(center, width, height)

    # Validate Real inputs accepted
    Box(center, 88, 888)

    # Check attributes are expected ones
    assert box.area.m == 8
    assert box.area.units == UNITS.m * UNITS.m
    assert box.perimeter.m == 12
    assert box.perimeter.units == UNITS.m
    assert box.center == center

    with pytest.raises(ValueError, match="Width must be a real positive value."):
        Box(center, Quantity(-4, DEFAULT_UNITS.LENGTH), height)

    with pytest.raises(ValueError, match="Height must be a real positive value."):
        Box(center, width, Quantity(-4, DEFAULT_UNITS.LENGTH))


def test_sketch_plane_translation():
    """Test all methods for sketch plane translation."""

    sketch = Sketch(Plane(Point3D([0, 0, 0], UNITS.mm)))

    sketch.translate_sketch_plane(Vector3D([10, 20, 30]))

    assert sketch.plane.origin == Point3D([10, 20, 30])
    assert sketch.plane.origin.unit == UNITS.mm

    sketch.translate_sketch_plane_by_distance(UnitVector3D([0, 0, 1]), Distance(10, UNITS.cm))

    assert sketch.plane.origin == Point3D([10, 20, 30.1])
    assert sketch.plane.origin.unit == UNITS.mm

    sketch.translate_sketch_plane_by_distance(UnitVector3D([1, 1, 1]), Distance(10, UNITS.cm))

    assert sketch.plane.origin == Point3D(
        [10.05773502691896259, 20.05773502691896259, 30.15773502691896259]
    )
    assert sketch.plane.origin.unit == UNITS.mm

    previous_origin = sketch.plane.origin
    sketch.translate_sketch_plane_by_offset()

    assert sketch.plane.origin == previous_origin
    assert sketch.plane.origin.unit == UNITS.mm

    sketch.translate_sketch_plane_by_offset(x=Distance(10, UNITS.m))
    sketch.translate_sketch_plane_by_offset(y=Distance(20, UNITS.m))
    sketch.translate_sketch_plane_by_offset(z=Distance(30, UNITS.m))

    assert sketch.plane.origin == Point3D(
        [20.05773502691896259, 40.05773502691896259, 60.15773502691896259]
    )
    assert sketch.plane.origin.unit == UNITS.mm

    sketch.translate_sketch_plane_by_offset(
        Quantity(10, UNITS.mm), Quantity(20, UNITS.mm), Quantity(30, UNITS.mm)
    )

    assert sketch.plane.origin == Point3D(
        [20.06773502691896259, 40.07773502691896259, 60.18773502691896259]
    )
    assert sketch.plane.origin.unit == UNITS.mm

    sketch.plane = Plane(Point3D([10, 100, 1000], UNITS.cm))

    assert sketch.plane.origin == Point3D([0.1, 1, 10])
    assert sketch.plane.origin.unit == UNITS.cm


def test_validate_arc():
    """
    Test for performing Arc rotation-sense validation when using PyVista.

    Server-side validation will be done with the body tessellation.
    """
    # =======================================================
    # Validate counterclockwise definition of an arc
    # =======================================================
    #
    # Create a Sketch instance
    sketch = Sketch()

    origin = Point2D([0, 0])
    arc_center = Point2D([0, 0])
    arc_start = Point2D([0, 5])
    arc_end = Point2D([5, 0])

    # Draw the segments
    sketch.segment(origin, arc_start)
    sketch.segment(arc_end, origin)

    # Draw the arc (by default, counterclockwise)
    sketch.arc(arc_start, arc_end, arc_center, clockwise=False)

    # Get the sketch
    pd = sketch.sketch_polydata()
    assert len(pd) == 3

    # Get the third element (arc)
    #
    # Remember, the arc is counterclockwise. Let's put in
    # some imagination to interpret the arc below
    # (arc with straight lines =) )
    #
    #                 - S
    #      Q2       -   |            Q1
    #             -     |
    #           -       |
    #         -         |
    # -------x---------------------E---------
    #         -         |         -
    #           -       |       -
    #      Q3     -     |     -       Q4
    #               -   |   -
    #                 - x -
    #
    # We will check that all Q4 points have a negative Y
    #
    #
    for point in pd[2].points:
        # Ignoring start and end points
        if np.allclose([0, 5, 0], point):
            pass
        elif np.allclose([5, 0, 0], point):
            pass
        # Ignoring negative X points - they can be both positive and negative
        elif point[0] < 0:
            pass
        # Check that if X is positive, we only have negative Y values
        else:  # if point[0] >= 0
            assert point[1] < 0

    # =======================================================
    # Validate clockwise definition of an arc
    # =======================================================
    #
    # Create a Sketch instance
    sketch = Sketch()

    # Draw the segments
    sketch.segment(origin, arc_start)
    sketch.segment(arc_end, origin)

    # Draw the arc (in this case, clockwise)
    sketch.arc(arc_start, arc_end, arc_center, clockwise=True)

    # Get the sketch
    pd = sketch.sketch_polydata()
    assert len(pd) == 3

    # Get the third element (arc)
    #
    # Remember, the arc is clockwise. Let's put in
    # some imagination to interpret the arc below
    # (arc with straight lines =) )
    #
    #                   S -
    #      Q2           |   -         Q1
    #                   |     -
    #                   |       -
    #                   |         -
    # -----------------------------E---------
    #                   |
    #                   |
    #      Q3           |             Q4
    #                   |
    #                   |
    #
    # We will check that all Q1 points have a positive Y
    #
    #
    for point in pd[2].points:
        if np.allclose([0, 5, 0], point):
            pass
        elif np.allclose([5, 0, 0], point):
            pass
        else:  # all points should be in Q1
            assert point[1] > 0


def test_arc():
    """Test arc generation and errors."""

    # Test errors first
    point_0_0 = Point2D([0, 0])
    point_5_0 = Point2D([5, 0])
    point_6_0 = Point2D([6, 0])
    point_0_5 = Point2D([0, 5])
    point_0_m5 = Point2D([0, -5])

    with pytest.raises(ValueError, match="Start and end points must be different."):
        Arc(point_0_0, point_0_5, point_0_5)

    with pytest.raises(ValueError, match="Center and start points must be different."):
        Arc(point_0_0, point_0_0, point_5_0)

    with pytest.raises(ValueError, match="Center and end points must be different."):
        Arc(point_0_0, point_0_5, point_0_0)

    with pytest.raises(ValueError, match="The start and end points of the arc are not"):
        Arc(point_0_0, point_0_5, point_6_0)

    # Let's create a simple arc
    arc = Arc(point_0_0, point_0_5, point_5_0)
    arc_2 = Arc(point_0_0, point_0_5, point_5_0)
    assert arc == arc_2
    assert not (arc != arc_2)

    assert arc.center == point_0_0
    assert arc.start == point_0_5
    assert arc.end == point_5_0
    assert np.isclose(arc.radius.m, 5.0)
    assert arc.radius.units == UNITS.m
    assert np.isclose(arc.angle.m, 3 * np.pi / 2)
    assert arc.angle.units == UNITS.rad

    # Arc length = (2*PI*R) * ang / 2PI = R * ang
    assert np.isclose(arc.length.m, 5 * (3 * np.pi / 2))

    # Sector area = PI * R**2 * (ang / 2PI) =  R**2 * (ang / 2)
    assert np.isclose(arc.sector_area.m, 5**2 * (3 * np.pi / 2) / 2)

    # Validate the PyVista hack for generating the PolyData
    #
    # Needed : 180º arc, counterclockwise
    arc_180 = Arc(point_0_0, point_0_5, point_0_m5, clockwise=False)
    pd = arc_180.visualization_polydata

    # Since the arc is counterclockwise, all X values should be <=0
    for point in pd.points:
        assert point[0] < 0 or np.isclose(point[0], 0)

    # Validate the PyVista hack for generating the PolyData
    #
    # Needed : 180º arc, clockwise
    arc_180 = Arc(point_0_0, point_0_5, point_0_m5, clockwise=True)
    pd = arc_180.visualization_polydata

    # Since the arc is clockwise, all X values should be >=0
    for point in pd.points:
        assert point[0] > 0 or np.isclose(point[0], 0)


def test_arc_from_three_points():
    """Test arc generation from three points."""

    # Fixing start and end points
    start = Point2D([0, 5])
    end = Point2D([5, 0])

    # Case 1: forcing a clockwise arc
    inter = Point2D([2, 4])
    arc = Arc.from_three_points(start, inter, end)
    pd = arc.visualization_polydata
    # Since the arc is clockwise, all X values should be >=0
    for point in pd.points:
        assert point[0] > 0 or np.isclose(point[0], 0)

    # Case 2: forcing a counter-clockwise arc
    inter = Point2D([0, -5])
    arc = Arc.from_three_points(start, inter, end)
    pd = arc.visualization_polydata
    # Since the arc is counter-clockwise, all X values should be <=0 for Y>0
    for point in pd.points:
        if point[1] > 0:
            assert point[0] < 0 or np.isclose(point[0], 0)


def test_polydata_methods():
    sketch = Sketch()
    sketch.polygon(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), sides=5, tag="Polygon1")
    sketch.arc(
        Point2D([10, 10], UNITS.m),
        Point2D([10, -10], UNITS.m),
        Point2D([10, 0], UNITS.m),
        tag="Arc1",
    )
    pd = sketch.sketch_polydata()
    pd_faces = sketch.sketch_polydata_faces()
    pd_edges = sketch.sketch_polydata_edges()
    assert len(pd) == 2
    assert len(pd_edges) == 1
    assert len(pd_faces) == 1
