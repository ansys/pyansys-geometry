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
"""Provides for creating and managing a polygon."""

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np
from pint import Quantity
import pyvista as pv
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math.matrix import Matrix33, Matrix44
from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Angle, Distance
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.typing import Real


class Polygon(SketchFace):
    """
    Provides for modeling regular polygons.

    Parameters
    ----------
    center: Point2D
        Center point of the circle.
    inner_radius : Union[Quantity, Distance, Real]
        Inner radius (apothem) of the polygon.
    sides : int
        Number of sides of the polygon.
    angle : Union[Quantity, Angle, Real], default: 0
        Placement angle for orientation alignment.
    """

    @check_input_types
    def __init__(
        self,
        center: Point2D,
        inner_radius: Union[Quantity, Distance, Real],
        sides: int,
        angle: Optional[Union[Quantity, Angle, Real]] = 0,
    ):
        """Initialize the polygon."""
        super().__init__()

        # Check the inputs
        self._center = center
        self._inner_radius = (
            inner_radius if isinstance(inner_radius, Distance) else Distance(inner_radius)
        )
        if self._inner_radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

        self._angle_offset = angle if isinstance(angle, Angle) else Angle(angle)

        # Verify that the number of sides is valid with preferred range
        if sides < 3:
            raise ValueError("The minimum number of sides to construct a polygon is three.")
        self._n_sides = sides

    @property
    def center(self) -> Point2D:
        """Center point of the polygon."""
        return self._center

    @property
    def inner_radius(self) -> Quantity:
        """Inner radius (apothem) of the polygon."""
        return self._inner_radius.value

    @property
    def n_sides(self) -> int:
        """Number of sides of the polygon."""
        return self._n_sides

    @property
    def angle(self) -> Quantity:
        """Orientation angle of the polygon."""
        return self._angle_offset.value

    @property
    def length(self) -> Quantity:
        """Side length of the polygon."""
        return 2 * self.inner_radius * np.tan(np.pi / self.n_sides)

    @property
    def outer_radius(self) -> Quantity:
        """Outer radius of the polygon."""
        return self.inner_radius / np.cos(np.pi / self.n_sides)

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the polygon."""
        return self.n_sides * self.length

    @property
    def area(self) -> Quantity:
        """Area of the polygon."""
        return (self.inner_radius * self.perimeter) / 2

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
        # Compensate z orientation by -np.pi / 2 to match Geometry service polygon processing
        # TODO : are we sure that the specific vertex we are targeting is the one matching the
        #        previous compensation angle? We could be rotating a different vertex for some
        #        reason. Anyway, it's a regular polygon, everything will look the same.
        #
        rotation = Matrix33(
            spatial_rotation.from_euler(
                "xyz",
                [0, 0, -np.pi / 2 + self.angle.m_as(UNITS.radian)],
                degrees=False,
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

        return pv.Polygon(
            radius=self.inner_radius.m_as(DEFAULT_UNITS.LENGTH),
            n_sides=self.n_sides,
        ).transform(transformation_matrix)
