"""``Plane`` class module."""

from ansys.geometry.core.primitives.point import Point3D
from ansys.geometry.core.primitives.vector import UnitVector3D


class Plane:
    """
    Provides primitive representation of a 2D plane in 3D space.

    Parameters
    ----------
    origin : Point3D
        Centered origin of the ``Plane``.
    direction_x: UnitVector3D
        X-plane direction.
    direction_y: UnitVector3D
        Y-plane direction.
    """

    def __init__(self, origin: Point3D, direction_x: UnitVector3D, direction_y: UnitVector3D):
        """Constructor method for ``Plane``."""

        if not isinstance(direction_x, UnitVector3D):
            raise TypeError(f"direction_x is invalid, type {UnitVector3D} expected.")

        if not isinstance(direction_y, UnitVector3D):
            raise TypeError(f"direction_y is invalid, type {UnitVector3D} expected.")

        self._origin = origin
        self._direction_x = direction_x
        self._direction_y = direction_y

    @property
    def origin(self):
        """Return the origin of the ``Plane``."""
        return self._origin

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Plane``."""
        if not isinstance(other, Plane):
            raise ValueError(f"Comparison of {self} against {other} is not possible.")

        return (
            self.origin == other.origin
            and self._direction_x == other._direction_x
            and self._direction_y == other._direction_y
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Plane``."""
        return not self == other
