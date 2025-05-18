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

from ansys.api.dbu.v0.admin_pb2 import BackendType as GRPCBackendType
from ansys.api.dbu.v0.dbumodels_pb2 import (
    DrivingDimension as GRPCDrivingDimension,
    EntityIdentifier,
    PartExportFormat as GRPCPartExportFormat,
)
from ansys.api.dbu.v0.drivingdimensions_pb2 import UpdateStatus as GRPCUpdateStatus
from ansys.api.geometry.v0.models_pb2 import (
    Arc as GRPCArc,
    Circle as GRPCCircle,
    CurveGeometry as GRPCCurveGeometry,
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
    Surface as GRPCSurface,
    SurfaceType as GRPCSurfaceType,
    Tessellation as GRPCTessellation,
    TessellationOptions as GRPCTessellationOptions,
    TrimmedCurve as GRPCTrimmedCurve,
    TrimmedSurface as GRPCTrimmedSurface,
)
from ansys.geometry.core.misc.checks import graphics_required

if TYPE_CHECKING:  # pragma: no cover
    import pyvista as pv

    from ansys.geometry.core.connection.backend import BackendType
    from ansys.geometry.core.designer.design import DesignFileFormat
    from ansys.geometry.core.materials.material import Material
    from ansys.geometry.core.materials.property import MaterialProperty
    from ansys.geometry.core.math.frame import Frame
    from ansys.geometry.core.math.plane import Plane
    from ansys.geometry.core.math.point import Point2D, Point3D
    from ansys.geometry.core.math.vector import UnitVector3D
    from ansys.geometry.core.misc.options import TessellationOptions
    from ansys.geometry.core.parameters.parameter import (
        Parameter,
        ParameterUpdateStatus,
    )
    from ansys.geometry.core.shapes.curves.curve import Curve
    from ansys.geometry.core.shapes.curves.trimmed_curve import TrimmedCurve
    from ansys.geometry.core.shapes.surfaces.surface import Surface
    from ansys.geometry.core.shapes.surfaces.trimmed_surface import TrimmedSurface
    from ansys.geometry.core.sketch.arc import Arc
    from ansys.geometry.core.sketch.circle import SketchCircle
    from ansys.geometry.core.sketch.edge import SketchEdge
    from ansys.geometry.core.sketch.ellipse import SketchEllipse
    from ansys.geometry.core.sketch.face import SketchFace
    from ansys.geometry.core.sketch.polygon import Polygon
    from ansys.geometry.core.sketch.segment import SketchSegment


def from_point3d_to_grpc_point(point: "Point3D") -> GRPCPoint:
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
    from ansys.geometry.core.misc.measurements import DEFAULT_UNITS

    return GRPCPoint(
        x=point.x.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        y=point.y.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        z=point.z.m_as(DEFAULT_UNITS.SERVER_LENGTH),
    )


def from_grpc_point_to_point3d(point: GRPCPoint) -> "Point3D":
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
    from ansys.geometry.core.math.point import Point3D
    from ansys.geometry.core.misc.measurements import DEFAULT_UNITS

    return Point3D(
        [point.x, point.y, point.z],
        DEFAULT_UNITS.SERVER_LENGTH,
    )


def from_point2d_to_grpc_point(plane: "Plane", point2d: "Point2D") -> GRPCPoint:
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
    from ansys.geometry.core.misc.measurements import DEFAULT_UNITS

    point3d = plane.transform_point2d_local_to_global(point2d)
    return GRPCPoint(
        x=point3d.x.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        y=point3d.y.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        z=point3d.z.m_as(DEFAULT_UNITS.SERVER_LENGTH),
    )


def from_unit_vector_to_grpc_direction(unit_vector: "UnitVector3D") -> GRPCDirection:
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


def from_grpc_material_to_material(material: GRPCMaterial) -> "Material":
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
    from ansys.geometry.core.materials.material import Material
    from ansys.geometry.core.materials.property import MaterialPropertyType
    from ansys.geometry.core.misc.units import UNITS

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
) -> "MaterialProperty":
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
    from ansys.geometry.core.materials.property import MaterialProperty, MaterialPropertyType

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


def from_frame_to_grpc_frame(frame: "Frame") -> GRPCFrame:
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


