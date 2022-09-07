"""``Polygon`` class module."""

from typing import List, Optional

import numpy as np

from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.typing import Real


class PolygonShape(BaseShape):
    """A class for modelling polygon."""

    def __init__(
        self,
        radius: Real,
        sides: int,
        origin: Point3D,
        dir_1: UnitVector3D([1, 0, 0]),
        dir_2: UnitVector3D([0, 1, 0]),
    ):
        """Initializes the polygon shape.

        Parameters
        ----------
        radius : Real
            The inradius(apothem) of the polygon.
        sides : int
            Number of sides of the polygon.
        origin : Point3D
            A :class:``Point3D`` representing the origin of the shape.
        dir_1 : UnitVector3D
            A :class:``UnitVector3D`` representing the first fundamental direction
            of the reference plane where the shape is contained.
        dir_2 : UnitVector3D
            A :class:``UnitVector3D`` representing the second fundamental direction
            of the reference plane where the shape is contained.

        """
        super().__init__(origin, dir_1, dir_2, is_closed=True)
        self._radius = radius
        self._sides = sides

    @property
    def radius(self) -> Real:
        """The radius of the polygon.

        Returns
        -------
        Real
            The radius of the polygon.

        """
        return self._radius

    @property
    def r(self) -> Real:
        """The radius of the polygon.

        Returns
        -------
        Real
            The radius of the polygon.

        """
        return self.radius

    @property
    def sides(self) -> int:
        """The sides of the polygon.

        Returns
        -------
        int
            The sides of the polygon.

        """
        return self._sides

    @property
    def n(self) -> int:
        """The sides of the polygon.

        Returns
        -------
        int
            The sides of the polygon.

        """
        return self.sides

    @property
    def outer_radius(self):
        """The side length of the polygon.

        Returns
        -------
        int
            The side length of the polygon.

        """
        return self.r / (np.cos(180 / self.n))

    @property
    def length(self) -> Real:
        """The side length of the polygon.

        Returns
        -------
        int
            The side length of the polygon.

        """
        return 2 * self.r * np.tan(180 / self.n)

    @property
    def perimeter(self) -> Real:
        """Return the perimeter of the polygon.

        Returns
        -------
        Real
            The perimeter of the polygon.

        """
        return self.n * self.length

    @property
    def area(self) -> Real:
        """Return the area of the polygon.

        Returns
        -------
        Real
            The area of the polygon.

        """
        return (self.r * self.perimeter) / 2

    def local_points(self, num_points: Optional[int] = 100) -> List[Point3D]:
        """Returns a list containing all the points belonging to the shape.

        Points are given in the local space.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        list[Point3D]
            A list of points representing the shape.

        """
        theta = np.linspace(0, 2 * np.pi, num_points)
        x_local = self.r * np.cos(theta)
        y_local = self.r * np.sin(theta)
        z_local = np.zeros(num_points)
        return [x_local, y_local, z_local]

    @classmethod
    def from_radius(
        cls,
        radius: Real,
        sides: int,
        origin: Optional[Point3D] = Point3D([0, 0, 0]),
        dir_1: Optional[UnitVector3D] = UnitVector3D([1, 0, 0]),
        dir_2: Optional[UnitVector3D] = UnitVector3D([0, 1, 0]),
    ):
        """Create a polygon from its origin, inradius(apothem) and number of sides.

        Parameters
        ----------
        radius : Real
            The inradius(apothem) of the polygon.
        sides : int
            Number of sides of the polygon.
        origin : Point3D
            A :class:``Point3D`` representing the origin of the ellipse.
        dir_1 : UnitVector3D
            A :class:``UnitVector3D`` representing the first fundamental direction
            of the reference plane where the shape is contained.
        dir_2 : UnitVector3D
            A :class:``UnitVector3D`` representing the second fundamental direction
            of the reference plane where the shape is contained.

        Returns
        -------
        PolygonShape
            An object for modelling polygonal shapes.

        """
        # Verify that the radius is a real positive value
        if radius <= 0:
            raise ValueError("Radius must be a real positive value.")

        # Generate all the point instances
        return cls(radius, sides, origin, dir_1, dir_2)
