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
"""Module containing v1 related conversions from PyAnsys Geometry objects to gRPC messages."""

from typing import TYPE_CHECKING

from ansys.api.discovery.v1.commonenums_pb2 import (
    BackendType as GRPCBackendType,
    FileFormat as GRPCFileFormat,
)
from ansys.api.discovery.v1.commonmessages_pb2 import (
    Arc as GRPCArc,
    Circle as GRPCCircle,
    Direction as GRPCDirection,
    Ellipse as GRPCEllipse,
    EntityIdentifier,
    Frame as GRPCFrame,
    Line as GRPCLine,
    Plane as GRPCPlane,
    Point as GRPCPoint,
    Polygon as GRPCPolygon,
    Quantity as GRPCQuantity,
)
from ansys.api.discovery.v1.design.designmessages_pb2 import (
    CurveGeometry as GRPCCurveGeometry,
    DrivingDimensionEntity as GRPCDrivingDimension,
    EdgeTessellation as GRPCEdgeTessellation,
    Geometries as GRPCGeometries,
    Knot as GRPCKnot,
    MaterialEntity as GRPCMaterial,
    MaterialProperty as GRPCMaterialProperty,
    Matrix as GRPCMatrix,
    NurbsCurve as GRPCNurbsCurve,
    NurbsSurface as GRPCNurbsSurface,
    Surface as GRPCSurface,
    Tessellation as GRPCTessellation,
    TessellationOptions as GRPCTessellationOptions,
    TrackedCommandResponse as GRPCTrackedCommandResponse,
    TrimmedCurve as GRPCTrimmedCurve,
    TrimmedSurface as GRPCTrimmedSurface,
)
from ansys.api.discovery.v1.design.parameters.drivingdimension_pb2 import (
    UpdateStatus as GRPCUpdateStatus,
)
from ansys.api.discovery.v1.geometryenums_pb2 import (
    SurfaceType as GRPCSurfaceType,
)
from ansys.api.discovery.v1.operations.prepare_pb2 import (
    EnclosureOptions as GRPCEnclosureOptions,
)
import pint

from ansys.geometry.core.errors import GeometryRuntimeError
from ansys.geometry.core.misc.checks import graphics_required
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS
from ansys.geometry.core.shapes.surfaces.nurbs import NURBSSurface

if TYPE_CHECKING:
    import pyvista as pv
    import semver

    from ansys.geometry.core.connection.backend import BackendType
    from ansys.geometry.core.designer.design import DesignFileFormat
    from ansys.geometry.core.designer.face import SurfaceType
    from ansys.geometry.core.materials.material import Material
    from ansys.geometry.core.materials.property import MaterialProperty
    from ansys.geometry.core.math.frame import Frame
    from ansys.geometry.core.math.matrix import Matrix44
    from ansys.geometry.core.math.plane import Plane
    from ansys.geometry.core.math.point import Point2D, Point3D
    from ansys.geometry.core.math.vector import UnitVector3D
    from ansys.geometry.core.misc.measurements import Measurement
    from ansys.geometry.core.misc.options import TessellationOptions
    from ansys.geometry.core.parameters.parameter import (
        Parameter,
        ParameterUpdateStatus,
    )
    from ansys.geometry.core.shapes.curves.curve import Curve
    from ansys.geometry.core.shapes.curves.line import Line
    from ansys.geometry.core.shapes.curves.nurbs import NURBSCurve
    from ansys.geometry.core.shapes.curves.trimmed_curve import TrimmedCurve
    from ansys.geometry.core.shapes.surfaces.surface import Surface
    from ansys.geometry.core.shapes.surfaces.trimmed_surface import TrimmedSurface
    from ansys.geometry.core.sketch.arc import Arc
    from ansys.geometry.core.sketch.circle import SketchCircle
    from ansys.geometry.core.sketch.edge import SketchEdge
    from ansys.geometry.core.sketch.ellipse import SketchEllipse
    from ansys.geometry.core.sketch.face import SketchFace
    from ansys.geometry.core.sketch.nurbs import SketchNurbs
    from ansys.geometry.core.sketch.polygon import Polygon
    from ansys.geometry.core.sketch.segment import SketchSegment
    from ansys.geometry.core.tools.prepare_tools import EnclosureOptions


