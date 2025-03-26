# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module containing v0 related conversions from PyAnsys Geometry objects to gRPC messages."""

from typing import TYPE_CHECKING

import pint

from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
from ansys.api.geometry.v0.models_pb2 import (
    Arc as GRPCArc,
    Circle as GRPCCircle,
    Direction as GRPCDirection,
    Ellipse as GRPCEllipse,
    Frame as GRPCFrame,
    Geometries as GRPCGeometries,
    Line as GRPCLine,
    Material as GRPCMaterial,
    MaterialProperty as GRPCMaterialProperty,
    Plane as GRPCPlane,
    Point as GRPCPoint,
    Polygon as GRPCPolygon,
    Tessellation,
    TessellationOptions as GRPCTessellationOptions,
)
from ansys.geometry.core.materials.material import Material
from ansys.geometry.core.materials.property import MaterialProperty, MaterialPropertyType
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc.checks import graphics_required
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS
from ansys.geometry.core.misc.options import TessellationOptions
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.sketch.arc import Arc
from ansys.geometry.core.sketch.circle import SketchCircle
from ansys.geometry.core.sketch.edge import SketchEdge
from ansys.geometry.core.sketch.ellipse import SketchEllipse
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.polygon import Polygon
from ansys.geometry.core.sketch.segment import SketchSegment

if TYPE_CHECKING:
    import pyvista as pv


def from_point3d_to_grpc_point(point: Point3D) -> GRPCPoint:
    """Convert a ``Point3D`` class to a point gRPC message.

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


def from_grpc_point_to_point3d(point: GRPCPoint) -> Point3D:
    """Convert a point gRPC message class to a ``Point3D`` class.

    Parameters
    ----------
    point : GRPCPoint
        Source point data.

    Returns
    -------
    Point3D
        Converted point.
    """
    return Point3D(
        [point.x, point.y, point.z],
        DEFAULT_UNITS.SERVER_LENGTH,
    )


def from_point2d_to_grpc_point(plane: Plane, point2d: Point2D) -> GRPCPoint:
    """Convert a ``Point2D`` class to a point gRPC message.

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


def from_unit_vector_to_grpc_direction(unit_vector: UnitVector3D) -> GRPCDirection:
    """Convert a ``UnitVector3D`` class to a unit vector gRPC message.

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


def build_grpc_id(id: str) -> EntityIdentifier:
    """Build an EntityIdentifier gRPC message.

    Parameters
    ----------
    id : str
        Source ID.

    Returns
    -------
    EntityIdentifier
        Geometry service gRPC entity identifier message.
    """
    return EntityIdentifier(id=id)


def from_grpc_material_to_material(material: GRPCMaterial) -> Material:
    """Convert a material gRPC message to a ``Material`` class.

    Parameters
    ----------
    material : GRPCMaterial
        Material gRPC message.

    Returns
    -------
    Material
        Converted material.
    """
    properties = []
    density = pint.Quantity(0, UNITS.kg / UNITS.m**3)
    for property in material.material_properties:
        mp = from_grpc_material_property_to_material_property(property)
        properties.append(mp)
        if mp.type == MaterialPropertyType.DENSITY:
            density = mp.quantity

    return Material(material.name, density, properties)


def from_grpc_material_property_to_material_property(
    material_property: GRPCMaterialProperty,
) -> MaterialProperty:
    """Convert a material property gRPC message to a ``MaterialProperty`` class.

    Parameters
    ----------
    material_property : GRPCMaterialProperty
        Material property gRPC message.

    Returns
    -------
    MaterialProperty
        Converted material property.
    """
    try:
        mp_type = MaterialPropertyType.from_id(material_property.id)
    except ValueError:
        mp_type = material_property.id

    try:
        mp_quantity = pint.Quantity(material_property.value, material_property.units)
    except (
        pint.UndefinedUnitError,
        TypeError,
    ):
        mp_quantity = material_property.value

    return MaterialProperty(mp_type, material_property.display_name, mp_quantity)


def from_frame_to_grpc_frame(frame: Frame) -> GRPCFrame:
    """Convert a ``Frame`` class to a frame gRPC message.

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
        origin=from_point3d_to_grpc_point(frame.origin),
        dir_x=from_unit_vector_to_grpc_direction(frame.direction_x),
        dir_y=from_unit_vector_to_grpc_direction(frame.direction_y),
    )


