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
"""Provides for creating and managing a segment."""

from beartype import beartype as check_input_types
import numpy as np
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.misc.checks import check_ndarray_is_all_nan
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS
from ansys.geometry.core.primitives.line import Line
from ansys.geometry.core.sketch.edge import SketchEdge


class SketchSegment(SketchEdge, Line):
    """
    Provides segment representation of a line.

    Parameters
    ----------
    start : Point2D
        Starting point of the line segment.
    end : Point2D
        Ending point of the line segment.
    plane : Plane, optional
        Plane containing the sketched circle, which is the global XY plane
        by default.
    """

    @check_input_types
    def __init__(
        self,
        start: Point2D,
        end: Point2D,
        plane: Plane = Plane(),
    ):
        """Initialize the ``SketchSegment`` class."""
        # Call SketchEdge init method
        SketchEdge.__init__(self)

        # Perform sanity checks on point values given
        check_ndarray_is_all_nan(start, "start")
        check_ndarray_is_all_nan(end, "end")

        # Assign values to start and end
        self._start = start
        self._end = end

        # Check segment points values and units
        if self._start == self._end:
            raise ValueError(
                "Parameters 'start' and 'end' have the same values. No segment can be created."
            )

        if not self._start.unit == self._end.unit:
            self._start.unit = self._end.unit = DEFAULT_UNITS.LENGTH

        # Call the Line init method
        self._init_primitive_line_from_plane(plane)

    def _init_primitive_line_from_plane(self, plane: Plane) -> None:
        """
        Initialize correctly the underlying primitive ``Line`` class.

        Parameters
        ----------
        plane : Plane
            Plane containing the sketched line.
        """
        # Find the global start and end points
        start_glb = plane.origin + Point3D(
            self.start[0] * plane.direction_x + self.start[1] * plane.direction_y,
            unit=self.start.base_unit,
        )
        end_glb = plane.origin + Point3D(
            self.end[0] * plane.direction_x + self.end[1] * plane.direction_y,
            unit=self.end.base_unit,
        )

        # Define the line direction
        line_direction = UnitVector3D.from_points(start_glb, end_glb)

        # Call the Line init method
        Line.__init__(self, start_glb, line_direction)

    @property
    def start(self) -> Point2D:
        """Starting point of the segment."""
        return self._start

    @property
    def end(self) -> Point2D:
        """Ending point of the segment."""
        return self._end

    @property
    def length(self) -> Quantity:
        """Length of the segment."""
        return np.sqrt(
            np.square(self._end.x - self._start.x) + np.square(self._end.y - self._start.y)
        )

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

        return pv.Line(
            np.array(
                [
                    self.start.x.m_as(DEFAULT_UNITS.LENGTH),
                    self.start.y.m_as(DEFAULT_UNITS.LENGTH),
                    0,
                ],
                dtype=np.float_,
            ),
            np.array(
                [self.end.x.m_as(DEFAULT_UNITS.LENGTH), self.end.y.m_as(DEFAULT_UNITS.LENGTH), 0],
                dtype=np.float_,
            ),
        )

    @check_input_types
    def __eq__(self, other: "SketchSegment") -> bool:
        """Equals operator for the ``SketchSegment`` class."""
        return self.start == other.start and self.end == other.end

    def __ne__(self, other: "SketchSegment") -> bool:
        """Not equals operator for the ``SketchSegment`` class."""
        return not self == other

    def plane_change(self, plane: "Plane") -> None:
        """
        Redefine the plane containing ``SketchSegment`` objects.

        Notes
        -----
        This implies that their 3D definition might suffer changes.

        Parameters
        ----------
        plane : Plane
            Desired new plane that is to contain the sketched segment.
        """
        # Reinitialize the line definition for the given plane
        self._init_primitive_line_from_plane(plane)
