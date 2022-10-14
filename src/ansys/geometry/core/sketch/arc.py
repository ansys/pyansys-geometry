"""``SketchArc`` class module."""

from typing import Optional

import numpy as np
from pint import Quantity

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.math.constants import UNITVECTOR3D_Z
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D, Vector3D
from ansys.geometry.core.misc import UNITS, check_type
from ansys.geometry.core.misc.checks import check_type_equivalence
from ansys.geometry.core.sketch.edge import SketchEdge


class SketchArc(SketchEdge):
    """A class for modeling arcs."""

    def __init__(
        self,
        center: Point2D,
        start: Point2D,
        end: Point2D,
        negative_angle: Optional[bool] = False,
    ):
        """Initializes the arc shape.

        Parameters
        ----------
        center : Point2D
            A :class:`Point2D` representing the center of the arc.
        start: Point2D
            A :class:`Point2D` representing the start of the arc.
        end : Point2D
            A :class:`Point2D` representing the end of the arc.
        negative_angle : bool, optional
            By default the arc spans the shortest angular sector between
            ``start`` and ``end``.

            By setting this to ``True``, the longest angular sector is
            used instead (i.e. the negative coterminal angle to the
            shortest one).
        """
        super().__init__()

        check_type(center, Point2D)
        check_type(start, Point2D)
        check_type(end, Point2D)

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
                "The start and end points of the arc are not equidistant from center point."
            )

        self._center, self._start, self._end = center, start, end
        start3D = Point3D([self._start.x.m, self._start.y.m, 0], self._start.unit)
        end3D = Point3D([self._end.x.m, self._end.y.m, 0], self._end.unit)
        center3D = Point3D([self._center.x.m, self._center.y.m, 0], self._center.unit)
        to_start_vector = Vector3D.from_points(start3D, center3D)
        self._radius = Quantity(to_start_vector.norm, self._start.base_unit)

        if not self._radius.m > 0:
            raise ValueError("Point configuration does not yield a positive length arc radius.")

        direction_x = UnitVector3D(to_start_vector.normalize())
        direction_y = UnitVector3D((UNITVECTOR3D_Z % direction_x).normalize())
        to_end_vector = UnitVector3D.from_points(end3D, center3D)
        self._angle = np.arctan2(direction_y * to_end_vector, direction_x * to_end_vector)
        if self._angle < 0:
            self._angle = (2 * np.pi) + self._angle

        if (self._angle > np.pi and not negative_angle) or (self._angle < np.pi and negative_angle):
            self._angle = (2 * np.pi) - self._angle
            self._positive_rotation_axis = False
        else:
            self._positive_rotation_axis = True

        self._negative_angle = negative_angle

    @property
    def start(self) -> Point2D:
        """Return the start of the arc line.

        Returns
        -------
        Point2D
            Starting point of the arc line.
        """
        return self._start

    @property
    def end(self) -> Point2D:
        """Return the end of the arc line.

        Returns
        -------
        Point2D
            Ending point of the arc line.
        """
        return self._end

    @property
    def length(self) -> Quantity:
        """Return the length of the arc.

        Returns
        -------
        Quantity
            The length of the arc.
        """
        return 2 * np.pi * self.radius * (self.angle.m / (2 * np.pi))

    @property
    def radius(self) -> Quantity:
        """The radius of the arc.

        Returns
        -------
        Quantity
            The radius of the arc.
        """
        return self._radius

    @property
    def center(self) -> Point2D:
        """The center of the arc.

        Returns
        -------
        Point2D
            The center of the arc.
        """
        return self._center

    @property
    def negative_angle(self) -> bool:
        """The arc setting determining angle target.

        Returns
        -------
        bool
            If ``True``, the longest angular sector is used.
            If ``False``, the shortest angular sector is used.
        """
        return self._negative_angle

    @property
    def angle(self) -> Quantity:
        """The angle of the arc.

        Returns
        -------
        Quantity
            The angle of the arc.
        """

        return Quantity(self._angle, UNITS.radian)

    @property
    def positive_rotation_axis(self) -> bool:
        """Indication for the axis of rotation direction.

        Returns
        -------
        bool
            ``True`` if the axis of rotation is the positive z-axis.
        """

        return self._positive_rotation_axis

    @property
    def sector_area(self) -> Quantity:
        """Return the area of the sector of the arc.

        Returns
        -------
        Quantity
            The area of the sector of the arc.
        """
        return self.radius**2 * self.angle.m / 2

    def __eq__(self, other: "SketchArc") -> bool:
        """Equals operator for ``SketchArc``."""
        check_type_equivalence(other, self)
        return (
            self.start == other.start
            and self.end == other.end
            and self.center == other.center
            and self._angle == other._angle
        )

    def __ne__(self, other: "SketchArc") -> bool:
        """Not equals operator for ``SketchArc``."""
        return not self == other
