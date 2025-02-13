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
"""Provides auxiliary math functions for PyAnsys Geometry."""

from beartype import beartype as check_input_types
import numpy as np

from ansys.geometry.core.misc.accuracy import Accuracy
from ansys.geometry.core.typing import Real


@check_input_types
def get_two_circle_intersections(
    x0: Real, y0: Real, r0: Real, x1: Real, y1: Real, r1: Real
) -> tuple[tuple[Real, Real], tuple[Real, Real]] | None:
    """Get the intersection points of two circles.

    Parameters
    ----------
    x0 : Real
        x coordinate of the first circle.
    y0 : Real
        y coordinate of the first circle.
    r0 : Real
        Radius of the first circle.
    x1 : Real
        x coordinate of the second circle.
    y1 : Real
        y coordinate of the second circle.
    r1 : Real
        Radius of the second circle.

    Returns
    -------
    tuple[tuple[Real, Real], tuple[Real, Real]] | None
        Intersection points of the two circles if they intersect.
        The points are returned as ``((x3, y3), (x4, y4))``, where ``(x3, y3)`` and ``(x4, y4)``
        are the intersection points of the two circles. If the circles do not
        intersect, then ``None`` is returned.

    Notes
    -----
    This function is based on the following StackOverflow post:
    https://stackoverflow.com/questions/55816902/finding-the-intersection-of-two-circles

    That post is based on the following implementation:
    https://paulbourke.net/geometry/circlesphere/
    """
    # circle 1: (x0, y0), radius r0
    # circle 2: (x1, y1), radius r1
    d = np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)

    # non-intersecting
    if d > r0 + r1:
        return None
    # one circle within other
    if d < abs(r0 - r1):
        return None
    # coincident circles
    if d == 0 and r0 == r1:
        return None
    else:
        a = (r0**2 - r1**2 + d**2) / (2 * d)
        h = np.sqrt(r0**2 - a**2)
        x2 = x0 + a * (x1 - x0) / d
        y2 = y0 + a * (y1 - y0) / d

        dx = h * (y1 - y0) / d
        dy = h * (x1 - x0) / d
        x3 = x2 + dx
        y3 = y2 - dy

        x4 = x2 - dx
        y4 = y2 + dy

        return ((x3, y3), (x4, y4))


def intersect_interval(first_min, second_min, first_max, second_max) -> tuple[bool, Real, Real]:
    """Find the intersection of two intervals.

    Parameters
    ----------
    first_min : Real
        The minimum value of the first interval.
    second_min : Real
        The minimum value of the second interval.
    first_max : Real
        The maximum value of the first interval.
    second_max : Real
        The maximum value of the second interval.

    Returns
    -------
    tuple[bool, Real, Real]
        Tuple with a boolean to indicate whether the intervals intersect,
        the minimum value of the intersection interval,
        and the maximum value of the intersection interval.
        If they do not intersect, then the boolean is False and the other values are 0.
    """
    minimum = second_min
    if first_min > minimum:
        minimum = first_min

    maximum = second_max
    if first_max < maximum:
        maximum = first_max

    if minimum > maximum:
        if minimum - maximum > Accuracy.length_accuracy():
            return False, 0, 0

        maximum, minimum = minimum, maximum

    return True, minimum, maximum
