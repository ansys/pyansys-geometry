"""``Vector3D`` class module"""
import numpy as np


class Vector3D(np.ndarray):
    """Provides 3D vector class.

    Parameters
    ----------
    array_input : np.ndarray
        One dimensional numpy.ndarray with shape(3,)
    """

    def __new__(cls, array_input):
        """Constructor for Vector3D"""

        vector = np.asarray(array_input).view(cls)

        if len(vector) != 3:
            raise ValueError("Vector3D must have three coordinates.")

        if not np.issubdtype(vector.dtype, np.number) or not all(
            isinstance(data, (int, float)) for data in vector.data
        ):
            raise ValueError("The parameters of 'array_inputs' should be integer or float.")

        return vector

    @property
    def x(self) -> float:
        """X coordinate of Vector3D"""
        return self[0]

    @x.setter
    def x(self, value: float) -> None:
        self[0] = value

    @property
    def y(self) -> float:
        """Y coordinate of Vector3D"""
        return self[1]

    @y.setter
    def y(self, value: float) -> None:
        self[1] = value

    @property
    def z(self) -> float:
        """Z coordinate of Vector3D"""
        return self[2]

    @z.setter
    def z(self, value: float) -> None:
        self[2] = value

    @property
    def norm(self):
        norm = np.linalg.norm(self)
        if norm == 0:
            norm = np.finfo(self.dtype).eps
        return norm

    def normalize(self):
        """Return a normalized version of the vector"""
        return self / self.norm

    def cross(self, v: "Vector3D") -> "Vector3D":
        """Return cross product of vector"""
        return Vector3D(np.cross(self, v))
