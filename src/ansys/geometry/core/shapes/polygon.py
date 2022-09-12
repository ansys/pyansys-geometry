"""``Polygon`` class module."""

from typing import List, Union

import numpy as np
from pint import Quantity

from ansys.geometry.core.math import Plane, Point
from ansys.geometry.core.misc import Distance, check_type
from ansys.geometry.core.shapes.base import BaseShape


class Polygon(BaseShape):
    """A class for modeling regular polygon.

    Parameters
    ----------
    plane : Plane
        A :class:`Plane` representing the planar surface where the shape is contained.
    center: Point
        A :class:`Point` representing the center of the circle.
    inner_radius : Union[Quantity, Distance]
        The inradius(apothem) of the polygon.
    sides : int
        Number of sides of the polygon.
    """

    def __init__(
        self,
        plane: Plane,
        center: Point,
        inner_radius: Union[Quantity, Distance],
        sides: int,
    ):
        """Initializes the polygon shape."""
        # Call the BaseShape ctor.
        super().__init__(plane, is_closed=True)

        # Check the inputs
        check_type(center, Point)
        self._center = center
        if not self.plane.is_point_contained(center):
            raise ValueError("Center must be contained in the plane.")

        check_type(inner_radius, (Quantity, Distance))
        self._inner_radius = (
            inner_radius if isinstance(inner_radius, Distance) else Distance(inner_radius)
        )
        if self._inner_radius.value.m_as(inner_radius.base_unit) <= 0:
            raise ValueError("Radius must be a real positive value.")

        # Verify that the number of sides is valid with preferred range
        if sides < 3:
            raise ValueError("The minimum number of sides to construct a polygon should be 3.")
        # TODO : raise warning if the number of sides greater than 64
        # it cannot be handled server side
        self._n_sides = sides

    @property
    def center(self) -> Point:
        """The center of the polygon.

        Returns
        -------
        Point
            The center of the polygon.
        """
        return self._center

    @property
    def inner_radius(self) -> Quantity:
        """The inradius(apothem) of the polygon.

        Returns
        -------
        Quantity
            The inradius(apothem) of the polygon.

        """
        return self._inner_radius.value

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
    def length(self) -> Quantity:
        """The side length of the polygon.

        Returns
        -------
        Quantity
            The side length of the polygon.

        """
        return 2 * self.inner_radius * np.tan(np.pi / self.n_sides)

    @property
    def outer_radius(self) -> Quantity:
        """The outer radius of the polygon.

        Returns
        -------
        Quantity
            The outer radius of the polygon.

        """
        return self.inner_radius / np.cos(np.pi / self.n_sides)

    @property
    def perimeter(self) -> Quantity:
        """Return the perimeter of the polygon.

        Returns
        -------
        Quantity
            The perimeter of the polygon.

        """
        return self.n_sides * self.length

    @property
    def area(self) -> Quantity:
        """Return the area of the polygon.

        Returns
        -------
        Quantity
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
            Point(
                [self.outer_radius.m * np.cos(ang), self.outer_radius.m * np.sin(ang), 0.0],
                unit=self.outer_radius.units,
            )
            for ang in theta
        ]
