"""``Circle`` class module."""

from ansys.geometry.core.primitives.point import Point3D
from ansys.geometry.core.primitives.vector import Vector3D


class Circle:
    """
    Provides 3D ``Circle`` representation.

    Parameters
    ----------
    origin : Point3D
        Centered origin of the ``Circle``.
    direction_x: Vector3D
        X-plane direction.
    direction_y: Vector3D
        Y-plane direction.
    radius: float
        Radius of ``Circle``.
    """

    def __init__(
        self, origin: Point3D, direction_x: Vector3D, direction_y: Vector3D, radius: float
    ):
        """Constructor method for ``Circle``."""
        self._origin = origin
        self._direction_x = direction_x
        self._direction_y = direction_y
        self._radius = radius

    @property
    def origin(self):
        """Centered origin of the ``Circle``."""
        return self._origin

    @property
    def radius(self):
        """Radius of ``Circle``."""
        return self._radius

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Circle``."""
        if not isinstance(other, Circle):
            raise ValueError(f"Comparison of {self} against {other} is not possible.")

        return (
            self.origin.__eq__(other.origin)
            and self.radius.__eq__(other.radius)
            and self._direction_x.__eq__(other._direction_x)
            and self._direction_y.__eq__(other._direction_y)
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Circle``."""
        return not self == other
