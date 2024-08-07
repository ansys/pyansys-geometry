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
"""Provides for creating and managing a circle."""

from beartype import beartype as check_input_types
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Distance
from ansys.geometry.core.shapes.curves.circle import Circle
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.typing import Real


class SketchCircle(SketchFace, Circle):
    """Provides for modeling a circle.

    Parameters
    ----------
    center: Point2D
        Center point of the circle.
    radius : ~pint.Quantity | Distance | Real
        Radius of the circle.
    plane : Plane, optional
        Plane containing the sketched circle, which is the global XY plane
        by default.
    """

    @check_input_types
    def __init__(self, center: Point2D, radius: Quantity | Distance | Real, plane: Plane = Plane()):
        """Initialize the circle."""
        # Call SketchFace init method
        SketchFace.__init__(self)

        # Store the 2D center of the circle
        self._center = center

        self._radius = radius if isinstance(radius, Distance) else Distance(radius)
        if self._radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

        # Call Circle init method
        self._init_primitive_circle_from_plane(plane, radius=radius)

    def _init_primitive_circle_from_plane(
        self, plane: Plane, radius: Quantity | Distance | None = None
    ) -> None:
        """Initialize correctly the underlying primitive ``Circle`` class.

        Parameters
        ----------
        plane : Plane
            Plane containing the sketched circle.
        radius : Quantity | Distance, default: None
            Radius of the circle (if any).
        """
        # Use the radius given (if any)
        radius = radius if radius else self.radius

        # Call Circle init method
        center_global = plane.origin + Point3D(
            self.center[0] * plane.direction_x + self.center[1] * plane.direction_y,
            unit=self.center.base_unit,
        )
        Circle.__init__(self, center_global, radius, plane.direction_x, plane.direction_z)

    @property
    def center(self) -> Point2D:
        """Center of the circle."""
        return self._center

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the circle.

        Notes
        -----
        This property resolves the dilemma between using the ``SkethFace.perimeter``
        property and the ``Circle.perimeter`` property.
        """
        return Circle.perimeter.fget(self)

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """VTK polydata representation for PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global Cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            VTK pyvista.Polydata configuration.
        """
        circle = pv.Circle(self.radius.m_as(DEFAULT_UNITS.LENGTH))
        return circle.translate(
            [
                self.center.x.m_as(DEFAULT_UNITS.LENGTH),
                self.center.y.m_as(DEFAULT_UNITS.LENGTH),
                0,
            ],
            inplace=True,
        )

    def plane_change(self, plane: Plane) -> None:
        """Redefine the plane containing the ``SketchCircle`` objects.

        Notes
        -----
        This implies that their 3D definition might suffer changes.

        Parameters
        ----------
        plane : Plane
            Desired new plane that is to contain the sketched circle.
        """
        # Reinitialize the circle definition for the given plane
        self._init_primitive_circle_from_plane(plane)
