"""``Conversions`` module."""

from typing import TYPE_CHECKING, List, Tuple

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

from ansys.geometry.core.math import Frame, Plane, Point3D, UnitVector3D
from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.misc import SERVER_UNIT_LENGTH
from ansys.geometry.core.shapes import Arc, BaseShape, Circle, Ellipse, Polygon, Segment
from ansys.geometry.core.sketch.arc import SketchArc
from ansys.geometry.core.sketch.circle import SketchCircle
from ansys.geometry.core.sketch.edge import SketchEdge
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.segment import SketchSegment
from ansys.geometry.core.sketch.trapezoid import Trapezoid
from ansys.geometry.core.sketch.triangle import Triangle
from ansys.geometry.core.typing import Real

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
    return vector_components_to_grpc_direction(unit_vector.x, unit_vector.y, unit_vector.z)


def vector_components_to_grpc_direction(x: Real, y: Real, z: Real) -> GRPCDirection:
    """Marshals vector components to Direction gRPC message of the Geometry Service.

    Parameters
    ----------
    x : Real
        Source vector x component.
    y : Real
        Source vector y component.
    z : Real
        Source vector z component.

    Returns
    -------
    GRPCDirection
        Geometry Service gRPC Direction message.
    """
    return GRPCDirection(x=x, y=y, z=z)


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
        origin=point_to_grpc_point(frame.origin),
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
            origin=point_to_grpc_point(plane.origin),
            dir_x=unit_vector_to_grpc_direction(plane.direction_x),
            dir_y=unit_vector_to_grpc_direction(plane.direction_y),
        )
    )


def one_profile_shape_to_grpc_geometries(
    plane: Plane,
    edges: List[SketchEdge],
    faces: List[SketchFace],
    shapes: List[BaseShape],
) -> Geometries:
    """Marshals a list of :class:`SketchEdge` and :class:`SketchFace` to
    a Geometries gRPC message of the Geometry Service.

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

    Returns
    -------
    Geometries
        Geometry Service gRPC Geometries message, units in meters.
    """
    geometries = Geometries()

    if len(edges) > 0:
        converted_sketch_edges = sketch_edges_to_grpc_geometries(plane, [edges[0]])
        geometries.lines.extend(converted_sketch_edges[0])
        geometries.arcs.extend(converted_sketch_edges[1])

    if len(edges) == 0 and len(faces) > 0:
        for face in faces:
            if isinstance(face, SketchCircle):
                geometries.circles.append(sketch_circle_to_grpc_circle(face, plane))
                break
            if isinstance(face, Triangle) or isinstance(face, Trapezoid):
                converted_face_edges = sketch_edges_to_grpc_geometries(plane, face.edges)
                geometries.lines.extend(converted_face_edges[0])
                geometries.arcs.extend(converted_face_edges[1])
                break

    if len(edges) == 0 and len(faces) == 0:
        for shape in shapes:
            for component_shape in shape.components:
                if isinstance(component_shape, Circle):
                    geometries.circles.append(circle_to_grpc_circle(component_shape))
                    break
                elif isinstance(component_shape, Segment):
                    geometries.lines.append(segment_to_grpc_line(component_shape))
                    break
                elif isinstance(component_shape, Arc):
                    geometries.arcs.append(arc_to_grpc_arc(component_shape))
                    break
                elif isinstance(component_shape, Ellipse):
                    geometries.ellipses.append(ellipse_to_grpc_ellipse(component_shape))
                    break
                elif isinstance(component_shape, Polygon):
                    geometries.polygons.append(polygon_to_grpc_polygon(component_shape))
                    break

    return geometries


def sketch_shapes_to_grpc_geometries(
    plane: Plane,
    edges: List[SketchEdge],
    faces: List[SketchFace],
    shapes: List[BaseShape],
) -> Geometries:
    """Marshals a list of :class:`BaseShape` to a Geometries gRPC message of
    the Geometry Service.

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

    Returns
    -------
    Geometries
        Geometry Service gRPC Geometries message, units in meters.
    """
    geometries = Geometries()

    converted_sketch_edges = sketch_edges_to_grpc_geometries(plane, edges)
    geometries.lines.extend(converted_sketch_edges[0])
    geometries.arcs.extend(converted_sketch_edges[1])

    for face in faces:
        if isinstance(face, SketchCircle):
            geometries.circles.append(sketch_circle_to_grpc_circle(face, plane))
        if isinstance(face, Triangle) or isinstance(face, Trapezoid):
            converted_face_edges = sketch_edges_to_grpc_geometries(plane, face.edges)
            geometries.lines.extend(converted_face_edges[0])
            geometries.arcs.extend(converted_face_edges[1])

    for shape in shapes:
        for component_shape in shape.components:
            if isinstance(component_shape, Circle):
                geometries.circles.append(circle_to_grpc_circle(component_shape))
            elif isinstance(component_shape, Segment):
                geometries.lines.append(segment_to_grpc_line(component_shape))
            elif isinstance(component_shape, Arc):
                geometries.arcs.append(arc_to_grpc_arc(component_shape))
            elif isinstance(component_shape, Ellipse):
                geometries.ellipses.append(ellipse_to_grpc_ellipse(component_shape))
            elif isinstance(component_shape, Polygon):
                geometries.polygons.append(polygon_to_grpc_polygon(component_shape))

    return geometries


