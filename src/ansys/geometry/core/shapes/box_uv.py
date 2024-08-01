# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
"""Provides the ``BoxUV`` class."""

from enum import Enum

from ansys.geometry.core.shapes.parameterization import Interval, ParamUV
from ansys.geometry.core.typing import Real


class LocationUV(Enum):
    """Provides the enumeration for indicating locations for BoxUV."""

    TopLeft = 1
    TopCenter = 2
    TopRight = 3
    BottomLeft = 4
    BottomCenter = 5
    BottomRight = 6
    LeftCenter = 7
    RightCenter = 8
    Center = 9


class BoxUV:
    """Provides the implementation for ``BoxUV`` class."""

    def __init__(self, range_u: Interval = None, range_v: Interval = None) -> None:
        """Root constructor for BoxUV."""
        if range_u is not None:
            self._interval_u = range_u
        if range_v is not None:
            self._interval_v = range_v

    @property
    def interval_u(self) -> Interval:
        """``u`` interval."""
        return self._interval_u

    @property
    def interval_v(self) -> Interval:
        """``v`` interval."""
        return self._interval_v

    def __eq__(self, other: object) -> bool:
        """Check whether two BoxUV instances are equal."""
        if not isinstance(other, BoxUV):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.interval_u.__eq__(other.interval_u) and self.interval_v.__eq__(other.interval_v)

    def __ne__(self, other: object) -> bool:
        """Check whether two BoxUV instances are not equal."""
        if not isinstance(other, BoxUV):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return not self.interval_u.__eq__(other.interval_u) or not self.interval_v.__eq__(
            other.interval_v
        )

    def is_empty(self):
        """Check if this BoxUV is empty."""
        return self.interval_u.is_empty() or self.interval_v.is_empty()

    def proportion(self, prop_u: Real, prop_v: Real) -> ParamUV:
        """Evaluate the BoxUV at the given proportions."""
        return ParamUV(
            self.interval_u.get_relative_val(prop_u), self.interval_v.get_relative_val(prop_v)
        )

    def get_center(self) -> ParamUV:
        """Evaluate the this BoxUV in the center."""
        return self.proportion(0.5, 0.5)

    def is_negative(self, tolerance_u: Real, tolerance_v: Real) -> bool:
        """Check whether the BoxUV is negative."""
        if self.is_empty():
            return False
        return self.interval_u.is_negative(tolerance_u) or self.interval_v.is_negative(tolerance_v)

    def contains(self, param: ParamUV) -> bool:
        """Check whether the BoxUV contains a given u and v pair parameter."""
        if self.is_empty():
            # Cannot check contains for an empty box uv.
            raise RuntimeError("Cannot check contains for an empty box uv.")
        return self.interval_u.contains(param.u) and self.interval_v.contains(param.v)

    def inflate(self, delta_u: Real, delta_v: Real) -> "BoxUV":
        """Enlarge the BoxUV u and v intervals by deltas."""
        if self.is_empty():
            # Cannot inflate an empty box uv.
            raise RuntimeError("Cannot inflate an empty box uv.")
        return BoxUV(self.interval_u.inflate(delta_u), self.interval_v.inflate(delta_v))

    def get_corner(self, location: LocationUV) -> ParamUV:
        """Get the corner location of the BoxUV."""
        u = 0
        v = 0
        if (
            location == LocationUV.TopLeft
            or location == LocationUV.BottomLeft
            or location == LocationUV.LeftCenter
        ):
            u = self.interval_u.get_relative_val(0)
        elif (
            location == LocationUV.TopRight
            or location == LocationUV.BottomRight
            or location == LocationUV.RightCenter
        ):
            u = self.interval_u.get_relative_val(1)
        else:
            u = self.interval_u.get_relative_val(0.5)

        if (
            location == LocationUV.BottomRight
            or location == LocationUV.BottomLeft
            or location == LocationUV.BottomCenter
        ):
            v = self.interval_u.get_relative_val(0)
        elif (
            location == LocationUV.TopRight
            or location == LocationUV.TopLeft
            or location == LocationUV.TopCenter
        ):
            v = self.interval_u.get_relative_val(1)
        else:
            v = self.interval_u.get_relative_val(0.5)
        return ParamUV(u, v)
