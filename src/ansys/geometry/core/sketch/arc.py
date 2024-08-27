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
"""Provides for creating and managing an arc."""

from beartype import beartype as check_input_types
import numpy as np
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math.matrix import Matrix
from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.math.vector import Vector2D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, Angle, Distance
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.sketch.edge import SketchEdge
from ansys.geometry.core.typing import Real


class Arc(SketchEdge):
    """Provides for modeling an arc.

    Parameters
    ----------
    start : Point2D
        Starting point of the arc.
    end : Point2D
        Ending point of the arc.
    center : Point2D
        Center point of the arc.
    clockwise : bool, default: False
        Whether the arc spans the clockwise angle between the start and end points.
        When ``False`` (default), the arc spans the counter-clockwise angle. When
        ``True``, the arc spands the clockwise angle.
    """

    @check_input_types
    def __init__(
        self,
        start: Point2D,
        end: Point2D,
        center: Point2D,
        clockwise: bool = False,
    ):
        """Initialize the arc shape."""
        super().__init__()
        if start == end:
            raise ValueError("Start and end points must be different.")
        if center == start:
            raise ValueError("Center and start points must be different.")
        if center == end:
            raise ValueError("Center and end points must be different.")

        if not np.isclose(
            np.linalg.norm(np.array(start - center)),
            np.linalg.norm(np.array(end - center)),
        ):
            raise ValueError(
                "The start and end points of the arc are not an equidistant from the center point."
            )

        # Store the main three points of the arc
        self._start, self._end, self._center = start, end, center

        # Compute the vectors from the center to the start and end points
        to_start_vector = Vector2D.from_points(start, center)
        to_end_vector = Vector2D.from_points(end, center)

        # Compute the radius of the arc
        self._radius = Quantity(to_start_vector.norm, self._start.base_unit)
        if not self._radius.m > 0:  # pragma: no cover
            raise ValueError("Point configuration does not yield a positive length arc radius.")

        # Compute the angle of the arc (always counter-clockwise at this point)
        self._angle = to_start_vector.get_angle_between(to_end_vector)

        # Check if the clockwise direction is desired... and recompute angle
        self._clockwise = clockwise
        if clockwise:
            self._angle = (2 * np.pi) - self._angle

    @property
    def start(self) -> Point2D:
        """Starting point of the arc line."""
        return self._start

    @property
    def end(self) -> Point2D:
        """Ending point of the arc line."""
        return self._end

    @property
    def center(self) -> Point2D:
        """Center point of the arc."""
        return self._center

    @property
    def length(self) -> Quantity:
        """Length of the arc."""
        return 2 * np.pi * self.radius * (self.angle.m / (2 * np.pi))

    @property
    def radius(self) -> Quantity:
        """Radius of the arc."""
        return self._radius

    @property
    def angle(self) -> Quantity:
        """Angle of the arc."""
        return Quantity(self._angle, UNITS.radian)

    @property
    def is_clockwise(self) -> bool:
        """Flag indicating whether the rotation of the angle is clockwise.

        Returns
        -------
        bool
            ``True`` if the sense of rotation is clockwise.
            ``False`` if the sense of rotation is counter-clockwise.
        """
        return self._clockwise

    @property
    def sector_area(self) -> Quantity:
        """Area of the sector of the arc."""
        return self.radius**2 * self.angle.m / 2

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """VTK polydata representation for PyVista visualization.

        Notes
        -----
        The representation lies in the X/Y plane within
        the standard global Cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            VTK pyvista.Polydata configuration.
        """
        if np.isclose(self.angle, np.pi):
            # PyVista hack... Maybe worth implementing something in PyVista...
            # A user should be able to define clockwise/counterclockwise sense of
            # rotation...
            return self.__arc_pyvista_hack()
        elif self.angle > np.pi:
            pv_negative = True

        else:
            pv_negative = False

        return pv.CircularArc(
            [
                self.start.x.m_as(DEFAULT_UNITS.LENGTH),
                self.start.y.m_as(DEFAULT_UNITS.LENGTH),
                0,
            ],
            [self.end.x.m_as(DEFAULT_UNITS.LENGTH), self.end.y.m_as(DEFAULT_UNITS.LENGTH), 0],
            [
                self.center.x.m_as(DEFAULT_UNITS.LENGTH),
                self.center.y.m_as(DEFAULT_UNITS.LENGTH),
                0,
            ],
            negative=pv_negative,
        )

    @check_input_types
    def __eq__(self, other: "Arc") -> bool:
        """Equals operator for the ``Arc`` class."""
        return bool(
            self.start == other.start
            and self.end == other.end
            and self.center == other.center
            and self.angle == other.angle
        )

    def __ne__(self, other: "Arc") -> bool:
        """Not equals operator for the ``Arc`` class."""
        return not self == other

    def __arc_pyvista_hack(self):
        """Hack for close to PI arcs.

        Notes
        -----
        PyVista does not know whether the rotation is
        clockwise or counterclockwise. It only understands the longest and shortest
        angle, which complicates things in the boundary.

        This means that the arc must be divided in two so that it is properly
        defined based on the known sense of rotation.

        Returns
        -------
        pyvista.PolyData
            VTK pyvista.Polydata configuration.
        """
        # Define the arc mid point
        if not self.is_clockwise:
            rot_matrix = np.array([[0, -1], [1, 0]])  # 90 degs rot matrix
        else:
            rot_matrix = np.array([[0, 1], [-1, 0]])  # -90 degs rot matrix
        center_to_start = Vector2D.from_points(self.center, self.start)
        center_to_mid = rot_matrix @ center_to_start
        mid_point2d = Point2D(
            [
                center_to_mid[0] + self.center.x.to_base_units().m,
                center_to_mid[1] + self.center.y.to_base_units().m,
            ],
            self.center.base_unit,
        )

        # Define auxiliary lists for PyVista containing the start, mid, end, and center points
        mid_point = [
            mid_point2d.x.m_as(DEFAULT_UNITS.LENGTH),
            mid_point2d.y.m_as(DEFAULT_UNITS.LENGTH),
            0,
        ]
        start_point = [
            self.start.x.m_as(DEFAULT_UNITS.LENGTH),
            self.start.y.m_as(DEFAULT_UNITS.LENGTH),
            0,
        ]
        end_point = [
            self.end.x.m_as(DEFAULT_UNITS.LENGTH),
            self.end.y.m_as(DEFAULT_UNITS.LENGTH),
            0,
        ]
        center_point = [
            self.center.x.m_as(DEFAULT_UNITS.LENGTH),
            self.center.y.m_as(DEFAULT_UNITS.LENGTH),
            0,
        ]

        # Compute the two independent arcs
        arc_sub1 = pv.CircularArc(
            start_point,
            mid_point,
            center_point,
        )
        arc_sub2 = pv.CircularArc(
            mid_point,
            end_point,
            center_point,
        )

        return arc_sub1 + arc_sub2

    @classmethod
    @check_input_types
    def from_three_points(cls, start: Point2D, inter: Point2D, end: Point2D):
        """Create an arc from three given points.

        Parameters
        ----------
        start : Point2D
            Starting point of the arc.
        inter : Point2D
            Intermediate point (location) of the arc.
        end : Point2D
            Ending point of the arc.

        Returns
        -------
        Arc
            Arc generated from the three points.
        """
        # Unpack the points into its coordinates (in DEFAULT_UNITS.LENGTH)
        x_s, y_s = start.tolist()
        x_i, y_i = inter.tolist()
        x_e, y_e = end.tolist()

        # Solve the circle equation to find out its center
        # (Xc - X)**2 + (Yc - Y)**2 = r**2
        #
        # Since r is the radius, and its constant, you can just simply solve
        # the system of equations formed by the three points, for (x_c, y_c)
        #
        # 2*(x_s - x_i)*x_c + 2*(y_s-y_i)*y_c + (x_i**2 + y_i**2 - x_s**2 - y_s**2) = 0
        # 2*(x_s - x_e)*x_c + 2*(y_s-y_e)*y_c + (x_e**2 + y_e**2 - x_s**2 - y_s**2) = 0
        #
        # Or...
        #
        # k11 * x_c + k12 * y_c = k1
        # k21 * x_c + k22 * y_c = k2
        #
        # Where...
        #
        # k11 = 2*(x_s - x_i)
        # k12 = 2*(y_s - y_i)
        # k21 = 2*(x_s - x_e)
        # k22 = 2*(y_s - y_e)
        #
        # k1 = (x_s**2 + y_s**2) - (x_i**2 + y_i**2)
        # k2 = (x_s**2 + y_s**2) - (x_e**2 + y_e**2)
        #
        # This is easily done with numpy!
        #
        k11 = 2 * (x_s - x_i)
        k12 = 2 * (y_s - y_i)
        k21 = 2 * (x_s - x_e)
        k22 = 2 * (y_s - y_e)

        k1 = (x_s**2 + y_s**2) - (x_i**2 + y_i**2)
        k2 = (x_s**2 + y_s**2) - (x_e**2 + y_e**2)

        x_c, y_c = np.linalg.solve([[k11, k12], [k21, k22]], [k1, k2])
        center = Point2D([x_c, y_c], unit=UNITS.meter)
        center.unit = DEFAULT_UNITS.LENGTH

        # Now, you should try to figure out if the rotation has to be clockwise or
        # counter-clockwise...
        center_start = Vector2D([x_s - x_c, y_s - y_c])
        center_inter = Vector2D([x_i - x_c, y_i - y_c])
        center_end = Vector2D([x_e - x_c, y_e - y_c])
        angle_s_i = Vector2D.get_angle_between(center_start, center_inter)
        angle_s_e = Vector2D.get_angle_between(center_start, center_end)

        is_clockwise = False if angle_s_i < angle_s_e else True

        # Finally... you can create the arc
        return Arc(start=start, end=end, center=center, clockwise=is_clockwise)

    @classmethod
    @check_input_types
    def from_start_end_and_radius(
        cls,
        start: Point2D,
        end: Point2D,
        radius: Quantity | Distance | Real,
        convex_arc: bool = False,
        clockwise: bool = False,
    ):
        """Create an arc from a starting point, an ending point, and a radius.

        Parameters
        ----------
        start : Point2D
            Starting point of the arc.
        end : Point2D
            Ending point of the arc.
        radius : ~pint.Quantity | Distance | Real
            Radius of the arc.
        convex_arc : bool, default: False
            Whether the arc is convex. The default is ``False``.
            When ``False``, the arc is concave. When ``True``, the arc is convex.
        clockwise : bool, default: False
            Whether the arc spans the clockwise angle between the start and end points.
            When ``False``, the arc spans the counter-clockwise angle.
            When ``True``, the arc spands the clockwise angle.

        Returns
        -------
        Arc
            Arc generated from the three points.
        """
        # Compute the potential centers of the circle
        # that could generate the arc
        from ansys.geometry.core.math.misc import get_two_circle_intersections

        # Sanitize the radius
        radius = radius if isinstance(radius, Distance) else Distance(radius)
        if radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

        # Unpack the points into its coordinates (in DEFAULT_UNITS.LENGTH)
        x_s, y_s = start.tolist()  # Always in meters
        x_e, y_e = end.tolist()  # Always in meters
        r0 = r1 = radius.value.m_as(UNITS.meter)  # Convert to meters as well

        # Compute the potential centers of the circle
        centers = get_two_circle_intersections(x0=x_s, y0=y_s, r0=r0, x1=x_e, y1=y_e, r1=r1)
        if centers is None:
            raise ValueError("The provided points and radius do not yield a valid arc.")

        # Choose the center depending on if the arc is convex
        center = Point2D(centers[1] if convex_arc else centers[0], unit=UNITS.meter)
        center.unit = DEFAULT_UNITS.LENGTH

        # Create the arc
        return Arc(start=start, end=end, center=center, clockwise=clockwise)

    @classmethod
    @check_input_types
    def from_start_center_and_angle(
        cls,
        start: Point2D,
        center: Point2D,
        angle: Angle | Quantity | Real,
        clockwise: bool = False,
    ):
        """Create an arc from a starting point, a center point, and an angle.

        Parameters
        ----------
        start : Point2D
            Starting point of the arc.
        center : Point2D
            Center point of the arc.
        angle : Angle | ~pint.Quantity | Real
            Angle of the arc.
        clockwise : bool, default: False
            Whether the provided angle should be considered clockwise.
            When ``False``, the angle is considered counter-clockwise.
            When ``True``, the angle is considered clockwise.

        Returns
        -------
        Arc
            Arc generated from the three points.
        """
        # Define a 2D vector from the center to the start point
        to_start_vector = Vector2D.from_points(center, start)

        # Perform sanity check for the angle
        angle = angle if isinstance(angle, Angle) else Angle(angle)
        rad_angle = angle.value.m_as(UNITS.radian)
        cang = np.cos(rad_angle)
        sang = np.sin(rad_angle)

        # Rotate the vector by the angle
        if clockwise:
            rot_matrix = Matrix([[cang, sang], [-sang, cang]])
        else:
            rot_matrix = Matrix([[cang, -sang], [sang, cang]])

        # Compute the end vector
        to_end_vector = rot_matrix @ to_start_vector

        # Define the end point
        end = Point2D(
            [
                to_end_vector[0] + center.x.to_base_units().m,
                to_end_vector[1] + center.y.to_base_units().m,
            ],
            center.base_unit,
        )

        # Create the arc
        return Arc(start=start, end=end, center=center, clockwise=clockwise)