def from_plane_to_grpc_plane(plane: Plane) -> GRPCPlane:
    """Convert a ``Plane`` class to a plane gRPC message.

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
            origin=from_point3d_to_grpc_point(plane.origin),
            dir_x=from_unit_vector_to_grpc_direction(plane.direction_x),
            dir_y=from_unit_vector_to_grpc_direction(plane.direction_y),
        )
    )


@graphics_required
def from_grpc_tess_to_pd(tess: Tessellation) -> "pv.PolyData":
    """Convert an ``ansys.api.geometry.Tessellation`` to ``pyvista.PolyData``."""
    # lazy imports here to improve initial load
    import numpy as np
    import pyvista as pv

    return pv.PolyData(var_inp=np.array(tess.vertices).reshape(-1, 3), faces=tess.faces)


def from_tess_options_to_grpc_tess_options(options: TessellationOptions) -> GRPCTessellationOptions:
    """Convert a ``TessellationOptions`` class to a tessellation options gRPC message.

    Parameters
    ----------
    options : TessellationOptions
        Source tessellation options data.

    Returns
    -------
    GRPCTessellationOptions
        Geometry service gRPC tessellation options message.
    """
    return GRPCTessellationOptions(
        surface_deviation=options.surface_deviation,
        angle_deviation=options.angle_deviation,
        maximum_aspect_ratio=options.max_aspect_ratio,
        maximum_edge_length=options.max_edge_length,
        watertight=options.watertight,
    )


def from_sketch_shapes_to_grpc_geometries(
    plane: Plane,
    edges: list[SketchEdge],
    faces: list[SketchFace],
    only_one_curve: bool = False,
) -> GRPCGeometries:
    """Convert lists of ``SketchEdge`` and ``SketchFace`` to a gRPC message.

    Parameters
    ----------
    plane : Plane
        Plane for positioning the 2D sketches.
    edges : list[SketchEdge]
        Source edge data.
    faces : list[SketchFace]
        Source face data.
    only_one_curve : bool, default: False
        Whether to project one curve of the whole set of geometries to
        enhance performance.

    Returns
    -------
    GRPCGeometries
        Geometry service gRPC geometries message. The unit is meters.
    """
    geometries = GRPCGeometries()

    converted_sketch_edges = from_sketch_edges_to_grpc_geometries(edges, plane)
    geometries.lines.extend(converted_sketch_edges[0])
    geometries.arcs.extend(converted_sketch_edges[1])

    for face in faces:
        if isinstance(face, SketchCircle):
            geometries.circles.append(from_sketch_circle_to_grpc_circle(face, plane))
        if isinstance(face, SketchEllipse):
            geometries.ellipses.append(from_sketch_ellipse_to_grpc_ellipse(face, plane))
        if isinstance(face, Polygon):
            geometries.polygons.append(from_sketch_polygon_to_grpc_polygon(face, plane))
        else:
            converted_face_edges = from_sketch_edges_to_grpc_geometries(face.edges, plane)
            geometries.lines.extend(converted_face_edges[0])
            geometries.arcs.extend(converted_face_edges[1])

    if only_one_curve:
        one_curve_geometry = GRPCGeometries()
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


def from_sketch_edges_to_grpc_geometries(
    edges: list[SketchEdge],
    plane: Plane,
) -> tuple[list[GRPCLine], list[GRPCArc]]:
    """Convert a list of ``SketchEdge`` to a gRPC message.

    Parameters
    ----------
    edges : list[SketchEdge]
        Source edge data.
    plane : Plane
        Plane for positioning the 2D sketches.

    Returns
    -------
    tuple[list[GRPCLine], list[GRPCArc]]
        Geometry service gRPC line and arc messages. The unit is meters.
    """
    arcs = []
    segments = []
    for edge in edges:
        if isinstance(edge, SketchSegment):
            segments.append(from_sketch_segment_to_grpc_line(edge, plane))
        elif isinstance(edge, Arc):
            arcs.append(from_sketch_arc_to_grpc_arc(edge, plane))

    return (segments, arcs)


def from_sketch_arc_to_grpc_arc(arc: Arc, plane: Plane) -> GRPCArc:
    """Convert an ``Arc`` class to an arc gRPC message.

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
        from_unit_vector_to_grpc_direction(plane.direction_z)
        if not arc.is_clockwise
        else from_unit_vector_to_grpc_direction(-plane.direction_z)
    )

    return GRPCArc(
        center=from_point2d_to_grpc_point(plane, arc.center),
        start=from_point2d_to_grpc_point(plane, arc.start),
        end=from_point2d_to_grpc_point(plane, arc.end),
        axis=axis,
    )


def from_sketch_ellipse_to_grpc_ellipse(ellipse: SketchEllipse, plane: Plane) -> GRPCEllipse:
    """Convert a ``SketchEllipse`` class to an ellipse gRPC message.

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
        center=from_point2d_to_grpc_point(plane, ellipse.center),
        majorradius=ellipse.major_radius.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        minorradius=ellipse.minor_radius.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        angle=ellipse.angle.m_as(DEFAULT_UNITS.SERVER_ANGLE),
    )


def from_sketch_circle_to_grpc_circle(circle: SketchCircle, plane: Plane) -> GRPCCircle:
    """Convert a ``SketchCircle`` class to a circle gRPC message.

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
        center=from_point2d_to_grpc_point(plane, circle.center),
        radius=circle.radius.m_as(DEFAULT_UNITS.SERVER_LENGTH),
    )


def from_sketch_polygon_to_grpc_polygon(polygon: Polygon, plane: Plane) -> GRPCPolygon:
    """Convert a ``Polygon`` class to a polygon gRPC message.

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
        center=from_point2d_to_grpc_point(plane, polygon.center),
        radius=polygon.inner_radius.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        numberofsides=polygon.n_sides,
        angle=polygon.angle.m_as(DEFAULT_UNITS.SERVER_ANGLE),
    )


def from_sketch_segment_to_grpc_line(segment: SketchSegment, plane: Plane) -> GRPCLine:
    """Convert a ``Segment`` class to a line gRPC message.

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
        start=from_point2d_to_grpc_point(plane, segment.start),
        end=from_point2d_to_grpc_point(plane, segment.end),
    )
