"""``Sphere`` class module."""

from ansys.geometry.core.primitives.point import Point3D


class Sphere:
    """
    Provides 3D ``Sphere`` representation.

    Parameters
    ----------
    origin : Point3D
        Centered origin of the ``Sphere``.
    radius: float
        Radius of ``Sphere``.
    """

    def __init__(self, origin: Point3D, radius: float):
        """Constructor method for ``Sphere``."""
        self._origin = origin
        self._radius = radius

    @property
    def origin(self):
        """Return the origin of the ``Sphere``."""
        return self._origin

    @property
    def radius(self):
        """Return the radius of the ``Sphere``."""
        return self._radius

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Sphere``."""
        if not isinstance(other, Sphere):
            raise ValueError(f"Comparison of {self} against {other} is not possible.")

        return self.origin.__eq__(other.origin) and self.radius.__eq__(other.radius)

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Sphere``."""
        return not self.__eq__(other)
