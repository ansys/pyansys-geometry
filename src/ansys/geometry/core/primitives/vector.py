"""``Vector`` class module"""
import numpy as np


class Vector3D(np.ndarray):
    """A three-dimensional vector with Cartesian coordinates.

    Parameters
    ----------
    input : np.ndarray or list
        One dimensional numpy.ndarray with shape(3,)
    """

    def __new__(cls, input):
        """Constructor for ``Vector3D``"""

        Vector3D = np.asarray(input).view(cls)

        if len(Vector3D) != 3:
            raise ValueError("Vector3D must have three coordinates.")

        if not np.issubdtype(Vector3D.dtype, np.number) or not all(
            isinstance(data, (int, float)) for data in Vector3D.data
        ):
            raise ValueError("The parameters of 'inputs' should be integer or float.")

        return Vector3D

    @property
    def x(self) -> float:
        """X coordinate of ``Vector3D``"""
        return self[0]

    @x.setter
    def x(self, value) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError("The parameter 'x' should be a float or an integer value.")
        self[0] = value

    @property
    def y(self) -> float:
        """Y coordinate of ``Vector3D``"""
        return self[1]

    @y.setter
    def y(self, value) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError("The parameter 'y' should be a float or an integer value.")
        self[1] = value

    @property
    def z(self) -> float:
        """Z coordinate of ``Vector3D``"""
        return self[2]

    @z.setter
    def z(self, value) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError("The parameter 'z' should be a float or an integer value.")
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
        if not isinstance(other, Vector3D):
            raise ValueError(f"Comparison of {self} against {other} is not possible.")

        return np.array_equal(self, other)

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Vector3D``."""
        return not self.__eq__(other)


class Vector2D(np.ndarray):
    """A two-dimensional vector with Cartesian coordinates.

    Parameters
    ----------
    input : np.ndarray
        One dimensional numpy.ndarray with shape(2,)
    """

    def __new__(cls, input):

        vector = np.asarray(input).view(cls)

        if len(vector) != 2:
            raise ValueError("Vector2D must have two coordinates.")

        if not np.issubdtype(vector.dtype, np.number) or not all(
            isinstance(data, (int, float)) for data in vector.data
        ):
            raise ValueError("The parameters of 'input' should be integer or float.")

        return vector

    @property
    def x(self) -> float:
        """X coordinate of ``Vector2D``"""
        return self[0]

    @x.setter
    def x(self, value) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError("The parameter 'x' should be a float or an integer value.")
        self[0] = value

    @property
    def y(self) -> float:
        """Y coordinate of ``Vector2D``"""
        return self[1]

    @y.setter
    def y(self, value) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError("The parameter 'y' should be a float or an integer value.")
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

    def __eq__(self, other: object) -> bool:
        """Equals operator for ``Vector2D``."""
        if not isinstance(other, Vector2D):
            raise ValueError(f"Comparison of {self} against {other} is not possible.")

        return np.array_equal(self, other)

    def __ne__(self, other) -> bool:
        """Not equals operator for ``Vector2D``."""
        return not self.__eq__(other)


class UnitVector3D(Vector3D):
    """A three-dimensional ``UnitVector`` class.

    Parameters
    ----------
    input : np.ndarray, ``Vector3D``
        * One dimensional numpy.ndarray with shape(3,)
        * Vector3D
    """

    def __new__(cls, input):
        obj = Vector3D(input)
        return obj.normalize()


class UnitVector2D(Vector2D):
    """A two-dimensional ``UnitVector`` with Cartesian coordinates.

    Parameters
    ----------
    input : np.ndarray, Vector2D
        * One dimensional numpy.ndarray with shape(2,)
        * Vector2D
    """

    def __new__(cls, input):
        obj = Vector2D(input)
        return obj.normalize()