def from_grpc_frame_to_frame(frame: GRPCFrame) -> "Frame":
    """Convert a frame gRPC message to a ``Frame`` class.

    Parameters
    ----------
    frame : GRPCFrame
        Source frame data.

    Returns
    -------
    Frame
        Converted frame.
    """
    from ansys.geometry.core.math.frame import Frame
    from ansys.geometry.core.math.point import Point3D
    from ansys.geometry.core.math.vector import UnitVector3D
    from ansys.geometry.core.misc.measurements import DEFAULT_UNITS

    return Frame(
        Point3D(
            input=[
                frame.origin.x,
                frame.origin.y,
                frame.origin.z,
            ],
            unit=DEFAULT_UNITS.SERVER_LENGTH,
        ),
        UnitVector3D(
            input=[
                frame.dir_x.x,
                frame.dir_x.y,
                frame.dir_x.z,
            ]
        ),
        UnitVector3D(
            input=[
                frame.dir_y.x,
                frame.dir_y.y,
                frame.dir_y.z,
            ]
        ),
    )


def from_plane_to_grpc_plane(plane: "Plane") -> GRPCPlane:
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
def from_grpc_tess_to_pd(tess: GRPCTessellation) -> "pv.PolyData":
    """Convert a ``Tessellation`` to ``pyvista.PolyData``."""
    # lazy imports here to improve initial load
    import numpy as np
    import pyvista as pv

    return pv.PolyData(var_inp=np.array(tess.vertices).reshape(-1, 3), faces=tess.faces)


def from_tess_options_to_grpc_tess_options(
    options: "TessellationOptions",
) -> GRPCTessellationOptions:
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
    plane: "Plane",
    edges: list["SketchEdge"],
    faces: list["SketchFace"],
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
    from ansys.geometry.core.sketch.circle import SketchCircle
    from ansys.geometry.core.sketch.ellipse import SketchEllipse
    from ansys.geometry.core.sketch.polygon import Polygon

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
    edges: list["SketchEdge"],
    plane: "Plane",
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
    from ansys.geometry.core.sketch.arc import Arc
    from ansys.geometry.core.sketch.segment import SketchSegment

    arcs = []
    segments = []
    for edge in edges:
        if isinstance(edge, SketchSegment):
            segments.append(from_sketch_segment_to_grpc_line(edge, plane))
        elif isinstance(edge, Arc):
            arcs.append(from_sketch_arc_to_grpc_arc(edge, plane))

    return (segments, arcs)


def from_sketch_arc_to_grpc_arc(arc: "Arc", plane: "Plane") -> GRPCArc:
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


def from_sketch_ellipse_to_grpc_ellipse(ellipse: "SketchEllipse", plane: "Plane") -> GRPCEllipse:
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
    from ansys.geometry.core.misc.measurements import DEFAULT_UNITS

    return GRPCEllipse(
        center=from_point2d_to_grpc_point(plane, ellipse.center),
        majorradius=ellipse.major_radius.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        minorradius=ellipse.minor_radius.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        angle=ellipse.angle.m_as(DEFAULT_UNITS.SERVER_ANGLE),
    )


def from_sketch_circle_to_grpc_circle(circle: "SketchCircle", plane: "Plane") -> GRPCCircle:
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
    from ansys.geometry.core.misc.measurements import DEFAULT_UNITS

    return GRPCCircle(
        center=from_point2d_to_grpc_point(plane, circle.center),
        radius=circle.radius.m_as(DEFAULT_UNITS.SERVER_LENGTH),
    )


def from_sketch_polygon_to_grpc_polygon(polygon: "Polygon", plane: "Plane") -> GRPCPolygon:
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
    from ansys.geometry.core.misc.measurements import DEFAULT_UNITS

    return GRPCPolygon(
        center=from_point2d_to_grpc_point(plane, polygon.center),
        radius=polygon.inner_radius.m_as(DEFAULT_UNITS.SERVER_LENGTH),
        numberofsides=polygon.n_sides,
        angle=polygon.angle.m_as(DEFAULT_UNITS.SERVER_ANGLE),
    )


def from_sketch_segment_to_grpc_line(segment: "SketchSegment", plane: "Plane") -> GRPCLine:
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


