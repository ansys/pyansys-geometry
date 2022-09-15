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

from ansys.geometry.core.math import Plane, Point, UnitVector
from ansys.geometry.core.misc import SERVER_UNIT_LENGTH
from ansys.geometry.core.shapes import Arc, BaseShape, Circle, Ellipse, Polygon, Segment


def unit_vector_to_grpc_direction(unit_vector: UnitVector) -> GRPCDirection:
    """Marshals a :class:`UnitVector` class to an ansys.api.geometry vector gRPC transfer model.

    Parameters
    ----------
    unit_vector : UnitVector
        Source vector data.

    Returns
    -------
    ansys.api.geometry.v0 Direction model
    """
    return GRPCDirection(x=unit_vector.x, y=unit_vector.y, z=unit_vector.z)


def plane_to_grpc_plane(plane: Plane) -> GRPCPlane:
    """Marshals a :class:`Plane` class to an ansys.api.geometry plane gRPC transfer model.

    Parameters
    ----------
    plan : Plane
        Source plane data.

    Returns
    -------
    ansys.api.geometry.v0 Plane model, units in meters
    """
    return GRPCPlane(
        frame=GRPCFrame(
            origin=point_to_grpc_point(plane.origin),
            dir_x=unit_vector_to_grpc_direction(plane.direction_x),
            dir_y=unit_vector_to_grpc_direction(plane.direction_y),
        )
    )


def sketch_shapes_to_grpc_geometries(shapes: List[BaseShape]) -> Geometries:
    """Marshals a list of :class:`BaseShape` to an ansys.api.geometry geometries gRPC transfer model.

    Parameters
    ----------
    shapes : List[BaseShape]
        Source shape data.

    Returns
    -------
    ansys.api.geometry.v0 Geometries model, units in meters
    """
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
    """Marshals an :class:`Arc` to an ansys.api.geometry arc gRPC transfer model.

    Parameters
    ----------
    arc : Arc
        Source arc data.

    Returns
    -------
    ansys.api.geometry.v0 Arc model, units in meters
    """
    return GRPCArc(
        center=point_to_grpc_point(arc.origin),
        start=point_to_grpc_point(arc.start_point),
        end=point_to_grpc_point(arc.end_point),
    )


def ellipse_to_grpc_ellipse(ellipse: Ellipse) -> GRPCEllipse:
    """Marshals an :class:`Ellipse` to an ansys.api.geometry ellipse gRPC transfer model.

    Parameters
    ----------
    ellipse : Ellipse
        Source ellipse data.

    Returns
    -------
    ansys.api.geometry.v0 Ellipse model, units in meters
    """
    return GRPCEllipse(
        center=point_to_grpc_point(ellipse.center),
        majorradius=ellipse.semi_major_axis.m_as(SERVER_UNIT_LENGTH),
        minorradius=ellipse.semi_minor_axis.m_as(SERVER_UNIT_LENGTH),
    )


def circle_to_grpc_circle(circle: Circle) -> GRPCCircle:
    """Marshals a :class:`Circle` to an ansys.api.geometry circle gRPC transfer model.

    Parameters
    ----------
    circle : Circle
        Source circle data.

    Returns
    -------
    ansys.api.geometry.v0 Circle model, units in meters
    """
    return GRPCCircle(
        center=point_to_grpc_point(circle.center),
        radius=circle.radius.m_as(SERVER_UNIT_LENGTH),
    )


def point_to_grpc_point(point: Point) -> GRPCPoint:
    """Marshals a :class:`Point` to an ansys.api.geometry point gRPC transfer model.

    Parameters
    ----------
    point : Point
        Source point data.

    Returns
    -------
    ansys.api.geometry.v0 Point model, units in meters
    """
    return GRPCPoint(
        x=point.x.m_as(SERVER_UNIT_LENGTH),
        y=point.y.m_as(SERVER_UNIT_LENGTH),
        z=point.z.m_as(SERVER_UNIT_LENGTH),
    )


def polygon_to_grpc_polygon(polygon: Polygon) -> GRPCPolygon:
    """Marshals a :class:`Polygon` to an ansys.api.geometry polygon gRPC transfer model.

    Parameters
    ----------
    polygon : Polygon
        Source polygon data.

    Returns
    -------
    ansys.api.geometry.v0 Polygon model, units in meters
    """
    return GRPCPolygon(
        center=point_to_grpc_point(polygon.origin),
        radius=polygon.inner_radius.m_as(SERVER_UNIT_LENGTH),
        numberofsides=polygon.n_sides,
    )


def segment_to_grpc_line(line: Segment) -> GRPCLine:
    """Marshals a :class:`Segment` to an ansys.api.geometry line gRPC transfer model.

    Parameters
    ----------
    segment : Segment
        Source segment data.

    Returns
    -------
    ansys.api.geometry.v0 Line model, units in meters
    """
    return GRPCLine(
        start=point_to_grpc_point(line.start),
        end=point_to_grpc_point(line.end),
    )
