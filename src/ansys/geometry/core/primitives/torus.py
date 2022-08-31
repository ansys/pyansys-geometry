"""``Torus`` class module."""

from ansys.geometry.core.primitives.point import Point3D
from ansys.geometry.core.primitives.vector import Vector3D


class Torus:
    """
    Provides 3D ``Torus`` representation.

    Parameters
    ----------
    origin : Point3D
        Centered origin of the ``Torus``.
    direction_x: Vector3D
        X-plane direction.
    direction_y: Vector3D
        Y-plane direction.
    major_radius: float
        Major radius of ``Torus``.
    minor_radius: float
        Minor radius of ``Torus``.
    """

    def __init__(
        self,
        origin: Point3D,
        direction_x: Vector3D,
        direction_y: Vector3D,
        major_radius: float,
        minor_radius: float,
    ):
        """Constructor method for ``Torus``."""
        self._origin = origin
        self._direction_x = direction_x
        self._direction_y = direction_y
        self._major_radius = major_radius
        self._minor_radius = minor_radius

    @property
    def origin(self):
        """Return the origin of the ``Torus``."""
        return self._origin

    @property
    def major_radius(self):
        """Return the major radius of the ``Torus``."""
        return self._major_radius

    @property
    def minor_radius(self):
        """Return the minor radius of the ``Torus``."""
        return self._minor_radius

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Torus``."""
        if not isinstance(other, Torus):
            raise ValueError(f"Comparison of {self} against {other} is not possible.")

        return (
            self.origin.__eq__(other.origin)
            and self.major_radius.__eq__(other.major_radius)
            and self.minor_radius.__eq__(other.minor_radius)
            and self._direction_x.__eq__(other._direction_x)
            and self._direction_y.__eq__(other._direction_y)
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Torus``."""
        return not self.__eq__(other)
