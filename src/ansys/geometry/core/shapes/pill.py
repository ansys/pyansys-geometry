"""``Pill`` class module."""
from typing import List, Optional, Union

import numpy as np
from pint import Quantity

from ansys.geometry.core.math import Plane, Point
from ansys.geometry.core.misc import Distance, check_type
from ansys.geometry.core.shapes.arc import Arc
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.shapes.line import Segment


class Pill(BaseShape):
    """A class for modeling 2D pill shaped.

    Parameters
    ----------
    plane : Plane
        A :class:`Plane` representing the planar surface where the shape is contained.
    center: Point
        A :class:`Point` representing the center of the pill.
    width : Union[Quantity, Distance]
        The width of the pill main body.
    height : Union[Quantity, Distance]
        The height of the pill.
    """

    def __init__(
        self,
        plane: Plane,
        center: Point,
        width: Union[Quantity, Distance],
        height: Union[Quantity, Distance],
    ):
        """Initializes the pill shape."""
        super().__init__(plane, is_closed=True)

        check_type(center, Point)
        self._center = center
        if not self.plane.is_point_contained(center):
            raise ValueError("Center must be contained in the plane.")

        check_type(width, (Quantity, Distance))
        check_type(height, (Quantity, Distance))

        self._width = width if isinstance(width, Distance) else Distance(width)
        if self._width.value <= 0:
            raise ValueError("Width must be a real positive value.")

        self._height = height if isinstance(height, Distance) else Distance(height)
        if self._height.value <= 0:
            raise ValueError("Height must be a real positive value.")

        pill_body_corner_1 = Point(center.x - self._width / 2, center.y + self._height / 2)
        pill_body_corner_2 = Point(center.x + self._width / 2, center.y + self._height / 2)
        pill_body_corner_3 = Point(center.x + self._width / 2, center.y - self._height / 2)
        pill_body_corner_4 = Point(center.x - self._width / 2, center.y - self._height / 2)

        segment1 = Segment(pill_body_corner_1, pill_body_corner_2)
        arc1 = Arc(
            plane,
            Point(center.x + self._width / 2, center.y),
            pill_body_corner_3,
            pill_body_corner_2,
            plane.direction_z,
        )
        segment2 = Segment(pill_body_corner_3, pill_body_corner_4)
        arc2 = Arc(
            plane,
            Point(center.x - self._width / 2, center.y),
            pill_body_corner_1,
            pill_body_corner_4,
            plane.direction_z,
        )

    @property
    def center(self) -> Point:
        """The center of the pill.

        Returns
        -------
        Point
            The center of the pill.
        """
        return self._center

    @property
    def width(self) -> Quantity:
        """The width of the pill.

        Returns
        -------
        Quantity
            The width of the pill.
        """
        return self._width.value

    @property
    def height(self) -> Quantity:
        """The height of the pill.

        Returns
        -------
        Quantity
            The height of the pill.
        """
        return self._height.value

    @property
    def perimeter(self) -> Quantity:
        """Return the perimeter of the pill.

        Returns
        -------
        Quantity
            The perimeter of the pill.
        """
        return 2 * np.pi * (self._height / 2) + 2 * self._width

    @property
    def area(self) -> Quantity:
        """Return the area of the pill.

        Returns
        -------
        Quantity
            The area of the pill.
        """
        return np.pi * (self._height / 2) ** 2 + self._width * self._height

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
        return []
