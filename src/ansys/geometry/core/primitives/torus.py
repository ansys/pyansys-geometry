"""``Torus`` class module."""

from ansys.geometry.core.primitives.direction import Direction2D
from ansys.geometry.core.primitives.point import Point3D


class Torus:
    """
    Provides ``Torus`` representation within a sketch environment.

    Parameters
    ----------
    origin : Point3D
        Centered origin of the ``Torus``.
    dir_x: Direction
        X-plane direction.
    dir_y: Direction
        Y-plane direction.
    majorRadius: float
        Major radius of ``Torus``.
    minorRadius: float
        Minor radius of ``Torus``.
    """

    def __init__(
        self,
        origin: Point3D,
        dir_x: Direction2D,
        dir_y: Direction2D,
        majorRadius: float,
        minorRadius: float,
    ):
        """Constructor method for ``Torus``."""
        self._origin = origin
        self._dir_x = dir_x
        self._dir_y = dir_y
        self._majorRadius = majorRadius
        self._minorRadius = minorRadius

    @property
    def origin(self):
        """Return the origin of the ``Torus``."""
        return self._origin

    @property
    def major_radius(self):
        """Return the major radius of the ``Torus``."""
        return self._majorRadius

    @property
    def minor_radius(self):
        """Return the minor radius of the ``Torus``."""
        return self._minorRadius

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Torus``."""
        if not isinstance(other, Torus):
            raise ValueError(f"Comparison of {self} against {other} is not possible.")

        return (
            self.origin.__eq__(other.origin)
            and self.major_radius.__eq__(other.major_radius)
            and self.minor_radius.__eq__(other.minor_radius)
            and self._dir_x.__eq__(other._dir_x)
            and self._dir_y.__eq__(other._dir_y)
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Torus``."""
        return not self.__eq__(other)
