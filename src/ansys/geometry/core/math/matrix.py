"""``Matrix`` class module."""
from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np

from ansys.geometry.core.misc import check_ndarray_is_float_int
from ansys.geometry.core.typing import Real, RealSequence

DEFAULT_MATRIX33 = np.identity(3)
"""Default value of 3x3 identity matrix for ``Matrix33``."""

DEFAULT_MATRIX44 = np.identity(4)
"""Default value of 4x4 identity matrix for ``Matrix44``."""


class Matrix(np.ndarray):
    """Provide Matrix primitive representation.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence]
        The matrix arguments as a :class:`np.ndarray <numpy.ndarray>` .
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence]):
        """Constructor for ``Matrix``."""
        obj = np.asarray(input).view(cls)
        obj.setflags(write=False)

        if obj is None or obj.ndim != 2:
            raise ValueError("Matrix should only be a 2D array.")

        check_ndarray_is_float_int(obj)

        return obj

    def determinant(self) -> Real:
        """Provides the determinant of the matrix."""
        if self.shape[0] != self.shape[1]:
            raise ValueError("The determinant is only defined for square matrices.")
        return np.linalg.det(self)

    def inverse(self) -> "Matrix":
        """Provides the inverse of the matrix."""
        det = self.determinant()
        if det <= 0:
            raise ValueError("The matrix cannot be inversed because its determinant is zero.")
        return np.linalg.inv(self)

    @check_input_types
    def __mul__(self, other: "Matrix") -> "Matrix":
        """Provides the multiplication of the matrix."""
        if self.shape[1] != other.shape[0]:
            raise ValueError(
                f"The matrices dimensions {self.shape[1]} and {other.shape[0]} are not multipliable."  # noqa : E501
            )
        return Matrix(np.matmul(self, other))

    @check_input_types
    def __eq__(self, other: "Matrix") -> bool:
        """Equals operator for ``Matrix``."""
        return np.array_equal(self, other)

    def __ne__(self, other: "Matrix") -> bool:
        """Not equals operator for ``Matrix``."""
        return not self == other


class Matrix33(Matrix):
    """Provides 3x3 matrix primitive representation.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence, Matrix], default: ``DEFAULT_MATRIX33``
        The matrix arguments as a :class:`np.ndarray <numpy.ndarray>` .
    """

    def __new__(cls, input: Optional[Union[np.ndarray, RealSequence, Matrix]] = DEFAULT_MATRIX33):
        """Constructor for ``Matrix33``."""

        obj = Matrix(input).view(cls)
        if input is DEFAULT_MATRIX33:
            return obj

        if obj.shape != (3, 3):
            raise ValueError("Matrix33 should only be a 2D array of shape (3,3).")

        return obj

    @check_input_types
    def __eq__(self, other: "Matrix33") -> bool:
        """Equals operator for ``Matrix33``."""
        return np.array_equal(self, other)

    def __ne__(self, other: "Matrix33") -> bool:
        """Not equals operator for ``Matrix33``."""
        return not self == other


class Matrix44(Matrix):
    """Provides 4x4 matrix primitive representation.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence, Matrix], default: ``DEFAULT_MATRIX44``
        The matrix arguments as a :class:`np.ndarray <numpy.ndarray>`.
    """

    def __new__(cls, input: Optional[Union[np.ndarray, RealSequence, Matrix]] = DEFAULT_MATRIX44):
        """Constructor for ``Matrix44``."""

        obj = Matrix(input).view(cls)
        if input is DEFAULT_MATRIX44:
            return obj

        if obj.shape != (4, 4):
            raise ValueError("Matrix44 should only be a 2D array of shape (4,4).")

        return obj

    @check_input_types
    def __eq__(self, other: "Matrix44") -> bool:
        """Equals operator for ``Matrix44``."""
        return np.array_equal(self, other)

    def __ne__(self, other: "Matrix44") -> bool:
        """Not equals operator for ``Matrix44``."""
        return not self == other
