"""``Cone`` class module."""

from ansys.geometry.core.primitives.point import Point3D
from ansys.geometry.core.primitives.vector import Vector3D


class Cone:
    """
    Provides 3D ``Cone`` representation.

    Parameters
    ----------
    origin : Point3D
        Centered origin of the ``Cone``.
    direction_x: Vector3D
        X-plane direction.
    direction_y: Vector3D
        Y-plane direction.
    radius: float
        Radius of ``Cone``.
    half_angle: float
        Angle determine upward angle of ``Cone``.
    """

    def __init__(
        self,
        origin: Point3D,
        direction_x: Vector3D,
        direction_y: Vector3D,
        radius: float,
        half_angle: float,
    ):
        """Constructor method for ``Cone``."""
        self._origin = origin
        self._direction_x = direction_x
        self._direction_y = direction_y
        self._radius = radius
        self._half_angle = half_angle

    @property
    def origin(self):
        """Return the origin of the ``Cone``."""
        return self._origin

    @property
    def radius(self):
        """Return the radius of the ``Cone``."""
        return self._radius

    @property
    def half_angle(self):
        """Return the half angle of the ``Cone``."""
        return self._half_angle

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Cone``."""
        if not isinstance(other, Cone):
            raise ValueError(f"Comparison of {self} against {other} is not possible.")

        return (
            self.origin.__eq__(other.origin)
            and self.radius.__eq__(other.radius)
            and self.half_angle.__eq__(other.half_angle)
            and self._direction_x.__eq__(other._direction_x)
            and self._direction_y.__eq__(other._direction_y)
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Cone``."""
        return not self.__eq__(other)