def from_trimmed_curve_to_grpc_trimmed_curve(curve: "TrimmedCurve") -> GRPCTrimmedCurve:
    """Convert a ``TrimmedCurve`` to a trimmed curve gRPC message.

    Parameters
    ----------
    curve : TrimmedCurve
        Curve to convert.

    Returns
    -------
    GRPCTrimmedCurve
        Geometry service gRPC ``TrimmedCurve`` message.
    """
    curve_geometry = from_curve_to_grpc_curve(curve.geometry)
    i_start = curve.interval.start
    i_end = curve.interval.end

    return GRPCTrimmedCurve(
        curve=curve_geometry,
        interval_start=i_start,
        interval_end=i_end,
    )


def from_curve_to_grpc_curve(curve: "Curve") -> GRPCCurveGeometry:
    """Convert a ``Curve`` object to a curve gRPC message.

    Parameters
    ----------
    curve : Curve
        Curve to convert.

    Returns
    -------
    GRPCCurve
        Return ``Curve`` as a ``ansys.api.geometry.CurveGeometry`` message.
    """
    from ansys.geometry.core.shapes.curves.circle import Circle
    from ansys.geometry.core.shapes.curves.ellipse import Ellipse
    from ansys.geometry.core.shapes.curves.line import Line

    grpc_curve = None

    if isinstance(curve, Line):
        origin = from_point3d_to_grpc_point(curve.origin)
        direction = from_unit_vector_to_grpc_direction(curve.direction)
        grpc_curve = GRPCCurveGeometry(origin=origin, direction=direction)
    elif isinstance(curve, (Circle, Ellipse)):
        origin = from_point3d_to_grpc_point(curve.origin)
        reference = from_unit_vector_to_grpc_direction(curve.dir_x)
        axis = from_unit_vector_to_grpc_direction(curve.dir_z)

        if isinstance(curve, Circle):
            grpc_curve = GRPCCurveGeometry(
                origin=origin, reference=reference, axis=axis, radius=curve.radius.m
            )
        elif isinstance(curve, Ellipse):
            grpc_curve = GRPCCurveGeometry(
                origin=origin,
                reference=reference,
                axis=axis,
                major_radius=curve.major_radius.m,
                minor_radius=curve.minor_radius.m,
            )
    else:
        raise ValueError(f"Unsupported curve type: {type(curve)}")

    return grpc_curve


def from_grpc_curve_to_curve(curve: GRPCCurveGeometry) -> "Curve":
    """Convert a curve gRPC message to a ``Curve``.

    Parameters
    ----------
    curve : GRPCCurve
        Geometry service gRPC curve message.

    Returns
    -------
    Curve
        Resulting converted curve.
    """
    from ansys.geometry.core.shapes.curves.circle import Circle
    from ansys.geometry.core.shapes.curves.ellipse import Ellipse
    from ansys.geometry.core.shapes.curves.line import Line

    origin = Point3D([curve.origin.x, curve.origin.y, curve.origin.z])
    try:
        reference = UnitVector3D([curve.reference.x, curve.reference.y, curve.reference.z])
        axis = UnitVector3D([curve.axis.x, curve.axis.y, curve.axis.z])
    except ValueError:
        # curve will be a line
        pass
    if curve.radius != 0:
        result = Circle(origin, curve.radius, reference, axis)
    elif curve.major_radius != 0 and curve.minor_radius != 0:
        result = Ellipse(origin, curve.major_radius, curve.minor_radius, reference, axis)
    elif curve.direction is not None:
        result = Line(
            origin,
            UnitVector3D(
                [
                    curve.direction.x,
                    curve.direction.y,
                    curve.direction.z,
                ]
            ),
        )
    else:
        result = None

    return result


def from_trimmed_surface_to_grpc_trimmed_surface(
    trimmed_surface: "TrimmedSurface",
) -> GRPCTrimmedSurface:
    """Convert a ``TrimmedSurface`` to a trimmed surface gRPC message.

    Parameters
    ----------
    trimmed_surface : TrimmedSurface
        Surface to convert.

    Returns
    -------
    GRPCTrimmedSurface
        Geometry service gRPC ``TrimmedSurface`` message.
    """
    surface_geometry, surface_type = from_surface_to_grpc_surface(trimmed_surface.geometry)

    return GRPCTrimmedSurface(
        surface=surface_geometry,
        type=surface_type,
        u_min=trimmed_surface.box_uv.interval_u.start,
        u_max=trimmed_surface.box_uv.interval_u.end,
        v_min=trimmed_surface.box_uv.interval_v.start,
        v_max=trimmed_surface.box_uv.interval_v.end,
    )


