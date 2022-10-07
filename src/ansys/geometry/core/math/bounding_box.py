"""``BoundingBox`` class module."""

import sys
from typing import List, overload

from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.misc import check_type


class BoundingBox2D:
    """
    Maintains x and y dimensions.

    Parameters
    ----------
    x_min : float
        Minimum value for the x-dimensional bounds.
    x_max : float
        Maximum value for the x-dimensional bounds.
    y_min : float
        Minimum value for the y-dimensional bounds.
    y_max : float
        Maximum value for the y-dimensional bounds.
    """

    def __init__(
        self,
        x_min: float = sys.float_info.max,
        x_max: float = sys.float_info.min,
        y_min: float = sys.float_info.max,
        y_max: float = sys.float_info.min,
    ):
        """Constructor method for ``BoundingBox2D``."""

        check_type(x_min, float)
        check_type(x_max, float)
        check_type(y_min, float)
        check_type(y_max, float)

        self._x_min = x_min
        self._x_max = x_max
        self._y_min = y_min
        self._y_max = y_max

    @property
    def x_min(self) -> float:
        """Minimum value of x bounds.

        Returns
        -------
        float
            Minimum value of x dimension.
        """
        return self._x_min

    @property
    def x_max(self) -> float:
        """Maximum value of x bounds.

        Returns
        -------
        float
            Maximum value of x dimension.
        """
        return self._x_max

    @property
    def y_min(self) -> float:
        """Minimum value of y bounds.

        Returns
        -------
        float
            Minimum value of y dimension.
        """
        return self._y_min

    @property
    def y_max(self) -> float:
        """Maximum value of y bounds.

        Returns
        -------
        float
            Maximum value of y dimension.
        """
        return self._y_max

    @overload
    def add_point(self, x: float, y: float) -> None:
        self._x_min = x if x < self._x_min else self._x_min
        self._x_max = x if x > self._x_max else self._x_max
        self._y_min = y if y < self._y_min else self._y_min
        self._y_max = y if y > self._y_max else self._y_max

    @overload
    def add_point(self, point: Point2D) -> None:
        self.add_point(point.x, point.y)

    @overload
    def add_points(self, points: List[Point2D]) -> None:
        for point in points:
            self.add_point(point)

    @overload
    def contains_point(self, point: Point2D) -> bool:
        return self.contains_point(point.X, point.Y, point.Z)

    @overload
    def contains_point(self, x: float, y: float) -> bool:
        return (
            not (x < self._x_min)
            and not (y < self._y_min)
            and not (x > self._x_max)
            and not (y > self._y_max)
        )

    def __eq__(self, other: "BoundingBox2D") -> bool:
        """Equals operator for ``BoundingBox2D``."""
        check_type_equivalence(other, self)

        return (
            self.x_min == other.x_min
            and self.x_max == other.x_max
            and self.y_min == other.y_min
            and self.y_max == other.y_max
        )

    def __ne__(self, other: "BoundingBox2D") -> bool:
        """Not equals operator for ``BoundingBox2D``."""
        return not self == other
