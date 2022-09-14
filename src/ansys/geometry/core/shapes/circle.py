"""``Circle`` class module."""
from typing import List, Optional, Union

import numpy as np
from pint import Quantity

from ansys.geometry.core.math import Plane, Point
from ansys.geometry.core.misc import Distance, check_type
from ansys.geometry.core.shapes.base import BaseShape


class Circle(BaseShape):
    """A class for modeling circles.

    Parameters
    ----------
    plane : Plane
        A :class:`Plane` representing the planar surface where the shape is contained.
    center: Point
        A :class:`Point` representing the center of the circle.
    radius : Union[Quantity, Distance]
        The radius of the circle.
    """

    def __init__(
        self,
        plane: Plane,
        center: Point,
        radius: Union[Quantity, Distance],
    ):
        """Initializes the circle shape."""
        super().__init__(plane, is_closed=True)

        check_type(center, Point)
        self._center = center
        if not self.plane.is_point_contained(center):
            raise ValueError("Center must be contained in the plane.")

        check_type(radius, (Quantity, Distance))
        self._radius = radius if isinstance(radius, Distance) else Distance(radius)
        if self._radius.value <= 0:
            raise ValueError("Radius must be a real positive value.")

    @property
    def center(self) -> Point:
        """The center of the circle.

        Returns
        -------
        Point
            The center of the circle.
        """
        return self._center

    @property
    def radius(self) -> Quantity:
        """The radius of the circle.

        Returns
        -------
        Quantity
            The radius of the circle.
        """
        return self._radius.value

    @property
    def diameter(self) -> Quantity:
        """The diameter of the circle.

        Returns
        -------
        Quantity
            The diameter of the circle.
        """
        return 2 * self.radius

    @property
    def perimeter(self) -> Quantity:
        """Return the perimeter of the circle.

        Returns
        -------
        Quantity
            The perimeter of the circle.
        """
        return 2 * np.pi * self.radius

    @property
    def area(self) -> Quantity:
        """Return the area of the circle.

        Returns
        -------
        Quantity
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

    def rotate(self, angle, axis):
        self._center = super().rotate(self.center, angle, axis)

    def translate(self, vector):
        self._center = super().translate(self.center, vector)

    def scale(self, vector):
        point = Point(
            [
                self.radius.m,
                0,
                0,
            ],
            unit=self.radius.units,
        )
        radius = super().scale(point, vector)
        self._radius.value = radius.x

    @classmethod
    def from_center_and_radius(
        cls, center: Point, radius: Union[Quantity, Distance], plane: Optional[Plane] = Plane()
    ):
        """Create a circle from its center and radius.

        Parameters
        ----------
        center: Point
            A :class:`Point` representing the center of the circle.
        radius : Real
            The radius of the circle.
        plane : Plane, optional
            A :class:`Plane` representing the planar surface where the shape is contained.
            By default, the base XY-Plane.

        Returns
        -------
        Circle
            An object for modeling circular shapes.
        """
        return cls(plane, center, radius)