def from_surface_to_grpc_surface(surface: "Surface") -> tuple[GRPCSurface, GRPCSurfaceType]:
    """Convert a ``Surface`` object to a surface gRPC message.

    Parameters
    ----------
    surface : Surface
        Surface to convert.

    Returns
    -------
    GRPCSurface
        Return ``Surface`` as a ``ansys.api.geometry.Surface`` message.
    GRPCSurfaceType
        Return the grpc surface type of ``Surface``.
    """
    from ansys.geometry.core.shapes.surfaces.cone import Cone
    from ansys.geometry.core.shapes.surfaces.cylinder import Cylinder
    from ansys.geometry.core.shapes.surfaces.plane import PlaneSurface
    from ansys.geometry.core.shapes.surfaces.sphere import Sphere
    from ansys.geometry.core.shapes.surfaces.torus import Torus

    grpc_surface = None
    surface_type = None
    origin = from_point3d_to_grpc_point(surface.origin)
    reference = from_unit_vector_to_grpc_direction(surface.dir_x)
    axis = from_unit_vector_to_grpc_direction(surface.dir_z)

    if isinstance(surface, PlaneSurface):
        grpc_surface = GRPCSurface(origin=origin, reference=reference, axis=axis)
        surface_type = GRPCSurfaceType.SURFACETYPE_PLANE
    elif isinstance(surface, Sphere):
        grpc_surface = GRPCSurface(
            origin=origin, reference=reference, axis=axis, radius=surface.radius.m
        )
        surface_type = GRPCSurfaceType.SURFACETYPE_SPHERE
    elif isinstance(surface, Cylinder):
        grpc_surface = GRPCSurface(
            origin=origin, reference=reference, axis=axis, radius=surface.radius.m
        )
        surface_type = GRPCSurfaceType.SURFACETYPE_CYLINDER
    elif isinstance(surface, Cone):
        grpc_surface = GRPCSurface(
            origin=origin,
            reference=reference,
            axis=axis,
            radius=surface.radius.m,
            half_angle=surface.half_angle.m,
        )
        surface_type = GRPCSurfaceType.SURFACETYPE_CONE
    elif isinstance(surface, Torus):
        grpc_surface = GRPCSurface(
            origin=origin,
            reference=reference,
            axis=axis,
            major_radius=surface.major_radius.m,
            minor_radius=surface.minor_radius.m,
        )
        surface_type = GRPCSurfaceType.SURFACETYPE_TORUS

    return grpc_surface, surface_type


def from_grpc_backend_type_to_backend_type(
    grpc_backend_type: GRPCBackendType,
) -> "BackendType":
    """Convert a gRPC backend type to a backend type.

    Parameters
    ----------
    backend_type : GRPCBackendType
        Source backend type.

    Returns
    -------
    BackendType
        Converted backend type.
    """
    from ansys.geometry.core.connection.backend import BackendType

    # Map the gRPC backend type to the corresponding BackendType
    backend_type = None

    if grpc_backend_type == GRPCBackendType.DISCOVERY:
        backend_type = BackendType.DISCOVERY
    elif grpc_backend_type == GRPCBackendType.SPACECLAIM:
        backend_type = BackendType.SPACECLAIM
    elif grpc_backend_type == GRPCBackendType.WINDOWS_DMS:
        backend_type = BackendType.WINDOWS_SERVICE
    elif grpc_backend_type == GRPCBackendType.LINUX_DMS:
        backend_type = BackendType.LINUX_SERVICE
    elif grpc_backend_type == GRPCBackendType.CORE_SERVICE_LINUX:
        backend_type = BackendType.CORE_LINUX
    elif grpc_backend_type == GRPCBackendType.CORE_SERVICE_WINDOWS:
        backend_type = BackendType.CORE_WINDOWS
    elif grpc_backend_type == GRPCBackendType.DISCOVERY_HEADLESS:
        backend_type = BackendType.DISCOVERY_HEADLESS
    else:
        raise ValueError(f"Invalid backend type: {grpc_backend_type}")

    return backend_type


