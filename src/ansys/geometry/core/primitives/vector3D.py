import numpy as np


class Vector3D(np.ndarray):
    """Subclassing ndarray and casting an existing ndarray as a given subclass
    View casting is the standard ndarray mechanism by which you take an ndarray of any subclass,
    and return a view of the array as another (specified) subclass
    The first is the use of the ndarray.__new__ method for the main work of object initialization,
    rather then the more usual __init__ method. The second is
    the use of the __array_finalize__ method to allow subclasses to clean up
    after the creation of views and new instances from templates."""

    def __new__(cls, *args):

        vector = np.asarray(args).view(cls)

        if len(vector) != 3:
            raise ValueError("Vector3D must have three coordinates.")

        if not all(isinstance(arg, (int, float)) for arg in args):
            raise ValueError("The parameters of 'input_array' should be integer or float.")

        return vector

    @property
    def x(self) -> float:
        return self[0]

    @x.setter
    def x(self, value: float) -> None:
        self[0] = value

    @property
    def y(self) -> float:
        return self[1]

    @y.setter
    def y(self, value: float) -> None:
        self[1] = value

    @property
    def z(self) -> float:
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
        return self / self.norm

    def cross(self, v: "Vector3D") -> "Vector3D":
        return Vector3D(np.cross(self, v))

    def dot(self, v: "Vector3D") -> float:
        return np.dot(self, v)
