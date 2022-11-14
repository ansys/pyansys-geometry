"""``Arc`` class module."""

from beartype import beartype as check_input_types
from beartype.typing import Optional
import numpy as np
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math import Point2D, Vector2D
from ansys.geometry.core.misc import UNIT_LENGTH, UNITS
from ansys.geometry.core.sketch.edge import SketchEdge


class Arc(SketchEdge):
    """Provides for modeling arcs."""

    @check_input_types
    def __init__(
        self,
        center: Point2D,
        start: Point2D,
        end: Point2D,
        clockwise: Optional[bool] = False,
    ):
        """Initializes the arc shape.

        Parameters
        ----------
        center : Point2D
            A :class:`Point2D <ansys.geometry.core.math.point.Point2D>` representing
            the center of the arc.
        start: Point2D
            :class:`Point2D <ansys.geometry.core.math.point.Point2D>` class representing
            the start of the arc.
        end : Point2D
            A :class:`Point2D <ansys.geometry.core.math.point.Point2D>` representing
            the end of the arc.
        clockwise : bool, default: False
            Whether the arc spans the clockwise angle between the start
            and end points. By default, the arc spans the counter-clockwise angle. When
            ``True``, the arc spands the clockwise angle.
        """
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
        self._center, self._start, self._end = center, start, end

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
        """2D point that is the start of the arc line."""
        return self._start

    @property
    def end(self) -> Point2D:
        """2D point that is the end of the arc line."""
        return self._end

    @property
    def length(self) -> Quantity:
        """Length of the arc."""
        return 2 * np.pi * self.radius * (self.angle.m / (2 * np.pi))

    @property
    def radius(self) -> Quantity:
        """Radius of the arc."""
        return self._radius

    @property
    def center(self) -> Point2D:
        """2D point that is the center of the arc."""
        return self._center

    @property
    def angle(self) -> Quantity:
        """Angle of the arc."""
        return Quantity(self._angle, UNITS.radian)

    @property
    def is_clockwise(self) -> bool:
        """Whether the rotation of the angle is clockwise.

        Returns
        -------
        bool
            ``True`` if the sense of rotation is clockwise.
            ``False`` if it is counter-clockwise.
        """

        return self._clockwise

    @property
    def sector_area(self) -> Quantity:
        """Area of the sector of the arc."""
        return self.radius**2 * self.angle.m / 2

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """VTK polydata representation for the PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global Cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            VTK pyvista.Polydata configuration.
        """

        if np.isclose(self.angle, np.pi):
            # TODO : PyVista hack... Maybe worth implementing something in PyVista...
            #        A user should be able to define clockwise/counterclockwise sense of
            #        rotation...
            return self.__arc_pyvista_hack()
        elif self.angle > np.pi:
            pv_negative = True

        else:
            pv_negative = False

        return pv.CircularArc(
            [
                self.start.x.m_as(UNIT_LENGTH),
                self.start.y.m_as(UNIT_LENGTH),
                0,
            ],
            [self.end.x.m_as(UNIT_LENGTH), self.end.y.m_as(UNIT_LENGTH), 0],
            [
                self.center.x.m_as(UNIT_LENGTH),
                self.center.y.m_as(UNIT_LENGTH),
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
        """
        Hack for close to PI arcs. PyVista does not know whether the
        rotation is clockwise or counterclockwise. It only understands
        the longest and shortest angle, which complicates things in the boundary.

        This means that we need to divide the arc in two so that it is properly
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
            mid_point2d.x.m_as(UNIT_LENGTH),
            mid_point2d.y.m_as(UNIT_LENGTH),
            0,
        ]
        start_point = [
            self.start.x.m_as(UNIT_LENGTH),
            self.start.y.m_as(UNIT_LENGTH),
            0,
        ]
        end_point = [self.end.x.m_as(UNIT_LENGTH), self.end.y.m_as(UNIT_LENGTH), 0]
        center_point = [
            self.center.x.m_as(UNIT_LENGTH),
            self.center.y.m_as(UNIT_LENGTH),
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