def from_grpc_driving_dimension_to_driving_dimension(
    driving_dimension: GRPCDrivingDimension,
) -> "Parameter":
    """Convert a gRPC driving dimension to a driving dimension object.

    Parameters
    ----------
    driving_dimension : GRPCDrivingDimension
        Source driving dimension type.

    Returns
    -------
    Parameter
        Converted driving dimension.
    """
    from ansys.geometry.core.parameters.parameter import Parameter, ParameterType

    return Parameter(
        id=driving_dimension.id,
        name=driving_dimension.name,
        dimension_type=ParameterType(driving_dimension.dimension_type),
        dimension_value=driving_dimension.dimension_value,
    )


def from_driving_dimension_to_grpc_driving_dimension(
    driving_dimension: "Parameter",
) -> GRPCDrivingDimension:
    """Convert a driving dimension object to a gRPC driving dimension.

    Parameters
    ----------
    driving_dimension : Parameter
        Source driving dimension type.

    Returns
    -------
    GRPCDrivingDimension
        Converted driving dimension.
    """
    return GRPCDrivingDimension(
        id=driving_dimension.id,
        name=driving_dimension.name,
        dimension_type=driving_dimension.dimension_type.value,
        dimension_value=driving_dimension.dimension_value,
    )


def from_grpc_update_status_to_parameter_update_status(
    update_status: GRPCUpdateStatus,
) -> "ParameterUpdateStatus":
    """Convert a gRPC update status to a parameter update status.

    Parameters
    ----------
    update_status : GRPCUpdateStatus
        Source update status.

    Returns
    -------
    ParameterUpdateStatus
        Converted update status.
    """
    from ansys.geometry.core.parameters.parameter import ParameterUpdateStatus

    status_mapping = {
        GRPCUpdateStatus.SUCCESS: ParameterUpdateStatus.SUCCESS,
        GRPCUpdateStatus.FAILURE: ParameterUpdateStatus.FAILURE,
        GRPCUpdateStatus.CONSTRAINED_PARAMETERS: ParameterUpdateStatus.CONSTRAINED_PARAMETERS,
    }
    return status_mapping.get(update_status, ParameterUpdateStatus.UNKNOWN)


def from_design_file_format_to_grpc_part_export_format(
    design_file_format: "DesignFileFormat",
) -> GRPCPartExportFormat:
    """Convert from a DesignFileFormat object to a gRPC PartExportFormat one.

    Parameters
    ----------
    design_file_format : DesignFileFormat
        The file format desired

    Returns
    -------
    GRPCPartExportFormat
        Converted gRPC Part format
    """
    from ansys.geometry.core.designer.design import DesignFileFormat

    if design_file_format == DesignFileFormat.SCDOCX:
        return GRPCPartExportFormat.PARTEXPORTFORMAT_SCDOCX
    elif design_file_format == DesignFileFormat.PARASOLID_TEXT:
        return GRPCPartExportFormat.PARTEXPORTFORMAT_PARASOLID_TEXT
    elif design_file_format == DesignFileFormat.PARASOLID_BIN:
        return GRPCPartExportFormat.PARTEXPORTFORMAT_PARASOLID_BINARY
    elif design_file_format == DesignFileFormat.FMD:
        return GRPCPartExportFormat.PARTEXPORTFORMAT_FMD
    elif design_file_format == DesignFileFormat.STEP:
        return GRPCPartExportFormat.PARTEXPORTFORMAT_STEP
    elif design_file_format == DesignFileFormat.IGES:
        return GRPCPartExportFormat.PARTEXPORTFORMAT_IGES
    elif design_file_format == DesignFileFormat.PMDB:
        return GRPCPartExportFormat.PARTEXPORTFORMAT_PMDB
    elif design_file_format == DesignFileFormat.STRIDE:
        return GRPCPartExportFormat.PARTEXPORTFORMAT_STRIDE
    elif design_file_format == DesignFileFormat.DISCO:
        return GRPCPartExportFormat.PARTEXPORTFORMAT_DISCO
    else:
        return None


def from_material_to_grpc_material(
    material: "Material",
) -> GRPCMaterial:
    """Convert a ``Material`` class to a material gRPC message.

    Parameters
    ----------
    material : Material
        Source material data.

    Returns
    -------
    GRPCMaterial
        Geometry service gRPC material message.
    """
    return GRPCMaterial(
        name=material.name,
        material_properties=[
            GRPCMaterialProperty(
                id=property.type.value,
                display_name=property.name,
                value=property.quantity.m,
                units=format(property.quantity.units),
            )
            for property in material.properties.values()
        ],
    )
