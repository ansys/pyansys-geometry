"""``Circle`` class module."""
from typing import List, Optional

import numpy as np

from ansys.geometry.core.math import UNIT_VECTOR_X, UNIT_VECTOR_Y
from ansys.geometry.core.math.point import Point
from ansys.geometry.core.math.vector import UnitVector
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.typing import Real


class Circle(BaseShape):
    """A class for modeling circles.

    Parameters
    ----------
    radius : Real
        The radius of the circle.
    origin : Point
        A :class:`Point` representing the origin of the shape.
    dir_1 : Optional[UnitVector]
        A :class:`UnitVector` representing the first fundamental direction
        of the reference plane where the shape is contained.
        By default, ``UNIT_VECTOR_X``.
    dir_2 : Optional[UnitVector]
        A :class:`UnitVector` representing the second fundamental direction
        of the reference plane where the shape is contained.
        By default, ``UNIT_VECTOR_Y``.
    """

    def __init__(
        self,
        radius: Real,
        origin: Point,
        dir_1: Optional[UnitVector] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector] = UNIT_VECTOR_Y,
    ):
        """Initializes the circle shape."""
        super().__init__(origin, dir_1=dir_1, dir_2=dir_2, is_closed=True)
        if radius <= 0:
            raise ValueError("Radius must be a real positive value.")
        self._radius = radius

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
    def diameter(self) -> Real:
        """The diameter of the circle.

        Returns
        -------
        Real
            The diameter of the circle.
        """
        return 2 * self.radius

    @property
    def perimeter(self) -> Real:
        """Return the perimeter of the circle.

        Returns
        -------
        Real
            The perimeter of the circle.
        """
        return 2 * np.pi * self.radius

    @property
    def area(self) -> Real:
        """Return the area of the circle.

        Returns
        -------
        Real
            The area of the circle.
        """
        return np.pi * self.radius**2

    def local_points(self, num_points: Optional[int] = 100) -> List[Point]:
        """Returns a list containing all the points belonging to the shape.

        Points are given in the local space.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point]
            A list of points representing the shape.
        """
        theta = np.linspace(0, 2 * np.pi, num_points)
        return [Point([self.radius * np.cos(ang), self.radius * np.sin(ang), 0.0]) for ang in theta]

    @classmethod
    def from_radius(
        cls,
        radius: Real,
        origin: Optional[Point] = Point([0, 0, 0]),
        dir_1: Optional[UnitVector] = UNIT_VECTOR_X,
        dir_2: Optional[UnitVector] = UNIT_VECTOR_Y,
    ):
        """Create a circle from its origin and radius.

        Parameters
        ----------
        radius : Real
            The radius of the circle.
        origin : Optional[Point]
            A :class:`Point` representing the origin of the ellipse.
            By default, [0, 0, 0].
        dir_1 : Optional[UnitVector]
            A :class:`UnitVector` representing the first fundamental direction
            of the reference plane where the shape is contained.
            By default, ``UNIT_VECTOR_X``.
        dir_2 : Optional[UnitVector]
            A :class:`UnitVector` representing the second fundamental direction
            of the reference plane where the shape is contained.
            By default, ``UNIT_VECTOR_Y``.

        Returns
        -------
        Circle
            An object for modeling circular shapes.
        """
        # Verify that the radius is a real positive value
        if radius <= 0:
            raise ValueError("Radius must be a real positive value.")

        # Generate all the point instances
        return cls(radius, origin, dir_1=dir_1, dir_2=dir_2)
