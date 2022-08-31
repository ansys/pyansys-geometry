"""``Point3D`` class module."""


class Point3D:
    """
    Provides Point3D geometry primitive representation.

    Parameters
    ----------
    x: int, float
        X plane component value.
    y: int, float
        Y plane component value.
    z: int, float
        Z plane component value.
    """

    def __init__(self, x: float, y: float, z: float):
        """Constructor method for ``Point3D``."""
        if not all(isinstance(value, (int, float)) for value in [x, y, z]):
            raise ValueError("The parameters 'x', 'y' and 'z' should be integer or float.")

        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        """Returns the X plane component value."""
        return self._x

    @x.setter
    def x(self, x):
        """Set the X plane component value."""
        if not isinstance(x, (int, float)):
            raise ValueError("The parameter 'x' should be a float or an integer value.")
        self._x = x

    @property
    def y(self):
        """Returns the Y plane component value."""
        return self._y

    @y.setter
    def y(self, y):
        """Set the Y plane component value."""
        if not isinstance(y, (int, float)):
            raise ValueError("The parameter 'y' should be a float or an integer value.")
        self._y = y

    @property
    def z(self):
        """Returns the Z plane component value."""
        return self._z

    @z.setter
    def z(self, z):
        """Set the Z plane component value."""
        if not isinstance(z, (int, float)):
            raise ValueError("The parameter 'z' should be a float or an integer value.")
        self._z = z

    def __eq__(self, __o: object) -> bool:
        """Equals operator for ``Point3D``."""
        if not isinstance(__o, Point3D):
            raise ValueError(f"Comparison of {self} against {__o} is not possible.")
        tolerance = 1e-5

        if (
            (abs(self.x - __o.x) < tolerance)
            and (abs(self.y - __o.y) < tolerance)
            and (abs(self.z - __o.z) < tolerance)
        ):
            return True
        else:
            return False