def sketch_edges_to_grpc_geometries(
    plane: Plane, edges: List[SketchEdge]
) -> Tuple[List[GRPCLine], List[GRPCArc]]:
    """Marshals a list of :class:`SketchEdge` to a Geometries gRPC message of
    the Geometry Service.

    Parameters
    ----------
    plane : Plane
        The plane to position the 2D sketches.
    edges : List[SketchEdge]
        Source edge data.

    Returns
    -------
    Tuple[List[GRPCLine], List[GRPCArc]]
        Geometry Service gRPC lines and arcs, units in meters.
    """
    arcs = []
    segments = []
    for edge in edges:
        if isinstance(edge, SketchSegment):
            segments.append(sketch_segment_to_grpc_line(edge, plane))
        elif isinstance(edge, SketchArc):
            arcs.append(sketch_arc_to_grpc_arc(edge, plane))

    return (segments, arcs)


def arc_to_grpc_arc(arc: Arc) -> GRPCArc:
    """Marshals an :class:`Arc` to an Arc gRPC message of the Geometry Service.

    Parameters
    ----------
    arc : Arc
        Source arc data.

    Returns
    -------
    GRPCArc
        Geometry Service gRPC Arc message, units in meters.
    """
    return GRPCArc(
        center=point_to_grpc_point(arc.center),
        start=point_to_grpc_point(arc.start),
        end=point_to_grpc_point(arc.end),
        axis=unit_vector_to_grpc_direction(arc.axis),
    )


def sketch_arc_to_grpc_arc(arc: SketchArc, plane: Plane) -> GRPCArc:
    """Marshals an :class:`SketchArc` to an Arc gRPC message of the Geometry Service.

    Parameters
    ----------
    arc : SketchArc
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
        if arc.positive_rotation_axis
        else vector_components_to_grpc_direction(
            -plane.direction_z.x, -plane.direction_z.y, -plane.direction_z.z
        )
    )

    return GRPCArc(
        center=point2D_to_grpc_point(plane, arc.center),
        start=point2D_to_grpc_point(plane, arc.start),
        end=point2D_to_grpc_point(plane, arc.end),
        axis=axis,
    )


def ellipse_to_grpc_ellipse(ellipse: Ellipse) -> GRPCEllipse:
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
        center=point_to_grpc_point(ellipse.center),
        majorradius=ellipse.semi_major_axis.m_as(SERVER_UNIT_LENGTH),
        minorradius=ellipse.semi_minor_axis.m_as(SERVER_UNIT_LENGTH),
    )


def circle_to_grpc_circle(circle: Circle) -> GRPCCircle:
    """Marshals a :class:`Circle` to a Circle gRPC message of the Geometry Service.

    Parameters
    ----------
    circle : Circle
        Source circle data.

    Returns
    -------
    GRPCCircle
        Geometry Service gRPC Circle message, units in meters.
    """
    return GRPCCircle(
        center=point_to_grpc_point(circle.center), radius=circle.radius.m_as(SERVER_UNIT_LENGTH)
    )


def sketch_circle_to_grpc_circle(circle: SketchCircle, plane: Plane) -> GRPCCircle:
    """
    Marshals a :class:`SketchCircle`
    to a Circle gRPC message of the Geometry Service.

    Parameters
    ----------
    circle : SketchCircle
        Source circle data.
    plane : Plane
        The plane to position the 2D circle.

    Returns
    -------
    GRPCCircle
        Geometry Service gRPC Circle message, units in meters.
    """
    return GRPCCircle(
        center=point2D_to_grpc_point(plane, circle.center),
        radius=circle.radius.m_as(SERVER_UNIT_LENGTH),
    )


def point_to_grpc_point(point: Point3D) -> GRPCPoint:
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


def point2D_to_grpc_point(plane: Plane, point2d: Point2D) -> GRPCPoint:
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
    point3d = plane.transform_point2D_global_to_local(point2d)
    return GRPCPoint(
        x=point3d.x.m_as(SERVER_UNIT_LENGTH),
        y=point3d.y.m_as(SERVER_UNIT_LENGTH),
        z=point3d.z.m_as(SERVER_UNIT_LENGTH),
    )


def polygon_to_grpc_polygon(polygon: Polygon) -> GRPCPolygon:
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
        center=point_to_grpc_point(polygon.center),
        radius=polygon.inner_radius.m_as(SERVER_UNIT_LENGTH),
        numberofsides=polygon.n_sides,
    )


def segment_to_grpc_line(line: Segment) -> GRPCLine:
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
        start=point_to_grpc_point(line.start),
        end=point_to_grpc_point(line.end),
    )


def sketch_segment_to_grpc_line(segment: SketchSegment, plane: Plane) -> GRPCLine:
    """Marshals a :class:`SketchSegment` to a Line gRPC message of the Geometry Service.

    Parameters
    ----------
    segment : SketchSegment
        Source segment data.

    Returns
    -------
    GRPCLine
        Geometry Service gRPC Line message, units in meters.
    """
    return GRPCLine(
        start=point2D_to_grpc_point(plane, segment.start),
        end=point2D_to_grpc_point(plane, segment.end),
    )


def tess_to_pd(tess: Tessellation) -> "PolyData":
    """Convert a ansys.api.geometry.Tessellation to a :class:`pyvista.PolyData`."""
    # lazy imports here to improve initial load
    import numpy as np
    import pyvista as pv

    return pv.PolyData(np.array(tess.vertices).reshape(-1, 3), tess.faces)
