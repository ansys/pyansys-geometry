import numpy as np


class Matrix3(np.ndarray):
    def __new__(cls, input):
        """Constructor for ``Point3D``."""

        matrix = np.asarray(input).view(cls)

        if matrix is None or matrix.ndim != 2 or matrix.shape != (3, 3):
            raise ValueError("Matrix3 should only be a 2D array of shape (3,3).")

        if not np.issubdtype(matrix.dtype, np.number) or not isinstance(matrix, (np.ndarray)):
            raise ValueError("The input parameters should be integer or float.")

        return matrix

    def inverse(self):
        det = np.linalg.det(self)
        if det == 0:
            raise ValueError("The determinent of matrix is zero, cannot be inversed")
        return np.linalg.inv(self)


class Matrix4(np.ndarray):
    def __new__(cls, input):
        """Constructor for ``Point3D``."""

        matrix = np.asarray(input).view(cls)

        if matrix is None or matrix.ndim != 2 or matrix.shape != (4, 4):
            raise ValueError("Matrix3 shouldonly be a 2D array of shape (3,3).")

        if not np.issubdtype(matrix.dtype, np.number) or not isinstance(matrix, (np.ndarray)):
            raise ValueError("The input parameters should be integer or float.")

        return matrix

    def inverse(self):
        det = np.linalg.det(self)
        if det == 0:
            raise ValueError("The determinent of matrix is zero, cannot be inversed")
        return np.linalg.inv(self)


# from ansys.geometry.core.primitives import Matrix3
# a = Matrix3([[1,2,3],[2,5,6],[2,5,10]])
