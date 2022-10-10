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
    sketch.segment(Point2D([2, 3]), "Segment1")
    assert len(sketch.edges) == 1
    assert sketch.edges[0].start == ZERO_POINT2D
    assert sketch.edges[0].end == Point2D([2, 3])

    # fluent api keeps last edge endpoint as context for new edge
    sketch.segment(Point2D([3, 3]), "Segment2").segment(Point2D([3, 2]), "Segment3")
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
    sketch.segment(Point2D([2, 0]), Vector2D([-1, 1]), "Segment5")
    assert len(sketch.edges) == 5
    assert sketch.edges[4].start == Point2D([2, 0])
    assert sketch.edges[4].end == Point2D([1, 1])

    sketch.segment(Vector2D([-1, -1]), "Segment6")
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
