# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
"""Provides primitive representation of a 2D plane in 3D space."""

from beartype import beartype as check_input_types
import numpy as np

from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Y, ZERO_POINT3D
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.typing import RealSequence


class Plane(Frame):
    """Provides primitive representation of a 2D plane in 3D space.

    Parameters
    ----------
    origin : ~numpy.ndarray | RealSequence | Point3D, default: ZERO_POINT3D
        Centered origin of the frame. The default is ``ZERO_POINT3D``, which is the
        Cartesian origin.
    direction_x : ~numpy.ndarray | RealSequence | UnitVector3D | Vector3D, default: UNITVECTOR3D_X
        X-axis direction.
    direction_y : ~numpy.ndarray | RealSequence | UnitVector3D | Vector3D, default: UNITVECTOR3D_Y
        Y-axis direction.
    """  # noqa : E501

    def __init__(
        self,
        origin: np.ndarray | RealSequence | Point3D = ZERO_POINT3D,
        direction_x: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_X,
        direction_y: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_Y,
    ):
        """Initialize ``Plane`` class."""
        super().__init__(origin, direction_x, direction_y)

    @check_input_types
    def is_point_contained(self, point: Point3D) -> bool:
        """Check if a 3D point is contained in the plane.

        Parameters
        ----------
        point : Point3D
            :class:`Point3D <ansys.geometry.core.math.point.Point3D>` class to check.

        Returns
        -------
        bool
            ``True`` if the 3D point is contained in the plane, ``False`` otherwise.
        """
        # Compute the plane equation A*(x-x0) + B*(y-y0) + C*(z-z0)
        plane_eq = (
            self.direction_z.x * (point.x - self.origin.x).m
            + self.direction_z.y * (point.y - self.origin.y).m
            + self.direction_z.z * (point.z - self.origin.z).m
        )

        # If plane equation is equal to 0, your point is contained
        return True if np.isclose(plane_eq, 0.0) else False

    @property
    def normal(self) -> UnitVector3D:
        """Calculate the normal vector of the plane.

        Returns
        -------
        UnitVector3D
            Normal vector of the plane.
        """
        return self.direction_z

    @check_input_types
    def __eq__(self, other: "Plane") -> bool:
        """Equals operator for the ``Plane`` class."""
        return (
            self.origin == other.origin
            and self.direction_x == other.direction_x
            and self.direction_y == other.direction_y
            and self.direction_z == other.direction_z
        )

    def __ne__(self, other: "Plane") -> bool:
        """Not equals operator for the ``Plane`` class."""
        return not self == other
