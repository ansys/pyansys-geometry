"""``Vector`` class module"""
import numpy as np

from ansys.geometry.core.misc import (
    check__eq__operation,
    check_is_float_int,
    check_ndarray_is_float_int,
)


class Vector3D(np.ndarray):
    """A three-dimensional vector with Cartesian coordinates.

    Parameters
    ----------
    input : numpy.ndarray or list
        One dimensional :class:`numpy.ndarray` with shape(3,)
    """

    def __new__(cls, input):
        """Constructor for ``Vector3D``"""

        obj = np.asarray(input).view(cls)

        # Check that the size is as expected
        if len(obj) != 3:
            raise ValueError("Vector3D must have three coordinates.")

        # Check the input data
        check_ndarray_is_float_int(obj, "input")

        return obj

    @property
    def x(self) -> float:
        """X coordinate of ``Vector3D``"""
        return self[0]

    @x.setter
    def x(self, value) -> None:
        check_is_float_int(value, "x")
        self[0] = value

    @property
    def y(self) -> float:
        """Y coordinate of ``Vector3D``"""
        return self[1]

    @y.setter
    def y(self, value) -> None:
        check_is_float_int(value, "y")
        self[1] = value

    @property
    def z(self) -> float:
        """Z coordinate of ``Vector3D``"""
        return self[2]

    @z.setter
    def z(self, value) -> None:
        check_is_float_int(value, "z")
        self[2] = value

    @property
    def norm(self):
        return np.linalg.norm(self)

    def normalize(self):
        """Return a normalized version of the ``Vector3D``"""
        norm = self.norm
        if norm > 0:
            return self / norm
        else:
            raise ValueError("The norm of the Vector3D is not valid.")

    def cross(self, v: "Vector3D") -> "Vector3D":
        """Return cross product of Vector3D"""
        return Vector3D(np.cross(self, v))

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Vector3D``."""
        check__eq__operation(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Vector3D``."""
        return not self == other


class Vector2D(np.ndarray):
    """A two-dimensional vector with Cartesian coordinates.

    Parameters
    ----------
    input : numpy.ndarray
        One dimensional :class:`numpy.ndarray` with shape(2,)
    """

    def __new__(cls, input):

        obj = np.asarray(input).view(cls)

        # Check that the size is as expected
        if len(obj) != 2:
            raise ValueError("Vector2D must have two coordinates.")

        # Check the input data
        check_ndarray_is_float_int(obj, "input")

        return obj

    @property
    def x(self) -> float:
        """X coordinate of ``Vector2D``"""
        return self[0]

    @x.setter
    def x(self, value) -> None:
        check_is_float_int(value, "x")
        self[0] = value

    @property
    def y(self) -> float:
        """Y coordinate of ``Vector2D``"""
        return self[1]

    @y.setter
    def y(self, value) -> None:
        check_is_float_int(value, "y")
        self[1] = value

    @property
    def norm(self):
        return np.linalg.norm(self)

    def normalize(self):
        """Return a normalized version of the ``Vector2D``"""
        norm = self.norm
        if norm > 0:
            return self / norm
        else:
            raise ValueError("The norm of the Vector2D is not valid.")

    def __eq__(self, other: "Vector2D") -> bool:
        """Equals operator for ``Vector2D``."""
        check__eq__operation(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Vector2D") -> bool:
        """Not equals operator for ``Vector2D``."""
        return not self == other


class UnitVector3D(Vector3D):
    """A three-dimensional ``UnitVector`` class.

    Parameters
    ----------
    input : numpy.ndarray, ``Vector3D``
        * One dimensional :class:`numpy.ndarray` with shape(3,)
        * Vector3D
    """

    def __new__(cls, input):
        obj = Vector3D(input)
        return obj.normalize()


class UnitVector2D(Vector2D):
    """A two-dimensional ``UnitVector`` with Cartesian coordinates.

    Parameters
    ----------
    input : numpy.ndarray, Vector2D
        * One dimensional :class:`numpy.ndarray` with shape(2,)
        * Vector2D
    """

    def __new__(cls, input):
        obj = Vector2D(input)
        return obj.normalize()
