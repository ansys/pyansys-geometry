"""``BoundingBox`` class module."""

import sys
from typing import List

from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.misc import (
    UNIT_LENGTH,
    Accuracy,
    check_is_float_int,
    check_type_equivalence,
)
from ansys.geometry.core.typing import Real


class BoundingBox2D:
    """
    Maintains x and y dimensions.

    Parameters
    ----------
    x_min : Real
        Minimum value for the x-dimensional bounds.
    x_max : Real
        Maximum value for the x-dimensional bounds.
    y_min : Real
        Minimum value for the y-dimensional bounds.
    y_max : Real
        Maximum value for the y-dimensional bounds.
    """

    def __init__(
        self,
        x_min: Real = sys.float_info.max,
        x_max: Real = sys.float_info.min,
        y_min: Real = sys.float_info.max,
        y_max: Real = sys.float_info.min,
    ):
        """Constructor method for ``BoundingBox2D``."""

        check_is_float_int(x_min)
        check_is_float_int(x_max)
        check_is_float_int(y_min)
        check_is_float_int(y_max)

        self._x_min = x_min
        self._x_max = x_max
        self._y_min = y_min
        self._y_max = y_max

    @property
    def x_min(self) -> Real:
        """Minimum value of x bounds.

        Returns
        -------
        Real
            Minimum value of x dimension.
        """
        return self._x_min

    @property
    def x_max(self) -> Real:
        """Maximum value of x bounds.

        Returns
        -------
        Real
            Maximum value of x dimension.
        """
        return self._x_max

    @property
    def y_min(self) -> Real:
        """Minimum value of y bounds.

        Returns
        -------
        Real
            Minimum value of y dimension.
        """
        return self._y_min

    @property
    def y_max(self) -> Real:
        """Maximum value of y bounds.

        Returns
        -------
        Real
            Maximum value of y dimension.
        """
        return self._y_max

    def add_point(self, point: Point2D) -> None:
        """Extends the ranges of the bounding box to include the point;
        only if point is outside current bounds.

        Parameters
        ----------
        point : Point2D
            The point to be included within the bounds.
        """
        self.add_point_components(point.x.m_as(UNIT_LENGTH), point.y.m_as(UNIT_LENGTH))

    def add_point_components(self, x: Real, y: Real) -> None:
        """Extends the ranges of the bounding box to include the point component x/y values;
        only if point components are outside current bounds.

        Parameters
        ----------
        x : Real
            The point x component to be included within the bounds.
        y : Real
            The point y component to be included within the bounds.
        """
        self._x_min = x if x < self._x_min else self._x_min
        self._x_max = x if x > self._x_max else self._x_max
        self._y_min = y if y < self._y_min else self._y_min
        self._y_max = y if y > self._y_max else self._y_max

    def add_points(self, points: List[Point2D]) -> None:
        """Extends the ranges of the bounding box to include all provided points.

        Parameters
        ----------
        points : List[Point2D]
            The list of points to be included within the bounds.
        """
        for point in points:
            self.add_point(point)

    def contains_point(self, point: Point2D) -> bool:
        """Evaluates whether a provided point lies within the current x/y ranges of the bounds.

        Parameters
        ----------
        point : Point2D
            The point to be compared against the bounds.

        Returns
        -------
        bool
            ``True`` if the point is contained in the bounding box. Otherwise, ``False``.
        """
        return self.contains_point_components(point.x.m_as(UNIT_LENGTH), point.y.m_as(UNIT_LENGTH))

    def contains_point_components(self, x: Real, y: Real) -> bool:
        """Evaluates whether the point components are within the current x/y ranges of the bounds.

        Parameters
        ----------
        x : Real
            The point x component to be compared against the bounds.
        y : Real
            The point y component to be compared against the bounds.

        Returns
        -------
        bool
            ``True`` if the components are contained in the bounding box. Otherwise, ``False``.
        """
        return (
            Accuracy.length_is_greater_than_or_equal(x, self._x_min)
            and Accuracy.length_is_greater_than_or_equal(y, self._y_min)
            and Accuracy.length_is_less_than_or_equal(x, self._x_max)
            and Accuracy.length_is_less_than_or_equal(y, self._y_max)
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
