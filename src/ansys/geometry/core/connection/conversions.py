"""``Conversions`` module."""

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
from ansys.api.geometry.v0.models_pb2 import Tessellation
from beartype.typing import TYPE_CHECKING, List, Optional, Tuple

from ansys.geometry.core.math import Frame, Plane, Point2D, Point3D, UnitVector3D
from ansys.geometry.core.misc import SERVER_UNIT_LENGTH
from ansys.geometry.core.misc.measurements import UNIT_ANGLE
from ansys.geometry.core.sketch import (
    Arc,
    Circle,
    Ellipse,
    Polygon,
    Segment,
    SketchEdge,
    SketchFace,
)

if TYPE_CHECKING:  # pragma: no cover
    from pyvista import PolyData


def unit_vector_to_grpc_direction(unit_vector: UnitVector3D) -> GRPCDirection:
    """Marshals a :class:`UnitVector3D` to a UnitVector gRPC message of the Geometry Service.

    Parameters
    ----------
    unit_vector : UnitVector3D
        Source vector data.

    Returns
    -------
    GRPCDirection
        Geometry Service gRPC Direction message.
    """
    return GRPCDirection(x=unit_vector.x, y=unit_vector.y, z=unit_vector.z)


def frame_to_grpc_frame(frame: Frame) -> GRPCFrame:
    """Marshals a :class:`Frame` to a Frame gRPC message of the Geometry Service.

    Parameters
    ----------
    frame : Frame
        Source frame data.

    Returns
    -------
    GRPCFrame
        Geometry Service gRPC Frame message. Frame origin units in meters.
    """
    return GRPCFrame(
        origin=point3d_to_grpc_point(frame.origin),
        dir_x=unit_vector_to_grpc_direction(frame.direction_x),
        dir_y=unit_vector_to_grpc_direction(frame.direction_y),
    )


def plane_to_grpc_plane(plane: Plane) -> GRPCPlane:
    """Marshals a :class:`Plane` to a Plane gRPC message of the Geometry Service.

    Parameters
    ----------
    plane : Plane
        Source plane data.

    Returns
    -------
    GRPCPlane
        Geometry Service gRPC Plane message, units in meters.
    """
    return GRPCPlane(
        frame=GRPCFrame(
            origin=point3d_to_grpc_point(plane.origin),
            dir_x=unit_vector_to_grpc_direction(plane.direction_x),
            dir_y=unit_vector_to_grpc_direction(plane.direction_y),
        )
    )


def sketch_shapes_to_grpc_geometries(
    plane: Plane,
    edges: List[SketchEdge],
    faces: List[SketchFace],
    only_one_curve: Optional[bool] = False,
) -> Geometries:
    """
    Marshals a list of :class:`SketchEdge` and :class:`SketchFace`
    to a Geometries gRPC message of the Geometry Service.

    Parameters
    ----------
    plane : Plane
        The plane to position the 2D sketches.
    edges : List[SketchEdge]
        Source edge data.
    faces : List[SketchFace]
        Source face data.
    shapes : List[BaseShape]
        Source shape data.
    only_one_curve : Optional[bool]
        Indicates that we only want to project one curve of the whole
        set of geometries, for performance enhancement. By default, ``False``.

    Returns
    -------
    Geometries
        Geometry Service gRPC Geometries message, units in meters.
    """
    geometries = Geometries()

    converted_sketch_edges = sketch_edges_to_grpc_geometries(edges, plane)
    geometries.lines.extend(converted_sketch_edges[0])
    geometries.arcs.extend(converted_sketch_edges[1])

    for face in faces:
        if isinstance(face, Circle):
            geometries.circles.append(sketch_circle_to_grpc_circle(face, plane))
        if isinstance(face, Ellipse):
            geometries.ellipses.append(sketch_ellipse_to_grpc_ellipse(face, plane))
        if isinstance(face, Polygon):
            geometries.polygons.append(sketch_polygon_to_grpc_polygon(face, plane))
        else:
            converted_face_edges = sketch_edges_to_grpc_geometries(face.edges, plane)
            geometries.lines.extend(converted_face_edges[0])
            geometries.arcs.extend(converted_face_edges[1])

    if only_one_curve:
        one_curve_geometry = Geometries()
        if len(geometries.lines) > 0:
            one_curve_geometry.lines.append(geometries.lines[0])
        elif len(geometries.arcs) > 0:
            one_curve_geometry.arcs.append(geometries.arcs[0])
        elif len(geometries.circles) > 0:
            one_curve_geometry.circles.append(geometries.circles[0])
        elif len(geometries.ellipses) > 0:
            one_curve_geometry.ellipses.append(geometries.ellipses[0])
        elif len(geometries.polygons) > 0:
            one_curve_geometry.polygons.append(geometries.polygons[0])
        return one_curve_geometry

    else:
        return geometries


def sketch_edges_to_grpc_geometries(
    edges: List[SketchEdge],
    plane: Plane,
) -> Tuple[List[GRPCLine], List[GRPCArc]]:
    """Marshals a list of :class:`SketchEdge` to a Geometries gRPC message of
    the Geometry Service.

    Parameters
    ----------
    edges : List[SketchEdge]
        Source edge data.
    plane : Plane
        The plane to position the 2D sketches.

    Returns
    -------
    Tuple[List[GRPCLine], List[GRPCArc]]
        Geometry Service gRPC lines and arcs, units in meters.
    """
    arcs = []
    segments = []
    for edge in edges:
        if isinstance(edge, Segment):
            segments.append(sketch_segment_to_grpc_line(edge, plane))
        elif isinstance(edge, Arc):
            arcs.append(sketch_arc_to_grpc_arc(edge, plane))

    return (segments, arcs)


