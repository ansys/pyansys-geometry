"""``ArcSketch`` class module."""
from typing import List, Optional

import numpy as np

from ansys.geometry.core.math import Point3D, Vector3D
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.typing import Real


class Arc(BaseShape):
    """A class for modelling arcs."""

    def __init__(
        self,
        center: Point3D,
        start_point: Point3D,
        end_point: Point3D,
    ):
        """Initializes the arc shape.

        Parameters
        ----------
        center : Point3D
            A :class:``Point3D`` representing the center of the arc.
        start_point : Point3D
            A :class:``Point3D`` representing the start of the arc.
        end_points : Point3D
            A :class:``Point3D`` representing the end of the arc.

        """
        # Verify both points are not the same
        if start_point == end_point:
            raise ValueError("Start and end points must be different.")
        if center == start_point:
            raise ValueError("Center and start points must be different.")
        if center == end_point:
            raise ValueError("Center and end points must be different.")

        self._center, self._start_point, self._end_point = (center, start_point, end_point)
        self._axis_direction = self._axis_direction
        self._radius = vector_from_points(self.center, self.start_point).norm()


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
        start_vector = vector_from_points(self.center, self.start_point)
        end_vector = vector_from_points(self.center, self.end_point)
        self._angle = start_vector * end_vector
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
        return self.radius**2 * self.angle/2

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
        x_local = self.radius * np.cos(theta)
        y_local = self.radius * np.sin(theta)
        z_local = np.zeros(num_points)
        return [x_local, y_local, z_local]


def vector_from_points(point_a:Point3D, point_b:Point3D) -> Vector3D:
    x = point_b[0]-point_a[0]
    y = point_b[1]-point_a[1]
    z = point_b[2]-point_a[2]
    return Vector3D([x, y, z])