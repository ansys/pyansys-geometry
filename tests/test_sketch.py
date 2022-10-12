import numpy as np
import pytest

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.math.constants import ZERO_POINT2D
from ansys.geometry.core.math.vector import Vector2D
from ansys.geometry.core.sketch.sketch import Sketch


def test_sketch_segment_edge_creation():
    """Test SketchSegment SketchEdge sketching."""

    # Create a Sketch instance
    sketch = Sketch()

    # fluent api has 0, 0 origin as default start position
    assert len(sketch.edges) == 0
    sketch.segment_to_point(Point2D([2, 3]), "Segment1")
    assert len(sketch.edges) == 1
    assert sketch.edges[0].start == ZERO_POINT2D
    assert sketch.edges[0].end == Point2D([2, 3])
    assert sketch.edges[0].length.m == pytest.approx(3.60555128, rel=1e-7, abs=1e-8)

    # fluent api keeps last edge endpoint as context for new edge
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


def test_sketch_arc_edge_creation():
    """Test SketchArc SketchEdge sketching."""

    # Create a Sketch instance
    sketch = Sketch()

    # fluent api has 0, 0 origin as default start position
    assert len(sketch.edges) == 0
    sketch.arc_to_point(Point2D([3, 3]), Point2D([3, 0]), False, "Arc1")
    assert len(sketch.edges) == 1
    assert sketch.edges[0].start == ZERO_POINT2D
    assert sketch.edges[0].end == Point2D([3, 3])
    assert sketch.edges[0].angle == np.pi / 2

    # fluent api keeps last edge endpoint as context for new edge
    sketch.arc_to_point(Point2D([0, 0]), Point2D([3, 0]), negative_angle=True, tag="Arc2")
    assert len(sketch.edges) == 2
    assert sketch.edges[1].start == Point2D([3, 3])
    assert sketch.edges[1].end == Point2D([0, 0])
    assert sketch.edges[1].angle == 1.5 * np.pi

    sketch.arc(Point2D([10, 10]), Point2D([10, -10]), Point2D([10, 0]), tag="Arc3")
    assert len(sketch.edges) == 3
    assert sketch.edges[2].start == Point2D([10, 10])
    assert sketch.edges[2].end == Point2D([10, -10])
    assert sketch.edges[2].angle == np.pi

    arc1_retrieved = sketch.get("Arc1")
    assert len(arc1_retrieved) == 1
    assert arc1_retrieved[0] == sketch.edges[0]

    arc2_retrieved = sketch.get("Arc2")
    assert len(arc2_retrieved) == 1
    assert arc2_retrieved[0] == sketch.edges[1]

    arc3_retrieved = sketch.get("Arc3")
    assert len(arc3_retrieved) == 1
    assert arc3_retrieved[0] == sketch.edges[2]


def test_sketch_triangle_face_creation():
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


def test_sketch_trapezoidal_face_creation():
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
    with pytest.raises(ValueError, match="Height must be a real positive value."):
        sketch.trapezoid(
            10, -10, np.pi / 8, np.pi / 16, Point2D([10, -10]), np.pi / 2, tag="trapezoid3"
        )

    with pytest.raises(ValueError, match="Width must be greater than height."):
        sketch.trapezoid(
            5, 10, np.pi / 8, np.pi / 16, Point2D([10, -10]), np.pi / 2, tag="trapezoid3"
        )