def from_grpc_backend_type_to_backend_type(
    grpc_backend_type: GRPCBackendType,
) -> "BackendType":
    """Convert a gRPC v1 backend type to a backend type.

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

    if grpc_backend_type == GRPCBackendType.BACKENDTYPE_DISCOVERY:
        backend_type = BackendType.DISCOVERY
    elif grpc_backend_type == GRPCBackendType.BACKENDTYPE_SPACECLAIM:
        backend_type = BackendType.SPACECLAIM
    elif grpc_backend_type == GRPCBackendType.BACKENDTYPE_WINDOWS_DMS:
        backend_type = BackendType.WINDOWS_SERVICE
    elif grpc_backend_type == GRPCBackendType.BACKENDTYPE_LINUX_DMS:
        backend_type = BackendType.LINUX_SERVICE
    elif grpc_backend_type == GRPCBackendType.BACKENDTYPE_CORE_SERVICE_LINUX:
        backend_type = BackendType.CORE_LINUX
    elif grpc_backend_type == GRPCBackendType.BACKENDTYPE_CORE_SERVICE_WINDOWS:
        backend_type = BackendType.CORE_WINDOWS
    elif grpc_backend_type == GRPCBackendType.BACKENDTYPE_DISCOVERY_HEADLESS:
        backend_type = BackendType.DISCOVERY_HEADLESS
    else:
        raise ValueError(f"Invalid backend type: {grpc_backend_type}")

    return backend_type


def build_grpc_id(id: str) -> EntityIdentifier:
    """Build a v1 EntityIdentifier gRPC message.

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
        x=GRPCQuantity(value_in_geometry_units=point.x.m_as(DEFAULT_UNITS.SERVER_LENGTH)),
        y=GRPCQuantity(value_in_geometry_units=point.y.m_as(DEFAULT_UNITS.SERVER_LENGTH)),
        z=GRPCQuantity(value_in_geometry_units=point.z.m_as(DEFAULT_UNITS.SERVER_LENGTH)),
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
        [
            point.x.value_in_geometry_units,
            point.y.value_in_geometry_units,
            point.z.value_in_geometry_units,
        ],
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


def from_line_to_grpc_line(line: "Line") -> GRPCLine:
    """Convert a ``Line`` to a line gRPC message.

    Parameters
    ----------
    line : Line
        Line to convert.

    Returns
    -------
    GRPCLine
        Geometry service gRPC ``Line`` message.
    """
    start = line.origin
    end = line.origin + line.direction
    return GRPCLine(start=from_point3d_to_grpc_point(start), end=from_point3d_to_grpc_point(end))


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

    if len(tess.faces) == 0 or len(tess.vertices) == 0:
        return pv.PolyData()

    return pv.PolyData(var_inp=np.array(tess.vertices).reshape(-1, 3), faces=tess.faces)


def from_grpc_tess_to_raw_data(tess: GRPCTessellation) -> dict:
    """Convert a ``Tessellation`` to raw data."""
    return {"vertices": tess.vertices, "faces": tess.faces}


@graphics_required
def from_grpc_edge_tess_to_pd(tess: GRPCEdgeTessellation) -> "pv.PolyData":
    """Convert a ``EdgeTessellation`` to ``pyvista.PolyData``."""
    # lazy imports here to improve initial load
    import numpy as np
    import pyvista as pv

    if len(tess.vertices) == 0:
        return pv.PolyData()

    points = np.reshape(np.array([from_grpc_point_to_point3d(pt) for pt in tess.vertices]), (-1, 3))
    lines = np.hstack([[len(points), *range(len(points))]])
    return pv.PolyData(points, lines=lines)