def sketch_arc_to_grpc_arc(arc: Arc, plane: Plane) -> GRPCArc:
    """Marshals an :class:`Arc` to an Arc gRPC message of the Geometry Service.

    Parameters
    ----------
    arc : Arc
        Source arc data.
    plane : Plane
        The plane to position the arc within.

    Returns
    -------
    GRPCArc
        Geometry Service gRPC Arc message, units in meters.
    """
    axis = (
        unit_vector_to_grpc_direction(plane.direction_z)
        if not arc.is_clockwise
        else unit_vector_to_grpc_direction(-plane.direction_z)
    )

    return GRPCArc(
        center=point2d_to_grpc_point(plane, arc.center),
        start=point2d_to_grpc_point(plane, arc.start),
        end=point2d_to_grpc_point(plane, arc.end),
        axis=axis,
    )


def sketch_ellipse_to_grpc_ellipse(ellipse: Ellipse, plane: Plane) -> GRPCEllipse:
    """Marshals an :class:`Ellipse` to an Ellipse gRPC message of the Geometry Service.

    Parameters
    ----------
    ellipse : Ellipse
        Source ellipse data.

    Returns
    -------
    GRPCEllipse
        Geometry Service gRPC Ellipse message, units in meters.
    """
    return GRPCEllipse(
        center=point2d_to_grpc_point(plane, ellipse.center),
        majorradius=ellipse.semi_major_axis.m_as(SERVER_UNIT_LENGTH),
        minorradius=ellipse.semi_minor_axis.m_as(SERVER_UNIT_LENGTH),
        angle=ellipse.angle.value.m_as(UNIT_ANGLE),
    )


def sketch_circle_to_grpc_circle(circle: Circle, plane: Plane) -> GRPCCircle:
    """
    Marshals a :class:`Circle`
    to a Circle gRPC message of the Geometry Service.

    Parameters
    ----------
    circle : Circle
        Source circle data.
    plane : Plane
        The plane to position the 2D circle.

    Returns
    -------
    GRPCCircle
        Geometry Service gRPC Circle message, units in meters.
    """
    return GRPCCircle(
        center=point2d_to_grpc_point(plane, circle.center),
        radius=circle.radius.m_as(SERVER_UNIT_LENGTH),
    )


def point3d_to_grpc_point(point: Point3D) -> GRPCPoint:
    """Marshals a :class:`Point3D` to a Point gRPC message of the Geometry Service.

    Parameters
    ----------
    point : Point3D
        Source point data.

    Returns
    -------
    GRPCPoint
        Geometry Service gRPC Point message, units in meters.
    """
    return GRPCPoint(
        x=point.x.m_as(SERVER_UNIT_LENGTH),
        y=point.y.m_as(SERVER_UNIT_LENGTH),
        z=point.z.m_as(SERVER_UNIT_LENGTH),
    )


def point2d_to_grpc_point(plane: Plane, point2d: Point2D) -> GRPCPoint:
    """
    Marshals a :class:`Point2D`
    to a Point gRPC message of the Geometry Service.

    Parameters
    ----------
    plane : Plane
        The plane to position the 2D point.
    point : Point3D
        Source point data.

    Returns
    -------
    GRPCPoint
        Geometry Service gRPC Point message, units in meters.
    """
    point3d = plane.transform_point2d_local_to_global(point2d)
    return GRPCPoint(
        x=point3d.x.m_as(SERVER_UNIT_LENGTH),
        y=point3d.y.m_as(SERVER_UNIT_LENGTH),
        z=point3d.z.m_as(SERVER_UNIT_LENGTH),
    )


def sketch_polygon_to_grpc_polygon(polygon: Polygon, plane: Plane) -> GRPCPolygon:
    """Marshals a :class:`Polygon` to a Polygon gRPC message of the Geometry Service.

    Parameters
    ----------
    polygon : Polygon
        Source polygon data.

    Returns
    -------
    GRPCPolygon
        Geometry Service gRPC Polygon message, units in meters.
    """
    return GRPCPolygon(
        center=point2d_to_grpc_point(plane, polygon.center),
        radius=polygon.inner_radius.m_as(SERVER_UNIT_LENGTH),
        numberofsides=polygon.n_sides,
        angle=polygon.angle.value.m_as(UNIT_ANGLE),
    )


def sketch_segment_to_grpc_line(segment: Segment, plane: Plane) -> GRPCLine:
    """Marshals a :class:`Segment` to a Line gRPC message of the Geometry Service.

    Parameters
    ----------
    segment : Segment
        Source segment data.

    Returns
    -------
    GRPCLine
        Geometry Service gRPC Line message, units in meters.
    """
    return GRPCLine(
        start=point2d_to_grpc_point(plane, segment.start),
        end=point2d_to_grpc_point(plane, segment.end),
    )


def tess_to_pd(tess: Tessellation) -> "PolyData":
    """Convert a ansys.api.geometry.Tessellation to a :class:`pyvista.PolyData`."""
    # lazy imports here to improve initial load
    import numpy as np
    import pyvista as pv

    return pv.PolyData(np.array(tess.vertices).reshape(-1, 3), tess.faces)
