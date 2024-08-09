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
"""Provides for creating and managing a face (closed 2D sketch)."""

from typing import TYPE_CHECKING

from pint import Quantity
import pyvista as pv

from ansys.geometry.core.sketch.edge import SketchEdge

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.math.plane import Plane


class SketchFace:
    """Provides for modeling a face."""

    def __init__(self):
        """Initialize the face."""
        # TODO: What about the circular faces? Circle, Ellipse are not making use of this...
        # https://github.com/ansys/pyansys-geometry/issues/1319
        self._edges = []

    @property
    def edges(self) -> list[SketchEdge]:
        """List of all component edges forming the face."""
        return self._edges

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the face."""
        perimeter = 0
        for edge in self._edges:
            perimeter += edge.length
        return perimeter

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
        meshes = [edge.visualization_polydata for edge in self.edges]
        return pv.merge(meshes)

    def plane_change(self, plane: "Plane") -> None:
        """Redefine the plane containing ``SketchFace`` objects.

        Notes
        -----
        This implies that their 3D definition might suffer changes. This method does
        nothing by default. It is required to be implemented in child ``SketchFace`` classes.

        Parameters
        ----------
        plane : Plane
            Desired new plane that is to contain the sketched face.
        """
        pass