def from_grpc_edge_tess_to_raw_data(tess: GRPCEdgeTessellation) -> dict:
    """Convert a ``EdgeTessellation`` to raw data."""
    return {"vertices": [coord for pt in tess.vertices for coord in (pt.x, pt.y, pt.z)]}


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
    geometries.nurbs_curves.extend(converted_sketch_edges[2])

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
        elif len(geometries.nurbs_curves) > 0:
            one_curve_geometry.nurbs_curves.append(geometries.nurbs_curves[0])
        return one_curve_geometry

    else:
        return geometries


def from_sketch_edges_to_grpc_geometries(
    edges: list["SketchEdge"],
    plane: "Plane",
) -> tuple[list[GRPCLine], list[GRPCArc], list[GRPCNurbsCurve]]:
    """Convert a list of ``SketchEdge`` to a gRPC message.

    Parameters
    ----------
    edges : list[SketchEdge]
        Source edge data.
    plane : Plane
        Plane for positioning the 2D sketches.

    Returns
    -------
    tuple[list[GRPCLine], list[GRPCArc], list[GRPCNurbsCurve]]
        Geometry service gRPC line, arc, and NURBS curve messages. The unit is meters.
    """
    from ansys.geometry.core.sketch.arc import Arc
    from ansys.geometry.core.sketch.nurbs import SketchNurbs
    from ansys.geometry.core.sketch.segment import SketchSegment

    arcs = []
    segments = []
    nurbs_curves = []
    for edge in edges:
        if isinstance(edge, SketchSegment):
            segments.append(from_sketch_segment_to_grpc_line(edge, plane))
        elif isinstance(edge, Arc):
            arcs.append(from_sketch_arc_to_grpc_arc(edge, plane))
        elif isinstance(edge, SketchNurbs):
            nurbs_curves.append(from_sketch_nurbs_to_grpc_nurbs_curve(edge, plane))

    return (segments, arcs, nurbs_curves)


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


