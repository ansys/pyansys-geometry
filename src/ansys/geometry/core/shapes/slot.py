"""``Slot`` class module."""
from numbers import Real
from typing import List, Optional, Union

import numpy as np
from pint import Quantity

from ansys.geometry.core.math import Plane, Point
from ansys.geometry.core.misc import Distance, check_type
from ansys.geometry.core.shapes.arc import Arc
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.shapes.line import Segment


class Slot(BaseShape):
    """A class for modeling 2D slot shaped.

    Parameters
    ----------
    plane : Plane
        A :class:`Plane` representing the planar surface where the shape is contained.
    center: Point
        A :class:`Point` representing the center of the slot.
    width : Union[Quantity, Distance]
        The width of the slot main body.
    height : Union[Quantity, Distance]
        The height of the slot.
    """

    def __init__(
        self,
        plane: Plane,
        center: Point,
        width: Union[Quantity, Distance, Real],
        height: Union[Quantity, Distance, Real],
    ):
        """Initializes the slot shape."""
        super().__init__(plane, is_closed=True)

        check_type(center, Point)
        self._center = center
        if not self.plane.is_point_contained(center):
            raise ValueError("Center must be contained in the plane.")

        check_type(width, (Quantity, Distance, Real))
        check_type(height, (Quantity, Distance, Real))

        self._width = width if isinstance(width, Distance) else Distance(width, center.unit)
        if self._width.value <= 0:
            raise ValueError("Width must be a real positive value.")

        self._height = height if isinstance(height, Distance) else Distance(height, center.unit)
        if self._height.value <= 0:
            raise ValueError("Height must be a real positive value.")

        slot_body_corner_1 = Point(
            center.x - self._width / 2, center.y + self._height / 2, center.unit
        )
        slot_body_corner_2 = Point(
            center.x + self._width / 2, center.y + self._height / 2, center.unit
        )
        slot_body_corner_3 = Point(
            center.x + self._width / 2, center.y - self._height / 2, center.unit
        )
        slot_body_corner_4 = Point(
            center.x - self._width / 2, center.y - self._height / 2, center.unit
        )

        self._segment1 = Segment(slot_body_corner_1, slot_body_corner_2)
        self._arc1 = Arc(
            plane,
            Point(center.x + self._width / 2, center.y, center.unit),
            slot_body_corner_3,
            slot_body_corner_2,
            plane.direction_z,
        )
        self._segment2 = Segment(slot_body_corner_3, slot_body_corner_4)
        self._arc2 = Arc(
            plane,
            Point(center.x - self._width / 2, center.y, center.unit),
            slot_body_corner_1,
            slot_body_corner_4,
            plane.direction_z,
        )

    @property
    def center(self) -> Point:
        """The center of the slot.

        Returns
        -------
        Point
            The center of the slot.
        """
        return self._center

    @property
    def width(self) -> Quantity:
        """The width of the slot.

        Returns
        -------
        Quantity
            The width of the slot.
        """
        return self._width.value

    @property
    def height(self) -> Quantity:
        """The height of the slot.

        Returns
        -------
        Quantity
            The height of the slot.
        """
        return self._height.value

    @property
    def perimeter(self) -> Quantity:
        """Return the perimeter of the slot.

        Returns
        -------
        Quantity
            The perimeter of the slot.
        """
        return 2 * np.pi * (self._height / 2) + 2 * self._width

    @property
    def area(self) -> Quantity:
        """Return the area of the slot.

        Returns
        -------
        Quantity
            The area of the slot.
        """
        return np.pi * (self._height / 2) ** 2 + self._width * self._height

    @property
    def components(self) -> List["BaseShape"]:
        """Returns a list containing all components required to generate the shape.

        Returns
        -------
        List[BaseShape]
            A list of component geometries forming the shape.
        """
        return [self._segment1, self._arc1, self._segment2, self._arc2]

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
        points = []
        points.extend(self._segment1.local_points(np.floor(num_points / 4)))
        points.extend(self._arc1.local_points(np.floor(num_points / 4)))
        points.extend(self._segment2.local_points(np.floor(num_points / 4)))
        points.extend(self._arc2.local_points(np.floor(num_points / 4)))
        return points
