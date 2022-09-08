"""``Polygon`` class module."""

from typing import List, Optional

import numpy as np

from ansys.geometry.core.math import UNIT_VECTOR_X, UNIT_VECTOR_Y
from ansys.geometry.core.math.point import Point3D
from ansys.geometry.core.math.vector import UnitVector3D
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.typing import Real


class Polygon(BaseShape):
    """A class for modeling regular polygons."""

    def __init__(
        self,
        radius: Real,
        sides: int,
        origin: Point3D,
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
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
            By default, [0, 0, 0].
        dir_1 : UnitVector3D
            A :class:``UnitVector3D`` representing the first fundamental direction
            of the reference plane where the shape is contained.
            By default, ``UNIT_VECTOR_X``.
        dir_2 : UnitVector3D
            A :class:``UnitVector3D`` representing the second fundamental direction
            of the reference plane where the shape is contained.
            By default, ``UNIT_VECTOR_Y``.
        """
        super().__init__(origin, dir_1=dir_1, dir_2=dir_2, is_closed=True)

        if radius <= 0:
            raise ValueError("Radius must be a real positive value.")
        self._radius = radius
        # Verify that the number of sides is valid with preferred range
        if sides < 3 or sides > 64:
            raise ValueError(
                "The number of sides to construct a polygon should be between 3 and 64."
            )
        self._n_sides = sides

    @property
    def radius(self) -> Real:
        """The inradius(apothem) of the polygon.

        Returns
        -------
        Real
            The inradius(apothem) of the polygon.

        """
        return self._radius

    @property
    def n_sides(self) -> int:
        """The number of sides of the polygon.

        Returns
        -------
        int
            The sides of the polygon.

        """
        return self._n_sides

    @property
    def length(self) -> Real:
        """The side length of the polygon.

        Returns
        -------
        int
            The side length of the polygon.

        """
        return 2 * self.radius * np.tan(np.pi / self.n_sides)

    @property
    def outer_radius(self) -> Real:
        """The outer radius of the polygon.

        Returns
        -------
        int
            The outer radius of the polygon.

        """
        return self.radius / np.cos(np.pi / self.n_sides)

    @property
    def perimeter(self) -> Real:
        """Return the perimeter of the polygon.

        Returns
        -------
        Real
            The perimeter of the polygon.

        """
        return self.n_sides * self.length

    @property
    def area(self) -> Real:
        """Return the area of the polygon.

        Returns
        -------
        Real
            The area of the polygon.

        """
        return (self.radius * self.perimeter) / 2

    def local_points(self) -> List[Point3D]:
        """Returns a list containing all the vertices of the polygon.

        Vertices are given in the local space.

        Returns
        -------
        list[Point3D]
            A list of vertices representing the shape.

        """
        theta = np.linspace(0, 2 * np.pi, self.n_sides + 1)
        x_local = self.outer_radius * np.cos(theta)
        y_local = self.outer_radius * np.sin(theta)
        z_local = np.zeros(self.n_sides + 1)
        return [x_local, y_local, z_local]

    @classmethod
    def from_radius(
        cls,
        radius: Real,
        sides: int,
        origin: Optional[Point3D] = Point3D([0, 0, 0]),
        dir_1: Optional[UnitVector3D] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector3D] = UNIT_VECTOR_Y,
    ):
        """Create a regular polygon from its origin, inradius(apothem) and number of sides.

        Parameters
        ----------
        radius : Real
            The inradius(apothem) of the polygon.
        sides : int
            Number of sides of the polygon.
        origin : Point3D
            A :class:``Point3D`` representing the origin of the polygon.
            By default, [0, 0, 0].
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
        # Generate the Polygon instance
        return cls(radius, sides, origin, dir_1=dir_1, dir_2=dir_2)
