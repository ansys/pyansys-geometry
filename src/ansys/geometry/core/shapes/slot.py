"""``Slot`` class module."""
import math
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
    """A class for modeling 2D slot shape.

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
        width_magnitude = self._width.value.m_as(center.unit)

        self._height = height if isinstance(height, Distance) else Distance(height, center.unit)
        if self._height.value <= 0:
            raise ValueError("Height must be a real positive value.")
        height_magnitude = self._height.value.m_as(center.unit)

        slot_body_corner_1 = Point(
            [center.x.m - width_magnitude / 2, center.y.m + height_magnitude / 2, center.z.m],
            center.unit,
        )
        slot_body_corner_2 = Point(
            [center.x.m + width_magnitude / 2, center.y.m + height_magnitude / 2, center.z.m],
            center.unit,
        )
        slot_body_corner_3 = Point(
            [center.x.m + width_magnitude / 2, center.y.m - height_magnitude / 2, center.z.m],
            center.unit,
        )
        slot_body_corner_4 = Point(
            [center.x.m - width_magnitude / 2, center.y.m - height_magnitude / 2, center.z.m],
            center.unit,
        )

        self._segment1 = Segment(plane, slot_body_corner_1, slot_body_corner_2)
        self._arc1 = Arc(
            plane,
            Point([center.x.m + width_magnitude / 2, center.y.m, center.z.m], center.unit),
            slot_body_corner_3,
            slot_body_corner_2,
            plane.direction_z,
        )
        self._segment2 = Segment(plane, slot_body_corner_3, slot_body_corner_4)
        self._arc2 = Arc(
            plane,
            Point([center.x.m - width_magnitude / 2, center.y.m, center.z.m], center.unit),
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
        return 2 * np.pi * (self._height.value / 2) + 2 * self._width.value

    @property
    def area(self) -> Quantity:
        """Return the area of the slot.

        Returns
        -------
        Quantity
            The area of the slot.
        """
        return np.pi * (self._height.value / 2) ** 2 + self._width.value * self._height.value

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
            Desired number of points belonging to the shape. Minimum of 8 required.

        Returns
        -------
        List[Point]
            A list of points representing the shape.
        """
        if num_points < 10:
            num_points = 10

        points_per_segment = math.floor(self._width.value.m / self.perimeter.m * num_points)
        points_per_arc = math.floor((num_points - 2 * points_per_segment) / 2)

        # Utilize component point creation but pop to avoid endpoint duplication
        segment_1_points = self._segment1.local_points(points_per_segment + 1)
        segment_1_points.pop()
        segment_2_points = self._segment2.local_points(points_per_segment + 1)
        segment_2_points.pop()
        arc_1_points = self._arc1.local_points(points_per_arc + 1)
        arc_1_points.pop()
        arc_2_points = self._arc2.local_points(
            num_points - 2 * points_per_segment - points_per_arc + 1
        )
        arc_2_points.pop()
        points = []
        points.extend(segment_1_points)
        points.extend(segment_2_points)
        points.extend(arc_1_points)
        points.extend(arc_2_points)
        return points
