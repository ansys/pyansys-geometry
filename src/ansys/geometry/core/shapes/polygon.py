"""``Polygon`` class module."""

from typing import List, Optional

import numpy as np

from ansys.geometry.core.math import UNIT_VECTOR_X, UNIT_VECTOR_Y
from ansys.geometry.core.math.point import Point
from ansys.geometry.core.math.vector import UnitVector
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.typing import Real


class Polygon(BaseShape):
    """A class for modeling polygon.

    Parameters
    ----------
    radius : Real
        The inradius(apothem) of the polygon.
    sides : int
        Number of sides of the polygon.
    origin : Point
        A :class:``Point`` representing the origin of the shape.
        By default, [0, 0, 0].
    dir_1 : UnitVector
        A :class:``UnitVector`` representing the first fundamental direction
        of the reference plane where the shape is contained.
        By default, ``UNIT_VECTOR_X``.
    dir_2 : UnitVector
        A :class:``UnitVector`` representing the second fundamental direction
        of the reference plane where the shape is contained.
        By default, ``UNIT_VECTOR_Y``.
    """

    def __init__(
        self,
        inner_radius: Real,
        sides: int,
        origin: Point,
        dir_1: Optional[UnitVector] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector] = UNIT_VECTOR_Y,
    ):
        """Initializes the polygon shape."""
        super().__init__(origin, dir_1=dir_1, dir_2=dir_2, is_closed=True)

        if inner_radius <= 0:
            raise ValueError("Radius must be a real positive value.")
        self._radius = inner_radius
        # Verify that the number of sides is valid with preferred range
        if sides < 3:
            raise ValueError("The minimum number of sides to construct a polygon should be 3.")
        # TODO : raise warning if the number of sides greater than 64
        # it cannot be handled server side
        self._n_sides = sides

    @property
    def inner_radius(self) -> Real:
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
        return 2 * self.inner_radius * np.tan(np.pi / self.n_sides)

    @property
    def outer_radius(self) -> Real:
        """The outer radius of the polygon.

        Returns
        -------
        int
            The outer radius of the polygon.

        """
        return self.inner_radius / np.cos(np.pi / self.n_sides)

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
        return (self.inner_radius * self.perimeter) / 2

    def local_points(self) -> List[Point]:
        """Returns a list containing all the vertices of the polygon.

        Vertices are given in the local space.

        Returns
        -------
        list[Point]
            A list of vertices representing the shape.

        """
        theta = np.linspace(0, 2 * np.pi, self.n_sides + 1)
        return [
            Point([self.outer_radius * np.cos(ang), self.outer_radius * np.sin(ang), 0.0])
            for ang in theta
        ]
