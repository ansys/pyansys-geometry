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

from typing import Any

from ansys.api.geometry.v0.models_pb2 import Point as GRPCPoint
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Measurement


def from_point3d_to_point(point: Point3D) -> Any:
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


def from_measurement_to_server_length(input: Measurement) -> float:
    """Convert a measurement to a length value.

    Parameters
    ----------
    value : Measurement
        Measurement value.

    Returns
    -------
    float
        Length value in server-defined units. By default, meters.
    """
    return input.value.m_as(DEFAULT_UNITS.SERVER_LENGTH)


def from_measurement_to_server_angle(input: Measurement) -> float:
    """Convert a measurement to an angle value.

    Parameters
    ----------
    value : Measurement
        Measurement value.

    Returns
    -------
    float
        Angle value in server-defined units. By default, radians.
    """
    return input.value.m_as(DEFAULT_UNITS.SERVER_ANGLE)
