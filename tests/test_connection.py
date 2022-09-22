import grpc
from pint import Quantity
import pytest

from ansys.geometry.core.connection.client import GrpcClient, wait_until_healthy
from ansys.geometry.core.connection.conversions import (
    arc_to_grpc_arc,
    circle_to_grpc_circle,
    ellipse_to_grpc_ellipse,
    frame_to_grpc_frame,
    plane_to_grpc_plane,
    point_to_grpc_point,
    polygon_to_grpc_polygon,
    segment_to_grpc_line,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.math import Frame, Plane, Point, UnitVector
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.shapes import Arc, Circle, Ellipse, Polygon, Segment


def test_wait_until_healthy():
    """Test checking that a channel is unhealthy."""
    # create a bogus channel
    channel = grpc.insecure_channel("9.0.0.1:80")
    with pytest.raises(TimeoutError):
        wait_until_healthy(channel, timeout=1)


def test_invalid_inputs():
    """Test checking that the input provided is a channel."""
    with pytest.raises(TypeError, match="Provided type"):
        GrpcClient(host=123)
    with pytest.raises(TypeError, match="Provided type"):
        GrpcClient(port=None)
    with pytest.raises(TypeError, match="Provided type"):
        GrpcClient(channel="a")
    with pytest.raises(TypeError, match="Provided type"):
        GrpcClient(timeout="a")


def test_circle_message_conversion():
    """Test conversion between :class:`Circle` and expected gRPC message type."""
    circle = Circle(
        Plane(Point([10, 100, 1000], UNITS.mm)),
        Point([10, 100, 1000], UNITS.mm),
        Quantity(300, UNITS.mm),
    )
    grpc_circle_message = circle_to_grpc_circle(circle)

    assert grpc_circle_message.center.x == 0.01
    assert grpc_circle_message.center.y == 0.1
    assert grpc_circle_message.center.z == 1.0
    assert grpc_circle_message.radius == 0.3


def test_ellipse_message_conversion():
    """Test conversion between :class:`Ellipse` and expected gRPC message type."""
    ellipse = Ellipse(
        Plane(Point([10, 100, 1000], UNITS.mm)),
        Point([10, 100, 1000], UNITS.mm),
        Quantity(300, UNITS.mm),
        Quantity(50, UNITS.mm),
    )
    grpc_ellipse_message = ellipse_to_grpc_ellipse(ellipse)

    assert grpc_ellipse_message.center.x == 0.01
    assert grpc_ellipse_message.center.y == 0.1
    assert grpc_ellipse_message.center.z == 1.0
    assert grpc_ellipse_message.majorradius == 0.3
    assert grpc_ellipse_message.minorradius == 0.05


def test_segment_message_conversion():
    """Test conversion between :class:`Segment` and expected gRPC message type."""
    segment = Segment(
        Plane(Point([10, 100, 1000], UNITS.mm)),
        Point([30, 400, 1000], UNITS.mm),
        Point([500, 600, 1000], UNITS.mm),
    )
    grpc_line_message = segment_to_grpc_line(segment)

    assert grpc_line_message.start.x == 0.03
    assert grpc_line_message.start.y == 0.4
    assert grpc_line_message.start.z == 1.0
    assert grpc_line_message.end.x == 0.5
    assert grpc_line_message.end.y == 0.6
    assert grpc_line_message.end.z == 1.0


def test_polygon_message_conversion():
    """Test conversion between :class:`Polygon` and expected gRPC message type."""
    polygon = Polygon(
        Plane(Point([10, 100, 1000], UNITS.mm)),
        Point([10, 100, 1000], UNITS.mm),
        Quantity(300, UNITS.mm),
        5,
    )
    grpc_polygon_message = polygon_to_grpc_polygon(polygon)

    assert grpc_polygon_message.center.x == 0.01
    assert grpc_polygon_message.center.y == 0.1
    assert grpc_polygon_message.center.z == 1.0
    assert grpc_polygon_message.radius == 0.3
    assert grpc_polygon_message.numberofsides == 5


def test_point_message_conversion():
    """Test conversion between :class:`Point` and expected gRPC message type."""
    point = Point([10, 100, 1000], UNITS.mm)
    grpc_point_message = point_to_grpc_point(point)

    assert grpc_point_message.x == 0.01
    assert grpc_point_message.y == 0.1
    assert grpc_point_message.z == 1.0


def test_unit_vector_message_conversion():
    """Test conversion between :class:`UnitVector` and expected gRPC message type."""
    unit_vector = UnitVector([1, 1, 1])
    grpc_unit_vector_message = unit_vector_to_grpc_direction(unit_vector)

    assert grpc_unit_vector_message.x == 0.5773502691896258
    assert grpc_unit_vector_message.y == 0.5773502691896258
    assert grpc_unit_vector_message.z == 0.5773502691896258


def test_arc_message_conversion():
    """Test conversion between :class:`Arc` and expected gRPC message type."""
    arc = Arc(
        Plane(Point([10, 100, 1000], UNITS.mm)),
        Point([30, 400, 1000], UNITS.mm),
        Point([500, 600, 1000], UNITS.mm),
        Point([900, 800, 1000], UNITS.mm),
        UnitVector([0, 0, 1]),
    )
    grpc_arc_message = arc_to_grpc_arc(arc)

    assert grpc_arc_message.center.x == 0.03
    assert grpc_arc_message.center.y == 0.4
    assert grpc_arc_message.center.z == 1.0

    assert grpc_arc_message.start.x == 0.5
    assert grpc_arc_message.start.y == 0.6
    assert grpc_arc_message.start.z == 1.0

    assert grpc_arc_message.end.x == 0.9
    assert grpc_arc_message.end.y == 0.8
    assert grpc_arc_message.end.z == 1.0

    assert grpc_arc_message.axis.x == 0
    assert grpc_arc_message.axis.y == 0
    assert grpc_arc_message.axis.z == 1


def test_plane_message_conversion():
    """Test conversion between :class:`Plane` and expected gRPC message type."""
    plane = Plane(Point([10, 200, 3000], UNITS.mm), UnitVector([1, 1, 0]), UnitVector([1, -1, 0]))
    grpc_plane_message = plane_to_grpc_plane(plane)

    assert grpc_plane_message.frame.origin.x == 0.01
    assert grpc_plane_message.frame.origin.y == 0.2
    assert grpc_plane_message.frame.origin.z == 3.0

    assert grpc_plane_message.frame.dir_x.x == pytest.approx(0.7071067811865475, rel=1e-7, abs=1e-8)
    assert grpc_plane_message.frame.dir_x.y == pytest.approx(0.7071067811865475, rel=1e-7, abs=1e-8)
    assert grpc_plane_message.frame.dir_x.z == 0.0

    assert grpc_plane_message.frame.dir_y.x == pytest.approx(0.7071067811865475, rel=1e-7, abs=1e-8)
    assert grpc_plane_message.frame.dir_y.y == pytest.approx(
        -0.7071067811865475, rel=1e-7, abs=1e-8
    )
    assert grpc_plane_message.frame.dir_y.z == 0.0


def test_frame_message_conversion():
    """Test conversion between :class:`Frame` and expected gRPC message type."""
    frame = Frame(Point([10, 200, 3000], UNITS.mm), UnitVector([1, 1, 0]), UnitVector([1, -1, 0]))
    grpc_frame_message = frame_to_grpc_frame(frame)

    assert grpc_frame_message.origin.x == 0.01
    assert grpc_frame_message.origin.y == 0.2
    assert grpc_frame_message.origin.z == 3.0

    assert grpc_frame_message.dir_x.x == pytest.approx(0.7071067811865475, rel=1e-7, abs=1e-8)
    assert grpc_frame_message.dir_x.y == pytest.approx(0.7071067811865475, rel=1e-7, abs=1e-8)
    assert grpc_frame_message.dir_x.z == 0.0

    assert grpc_frame_message.dir_y.x == pytest.approx(0.7071067811865475, rel=1e-7, abs=1e-8)
    assert grpc_frame_message.dir_y.y == pytest.approx(-0.7071067811865475, rel=1e-7, abs=1e-8)
    assert grpc_frame_message.dir_y.z == 0.0
