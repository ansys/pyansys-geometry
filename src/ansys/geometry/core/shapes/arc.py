"""``ArcSketch`` class module."""
from typing import List, Optional

import numpy as np

from ansys.geometry.core.math import Point3D, vector
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.typing import Real


class Arc(BaseShape):
    """A class for modelling arcs."""

    def __init__(
        self,
        origin: Point3D,
        start_point: Point3D,
        end_point: Point3D,
    ):
        """Initializes the arc shape.

        Parameters
        ----------
        origin : Point3D
            A :class:``Point3D`` representing the center of the arc.
        start_point : Point3D
            A :class:``Point3D`` representing the start of the arc.
        end_points : Point3D
            A :class:``Point3D`` representing the end of the arc.

        """
        # Verify both points are not the same
        if start_point == end_point:
            raise ValueError("Start and end points must be different.")
        if origin == start_point:
            raise ValueError("Center and start points must be different.")
        if origin == end_point:
            raise ValueError("Center and end points must be different.")

        self._origin, self._start_point, self._end_point = (origin, start_point, end_point)

        self._start_vector = vector.Vector3D.from_points(self._origin, self._start_point)
        self._end_vector = vector.Vector3D.from_points(self._origin, self._end_point)
        self._radius = self._start_vector.norm

    @property
    def start_point(self) -> Point3D:
        """Return the start of the arc line.

        Returns
        -------
        Point3D
            Starting point of the arc line.

        """
        return self._start_point

    @property
    def end_point(self) -> Point3D:
        """Return the end of the arc line.

        Returns
        -------
        Point3D
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
        """The angle of the circle.

        Returns
        -------
        Real
            The angle of the circle.

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

    def local_points(self, num_points: Optional[int] = 100) -> List[Point3D]:
        """Returns al list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point3D]
            A list of points representing the shape.

        """
        theta = np.linspace(0, self.angle, num_points)
        x_local = self.radius * np.cos(theta) + self.origin[0]
        y_local = self.radius * np.sin(theta) + self.origin[1]
        z_local = np.zeros(num_points) + self.origin[2]
        return [x_local, y_local, z_local]
