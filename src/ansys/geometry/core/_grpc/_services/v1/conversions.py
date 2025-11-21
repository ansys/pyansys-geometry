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

from ansys.api.discovery.v1.commonenums_pb2 import BackendType as GRPCBackendType
from ansys.api.discovery.v1.commonmessages_pb2 import (
    Direction as GRPCDirection,
    EntityIdentifier,
    Line as GRPCLine,
    Point as GRPCPoint,
)
from ansys.api.discovery.v1.design.designmessages_pb2 import (
    CurveGeometry as GRPCCurveGeometry,
    Surface as GRPCSurface,
    TrackedCommandResponse as GRPCTrackedCommandResponse,
)

if TYPE_CHECKING:
    from ansys.geometry.core.connection.backend import BackendType
    from ansys.geometry.core.designer.face import SurfaceType
    from ansys.geometry.core.math.point import Point3D
    from ansys.geometry.core.math.vector import UnitVector3D
    from ansys.geometry.core.shapes.curves.curve import Curve
    from ansys.geometry.core.shapes.curves.line import Line
    from ansys.geometry.core.shapes.surfaces.surface import Surface


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


def from_grpc_surface_to_surface(surface: GRPCSurface, surface_type: "SurfaceType") -> "Surface":
    """Convert a gRPC v1 surface message to a ``Surface`` class.

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


def from_grpc_point_to_point3d(point: GRPCPoint) -> "Point3D":
    """Convert a gRPC v1 point message class to a ``Point3D`` class.

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


def from_grpc_curve_to_curve(curve: GRPCCurveGeometry) -> "Curve":
    """Convert a gRPC v1 curve message to a ``Curve`` class.

    Parameters
    ----------
    curve : GRPCCurveGeometry
        Geometry service gRPC curve message.

    Returns
    -------
    Curve
        Resulting converted curve.
    """
    from ansys.geometry.core.math.point import Point3D
    from ansys.geometry.core.math.vector import UnitVector3D
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

    result = None
    if curve.radius != 0:
        result = Circle(origin, curve.radius, reference, axis)
    elif curve.major_radius != 0 and curve.minor_radius != 0:
        result = Ellipse(origin, curve.major_radius, curve.minor_radius, reference, axis)
    elif curve.direction is not None and (
        curve.direction.x != 0 or curve.direction.y != 0 or curve.direction.z != 0
    ):
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
    # Note: NURBS curves not yet supported in v1 conversions

    return result


def from_unit_vector_to_grpc_direction(unit_vector: "UnitVector3D") -> GRPCDirection:
    """Convert a ``UnitVector3D`` class to a gRPC v1 unit vector message.

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


def from_grpc_direction_to_unit_vector(direction: GRPCDirection) -> "UnitVector3D":
    """Convert a gRPC v1 direction message to a ``UnitVector3D`` class.

    Parameters
    ----------
    direction : GRPCDirection
        Source direction data.

    Returns
    -------
    UnitVector3D
        Converted unit vector.
    """
    from ansys.geometry.core.math.vector import UnitVector3D

    return UnitVector3D([direction.x, direction.y, direction.z])


def from_point3d_to_grpc_point(point: "Point3D") -> GRPCPoint:
    """Convert a ``Point3D`` class to a gRPC v1 point message.

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


def from_line_to_grpc_line(line: "Line") -> GRPCLine:
    """Convert a ``Line`` to a gRPC v1 line message.

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


def serialize_tracked_command_response(response: GRPCTrackedCommandResponse) -> dict:
    """Serialize a GRPC v1 TrackedCommandResponse object into a dictionary.

    Parameters
    ----------
    response : TrackedCommandResponse
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


    tracked_changes = response.tracked_changes
    return {
        "success": response.command_response.success,
        "created_bodies": [
            serialize_body(body) for body in getattr(tracked_changes, "created_bodies", [])
        ],
        "modified_bodies": [
            serialize_body(body) for body in getattr(tracked_changes, "modified_bodies", [])
        ],
        "deleted_bodies": [
            serialize_entity_identifier(entity)
            for entity in getattr(tracked_changes, "deleted_bodies", [])
        ],
        "created_faces": [
            serialize_entity_identifier(face_id)
            for face_id in getattr(tracked_changes, "created_face_ids", [])
        ],
        "modified_faces": [
            serialize_entity_identifier(face_id)
            for face_id in getattr(tracked_changes, "modified_face_ids", [])
        ],
        "deleted_faces": [
            serialize_entity_identifier(face_id)
            for face_id in getattr(tracked_changes, "deleted_face_ids", [])
        ],
        "created_edges": [
            serialize_entity_identifier(edge_id)
            for edge_id in getattr(tracked_changes, "created_edge_ids", [])
        ],
        "modified_edges": [
            serialize_entity_identifier(edge_id)
            for edge_id in getattr(tracked_changes, "modified_edge_ids", [])
        ],
        "deleted_edges": [
            serialize_entity_identifier(edge_id)
            for edge_id in getattr(tracked_changes, "deleted_edge_ids", [])
        ],
    }