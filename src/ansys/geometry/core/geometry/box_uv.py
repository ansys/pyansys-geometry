"""Provides the ``BoxUV`` class."""
from enum import Enum

from ansys.geometry.core.geometry.parameterization import Interval, ParamUV
from ansys.geometry.core.typing import Real


class LocationUV(Enum):
    """Provides the ``LocationUV`` class to indicate locations for BoxUV."""

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
    """BoxUV class."""

    def __init__(self, rangeU: Interval = None, rangeV: Interval = None) -> None:
        """Root constructor for BoxUV."""
        if rangeV is not None:
            self.interval_v = rangeV
        if rangeU is not None:
            self.interval_u = rangeU

    @classmethod
    def from_param(cls, param: ParamUV):
        """Secondary constructor for BoxUV using a ParamUV object type."""
        return cls(Interval(param.U, param.U), Interval(param.V, param.V))

    @classmethod
    def from_two_params(cls, param1: ParamUV, param2: ParamUV):
        """Secondary constructor for BoxUV using two ParamUV object types."""
        return cls(
            Interval(min(param1.U, param2.U), max(param1.U, param2.U)),
            Interval(min(param1.V, param2.V), max(param1.V, param2.V)),
        )

    @property
    def IntervalU(self) -> Interval:
        """Return the u interval."""
        return self.interval_u

    @property
    def IntervalV(self) -> Interval:
        """Return the v interval."""
        return self.interval_v

    def __eq__(self, other: object) -> bool:
        """Check whether two BoxUV instances are equal."""
        if not isinstance(other, BoxUV):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.IntervalU.__eq__(other.IntervalU) and self.IntervalV.__eq__(other.IntervalV)

    def __ne__(self, other: object) -> bool:
        """Check whether two BoxUV instances are not equal."""
        if not isinstance(other, BoxUV):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return not self.IntervalU.__eq__(other.IntervalU) or not self.IntervalV.__eq__(
            other.IntervalV
        )

    def is_empty(self):
        """Return whether this BoxUV is empty."""
        return self.IntervalU.is_empty() or self.IntervalV.is_empty()

    def proportion(self, prop_u: Real, prop_v: Real) -> ParamUV:
        """Evaluate the BoxUV at the given proportions."""
        return ParamUV(
            self.IntervalU.get_relative_val(prop_u), self.IntervalV.get_relative_val(prop_v)
        )

    def get_center(self) -> ParamUV:
        """Evaluate the BoxUV in the middle."""
        return self.proportion(0.5, 0.5)

    def is_negative(self, tolerance_u: Real, tolerance_v: Real) -> bool:
        """Check whether the BoxUV is negative."""
        if self.is_empty():
            return False
        return self.IntervalU.is_negative(tolerance_u) or self.IntervalV.is_negative(tolerance_v)

    @staticmethod
    def unite(first: "BoxUV", second: "BoxUV") -> "BoxUV":
        """Return the union of two BoxUV instances."""
        if first.is_empty():
            return second
        if second.is_empty():
            return first
        return BoxUV(
            Interval.unite(first.IntervalU, second.IntervalU),
            Interval.unite(first.IntervalV, second.IntervalV),
        )

    @staticmethod
    def Intersect(first: "BoxUV", second: "BoxUV", toleranceU: Real, toleranceV: Real) -> "BoxUV":
        """Return the intersection of two BoxUV instances."""
        if first.is_empty() or second.is_empty():
            return None  # supposed to be empty
        intersection = BoxUV(
            Interval.intersect(first.IntervalU, second.IntervalU, toleranceU),
            Interval.intersect(first.IntervalV, second.IntervalV, toleranceV),
        )
        if not intersection.is_negative(toleranceU, toleranceV):
            return intersection
        return None  # supposed to be empty

    def contains(self, param: ParamUV) -> bool:
        """Check whether the BoxUV contains a given u and v pair parameter."""
        if self.is_empty():
            # throw Error.InvalidMethodOnEmptyObjectException(GetType())
            raise Exception("Invalid Method On Empty Object Exception" + type(self).__name__)
        return self.IntervalU.contains(param.u) and self.IntervalV.contains(param.v)

    def inflate(self, deltaU: Real, deltaV: Real) -> "BoxUV":
        """Enlarge the BoxUV u and v intervals by deltaU and deltaV respectively."""
        if self.is_empty():
            # throw Error.InvalidMethodOnEmptyObjectException(GetType())
            raise Exception("Invalid Method On Empty Object Exception" + type(self).__name__)
        return BoxUV(self.InteravlU.inflate(deltaU), self.InteravlV.inflate(deltaV))

    def inflate(self, delta: Real) -> "BoxUV":
        """Enlarge the BoxUV by a given delta."""
        if self.is_empty():
            # throw Error.InvalidMethodOnEmptyObjectException(GetType())
            raise Exception("Invalid Method On Empty Object Exception" + type(self).__name__)
        return BoxUV(self.InteravlU.inflate(delta), self.InteravlV.inflate(delta))

    def get_corner(self, location: LocationUV) -> ParamUV:
        """Return the corner location of the BoxUV."""
        u = 0
        v = 0
        if (
            location == LocationUV.TopLeft
            or location == LocationUV.BottomLeft
            or location == LocationUV.LeftCenter
        ):
            u = self.IntervalU.get_relative_val(0)
        elif (
            location == LocationUV.TopRight
            or location == LocationUV.BottomRight
            or location == LocationUV.RightCenter
        ):
            u = self.IntervalU.get_relative_val(1)
        else:
            u = self.IntervalU.get_relative_val(0.5)

        if (
            location == LocationUV.BottomRight
            or location == LocationUV.BottomLeft
            or location == LocationUV.BottomCenter
        ):
            v = self.IntervalU.get_relative_val(0)
        elif (
            location == LocationUV.TopRight
            or location == LocationUV.TopLeft
            or location == LocationUV.TopCenter
        ):
            v = self.IntervalU.get_relative_val(1)
        else:
            v = self.IntervalU.get_relative_val(0.5)
        return ParamUV(u, v)
