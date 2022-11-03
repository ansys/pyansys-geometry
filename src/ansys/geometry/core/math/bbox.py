"""Provides the ``BoundingBox`` class."""

import sys

from beartype import beartype as check_input_types
from beartype.typing import List

from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.misc import UNIT_LENGTH, Accuracy
from ansys.geometry.core.typing import Real


class BoundingBox2D:
    """
    Maintains the X and Y dimensions.

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

    @check_input_types
    def __init__(
        self,
        x_min: Real = sys.float_info.max,
        x_max: Real = sys.float_info.min,
        y_min: Real = sys.float_info.max,
        y_max: Real = sys.float_info.min,
    ):
        """Constructor method for ``BoundingBox2D``."""
        self._x_min = x_min
        self._x_max = x_max
        self._y_min = y_min
        self._y_max = y_max

    @property
    def x_min(self) -> Real:
        """Minimum value of X-dimensional bounds.

        Returns
        -------
        Real
            Minimum value of the X-dimensional bounds.
        """
        return self._x_min

    @property
    def x_max(self) -> Real:
        """Maximum value of the X-dimensional bounds.

        Returns
        -------
        Real
            Maximum value of the X-dimensional bounds.
        """
        return self._x_max

    @property
    def y_min(self) -> Real:
        """Minimum value of Y-dimensional bounds.

        Returns
        -------
        Real
            Minimum value of Y-dimensional bounds.
        """
        return self._y_min

    @property
    def y_max(self) -> Real:
        """Maximum value of Y-dimensional bounds.

        Returns
        -------
        Real
            Maximum value of Y-dimensional bounds.
        """
        return self._y_max

    @check_input_types
    def add_point(self, point: Point2D) -> None:
        """Extend the ranges of the bounding box to include a point only if the point
        is outside the current bounds.

        Parameters
        ----------
        point : Point2D
            Point to include within the bounds.
        """
        self.add_point_components(point.x.m_as(UNIT_LENGTH), point.y.m_as(UNIT_LENGTH))

    @check_input_types
    def add_point_components(self, x: Real, y: Real) -> None:
        """Extend the ranges of the bounding box to include the point component X and Y values
        only if the point components are outside the current bounds.

        Parameters
        ----------
        x : Real
            Point X component to include within the bounds.
        y : Real
            Point Y component to include within the bounds.
        """
        self._x_min = x if x < self._x_min else self._x_min
        self._x_max = x if x > self._x_max else self._x_max
        self._y_min = y if y < self._y_min else self._y_min
        self._y_max = y if y > self._y_max else self._y_max

    @check_input_types
    def add_points(self, points: List[Point2D]) -> None:
        """Extend the ranges of the bounding box to include given points.

        Parameters
        ----------
        points : List[Point2D]
            List of points to include within the bounds.
        """
        for point in points:
            self.add_point(point)

    @check_input_types
    def contains_point(self, point: Point2D) -> bool:
        """Evaluate whether a provided point lies within the current X and Y ranges of the bounds.

        Parameters
        ----------
        point : Point2D
            Point to compare against the bounds.

        Returns
        -------
        bool
            ``True`` if the point is contained in the bounding box. Otherwise, ``False``.
        """
        return self.contains_point_components(point.x.m_as(UNIT_LENGTH), point.y.m_as(UNIT_LENGTH))

    @check_input_types
    def contains_point_components(self, x: Real, y: Real) -> bool:
        """Check if point components are within current X and Y ranges of the bounds.

        Parameters
        ----------
        x : Real
            Point X component to compare against the bounds.
        y : Real
            Point Y component to compare against the bounds.

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

    @check_input_types
    def __eq__(self, other: "BoundingBox2D") -> bool:
        """Equals operator for the ``BoundingBox2D`` class."""
        return (
            self.x_min == other.x_min
            and self.x_max == other.x_max
            and self.y_min == other.y_min
            and self.y_max == other.y_max
        )

    def __ne__(self, other: "BoundingBox2D") -> bool:
        """Not equals operator for the ``BoundingBox2D`` class."""
        return not self == other
