# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.

from beartype.roar import BeartypeCallHintParamViolation
import grpc
import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core.connection.client import GrpcClient, wait_until_healthy
from ansys.geometry.core.connection.conversions import (
    frame_to_grpc_frame,
    plane_to_grpc_plane,
    point2d_to_grpc_point,
    point3d_to_grpc_point,
    sketch_arc_to_grpc_arc,
    sketch_circle_to_grpc_circle,
    sketch_ellipse_to_grpc_ellipse,
    sketch_polygon_to_grpc_polygon,
    sketch_segment_to_grpc_line,
    unit_vector_to_grpc_direction,
)
from ansys.geometry.core.math import Frame, Plane, Point2D, Point3D, UnitVector3D
from ansys.geometry.core.misc import UNITS, Angle
from ansys.geometry.core.sketch import Arc, Polygon, SketchCircle, SketchEllipse, SketchSegment


def test_wait_until_healthy():
    """Test checking that a channel is unhealthy."""
    # create a bogus channel
    channel = grpc.insecure_channel("9.0.0.1:80")
    with pytest.raises(TimeoutError):
        wait_until_healthy(channel, timeout=1)


def test_invalid_inputs():
    """Test checking that the input provided is a channel."""
    with pytest.raises(BeartypeCallHintParamViolation):
        GrpcClient(host=123)
    with pytest.raises(BeartypeCallHintParamViolation):
        GrpcClient(port=None)
    with pytest.raises(BeartypeCallHintParamViolation):
        GrpcClient(channel="a")
    with pytest.raises(BeartypeCallHintParamViolation):
        GrpcClient(timeout="a")


def test_circle_message_conversion():
    """Test conversion between :class: `SketchCircle
    <ansys.geometry.core.sketch.circle.SketchCircle>` and expected gRPC message type."""
    circle = SketchCircle(
        Point2D([10, 100], UNITS.mm),
        Quantity(300, UNITS.mm),
    )
    grpc_circle_message = sketch_circle_to_grpc_circle(
        circle, Plane(Point3D([10, 100, 1000], UNITS.mm))
    )

    assert grpc_circle_message.center.x == 0.02
    assert grpc_circle_message.center.y == 0.2
    assert grpc_circle_message.center.z == 1.0
    assert grpc_circle_message.radius == 0.3


def test_ellipse_message_conversion():
    """Test conversion between :class:`SketchEllipse <
    ansys.geometry.core.sketch.ellipse.SketchEllipse>` and expected gRPC message
    type."""
    ellipse = SketchEllipse(
        Point2D([10, 100], UNITS.mm),
        Quantity(300, UNITS.mm),
        Quantity(50, UNITS.mm),
    )
    grpc_ellipse_message = sketch_ellipse_to_grpc_ellipse(
        ellipse, Plane(Point3D([10, 100, 1000], UNITS.mm))
    )

    assert grpc_ellipse_message.center.x == 0.02
    assert grpc_ellipse_message.center.y == 0.2
    assert grpc_ellipse_message.center.z == 1.0
    assert grpc_ellipse_message.majorradius == 0.3
    assert grpc_ellipse_message.minorradius == 0.05
    assert grpc_ellipse_message.angle == 0

    rotated_ellipse = SketchEllipse(
        Point2D([10, 100], UNITS.mm),
        Quantity(300, UNITS.mm),
        Quantity(50, UNITS.mm),
        angle=Angle(45, UNITS.degrees),
    )
    rotated_grpc_ellipse_message = sketch_ellipse_to_grpc_ellipse(
        rotated_ellipse, Plane(Point3D([10, 100, 1000], UNITS.mm))
    )

    assert rotated_grpc_ellipse_message.center.x == 0.02
    assert rotated_grpc_ellipse_message.center.y == 0.2
    assert rotated_grpc_ellipse_message.center.z == 1.0
    assert rotated_grpc_ellipse_message.majorradius == 0.3
    assert rotated_grpc_ellipse_message.minorradius == 0.05
    assert rotated_grpc_ellipse_message.angle == np.pi / 4


def test_segment_message_conversion():
    """Test conversion between :class: `SketchSegment
    <ansys.geometry.core.sketch.segment.SketchSegment>` and expected gRPC message
    type."""
    segment = SketchSegment(
        Point2D([30, 400], UNITS.mm),
        Point2D([500, 600], UNITS.mm),
    )
    grpc_line_message = sketch_segment_to_grpc_line(
        segment, Plane(Point3D([10, 100, 1000], UNITS.mm))
    )

    assert grpc_line_message.start.x == 0.04
    assert grpc_line_message.start.y == 0.5
    assert grpc_line_message.start.z == 1.0
    assert grpc_line_message.end.x == 0.51
    assert grpc_line_message.end.y == pytest.approx(0.7000000000000001, 1e-8, 1e-8)
    assert grpc_line_message.end.z == 1.0


