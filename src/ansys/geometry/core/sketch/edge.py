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
"""Provides for creating and managing an edge."""

from typing import TYPE_CHECKING

from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math.point import Point2D

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.math.plane import Plane


class SketchEdge:
    """Provides for modeling edges forming sketched shapes."""

    @property
    def start(self) -> Point2D:
        """Starting point of the edge."""
        raise NotImplementedError("Each edge must provide the start point definition.")

    @property
    def end(self) -> Point2D:
        """Ending point of the edge."""
        raise NotImplementedError("Each edge must provide the end point definition.")

    @property
    def length(self) -> Quantity:
        """Length of the edge."""
        raise NotImplementedError("Each edge must provide the length definition.")

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
        raise NotImplementedError("Each edge must provide the polydata definition.")

    def plane_change(self, plane: "Plane") -> None:
        """Redefine the plane containing ``SketchEdge`` objects.

        Notes
        -----
        This implies that their 3D definition might suffer changes. By default, this
        metho does nothing. It is required to be implemented in child ``SketchEdge``
        classes.

        Parameters
        ----------
        plane : Plane
            Desired new plane that is to contain the sketched edge.
        """
        pass
