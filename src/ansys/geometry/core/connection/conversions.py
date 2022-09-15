"""``Conversions`` module."""

from typing import List

from ansys.api.geometry.v0.models_pb2 import Arc as GRPCArc
from ansys.api.geometry.v0.models_pb2 import Circle as GRPCCircle
from ansys.api.geometry.v0.models_pb2 import Direction as GRPCDirection
from ansys.api.geometry.v0.models_pb2 import Ellipse as GRPCEllipse
from ansys.api.geometry.v0.models_pb2 import Frame as GRPCFrame
from ansys.api.geometry.v0.models_pb2 import Geometries
from ansys.api.geometry.v0.models_pb2 import Line as GRPCLine
from ansys.api.geometry.v0.models_pb2 import Plane as GRPCPlane
from ansys.api.geometry.v0.models_pb2 import Point as GRPCPoint
from ansys.api.geometry.v0.models_pb2 import Polygon as GRPCPolygon

from ansys.geometry.core.math import Plane, Point, Vector
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.shapes import Arc, BaseShape, Circle, Ellipse, Polygon, Segment


def vector_to_direction(vector: Vector) -> GRPCDirection:
    return GRPCDirection(x=vector.x, y=vector.y, z=vector.z)


def plane_to_grpc_plane(plane: Plane) -> GRPCPlane:
    return GRPCPlane(
        frame=GRPCFrame(
            origin=point_to_grpc_point(plane.origin),
            dir_x=vector_to_direction(plane.direction_x),
            dir_y=vector_to_direction(plane.direction_y),
        )
    )


def sketch_shapes_to_grpc_geometries(shapes: List[BaseShape]) -> Geometries:
    geometries = Geometries()
    for shape in shapes:
        if isinstance(shape, Circle):
            geometries.circles.append(circle_to_grpc_circle(shape))
        elif isinstance(shape, Segment):
            geometries.lines.append(segment_to_grpc_line(shape))
        elif isinstance(shape, Arc):
            geometries.arcs.append(arc_to_grpc_arc(shape))
        elif isinstance(shape, Ellipse):
            geometries.ellipses.append(ellipse_to_grpc_ellipse(shape))
        elif isinstance(shape, Polygon):
            geometries.polygons.append(polygon_to_grpc_polygon(shape))

    return geometries


def arc_to_grpc_arc(arc: Arc) -> GRPCArc:
    """Returns a grpc arc with default units of m."""
    return GRPCArc(
        center=point_to_grpc_point(arc.origin),
        start=point_to_grpc_point(arc.start_point),
        end=point_to_grpc_point(arc.end_point),
    )


def ellipse_to_grpc_ellipse(ellipse: Ellipse) -> GRPCEllipse:
    """Returns a grpc ellipse with default units of m."""
    return GRPCEllipse(
        center=point_to_grpc_point(ellipse.origin),
        majorradius=ellipse.semi_major_axis.m_as(UNITS.m),
        minorradius=ellipse.semi_minor_axis.m_as(UNITS.m),
    )


def circle_to_grpc_circle(circle: Circle) -> GRPCCircle:
    """Returns a grpc circle with default units of m."""
    return GRPCCircle(
        center=point_to_grpc_point(circle.origin),
        radius=circle.radius.m_as(UNITS.m),
    )


def point_to_grpc_point(point: Point) -> GRPCPoint:
    """Returns a grpc point with default units of m."""
    return GRPCPoint(
        x=point.x.m_as(UNITS.m),
        y=point.y.m_as(UNITS.m),
        z=point.z.m_as(UNITS.m),
    )


def polygon_to_grpc_polygon(polygon: Polygon) -> GRPCPolygon:
    """Returns a grpc polygon with default units of m."""
    return GRPCPolygon(
        center=point_to_grpc_point(polygon.origin),
        radius=polygon.inner_radius.m_as(UNITS.m),
        numberofsides=polygon.n_sides,
    )


def segment_to_grpc_line(line: Segment) -> GRPCLine:
    """Returns a grpc line with default units of m."""
    return GRPCLine(
        start=point_to_grpc_point(line.start),
        end=point_to_grpc_point(line.end),
    )