def test_polygon_message_conversion():
    """Test conversion between :class:`Polygon
    <ansys.geometry.core.sketch.polygon.Polygon>` and expected gRPC message type."""
    polygon = Polygon(
        Point2D([10, 100], UNITS.mm),
        Quantity(300, UNITS.mm),
        5,
    )
    grpc_polygon_message = sketch_polygon_to_grpc_polygon(
        polygon, Plane(Point3D([10, 100, 1000], UNITS.mm))
    )

    assert grpc_polygon_message.center.x == 0.02
    assert grpc_polygon_message.center.y == 0.2
    assert grpc_polygon_message.center.z == 1.0
    assert grpc_polygon_message.radius == 0.3
    assert grpc_polygon_message.numberofsides == 5
    assert grpc_polygon_message.angle == 0

    rotated_polygon = Polygon(
        Point2D([10, 100], UNITS.mm), Quantity(300, UNITS.mm), 5, angle=Angle(45, UNITS.degrees)
    )
    rotated_grpc_polygon_message = sketch_polygon_to_grpc_polygon(
        rotated_polygon, Plane(Point3D([10, 100, 1000], UNITS.mm))
    )

    assert rotated_grpc_polygon_message.center.x == 0.02
    assert rotated_grpc_polygon_message.center.y == 0.2
    assert rotated_grpc_polygon_message.center.z == 1.0
    assert rotated_grpc_polygon_message.radius == 0.3
    assert rotated_grpc_polygon_message.numberofsides == 5
    assert rotated_grpc_polygon_message.angle == np.pi / 4


def test_point3d_message_conversion():
    """Test conversion between :class:`Point3D <ansys.geometry.core.math.point.Point3D>`
    and expected gRPC message type."""
    point = Point3D([10, 100, 1000], UNITS.mm)
    grpc_point_message = point3d_to_grpc_point(point)

    assert grpc_point_message.x == 0.01
    assert grpc_point_message.y == 0.1
    assert grpc_point_message.z == 1.0


def test_point2d_message_conversion():
    """Test conversion between :class:`Point2D` and expected gRPC message type."""
    point = Point2D([10, 100], UNITS.mm)
    grpc_point_message = point2d_to_grpc_point(Plane(Point3D([10, 100, 1000], UNITS.mm)), point)

    assert grpc_point_message.x == 0.02
    assert grpc_point_message.y == 0.2
    assert grpc_point_message.z == 1.0


def test_unit_vector_message_conversion():
    """Test conversion between :class:`UnitVector3D
    <ansys.geometry.core.math.vector.unitVector3D>` and expected gRPC message type."""
    unit_vector = UnitVector3D([1, 1, 1])
    grpc_unit_vector_message = unit_vector_to_grpc_direction(unit_vector)

    assert grpc_unit_vector_message.x == 0.5773502691896258
    assert grpc_unit_vector_message.y == 0.5773502691896258
    assert grpc_unit_vector_message.z == 0.5773502691896258


def test_arc_message_conversion():
    """Test conversion between :class:`Arc <ansys.geometry.core.sketch.arc.Arc>` and
    expected gRPC message type."""
    arc = Arc(
        Point2D([500, 600], UNITS.mm),
        Point2D([100, 400], UNITS.mm),
        Point2D([900, 800], UNITS.mm),
    )
    grpc_arc_message = sketch_arc_to_grpc_arc(arc, Plane(Point3D([10, 100, 1000], UNITS.mm)))

    assert grpc_arc_message.center.x == 0.51
    assert grpc_arc_message.center.y == pytest.approx(0.7000000000000001, 1e-8, 1e-8)
    assert grpc_arc_message.center.z == 1.0

    assert grpc_arc_message.start.x == 0.11
    assert grpc_arc_message.start.y == 0.5
    assert grpc_arc_message.start.z == 1.0

    assert grpc_arc_message.end.x == 0.91
    assert grpc_arc_message.end.y == 0.9
    assert grpc_arc_message.end.z == 1.0

    assert grpc_arc_message.axis.x == 0
    assert grpc_arc_message.axis.y == 0
    assert grpc_arc_message.axis.z == 1

    arc2 = Arc(
        Point2D([600, 700], UNITS.mm),
        Point2D([200, 500], UNITS.mm),
        Point2D([1000, 900], UNITS.mm),
        True,
    )
    grpc_arc_message2 = sketch_arc_to_grpc_arc(arc2, Plane(Point3D([10, 100, 1000], UNITS.mm)))

    assert grpc_arc_message2.center.x == 0.61
    assert grpc_arc_message2.center.y == pytest.approx(0.8000000000000002, 1e-8, 1e-8)
    assert grpc_arc_message2.center.z == 1.0

    assert grpc_arc_message2.start.x == pytest.approx(0.21000000000000002, 1e-8, 1e-8)
    assert grpc_arc_message2.start.y == 0.6
    assert grpc_arc_message2.start.z == 1.0

    assert grpc_arc_message2.end.x == 1.01
    assert grpc_arc_message2.end.y == 1.0
    assert grpc_arc_message2.end.z == 1.0

    assert grpc_arc_message2.axis.x == 0
    assert grpc_arc_message2.axis.y == 0
    assert grpc_arc_message2.axis.z == -1


def test_plane_message_conversion():
    """Test conversion between :class:`Plane <ansys.geometry.core.math.plane.Plane>` and
    expected gRPC message type."""
    plane = Plane(
        Point3D([10, 200, 3000], UNITS.mm), UnitVector3D([1, 1, 0]), UnitVector3D([1, -1, 0])
    )
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
    """Test conversion between :class:`Frame <ansys.geometry.core.math.frame.Frame>` and
    expected gRPC message type."""
    frame = Frame(
        Point3D([10, 200, 3000], UNITS.mm), UnitVector3D([1, 1, 0]), UnitVector3D([1, -1, 0])
    )
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
