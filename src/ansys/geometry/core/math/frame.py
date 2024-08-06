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
"""Provides for managing a frame."""

from beartype import beartype as check_input_types
import numpy as np

from ansys.geometry.core.math.constants import UNITVECTOR3D_X, UNITVECTOR3D_Y, ZERO_POINT3D
from ansys.geometry.core.math.matrix import Matrix33, Matrix44
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.typing import RealSequence


class Frame:
    """Representation of a frame.

    Parameters
    ----------
    origin : ~numpy.ndarray | RealSequence | Point3D, default: ZERO_POINT3D
        Centered origin of the`frame. The default is ``ZERO_POINT3D``, which is the
        Cartesian origin.
    direction_x : ~numpy.ndarray | RealSequence | UnitVector3D | Vector3D, default: UNITVECTOR3D_X
        X-axis direction.
    direction_y : ~numpy.ndarray | RealSequence | UnitVector3D | Vector3D, default: UNITVECTOR3D_Y
        Y-axis direction.
    """  # noqa : E501

    @check_input_types
    def __init__(
        self,
        origin: np.ndarray | RealSequence | Point3D = ZERO_POINT3D,
        direction_x: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_X,
        direction_y: np.ndarray | RealSequence | UnitVector3D | Vector3D = UNITVECTOR3D_Y,
    ):
        """Initialize the ``Frame`` class."""
        self._origin = Point3D(origin) if not isinstance(origin, Point3D) else origin
        self._direction_x = (
            UnitVector3D(direction_x) if not isinstance(direction_x, UnitVector3D) else direction_x
        )
        self._direction_y = (
            UnitVector3D(direction_y) if not isinstance(direction_y, UnitVector3D) else direction_y
        )

        # origin is fixed once the frame is built
        self._origin.setflags(write=False)

        if not self._direction_x.is_perpendicular_to(self._direction_y):
            raise ValueError("Direction x and direction y must be perpendicular.")

        self._direction_z = UnitVector3D(self._direction_x % self._direction_y)

        self._rotation_matrix = Matrix33(
            np.array(
                [
                    self.direction_x.tolist(),
                    self.direction_y.tolist(),
                    self.direction_z.tolist(),
                ]
            )
        )

        self._transformation_matrix = Matrix44(
            [
                [
                    self.direction_x.x,
                    self.direction_y.x,
                    self.direction_z.x,
                    self.origin.x.to_base_units().m,
                ],
                [
                    self.direction_x.y,
                    self.direction_y.y,
                    self.direction_z.y,
                    self.origin.y.to_base_units().m,
                ],
                [
                    self.direction_x.z,
                    self.direction_y.z,
                    self.direction_z.z,
                    self.origin.z.to_base_units().m,
                ],
                [0, 0, 0, 1],
            ]
        )

    @property
    def origin(self) -> Point3D:
        """Origin of the frame."""
        return self._origin

    @property
    def direction_x(self) -> UnitVector3D:
        """X-axis direction of the frame."""
        return self._direction_x

    @property
    def direction_y(self) -> UnitVector3D:
        """Y-axis direction of the frame."""
        return self._direction_y

    @property
    def direction_z(self) -> UnitVector3D:
        """Z-axis direction of the frame."""
        return self._direction_z

    @property
    def global_to_local_rotation(self) -> Matrix33:
        """Global to local space transformation matrix.

        Returns
        -------
        Matrix33
            3x3 matrix representing the transformation from global to local
            coordinate space, excluding origin translation.
        """
        return self._rotation_matrix

    @property
    def local_to_global_rotation(self) -> Matrix33:
        """Local to global space transformation matrix.

        Returns
        -------
        Matrix33
            3x3 matrix representing the transformation from local to global
            coordinate space.
        """
        return self._rotation_matrix.T

    @property
    def transformation_matrix(self) -> Matrix44:
        """Full 4x4 transformation matrix.

        Returns
        -------
        Matrix44
            4x4 matrix representing the transformation from global to local
            coordinate space.
        """
        return self._transformation_matrix

    @check_input_types
    def transform_point2d_local_to_global(self, point: Point2D) -> Point3D:
        """Transform a 2D point to a global 3D point.

        This method transforms a local, plane-contained ``Point2D`` object in the global
        coordinate system, thus representing it as a ``Point3D`` object.

        Parameters
        ----------
        point : Point2D
            ``Point2D`` local object to express in global coordinates.

        Returns
        -------
        Point3D
            Global coordinates for the 3D point.
        """
        return self.origin + Vector3D(self.local_to_global_rotation @ [point[0], point[1], 0])

    @check_input_types
    def __eq__(self, other: "Frame") -> bool:
        """Equals operator for the ``Frame`` class."""
        return (
            self.origin == other.origin
            and self.direction_x == other.direction_x
            and self.direction_y == other.direction_y
            and self.direction_z == other.direction_z
        )

    def __ne__(self, other: "Frame") -> bool:
        """Not equals operator for the ``Frame`` class."""
        return not self == other
