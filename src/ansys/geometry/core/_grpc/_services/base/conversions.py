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
"""Module containing server-version agnostic conversions."""

from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Distance, Measurement


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


def to_distance(value: float | int) -> Distance:
    """Convert a server value to a Distance object.

    Notes
    -----
    The value is converted to a Distance object using the default server length unit.
    The value should represent a length in the server's unit system.

    Parameters
    ----------
    value : float | int
        Value to convert.

    Returns
    -------
    Distance
        Converted distance.
    """
    return Distance(value, DEFAULT_UNITS.SERVER_LENGTH)
