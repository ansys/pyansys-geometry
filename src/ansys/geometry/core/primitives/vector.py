"""``Vector`` class module"""
import numpy as np


class Vector3D(np.ndarray):
    """Provides Vector3D class.

    Parameters
    ----------
    input : np.ndarray or list
        * One dimensional numpy.ndarray with shape(3,)
    """

    def __new__(cls, input):
        """Constructor for Vector3D"""

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
        """X coordinate of Vector3D"""
        return self[0]

    @x.setter
    def x(self, value) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError("The parameter 'x' should be a float or an integer value.")
        self[0] = value

    @property
    def y(self) -> float:
        """Y coordinate of Vector3D"""
        return self[1]

    @y.setter
    def y(self, value) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError("The parameter 'y' should be a float or an integer value.")
        self[1] = value

    @property
    def z(self) -> float:
        """Z coordinate of Vector3D"""
        return self[2]

    @z.setter
    def z(self, value) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError("The parameter 'z' should be a float or an integer value.")
        self[2] = value

    @property
    def norm(self):
        norm = np.linalg.norm(self)
        if norm == 0:
            norm = np.finfo(self.dtype).eps
        return norm

    def normalize(self):
        """Return a normalized version of the Vector3D"""
        return self / self.norm

    def cross(self, v: "Vector3D") -> "Vector3D":
        """Return cross product of Vector3D"""
        return Vector3D(np.cross(self, v))

    def __eq__(self, other):
        """Returns True if Vector3D points are the same, else False"""
        return self == other

    def __ne__(self, other):
        """Returns True if the Vector3D points are not the same, else False"""
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
            raise ValueError("VectorUV must have two coordinates.")

        if not np.issubdtype(vector.dtype, np.number) or not all(
            isinstance(data, (int, float)) for data in vector.data
        ):
            raise ValueError("The parameters of 'input' should be integer or float.")

        return vector

    @property
    def x(self) -> float:
        """X coordinate of VectorUV"""
        return self[0]

    @x.setter
    def x(self, value) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError("The parameter 'x' should be a float or an integer value.")
        self[0] = value

    @property
    def y(self) -> float:
        """Y coordinate of VectorUV"""
        return self[1]

    @y.setter
    def y(self, value) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError("The parameter 'y' should be a float or an integer value.")
        self[1] = value

    @property
    def norm(self):
        norm = np.linalg.norm(self)
        if norm == 0:
            norm = np.finfo(self.dtype).eps
        return norm

    def normalize(self):
        """Return a normalized version of the vector"""
        return self / self.norm

    def __eq__(self, other):
        """Returns True vectors points are the same (same length and same direction), else False"""
        return self == other.point()

    def __ne__(self, other):
        """Returns True if the vectors pointing are not the same, else False"""
        return not self.__eq__(other)


class UnitVector3D(Vector3D):
    def __init__(self, input):
        self._value = Vector3D(input)

    def __call__(self):
        return self._value.normalize()


class UnitVector2D(Vector2D):
    def __init__(self, input):
        self._value = Vector2D(input)

    def __call__(self):
        return self._value.normalize()
