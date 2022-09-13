"""``ArcSketch`` class module."""

from typing import List, Optional

import numpy as np
from pint import Quantity

from ansys.geometry.core.math import Plane, Point, QuantityVector
from ansys.geometry.core.math.vector import UnitVector
from ansys.geometry.core.misc import UNITS, check_type
from ansys.geometry.core.shapes.base import BaseShape


class Arc(BaseShape):
    """A class for modeling arcs."""

    def __init__(self, plane: Plane, center: Point, start: Point, end: Point, axis: UnitVector):
        """Initializes the arc shape.

        Parameters
        ----------
        plane : Plane
            A :class:`Plane` representing the planar surface where the shape is contained.
        center : Point
            A :class:``Point`` representing the center of the arc.
        start: Point
            A :class:``Point`` representing the start of the arc.
        end : Point
            A :class:``Point`` representing the end of the arc.
        axis : Vector
            A :class:``UnitVector`` determining the rotation direction of the arc.

        """
        super().__init__(plane, is_closed=False)
        # Verify points
        check_type(center, Point)
        check_type(start, Point)
        check_type(end, Point)
        if start == end:
            raise ValueError("Start and end points must be different.")
        if center == start:
            raise ValueError("Center and start points must be different.")
        if center == end:
            raise ValueError("Center and end points must be different.")
        if not self._plane.is_point_contained(center):
            raise ValueError("Center point must be contained in the plane.")
        if not self._plane.is_point_contained(start):
            raise ValueError("Arc start point must be contained in the plane.")
        if not self._plane.is_point_contained(end):
            raise ValueError("Arc end point must be contained in the plane.")

        self._center, self._start, self._end = center, start, end
        self._axis = axis

        to_start_vector = QuantityVector.from_points(self._start, self._center)
        self._radius = to_start_vector.norm

        if not self._radius.m > 0:
            raise ValueError("Point configuration does not yield a positive length arc radius.")

        direction_x = UnitVector(to_start_vector.normalize())
        direction_y = UnitVector((axis % direction_x).normalize())
        to_end_vector = UnitVector.from_points(self._end, self._center)
        self._angle = np.arctan2(direction_y * to_end_vector, direction_x * to_end_vector)
        if self._angle < 0:
            self._angle = (2 * np.pi) + self._angle

    @property
    def start(self) -> Point:
        """Return the start of the arc line.

        Returns
        -------
        Point
            Starting point of the arc line.

        """
        return self._start

    @property
    def end(self) -> Point:
        """Return the end of the arc line.

        Returns
        -------
        Point
            Ending point of the arc line.

        """
        return self._end

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
    def center(self) -> Point:
        """The center of the arc.

        Returns
        -------
        Point
            The center of the arc.

        """
        return self._center

    @property
    def axis(self) -> UnitVector:
        """The axis determining arc rotation.

        Returns
        -------
        UnitVector
            The axis determining arc rotation.

        """
        return self._axis

    @property
    def angle(self) -> Quantity:
        """The angle of the arc.

        Returns
        -------
        Quantity
            The angle of the arc.

        """

        self._angle = np.arctan2(
            (self._start_vector.cross(self._end_vector)).norm.m,
            (self._start_vector.dot(self._end_vector)),
        )
        return Quantity(self._angle, UNITS.radian)

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
    def sector_area(self) -> Quantity:
        """Return the area of the sector of the arc.

        Returns
        -------
        Quantity
            The area of the sector of the arc.

        """
        return self.radius**2 * self.angle.m / 2

    def local_points(self, num_points: Optional[int] = 100) -> List[Point]:
        """Returns al list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point]
            A list of points representing the shape.

        """
        local_start_vector = (self.plane.global_to_local @ self._start_vector).tolist()

        start_angle = np.arctan2(
            (Vector(local_start_vector).cross(Vector([1, 0, 0]))).norm,
            Vector(local_start_vector).dot(Vector([1, 0, 0])),
        )

        theta = np.linspace(start_angle, start_angle + self.angle.m, num_points)
        return [
            Point(
                [
                    self.center.x.to(self.radius.units).m + self.radius.m * np.cos(ang),
                    self.center.y.to(self.radius.units).m + self.radius.m * np.sin(ang),
                    self.center.z.to(self.radius.units).m,
                ],
                unit=self.radius.units,
            )
            for ang in theta
        ]
