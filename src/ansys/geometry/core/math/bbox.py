# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Provides for managing a bounding box."""

import sys
from typing import Union

from beartype import beartype as check_input_types

from ansys.geometry.core.math.misc import intersect_interval
from ansys.geometry.core.math.point import Point2D, Point3D
from ansys.geometry.core.misc.accuracy import Accuracy
from ansys.geometry.core.misc.checks import deprecated_method
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS
from ansys.geometry.core.typing import Real


class BoundingBox2D:
    """Maintains the X and Y dimensions.

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
    @deprecated_method(alternative="BoundingBox", version="0.10.0", remove="0.11.0")
    def __init__(
        self,
        x_min: Real = sys.float_info.max,
        x_max: Real = sys.float_info.min,
        y_min: Real = sys.float_info.max,
        y_max: Real = sys.float_info.min,
    ):
        """Initialize the ``BoundingBox2D`` class."""
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
        """Extend the ranges of the bounding box to include a point.

        Parameters
        ----------
        point : Point2D
            Point to include within the bounds.

        Notes
        -----
        This method is only applicable if the point components are outside
        the current bounds.
        """
        self.add_point_components(
            point.x.m_as(DEFAULT_UNITS.LENGTH), point.y.m_as(DEFAULT_UNITS.LENGTH)
        )

    @check_input_types
    def add_point_components(self, x: Real, y: Real) -> None:
        """Extend the ranges of the bounding box to include the X and Y values.

        Parameters
        ----------
        x : Real
            Point X component to include within the bounds.
        y : Real
            Point Y component to include within the bounds.

        Notes
        -----
        This method is only applicable if the point components are outside
        the current bounds.
        """
        self._x_min = x if x < self._x_min else self._x_min
        self._x_max = x if x > self._x_max else self._x_max
        self._y_min = y if y < self._y_min else self._y_min
        self._y_max = y if y > self._y_max else self._y_max

    @check_input_types
    def add_points(self, points: list[Point2D]) -> None:
        """Extend the ranges of the bounding box to include given points.

        Parameters
        ----------
        points : list[Point2D]
            List of points to include within the bounds.
        """
        for point in points:
            self.add_point(point)

    @check_input_types
    def contains_point(self, point: Point2D) -> bool:
        """Evaluate whether a point lies within the X and Y range bounds.

        Parameters
        ----------
        point : Point2D
            Point to compare against the bounds.

        Returns
        -------
        bool
            ``True`` if the point is contained in the bounding box. Otherwise, ``False``.
        """
        return self.contains_point_components(
            point.x.m_as(DEFAULT_UNITS.LENGTH), point.y.m_as(DEFAULT_UNITS.LENGTH)
        )

    @check_input_types
    def contains_point_components(self, x: Real, y: Real) -> bool:
        """Check if point components are within the X and Y range bounds.

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

    @check_input_types
    def __ne__(self, other: "BoundingBox2D") -> bool:
        """Not equals operator for the ``BoundingBox2D`` class."""
        return not self == other

    @staticmethod
    def intersect_bboxes(
        box_1: "BoundingBox2D", box_2: "BoundingBox2D"
    ) -> Union[None, "BoundingBox2D"]:
        """Find the intersection of 2 BoundingBox2D objects.

        Parameters
        ----------
        box_1: BoundingBox2D
            The box to consider the intersection of with respect to box_2.
        box_2: BoundingBox2D
            The box to consider the intersection of with respect to box_1.

        Returns
        -------
        BoundingBox2D:
            The box representing the intersection of the two passed in boxes.
        """
        intersect, min_x, max_x = intersect_interval(
            box_1.x_min, box_2.x_min, box_1.x_max, box_2.x_max
        )
        if not intersect:
            return None

        intersect, min_y, max_y = intersect_interval(
            box_1.y_min, box_2.y_min, box_1.y_max, box_2.y_max
        )
        if not intersect:
            return None

        return BoundingBox2D(min_x, max_x, min_y, max_y)


