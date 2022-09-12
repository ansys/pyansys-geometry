"""``ArcSketch`` class module."""
from typing import List, Optional

import numpy as np

from ansys.geometry.core.math import Point, Vector
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.typing import Real


class Arc(BaseShape):
    """A class for modeling arcs."""

    def __init__(
        self,
        origin: Point,
        start_point: Point,
        end_point: Point,
    ):
        """Initializes the arc shape.

        Parameters
        ----------
        origin : Point
            A :class:``Point`` representing the center of the arc.
        start_point : Point
            A :class:``Point`` representing the start of the arc.
        end_points : Point
            A :class:``Point`` representing the end of the arc.

        """

        super().__init__(origin, dir_1=dir_1, dir_2=dir_2, is_closed=True)

        # Verify both points are not the same
        if start_point == end_point:
            raise ValueError("Start and end points must be different.")
        if origin == start_point:
            raise ValueError("Center and start points must be different.")
        if origin == end_point:
            raise ValueError("Center and end points must be different.")

        self._origin, self._start_point, self._end_point = (origin, start_point, end_point)

        self._start_vector = Vector.from_points(self._origin, self._start_point)
        self._end_vector = Vector.from_points(self._origin, self._end_point)

        super().__init__(
            origin,
            dir_1=self._start_vector / self._start_vector.norm,
            dir_2=self._end_vector // self._end_vector.norm,
        )

        self._radius = self._start_vector.norm

    @property
    def start_point(self) -> Point:
        """Return the start of the arc line.

        Returns
        -------
        Point
            Starting point of the arc line.

        """
        return self._start_point

    @property
    def end_point(self) -> Point:
        """Return the end of the arc line.

        Returns
        -------
        Point
            Ending point of the arc line.

        """
        return self._end_point

    @property
    def radius(self) -> Real:
        """The radius of the circle.

        Returns
        -------
        Real
            The radius of the circle.

        """
        return self._radius

    @property
    def angle(self) -> Real:
        """The angle of the arc.

        Returns
        -------
        Real
            The angle of the arc.

        """

        self._angle = np.arccos(self._start_vector * self._end_vector / self.radius**2)
        return self._angle

    @property
    def length(self) -> Real:
        """Return the length of the arc.

        Returns
        -------
        Real
            The length of the arc.

        """
        return 2 * np.pi * self.radius * self.angle

    @property
    def sector_area(self) -> Real:
        """Return the area of the sector of the arc.

        Returns
        -------
        Real
            The area of the sector of the arc.

        """
        return self.radius**2 * self.angle / 2

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
        theta = np.linspace(0, self.angle, num_points)
        return [
            Point(
                [
                    self.radius * np.cos(ang) + self.origin[0],
                    self.radius * np.sin(ang) + self.origin[1],
                    self.origin[2],
                ]
            )
            for ang in theta
        ]
