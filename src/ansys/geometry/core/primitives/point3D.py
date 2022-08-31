"""``Point3D`` class module."""


class Point3D:
    """
    Provides Point3D geometry primitive representation.

    Parameters
    ----------
    x: float
        X plane component value.
    y: float
        Y plane component value.
    z: float
        Z plane component value.
    """

    def __init__(self, x: float, y: float, z: float):
        """Constructor method for ``Point3D``."""
        self._x = x
        self._y = y
        self._z = z
