"""``Box`` class module."""
from typing import List, Optional, Union

from pint import Quantity

from ansys.geometry.core.math import Plane, Point
from ansys.geometry.core.misc import Distance, check_type
from ansys.geometry.core.shapes.base import BaseShape


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

        self._width = width if isinstance(width, Distance) else Distance(width)
        if self._width.value <= 0:
            raise ValueError("Width must be a real positive value.")

        self._height = height if isinstance(height, Distance) else Distance(height)
        if self._height.value <= 0:
            raise ValueError("Height must be a real positive value.")

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
        return 2 * self._width + 2 * self._height

    @property
    def area(self) -> Quantity:
        """Return the area of the box.

        Returns
        -------
        Quantity
            The area of the box.
        """
        return self._width * self._height

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
