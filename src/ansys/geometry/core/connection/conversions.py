"""Provides the ``Conversions`` module."""

from ansys.api.geometry.v0.models_pb2 import Arc as GRPCArc
from ansys.api.geometry.v0.models_pb2 import Circle as GRPCCircle
from ansys.api.geometry.v0.models_pb2 import Direction as GRPCDirection
from ansys.api.geometry.v0.models_pb2 import Ellipse as GRPCEllipse
from ansys.api.geometry.v0.models_pb2 import Frame as GRPCFrame
from ansys.api.geometry.v0.models_pb2 import Geometries
from ansys.api.geometry.v0.models_pb2 import Line as GRPCLine
from ansys.api.geometry.v0.models_pb2 import Matrix as GRPCMatrix
from ansys.api.geometry.v0.models_pb2 import Plane as GRPCPlane
from ansys.api.geometry.v0.models_pb2 import Point as GRPCPoint
from ansys.api.geometry.v0.models_pb2 import Polygon as GRPCPolygon
from ansys.api.geometry.v0.models_pb2 import Tessellation
from beartype.typing import TYPE_CHECKING, List, Optional, Tuple

from ansys.geometry.core.math import Frame, Matrix44, Plane, Point2D, Point3D, UnitVector3D
from ansys.geometry.core.misc import DEFAULT_UNITS
from ansys.geometry.core.sketch import (
    Arc,
    Polygon,
    SketchCircle,
    SketchEdge,
    SketchEllipse,
    SketchFace,
    SketchSegment,
)

if TYPE_CHECKING:  # pragma: no cover
    from pyvista import PolyData


def unit_vector_to_grpc_direction(unit_vector: UnitVector3D) -> GRPCDirection:
    """
    Marshals a ``UnitVector3D`` class to a unit vector Geometry service gRPC message.

    Parameters
    ----------
    unit_vector : UnitVector3D
        Source vector data.

    Returns
    -------
    GRPCDirection
        Geometry service gRPC direction message.
    """
    return GRPCDirection(x=unit_vector.x, y=unit_vector.y, z=unit_vector.z)


def frame_to_grpc_frame(frame: Frame) -> GRPCFrame:
    """
    Marshals a ``Frame`` class to a frame Geometry service gRPC message.

    Parameters
    ----------
    frame : Frame
        Source frame data.

    Returns
    -------
    GRPCFrame
        Geometry service gRPC frame message. The unit for the frame origin is meters.
    """
    return GRPCFrame(
        origin=point3d_to_grpc_point(frame.origin),
        dir_x=unit_vector_to_grpc_direction(frame.direction_x),
        dir_y=unit_vector_to_grpc_direction(frame.direction_y),
    )


def plane_to_grpc_plane(plane: Plane) -> GRPCPlane:
    """
    Marshals a ``Plane`` class to a plane Geometry service gRPC message.

    Parameters
    ----------
    plane : Plane
        Source plane data.

    Returns
    -------
    GRPCPlane
        Geometry service gRPC plane message. The unit is meters.
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
    Marshals a list of ``SketchEdge`` and ``SketchFace`` to a geometries gRPC message.

    Parameters
    ----------
    plane : Plane
        Plane for positioning the 2D sketches.
    edges : List[SketchEdge]
        Source edge data.
    faces : List[SketchFace]
        Source face data.
    shapes : List[BaseShape]
        Source shape data.
    only_one_curve : bool, default: False
        Whether to project one curve of the whole set of geometries to
        enhance performance.

    Returns
    -------
    Geometries
        Geometry service gRPC geometries message. The unit is meters.
    """
    geometries = Geometries()

    converted_sketch_edges = sketch_edges_to_grpc_geometries(edges, plane)
    geometries.lines.extend(converted_sketch_edges[0])
    geometries.arcs.extend(converted_sketch_edges[1])

    for face in faces:
        if isinstance(face, SketchCircle):
            geometries.circles.append(sketch_circle_to_grpc_circle(face, plane))
        if isinstance(face, SketchEllipse):
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
    """
    Marshals a list of ``SketchEdge`` to a geometries gRPC message.

    Parameters
    ----------
    edges : List[SketchEdge]
        Source edge data.
    plane : Plane
        Plane for positioning the 2D sketches.

    Returns
    -------
    Tuple[List[GRPCLine], List[GRPCArc]]
        Geometry service gRPC line and arc messages. The unit is meters.
    """
    arcs = []
    segments = []
    for edge in edges:
        if isinstance(edge, SketchSegment):
            segments.append(sketch_segment_to_grpc_line(edge, plane))
        elif isinstance(edge, Arc):
            arcs.append(sketch_arc_to_grpc_arc(edge, plane))

    return (segments, arcs)


