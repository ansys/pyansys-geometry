"""``Cylinder`` class module."""

from ansys.geometry.core.primitives import Point3D, Vector3D


class Cylinder:
    """
    Provides 3D ``Cylinder`` representation.

    Parameters
    ----------
    origin : Point3D
        Centered origin of the ``Cylinder``.
    direction_x: Vector3D
        X-plane direction.
    direction_y: Vector3D
        Y-plane direction.
    radius: float
        Radius of ``Cylinder``.
    """

    def __init__(
        self, origin: Point3D, direction_x: Vector3D, direction_y: Vector3D, radius: float
    ):
        """Constructor method for ``Cylinder``."""
        self._origin = origin
        self._direction_x = direction_x
        self._direction_y = direction_y
        self._radius = radius

    @property
    def origin(self):
        """Return the origin of the ``Cylinder``."""
        return self._origin

    @property
    def radius(self):
        """Return the radius of the ``Cylinder``."""
        return self._radius

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Cylinder``."""
        if not isinstance(other, Cylinder):
            raise ValueError(f"Comparison of {self} against {other} is not possible.")

        return (
            self.origin.__eq__(other.origin)
            and self.radius.__eq__(other.radius)
            and self._direction_x.__eq__(other._direction_x)
            and self._direction_y.__eq__(other._direction_y)
        )

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Cylinder``."""
        return not self.__eq__(other)
