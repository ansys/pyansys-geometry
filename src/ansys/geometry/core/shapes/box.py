"""``Box`` class module."""
import math
from typing import List, Optional, Union

from pint import Quantity

from ansys.geometry.core.math import Plane, Point
from ansys.geometry.core.misc import Distance, check_type
from ansys.geometry.core.shapes.base import BaseShape
from ansys.geometry.core.shapes.line import Segment


class Box(BaseShape):
    """A class for modeling quadrilaterals.

    Parameters
    ----------
    plane : Plane
        A :class:`Plane` representing the planar surface where the shape is contained.
    center: Point
        A :class:`Point` representing the center of the box.
    width : Union[Quantity, Distance]
        The width of the box.
    height : Union[Quantity, Distance]
        The height of the box.
    """

    def __init__(
        self,
        plane: Plane,
        center: Point,
        width: Union[Quantity, Distance],
        height: Union[Quantity, Distance],
    ):
        """Initializes the box shape."""
        super().__init__(plane, is_closed=True)

        check_type(center, Point)
        self._center = center
        if not self.plane.is_point_contained(center):
            raise ValueError("Center must be contained in the plane.")

        check_type(width, (Quantity, Distance))
        check_type(height, (Quantity, Distance))

        self._width = width if isinstance(width, Distance) else Distance(width, center.unit)
        if self._width.value <= 0:
            raise ValueError("Width must be a real positive value.")
        width_magnitude = self._width.value.m_as(center.unit)

        self._height = height if isinstance(height, Distance) else Distance(height, center.unit)
        if self._height.value <= 0:
            raise ValueError("Height must be a real positive value.")
        height_magnitude = self._height.value.m_as(center.unit)

        corner_1 = Point(
            [center.x.m - width_magnitude / 2, center.y.m + height_magnitude / 2, center.z.m],
            center.unit,
        )
        corner_2 = Point(
            [center.x.m + width_magnitude / 2, center.y.m + height_magnitude / 2, center.z.m],
            center.unit,
        )
        corner_3 = Point(
            [center.x.m + width_magnitude / 2, center.y.m - height_magnitude / 2, center.z.m],
            center.unit,
        )
        corner_4 = Point(
            [center.x.m - width_magnitude / 2, center.y.m - height_magnitude / 2, center.z.m],
            center.unit,
        )

        self._width_segment1 = Segment(plane, corner_1, corner_2)
        self._height_segment1 = Segment(plane, corner_2, corner_3)
        self._width_segment2 = Segment(plane, corner_3, corner_4)
        self._height_segment2 = Segment(plane, corner_4, corner_1)

    @property
    def center(self) -> Point:
        """The center of the box.

        Returns
        -------
        Point
            The center of the box.
        """
        return self._center

    @property
    def width(self) -> Quantity:
        """The width of the box.

        Returns
        -------
        Quantity
            The width of the box.
        """
        return self._width.value

    @property
    def height(self) -> Quantity:
        """The height of the box.

        Returns
        -------
        Quantity
            The height of the box.
        """
        return self._height.value

    @property
    def perimeter(self) -> Quantity:
        """Return the perimeter of the box.

        Returns
        -------
        Quantity
            The perimeter of the box.
        """
        return 2 * self.width + 2 * self.height

    @property
    def area(self) -> Quantity:
        """Return the area of the box.

        Returns
        -------
        Quantity
            The area of the box.
        """
        return self.width * self.height

    @property
    def components(self) -> List["BaseShape"]:
        """Returns a list containing all components required to generate the shape.

        Returns
        -------
        List[BaseShape]
            A list of component geometries forming the shape.
        """
        return [
            self._width_segment1,
            self._height_segment1,
            self._width_segment2,
            self._height_segment2,
        ]

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

        if num_points < 4:
            num_points = 4

        points_per_width_segment = math.floor(self._width.value.m / self.perimeter.m * num_points)
        points_per_height_segment = math.floor((num_points - points_per_width_segment * 2) / 2)

        # Utilize component point creation but pop to avoid endpoint duplication
        segment_1_points = self._width_segment1.local_points(points_per_width_segment + 1)
        segment_1_points.pop()
        segment_2_points = self._height_segment1.local_points(points_per_height_segment + 1)
        segment_2_points.pop()
        segment_3_points = self._width_segment2.local_points(points_per_width_segment + 1)
        segment_3_points.pop()
        segment_4_points = self._height_segment2.local_points(
            num_points - 2 * points_per_width_segment - points_per_height_segment + 1
        )
        segment_4_points.pop()
        points.extend(segment_1_points)
        points.extend(segment_2_points)
        points.extend(segment_3_points)
        points.extend(segment_4_points)
        return points
