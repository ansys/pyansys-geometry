import numpy as np


class Matrix3:
    def __new__(cls, input):
        """Constructor for ``Point3D``."""

        matrix = np.asarray(input).view(cls)

        if matrix is None or matrix.ndim != 2 and matrix.shape != (3, 3):
            raise ValueError("Matrix3 shouldonly be a 2D array of shape (3,3).")

        if not np.issubdtype(matrix.dtype, np.number) or not isinstance(input, (np.ndarray)):
            raise ValueError("The input parameters should be integer or float.")

        return matrix

    def __copy__(self):
        m_copy = self.matrix
        return m_copy

    @property
    def matrix(self):
        return self.matrix

    @matrix.setter
    def matrix(self, matrix):
        self = matrix


# a b c d
# e f g h
# i j k l
# m n o p


class Matrix4:
    def __new__(cls, input):
        """Constructor for ``Point3D``."""

        matrix = np.asarray(input).view(cls)

        if matrix is None or matrix.ndim != 2 and matrix.shape != (3, 3):
            raise ValueError("Matrix3 shouldonly be a 2D array of shape (3,3).")

        if not np.issubdtype(matrix.dtype, np.number) or not isinstance(input, (np.ndarray)):
            raise ValueError("The input parameters should be integer or float.")

        return matrix

    def __copy__(self):
        m_copy = self.matrix
        return m_copy

    @property
    def matrix(self):
        return self.matrix

    @matrix.setter
    def matrix(self, matrix):
        self = matrix
