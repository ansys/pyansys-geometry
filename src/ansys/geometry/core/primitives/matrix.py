"""``Matrix`` Class Module."""
from typing import Optional, Union

import numpy as np

from ansys.geometry.core.misc.checks import check_ndarray_is_float_int, check_type_equivalence
from ansys.geometry.core.typing import Real, RealSequence

DEFAULT_MATRIX33 = np.identity(3)
"""Default value of 3x3 identity matrix for ``Matrix33``."""

DEFAULT_MATRIX44 = np.identity(4)
"""Default value of 4x4 identity matrix for ``Matrix44``."""


class Matrix(np.ndarray):
    """Provide Matrix primitive representation

    Parameters
    ----------
    input : Union[numpy.ndarray, List[Real]]
        The matrix arguments as a :class:`np.ndarray`.
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence]):
        """Constructor for ``Matrix``."""
        obj = np.asarray(input).view(cls)

        if obj is None or obj.ndim != 2:
            raise ValueError("Matrix should only be a 2D array")

        check_ndarray_is_float_int(obj)

        return obj

    def determinant(self) -> Real:
        """Provides the determinant of the matrix."""
        if self.shape[0] != self.shape[1]:
            raise ValueError("The determinant is only defined for square matrices.")
        return np.linalg.det(self)

    def inverse(self) -> "Matrix":
        """Provides the inverse of the matrix."""
        det = np.linalg.det(self)
        if det <= 0:
            raise ValueError("The matrix cannot be inversed because its determinant is zero.")
        return np.linalg.inv(self)

    def __mul__(self, other: "Matrix") -> "Matrix":
        """Provides the multiplication of the matrix."""
        return np.matmul(self, other)

    def __eq__(self, other: "Matrix") -> bool:
        """Equals operator for ``Matrix``."""
        check_type_equivalence(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Matrix") -> bool:
        """Not equals operator for ``Matrix``."""
        return not self == other


class Matrix33(Matrix):
    """Provides  3x3 matrix primitive representation.

    Parameters
    ----------
    input : Union[numpy.ndarray, List[Real]], optional
        The matrix arguments as a :class:`np.ndarray`.
        By default, ``DEFAULT_MATRIX33``.
    """

    def __new__(cls, input: Optional[Union[np.ndarray, RealSequence, Matrix]] = DEFAULT_MATRIX33):
        """Constructor for ``Matrix33``."""

        obj = Matrix(input).view(cls)
        if input is DEFAULT_MATRIX33:
            return obj

        if obj.shape != (3, 3):
            raise ValueError("Matrix33 should only be a 2D array of shape (3,3).")

        return obj


class Matrix44(Matrix):
    """Provides  4x4 matrix primitive representation.

    Parameters
    ----------
    input : numpy.ndarray, optional
        The matrix arguments as a :class:`np.ndarray`.
        By default, ``DEFAULT_MATRIX44``.
    """

    def __new__(cls, input: Optional[Union[np.ndarray, RealSequence, Matrix]] = DEFAULT_MATRIX44):
        """Constructor for ``Matrix44``."""

        obj = Matrix(input).view(cls)
        if input is DEFAULT_MATRIX44:
            return obj

        if obj.shape != (4, 4):
            raise ValueError("Matrix44 should only be a 2D array of shape (4,4).")

        return obj
