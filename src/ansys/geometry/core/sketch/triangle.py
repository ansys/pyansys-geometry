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
"""Provides for creating and managing a triangle."""

from beartype import beartype as check_input_types
import pyvista as pv

from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.segment import SketchSegment


class Triangle(SketchFace):
    """
    Provides for modeling 2D triangles.

    Parameters
    ----------
    point1: Point2D
        Point that represents a triangle vertex.
    point2: Point2D
        Point that represents a triangle vertex.
    point3: Point2D
        Point that represents a triangle vertex.
    """

    @check_input_types
    def __init__(self, point1: Point2D, point2: Point2D, point3: Point2D):
        """Initialize the triangle."""
        super().__init__()

        self._point1 = point1
        self._point2 = point2
        self._point3 = point3

        # TODO: add plane to SketchSegment when available

        self._edges.append(SketchSegment(self._point1, self._point2))
        self._edges.append(SketchSegment(self._point2, self._point3))
        self._edges.append(SketchSegment(self._point3, self._point1))

    @property
    def point1(self) -> Point2D:
        """Triangle vertex 1."""
        return self._point1

    @property
    def point2(self) -> Point2D:
        """Triangle vertex 2."""
        return self._point2

    @property
    def point3(self) -> Point2D:
        """Triangle vertex 3."""
        return self._point3

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
        import numpy as np

        return pv.Triangle(
            np.array(
                [
                    [
                        self.point1.x.m_as(DEFAULT_UNITS.LENGTH),
                        self.point1.y.m_as(DEFAULT_UNITS.LENGTH),
                        0,
                    ],
                    [
                        self.point2.x.m_as(DEFAULT_UNITS.LENGTH),
                        self.point2.y.m_as(DEFAULT_UNITS.LENGTH),
                        0,
                    ],
                    [
                        self.point3.x.m_as(DEFAULT_UNITS.LENGTH),
                        self.point3.y.m_as(DEFAULT_UNITS.LENGTH),
                        0,
                    ],
                ],
                dtype=np.float_,
            )
        )