class BoundingBox:
    """Maintains the box structure for Bounding Boxes.

    Parameters
    ----------
    min_corner : Point3D
        Minimum corner for the box.
    max_corner : Point3D
        Maximum corner for the box.
    center : Point3D
        Center of the box.
    """

    @check_input_types
    def __init__(self, min_corner: Point3D, max_corner: Point3D, center: Point3D = None):
        """Initialize the ``BoundingBox`` class."""
        self._min_corner = min_corner
        self._max_corner = max_corner

        if center is not None:
            self._center = center
        else:
            mid_x = (max_corner.x.m - min_corner.x.m) / 2
            mid_y = (max_corner.y.m - min_corner.y.m) / 2
            mid_z = (max_corner.z.m - min_corner.z.m) / 2
            self._center = Point3D([mid_x, mid_y, mid_z])

    @property
    def min_corner(self) -> Point3D:
        """Minimum corner of the bounding box."""
        return self._min_corner

    @property
    def max_corner(self) -> Point3D:
        """Maximum corner of the bounding box."""
        return self._max_corner

    @property
    def center(self) -> Point3D:
        """Center of the bounding box."""
        return self._center

    @check_input_types
    def contains_point(self, point: Point3D) -> bool:
        """Evaluate whether a point lies within the box.

        Parameters
        ----------
        point : Point3D
            Point to compare against the bounds.

        Returns
        -------
        bool
            ``True`` if the point is contained in the bounding box. Otherwise, ``False``.
        """
        return self.contains_point_components(
            point.x.m_as(DEFAULT_UNITS.LENGTH),
            point.y.m_as(DEFAULT_UNITS.LENGTH),
            point.z.m_as(DEFAULT_UNITS.LENGTH),
        )

    @check_input_types
    def contains_point_components(self, x: Real, y: Real, z: Real) -> bool:
        """Check if point components are within box.

        Parameters
        ----------
        x : Real
            Point X component to compare against the bounds.
        y : Real
            Point Y component to compare against the bounds.
        z : Real
            Point Z component to compare against the bounds.

        Returns
        -------
        bool
            ``True`` if the components are contained in the bounding box. Otherwise, ``False``.
        """
        return (
            Accuracy.length_is_greater_than_or_equal(x, self._min_corner.x.m)
            and Accuracy.length_is_greater_than_or_equal(y, self._min_corner.y.m)
            and Accuracy.length_is_greater_than_or_equal(z, self._min_corner.z.m)
            and Accuracy.length_is_less_than_or_equal(x, self._max_corner.x.m)
            and Accuracy.length_is_less_than_or_equal(y, self._max_corner.y.m)
            and Accuracy.length_is_less_than_or_equal(z, self._max_corner.z.m)
        )

    @check_input_types
    def __eq__(self, other: "BoundingBox") -> bool:
        """Equals operator for the ``BoundingBox`` class."""
        return (
            self._min_corner.x == other._min_corner.x
            and self._max_corner.x == other._max_corner.x
            and self._min_corner.y == other._min_corner.y
            and self._max_corner.y == other._max_corner.y
            and self._min_corner.z == other._min_corner.z
            and self._max_corner.z == other._max_corner.z
        )

    @check_input_types
    def __ne__(self, other: "BoundingBox") -> bool:
        """Not equals operator for the ``BoundingBox`` class."""
        return not self == other

    @staticmethod
    def intersect_bboxes(box_1: "BoundingBox", box_2: "BoundingBox") -> Union[None, "BoundingBox"]:
        """Find the intersection of 2 BoundingBox objects.

        Parameters
        ----------
        box_1: BoundingBox
            The box to consider the intersection of with respect to box_2.
        box_2: BoundingBox
            The box to consider the intersection of with respect to box_1.

        Returns
        -------
        BoundingBox:
            The box representing the intersection of the two passed in boxes.
        """
        intersect, min_x, max_x = intersect_interval(
            box_1._min_corner.x.m,
            box_2._min_corner.x.m,
            box_1._max_corner.x.m,
            box_2._max_corner.x.m,
        )
        if not intersect:
            return None

        intersect, min_y, max_y = intersect_interval(
            box_1._min_corner.y.m,
            box_2._min_corner.y.m,
            box_1._max_corner.y.m,
            box_2._max_corner.y.m,
        )
        if not intersect:
            return None

        intersect, min_z, max_z = intersect_interval(
            box_1._min_corner.z.m,
            box_2._min_corner.z.m,
            box_1._max_corner.z.m,
            box_2._max_corner.z.m,
        )
        if not intersect:
            return None

        min_point = Point3D([min_x, min_y, min_z])
        max_point = Point3D([max_x, max_y, max_z])
        return BoundingBox(min_point, max_point)
