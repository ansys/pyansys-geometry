import numpy as np


class VectorUV(np.ndarray):
    """A two-dimensional vector with Cartesian coordinates."""

    def __new__(cls, array_input):

        vector = np.asarray(array_input).view(cls)

        if len(vector) != 2:
            raise ValueError("VectorUV must have two coordinates.")

        if not np.issubdtype(vector.dtype, np.number) or not all(
            isinstance(data, (int, float)) for data in vector.data
        ):
            raise ValueError("The parameters of 'array_input' should be integer or float.")

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
    def norm(self):
        norm = np.linalg.norm(self)
        if norm == 0:
            norm = np.finfo(self.dtype).eps
        return norm

    def normalize(self):
        return self / self.norm