def from_sketch_nurbs_to_grpc_nurbs_curve(curve: "SketchNurbs", plane: "Plane") -> GRPCNurbsCurve:
    """Convert a ``SketchNurbs`` class to a NURBS curve gRPC message.

    Parameters
    ----------
    nurbs : SketchNurbs
        Source NURBS data.
    plane : Plane
        Plane for positioning the NURBS curve.

    Returns
    -------
    GRPCNurbsCurve
        Geometry service gRPC NURBS curve message. The unit is meters.
    """
    from ansys.api.geometry.v0.models_pb2 import (
        ControlPoint as GRPCControlPoint,
        NurbsData as GRPCNurbsData,
    )

    # Convert control points
    control_points = [
        GRPCControlPoint(
            position=from_point2d_to_grpc_point(plane, pt),
            weight=curve.weights[i],
        )
        for i, pt in enumerate(curve.control_points)
    ]

    # Convert nurbs data
    nurbs_data = GRPCNurbsData(
        degree=curve.degree,
        knots=from_knots_to_grpc_knots(curve.knots),
        order=curve.degree + 1,
    )

    return GRPCNurbsCurve(
        control_points=control_points,
        nurbs_data=nurbs_data,
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
    from ansys.geometry.core.shapes.curves.nurbs import NURBSCurve

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
    elif isinstance(curve, NURBSCurve):
        grpc_curve = GRPCCurveGeometry(nurbs_curve=from_nurbs_curve_to_grpc_nurbs_curve(curve))
    else:
        raise ValueError(f"Unsupported curve type: {type(curve)}")

    return grpc_curve


def from_nurbs_curve_to_grpc_nurbs_curve(curve: "NURBSCurve") -> GRPCNurbsCurve:
    """Convert a ``NURBSCurve`` to a NURBS curve gRPC message.

    Parameters
    ----------
    curve : NURBSCurve
        Curve to convert.

    Returns
    -------
    GRPCNurbsCurve
        Geometry service gRPC ``NURBSCurve`` message.
    """
    from ansys.api.geometry.v0.models_pb2 import (
        ControlPoint as GRPCControlPoint,
        NurbsData as GRPCNurbsData,
    )

    # Convert control points
    control_points = [
        GRPCControlPoint(
            position=from_point3d_to_grpc_point(pt),
            weight=curve.weights[i],
        )
        for i, pt in enumerate(curve.control_points)
    ]

    # Convert nurbs data
    nurbs_data = GRPCNurbsData(
        degree=curve.degree,
        knots=from_knots_to_grpc_knots(curve.knots),
        order=curve.degree + 1,
    )

    return GRPCNurbsCurve(
        control_points=control_points,
        nurbs_data=nurbs_data,
    )


def from_nurbs_surface_to_grpc_nurbs_surface(surface: "NURBSSurface") -> GRPCNurbsSurface:
    """Convert a ``NURBSSurface`` to a NURBS surface gRPC message.

    Parameters
    ----------
    surface : NURBSSurface
        Surface to convert.

    Returns
    -------
    GRPCNurbsSurface
        Geometry service gRPC ``NURBSSurface`` message.
    """
    from ansys.api.geometry.v0.models_pb2 import (
        ControlPoint as GRPCControlPoint,
        NurbsData as GRPCNurbsData,
    )

    # Convert control points
    control_points = [
        GRPCControlPoint(
            position=from_point3d_to_grpc_point(point),
            weight=weight,
        )
        for weight, point in zip(surface.weights, surface.control_points)
    ]

    # Convert nurbs data
    nurbs_data_u = GRPCNurbsData(
        degree=surface.degree_u,
        knots=from_knots_to_grpc_knots(surface.knotvector_u),
        order=surface.degree_u + 1,
    )

    nurbs_data_v = GRPCNurbsData(
        degree=surface.degree_v,
        knots=from_knots_to_grpc_knots(surface.knotvector_v),
        order=surface.degree_v + 1,
    )

    return GRPCNurbsSurface(
        control_points=control_points,
        nurbs_data_u=nurbs_data_u,
        nurbs_data_v=nurbs_data_v,
    )


def from_grpc_nurbs_curve_to_nurbs_curve(curve: GRPCNurbsCurve) -> "NURBSCurve":
    """Convert a NURBS curve gRPC message to a ``NURBSCurve``.

    Parameters
    ----------
    curve : GRPCNurbsCurve
        Geometry service gRPC NURBS curve message.

    Returns
    -------
    NURBSCurve
        Resulting converted NURBS curve.
    """
    from ansys.geometry.core.shapes.curves.nurbs import NURBSCurve

    # Extract control points
    control_points = [from_grpc_point_to_point3d(cp.position) for cp in curve.control_points]

    # Extract weights
    weights = [cp.weight for cp in curve.control_points]

    # Extract degree
    degree = curve.nurbs_data.degree

    # Convert gRPC knots to full knot vector
    knots = []
    for grpc_knot in curve.nurbs_data.knots:
        knots.extend([grpc_knot.parameter] * grpc_knot.multiplicity)

    # Create and return the NURBS curve
    return NURBSCurve.from_control_points(
        control_points=control_points,
        degree=degree,
        knots=knots,
        weights=weights,
    )


def from_knots_to_grpc_knots(knots: list[float]) -> list[GRPCKnot]:
    """Convert a list of knots to a list of gRPC knot messages.

    Parameters
    ----------
    knots : list[float]
        Source knots data.

    Returns
    -------
    list[GRPCKnot]
        Geometry service gRPC knot messages.
    """
    from collections import Counter

    # Count multiplicities
    multiplicities = Counter(knots)

    # Get unique knots (parameters) in order
    unique_knots = sorted(set(knots))
    knot_multiplicities = [(knot, multiplicities[knot]) for knot in unique_knots]

    # Convert to gRPC knot messages
    grpc_knots = [
        GRPCKnot(
            parameter=knot,
            multiplicity=multiplicity,
        )
        for knot, multiplicity in knot_multiplicities
    ]

    return grpc_knots


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
    from ansys.geometry.core.math.vector import UnitVector3D
    from ansys.geometry.core.shapes.curves.circle import Circle
    from ansys.geometry.core.shapes.curves.ellipse import Ellipse
    from ansys.geometry.core.shapes.curves.line import Line

    origin = from_grpc_point_to_point3d(curve.origin)
    try:
        reference = UnitVector3D([curve.reference.x, curve.reference.y, curve.reference.z])
        axis = UnitVector3D([curve.axis.x, curve.axis.y, curve.axis.z])
    except ValueError:
        # curve will be a line
        pass

    radius = curve.radius.value_in_geometry_units
    major_radius = curve.major_radius.value_in_geometry_units
    minor_radius = curve.minor_radius.value_in_geometry_units
    if radius != 0:
        result = Circle(origin, radius, reference, axis)
    elif major_radius != 0 and minor_radius != 0:
        result = Ellipse(origin, major_radius, minor_radius, reference, axis)
    elif curve.nurbs_curve.nurbs_data.degree != 0:
        result = from_grpc_nurbs_curve_to_nurbs_curve(curve.nurbs_curve)
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
    elif isinstance(surface, NURBSSurface):
        grpc_surface = GRPCSurface(
            origin=origin,
            reference=reference,
            axis=axis,
            nurbs_surface=from_nurbs_surface_to_grpc_nurbs_surface(surface),
        )
        surface_type = GRPCSurfaceType.SURFACETYPE_NURBS

    return grpc_surface, surface_type


def from_grpc_surface_to_surface(surface: GRPCSurface, surface_type: "SurfaceType") -> "Surface":
    """Convert a surface gRPC message to a ``Surface`` class.

    Parameters
    ----------
    surface : GRPCSurface
        Geometry service gRPC surface message.

    Returns
    -------
    Surface
        Resulting converted surface.
    """
    from ansys.geometry.core.designer.face import SurfaceType
    from ansys.geometry.core.math.vector import UnitVector3D
    from ansys.geometry.core.shapes.surfaces.cone import Cone
    from ansys.geometry.core.shapes.surfaces.cylinder import Cylinder
    from ansys.geometry.core.shapes.surfaces.plane import PlaneSurface
    from ansys.geometry.core.shapes.surfaces.sphere import Sphere
    from ansys.geometry.core.shapes.surfaces.torus import Torus

    origin = from_grpc_point_to_point3d(surface.origin)
    axis = UnitVector3D([surface.axis.x, surface.axis.y, surface.axis.z])
    reference = UnitVector3D([surface.reference.x, surface.reference.y, surface.reference.z])

    if surface_type == SurfaceType.SURFACETYPE_CONE:
        result = Cone(origin, surface.radius, surface.half_angle, reference, axis)
    elif surface_type == SurfaceType.SURFACETYPE_CYLINDER:
        result = Cylinder(origin, surface.radius, reference, axis)
    elif surface_type == SurfaceType.SURFACETYPE_SPHERE:
        result = Sphere(origin, surface.radius, reference, axis)
    elif surface_type == SurfaceType.SURFACETYPE_TORUS:
        result = Torus(origin, surface.major_radius, surface.minor_radius, reference, axis)
    elif surface_type == SurfaceType.SURFACETYPE_PLANE:
        result = PlaneSurface(origin, reference, axis)
    else:
        result = None
    return result


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


def from_grpc_matrix_to_matrix(matrix: GRPCMatrix) -> "Matrix44":
    """Convert a gRPC matrix to a matrix.

    Parameters
    ----------
    matrix : GRPCMatrix
        Source gRPC matrix data.

    Returns
    -------
    Matrix44
        Converted matrix.
    """
    import numpy as np

    from ansys.geometry.core.math.matrix import Matrix44

    return Matrix44(
        np.round(
            [
                [matrix.m00, matrix.m01, matrix.m02, matrix.m03],
                [matrix.m10, matrix.m11, matrix.m12, matrix.m13],
                [matrix.m20, matrix.m21, matrix.m22, matrix.m23],
                [matrix.m30, matrix.m31, matrix.m32, matrix.m33],
            ],
            8,
        )
    )


def from_grpc_direction_to_unit_vector(direction: GRPCDirection) -> "UnitVector3D":
    """Convert a gRPC direction to a unit vector.

    Parameters
    ----------
    direction : GRPCDirection
        Source gRPC direction data.

    Returns
    -------
    UnitVector3D
        Converted unit vector.
    """
    from ansys.geometry.core.math.vector import UnitVector3D

    return UnitVector3D([direction.x, direction.y, direction.z])


def from_length_to_grpc_quantity(input: "Measurement") -> GRPCQuantity:
    """Convert a ``Measurement`` containing a length to a gRPC quantity.

    Parameters
    ----------
    input : Measurement
        Source measurement data.

    Returns
    -------
    GRPCQuantity
        Converted gRPC quantity.
    """
    return GRPCQuantity(value_in_geometry_units=input.value.m_as(DEFAULT_UNITS.SERVER_LENGTH))


def from_angle_to_grpc_quantity(input: "Measurement") -> GRPCQuantity:
    """Convert a ``Measurement`` containing an angle to a gRPC quantity.

    Parameters
    ----------
    input : Measurement
        Source measurement data.

    Returns
    -------
    GRPCQuantity
        Converted gRPC quantity.
    """
    return GRPCQuantity(value_in_geometry_units=input.value.m_as(DEFAULT_UNITS.SERVER_ANGLE))


def _nurbs_curves_compatibility(backend_version: "semver.Version", grpc_geometries: GRPCGeometries):
    """Check if the backend version is compatible with NURBS curves in sketches.

    Parameters
    ----------
    backend_version : semver.Version
        The version of the backend.
    grpc_geometries : GRPCGeometries
        The gRPC geometries potentially containing NURBS curves.

    Raises
    ------
    GeometryRuntimeError
        If the backend version is lower than 26.1.0 and NURBS curves are present.
    """
    if grpc_geometries.nurbs_curves and backend_version < (26, 1, 0):
        raise GeometryRuntimeError(
            "The usage of NURBS in sketches requires a minimum Ansys release version of "  # noqa: E501
            + "26.1.0, but the current version used is "
            + f"{backend_version}."
        )


def _check_write_body_facets_input(backend_version: "semver.Version", write_body_facets: bool):
    """Check if the backend version is compatible with NURBS curves in sketches.

    Parameters
    ----------
    backend_version : semver.Version
        The version of the backend.
    write_body_facets : bool
        Option to write out body facets.
    """
    if write_body_facets and backend_version < (26, 1, 0):
        from ansys.geometry.core.logger import LOG

        LOG.warning(
            "The usage of write_body_facets requires a minimum Ansys release version of "
            + "26.1.0, but the current version used is "
            + f"{backend_version}."
        )


def from_enclosure_options_to_grpc_enclosure_options(
    enclosure_options: "EnclosureOptions",
) -> GRPCEnclosureOptions:
    """Convert enclosure_options to grpc definition.

    Parameters
    ----------
    enclosure_options : EnclosureOptions
        Definition of the enclosure options.

    Returns
    -------
    GRPCEnclosureOptions
        Grpc converted definition.
    """
    frame = enclosure_options.frame
    return GRPCEnclosureOptions(
        create_shared_topology=enclosure_options.create_shared_topology,
        subtract_bodies=enclosure_options.subtract_bodies,
        frame=from_frame_to_grpc_frame(frame) if frame is not None else None,
        cushion_proportion=enclosure_options.cushion_proportion,
    )


def from_design_file_format_to_grpc_file_format(
    design_file_format: "DesignFileFormat",
) -> GRPCFileFormat:
    """Convert from a ``DesignFileFormat`` object to a gRPC file format.

    Parameters
    ----------
    design_file_format : DesignFileFormat
        The file format desired

    Returns
    -------
    GRPCFileFormat
        Converted gRPC FileFormat.
    """
    from ansys.geometry.core.designer.design import DesignFileFormat

    if design_file_format == DesignFileFormat.SCDOCX:
        return GRPCFileFormat.FILEFORMAT_SCDOCX
    elif design_file_format == DesignFileFormat.PARASOLID_TEXT:
        return GRPCFileFormat.FILEFORMAT_PARASOLID_TEXT
    elif design_file_format == DesignFileFormat.PARASOLID_BIN:
        return GRPCFileFormat.FILEFORMAT_PARASOLID_BINARY
    elif design_file_format == DesignFileFormat.FMD:
        return GRPCFileFormat.FILEFORMAT_FMD
    elif design_file_format == DesignFileFormat.STEP:
        return GRPCFileFormat.FILEFORMAT_STEP
    elif design_file_format == DesignFileFormat.IGES:
        return GRPCFileFormat.FILEFORMAT_IGES
    elif design_file_format == DesignFileFormat.PMDB:
        return GRPCFileFormat.FILEFORMAT_PMDB
    elif design_file_format == DesignFileFormat.STRIDE:
        return GRPCFileFormat.FILEFORMAT_STRIDE
    elif design_file_format == DesignFileFormat.DISCO:
        return GRPCFileFormat.FILEFORMAT_DISCO
    else:
        return None


def serialize_tracked_command_response(response: GRPCTrackedCommandResponse) -> dict:
    """Serialize a TrackedCommandResponse object into a dictionary.

    Parameters
    ----------
    response : GRPCTrackedCommandResponse
        The gRPC TrackedCommandResponse object to serialize.

    Returns
    -------
    dict
        A dictionary representation of the TrackedCommandResponse object.
    """

    def serialize_body(body):
        return {
            "id": body.id,
            "name": body.name,
            "can_suppress": body.can_suppress,
            "transform_to_master": {
                "m00": body.transform_to_master.m00,
                "m11": body.transform_to_master.m11,
                "m22": body.transform_to_master.m22,
                "m33": body.transform_to_master.m33,
            },
            "master_id": body.master_id,
            "parent_id": body.parent_id,
            "is_surface": body.is_surface,
        }

    def serialize_entity_identifier(entity):
        """Serialize an EntityIdentifier object into a dictionary."""
        return {
            "id": entity.id,
        }

    return {
        "success": getattr(response.command_response, "success", False),
        "created_bodies": [
            serialize_body(body) for body in getattr(response.tracked_changes, "created_bodies", [])
        ],
        "modified_bodies": [
            serialize_body(body)
            for body in getattr(response.tracked_changes, "modified_bodies", [])
        ],
        "deleted_bodies": [
            serialize_entity_identifier(entity)
            for entity in getattr(response.tracked_changes, "deleted_bodies", [])
        ],
        "created_faces": [
            serialize_entity_identifier(entity)
            for entity in getattr(response.tracked_changes, "created_face_ids", [])
        ],
        "modified_faces": [
            serialize_entity_identifier(entity)
            for entity in getattr(response.tracked_changes, "modified_face_ids", [])
        ],
        "deleted_faces": [
            serialize_entity_identifier(entity)
            for entity in getattr(response.tracked_changes, "deleted_face_ids", [])
        ],
        "created_edges": [
            serialize_entity_identifier(entity)
            for entity in getattr(response.tracked_changes, "created_edge_ids", [])
        ],
        "modified_edges": [
            serialize_entity_identifier(entity)
            for entity in getattr(response.tracked_changes, "modified_edge_ids", [])
        ],
        "deleted_edges": [
            serialize_entity_identifier(entity)
            for entity in getattr(response.tracked_changes, "deleted_edge_ids", [])
        ],
    }


def get_standard_tracker_response(response) -> dict:
    """Get a standard dictionary response from a TrackerCommandResponse gRPC object.

    Parameters
    ----------
    response : TrackerCommandResponse
        The gRPC TrackerCommandResponse object.

    Returns
    -------
    dict
        A dictionary representing the standard tracker response
    """
    return {
        "success": response.command_response.success,
        "tracker_response": serialize_tracked_command_response(response.tracked_changes),
    }


def get_tracker_response_with_created_bodies(response) -> dict:
    """Get a dictionary response from a TrackerCommandResponse gRPC object including created bodies.

    Parameters
    ----------
    response : TrackerCommandResponse
        The gRPC TrackerCommandResponse object.

    Returns
    -------
    dict
        A dictionary representing the tracker response with created bodies.
    """
    serialized_response = get_standard_tracker_response(response)
    serialized_response["created_bodies"] = serialized_response["tracker_response"].get(
        "created_bodies", []
    )
    return serialized_response
