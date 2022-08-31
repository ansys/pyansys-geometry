"""``Point3D`` class module."""

import numpy as np

class Point3D(np.ndarray):
    """
    Provides Point3D geometry primitive representation.
    """

    def __new__(cls, input_array):
        obj = np.asarray(input_array).view(cls)

        if len(obj) != 3:
            raise ValueError("Point3D must have three coordinates.")

        if not all(isinstance(value, (int, float)) for value in obj):
            raise ValueError("The parameters of 'input_array' should be integer or float.")

        return obj

    def __init__(self, x: float, y: float, z: float):
        """Constructor method for ``Point3D``."""
        if not all(isinstance(value, (int, float)) for value in [x, y, z]):
            raise ValueError("The parameters 'x', 'y' and 'z' should be integer or float.")

        self = np.asarray([x, y, z])

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