def sketch_arc_to_grpc_arc(arc: Arc, plane: Plane) -> GRPCArc:
    """
    Marshals an ``Arc`` class to an arc Geometry service gRPC message.

    Parameters
    ----------
    arc : Arc
        Source arc data.
    plane : Plane
        Plane for positioning the arc within.

    Returns
    -------
    GRPCArc
        Geometry service gRPC arc message. The unit is meters.
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


def sketch_ellipse_to_grpc_ellipse(ellipse: SketchEllipse, plane: Plane) -> GRPCEllipse:
    """
    Marshals a ``SketchEllipse`` class to an ellipse Geometry service gRPC message.

    Parameters
    ----------
    ellipse : SketchEllipse
        Source ellipse data.

    Returns
    -------
    GRPCEllipse
        Geometry service gRPC ellipse message. The unit is meters.
    """
    return GRPCEllipse(
        center=point2d_to_grpc_point(plane, ellipse.center),
        majorradius=ellipse.major_radius.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        minorradius=ellipse.minor_radius.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        angle=ellipse.angle.m_as(DEFAULT_UNITS.SERVER_ANGLE),
    )


def sketch_circle_to_grpc_circle(circle: SketchCircle, plane: Plane) -> GRPCCircle:
    """
    Marshals a ``SketchCircle`` class to a circle Geometry service gRPC message.

    Parameters
    ----------
    circle : SketchCircle
        Source circle data.
    plane : Plane
        Plane for positioning the circle.

    Returns
    -------
    GRPCCircle
        Geometry service gRPC circle message. The unit is meters.
    """
    return GRPCCircle(
        center=point2d_to_grpc_point(plane, circle.center),
        radius=circle.radius.m_as(DEFAULT_UNITS.SERVER_LENGTH),
    )


def point3d_to_grpc_point(point: Point3D) -> GRPCPoint:
    """
    Marshals a ``Point3D`` class to a point Geometry service gRPC message.

    Parameters
    ----------
    point : Point3D
        Source point data.

    Returns
    -------
    GRPCPoint
        Geometry service gRPC point message. The unit is meters.
    """
    return GRPCPoint(
        x=point.x.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        y=point.y.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        z=point.z.m_as(DEFAULT_UNITS.SERVER_LENGTH),
    )


def point2d_to_grpc_point(plane: Plane, point2d: Point2D) -> GRPCPoint:
    """
    Marshals a ``Point2D`` class to a point Geometry service gRPC message.

    Parameters
    ----------
    plane : Plane
        Plane for positioning the 2D point.
    point : Point2D
        Source point data.

    Returns
    -------
    GRPCPoint
        Geometry service gRPC point message. The unit is meters.
    """
    point3d = plane.transform_point2d_local_to_global(point2d)
    return GRPCPoint(
        x=point3d.x.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        y=point3d.y.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        z=point3d.z.m_as(DEFAULT_UNITS.SERVER_LENGTH),
    )


def sketch_polygon_to_grpc_polygon(polygon: Polygon, plane: Plane) -> GRPCPolygon:
    """
    Marshals a ``Polygon`` class to a polygon Geometry service gRPC message.

    Parameters
    ----------
    polygon : Polygon
        Source polygon data.

    Returns
    -------
    GRPCPolygon
        Geometry service gRPC polygon message. The unit is meters.
    """
    return GRPCPolygon(
        center=point2d_to_grpc_point(plane, polygon.center),
        radius=polygon.inner_radius.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        numberofsides=polygon.n_sides,
        angle=polygon.angle.m_as(DEFAULT_UNITS.SERVER_ANGLE),
    )


def sketch_segment_to_grpc_line(segment: SketchSegment, plane: Plane) -> GRPCLine:
    """
    Marshals a ``Segment`` class to a line Geometry service gRPC message.

    Parameters
    ----------
    segment : SketchSegment
        Source segment data.

    Returns
    -------
    GRPCLine
        Geometry service gRPC line message. The unit is meters.
    """
    return GRPCLine(
        start=point2d_to_grpc_point(plane, segment.start),
        end=point2d_to_grpc_point(plane, segment.end),
    )


def tess_to_pd(tess: Tessellation) -> "PolyData":
    """Convert an ``ansys.api.geometry.Tessellation`` class to a `pyvista.PolyData` class."""
    # lazy imports here to improve initial load
    import numpy as np
    import pyvista as pv

    return pv.PolyData(np.array(tess.vertices).reshape(-1, 3), tess.faces)


def grpc_matrix_to_matrix(m: GRPCMatrix) -> Matrix44:
    """Convert an ``ansys.api.geometry.Matrix`` class to a `ansys.geometry.core.math.Matrix44` class."""  # noqa: E501
    import numpy as np

    return Matrix44(
        np.round(
            [
                [m.m00, m.m01, m.m02, m.m03],
                [m.m10, m.m11, m.m12, m.m13],
                [m.m20, m.m21, m.m22, m.m23],
                [m.m30, m.m31, m.m32, m.m33],
            ],
            8,
        )
    )


def grpc_frame_to_frame(frame: GRPCFrame) -> Frame:
    """Convert an ``ansys.api.geometry.Frame`` grpc message to a ``Frame`` class.

    Parameters
    ----------
    GRPCFrame
        Geometry service gRPC frame message. The unit for the frame origin is meters.

    Returns
    -------
    frame : Frame
        Resulting converted frame.
    """
    return Frame(
        Point3D(
            [
                frame.origin.x,
                frame.origin.y,
                frame.origin.z,
            ],
            DEFAULT_UNITS.SERVER_LENGTH,
        ),
        UnitVector3D(
            [
                frame.dir_x.x,
                frame.dir_x.y,
                frame.dir_x.z,
            ]
        ),
        UnitVector3D(
            [
                frame.dir_y.x,
                frame.dir_y.y,
                frame.dir_y.z,
            ]
        ),
    )
