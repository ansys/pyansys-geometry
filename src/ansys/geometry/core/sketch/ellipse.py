# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
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
"""Provides for creating and managing an ellipse."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np
from pint import Quantity
import pyvista as pv
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math.matrix import Matrix33, Matrix44
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.math.vector import Vector3D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Angle, Distance
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.primitives.ellipse import Ellipse
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.typing import Real


class SketchEllipse(SketchFace, Ellipse):
    """
    Provides for modeling an ellipse.

    Parameters
    ----------
    center: Point2D
        Center point of the ellipse.
    major_radius : Union[Quantity, Distance, Real]
        Major radius of the ellipse.
    minor_radius : Union[Quantity, Distance, Real]
        Minor radius of the ellipse.
    angle : Union[Quantity, Angle, Real], default: 0
        Placement angle for orientation alignment.
    plane : Plane, optional
        Plane containing the sketched ellipse, which is the global XY plane
        by default.
    """

    @check_input_types
    def __init__(
        self,
        center: Point2D,
        major_radius: Union[Quantity, Distance, Real],
        minor_radius: Union[Quantity, Distance, Real],
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
        plane: Plane = Plane(),
    ):
        """Initialize the ellipse."""
        # Call SketchFace init method
        SketchFace.__init__(self)

        # Store the 2D center of the ellipse
        self._center = center

        self._major_radius = (
            major_radius if isinstance(major_radius, Distance) else Distance(major_radius)
        )
        self._minor_radius = (
            minor_radius if isinstance(minor_radius, Distance) else Distance(minor_radius)
        )

        self._angle_offset = angle if isinstance(angle, Angle) else Angle(angle)

        # Call Ellipse init method
        self._init_primitive_ellipse_from_plane(
            plane, self._major_radius, self._minor_radius, self._angle_offset
        )

    def _init_primitive_ellipse_from_plane(
        self,
        plane: Plane,
        major_radius: Optional[Distance] = None,
        minor_radius: Optional[Distance] = None,
        angle: Optional[Angle] = None,
    ) -> None:
        """
        Initialize correctly the underlying primitive ``Ellipse`` class.

        Parameters
        ----------
        plane : Plane
            Plane containing the sketched ellipse.
        major_radius : [Distance], default: None
            Major radius of the ellipse (if any).
        minor_radius : [Distance], default: None
            Minor radius of the ellipse (if any).
        angle : [Angle], default: None
            Placement angle for orientation alignment.
        """
        major_radius = major_radius if major_radius else self.major_radius
        minor_radius = minor_radius if minor_radius else self.minor_radius
        angle = angle if angle else self.angle

        # Call Ellipse init method
        center_global = plane.origin + Point3D(
            self.center[0] * plane.direction_x + self.center[1] * plane.direction_y,
            unit=self.center.base_unit,
        )

        angle_rad = angle.value.m_as(UNITS.radian)
        new_rotated_dir_x = Vector3D(
            [
                np.cos(angle_rad) * plane.direction_x.x - np.sin(angle_rad) * plane.direction_x.y,
                np.sin(angle_rad) * plane.direction_x.x + np.cos(angle_rad) * plane.direction_x.y,
                plane.direction_x.z,
            ]
        )

        Ellipse.__init__(
            self, center_global, major_radius, minor_radius, new_rotated_dir_x, plane.direction_z
        )

    @property
    def center(self) -> Point2D:
        """Center point of the ellipse."""
        return self._center

    @property
    def angle(self) -> Quantity:
        """Orientation angle of the ellipse."""
        return self._angle_offset.value

    @property
    def perimeter(self) -> Quantity:
        """
        Perimeter of the circle.

        Notes
        -----
        This property resolves the dilemma between using the ``SkethFace.perimeter``
        property and the ``Ellipse.perimeter`` property.
        """
        return Ellipse.perimeter.fget(self)

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """
        VTK polydata representation for PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global Cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            VTK pyvista.Polydata configuration.
        """
        rotation = Matrix33(
            spatial_rotation.from_euler(
                "xyz", [0, 0, self._angle_offset.value.m_as(UNITS.radian)], degrees=False
            ).as_matrix()
        )

        transformation_matrix = Matrix44(
            [
                [
                    rotation[0, 0],
                    rotation[0, 1],
                    rotation[0, 2],
                    self.center.x.m_as(DEFAULT_UNITS.LENGTH),
                ],
                [
                    rotation[1, 0],
                    rotation[1, 1],
                    rotation[1, 2],
                    self.center.y.m_as(DEFAULT_UNITS.LENGTH),
                ],
                [
                    rotation[2, 0],
                    rotation[2, 1],
                    rotation[2, 2],
                    0,
                ],
                [0, 0, 0, 1],
            ]
        )

        return pv.Ellipse(
            semi_major_axis=self.major_radius.m_as(DEFAULT_UNITS.LENGTH),
            semi_minor_axis=self.minor_radius.m_as(DEFAULT_UNITS.LENGTH),
        ).transform(transformation_matrix)

    def plane_change(self, plane: Plane) -> None:
        """
        Redefine the plane containing ``SketchEllipse`` objects.

        Notes
        -----
        This implies that their 3D definition might suffer changes.

        Parameters
        ----------
        plane : Plane
            Desired new plane that is to contain the sketched ellipse.
        """
        # Reinitialize the Circle definition for the given plane
        self._init_primitive_ellipse_from_plane(plane)
