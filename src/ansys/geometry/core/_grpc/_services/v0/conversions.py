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

import pint

from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
from ansys.api.geometry.v0.models_pb2 import (
    Direction as GRPCDirection,
    Material as GRPCMaterial,
    MaterialProperty as GRPCMaterialProperty,
    Point as GRPCPoint,
)
from ansys.geometry.core.materials.material import Material
from ansys.geometry.core.materials.property import MaterialProperty, MaterialPropertyType
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS
from ansys.geometry.core.misc.units import UNITS


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


def grpc_point_to_point3d(point: GRPCPoint) -> Point3D:
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
