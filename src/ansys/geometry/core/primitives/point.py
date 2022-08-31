"""``Point3D`` class module."""

import numpy as np


class Point3D(np.ndarray):
    """
    Provides Point3D geometry primitive representation.
    """

    def __new__(cls, *args):

        if (len(args) == 1) or (len(args) == 3):
            obj = np.asarray(args).view(cls)

        if len(obj) != 3:
            raise ValueError("Point3D must have three coordinates.")

        if not all(isinstance(value, (int, float)) for value in args):
            raise ValueError("The parameters of 'input_array' should be integer or float.")

        return obj

    @property
    def x(self):
        """Returns the X plane component value."""
        return self[0]

    @x.setter
    def x(self, x):
        """Set the X plane component value."""
        if not isinstance(x, (int, float)):
            raise ValueError("The parameter 'x' should be a float or an integer value.")
        self[0] = x

    @property
    def y(self):
        """Returns the Y plane component value."""
        return self[1]

    @y.setter
    def y(self, y):
        """Set the Y plane component value."""
        if not isinstance(y, (int, float)):
            raise ValueError("The parameter 'y' should be a float or an integer value.")
        self[1] = y

    @property
    def z(self):
        """Returns the Z plane component value."""
        return self[2]

    @z.setter
    def z(self, z):
        """Set the Z plane component value."""
        if not isinstance(z, (int, float)):
            raise ValueError("The parameter 'z' should be a float or an integer value.")
        self[2] = z

    def __eq__(self, __o: object) -> bool:
        """Equals operator for ``Point3D``."""
        if not isinstance(__o, Point3D):
            raise ValueError(f"Comparison of {self} against {__o} is not possible.")

        return np.array_equal(self, __o)

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Point3D``."""
        return not self.__eq__(other)
