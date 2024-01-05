# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Provides matrix primitive representations."""
from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import numpy as np

from ansys.geometry.core.misc import check_ndarray_is_float_int
from ansys.geometry.core.typing import Real, RealSequence

DEFAULT_MATRIX33 = np.identity(3)
"""Default value of the 3x3 identity matrix for the ``Matrix33`` class."""

DEFAULT_MATRIX44 = np.identity(4)
"""Default value of the 4x4 identity matrix for the ``Matrix44`` class."""


class Matrix(np.ndarray):
    """
    Provides matrix primitive representation.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence]
        Matrix arguments as a :class:`np.ndarray <numpy.ndarray>` class.
    """

    def __new__(cls, input: Union[np.ndarray, RealSequence]):
        """Initialize ``Matrix`` class."""
        obj = np.asarray(input).view(cls)
        obj.setflags(write=False)

        if obj is None or obj.ndim != 2:
            raise ValueError("Matrix should only be a 2D array.")

        check_ndarray_is_float_int(obj)

        return obj

    def determinant(self) -> Real:
        """Get the determinant of the matrix."""
        if self.shape[0] != self.shape[1]:
            raise ValueError("The determinant is only defined for square matrices.")
        return np.linalg.det(self)

    def inverse(self) -> "Matrix":
        """Provide the inverse of the matrix."""
        det = self.determinant()
        if det <= 0:
            raise ValueError("The matrix cannot be inversed because its determinant is zero.")
        return np.linalg.inv(self)

    @check_input_types
    def __mul__(self, other: Union["Matrix", np.ndarray]) -> "Matrix":
        """Get the multiplication of the matrix."""
        if self.shape[1] != other.shape[0]:
            raise ValueError(
                f"The dimensions of the matrices {self.shape[1]} and {other.shape[0]} are not multipliable."  # noqa : E501
            )
        return np.matmul(self, other).view(Matrix)

    @check_input_types
    def __eq__(self, other: "Matrix") -> bool:
        """Equals operator for the ``Matrix`` class."""
        return np.array_equal(self, other)

    def __ne__(self, other: "Matrix") -> bool:
        """Not equals operator for the ``Matrix`` class."""
        return not self == other


class Matrix33(Matrix):
    """
    Provides 3x3 matrix primitive representation.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence, Matrix], default: DEFAULT_MATRIX33
        Matrix arguments as a :class:`np.ndarray <numpy.ndarray>` class.
    """

    def __new__(cls, input: Optional[Union[np.ndarray, RealSequence, Matrix]] = DEFAULT_MATRIX33):
        """Initialize the ``Matrix33`` class."""
        obj = Matrix(input).view(cls)
        if input is DEFAULT_MATRIX33:
            return obj

        if obj.shape != (3, 3):
            raise ValueError("Matrix33 should only be a 2D array of shape (3,3).")

        return obj


class Matrix44(Matrix):
    """
    Provides 4x4 matrix primitive representation.

    Parameters
    ----------
    input : Union[~numpy.ndarray, RealSequence, Matrix], default: DEFAULT_MATRIX44
        Matrix arguments as a :class:`np.ndarray <numpy.ndarray>` class.
    """

    def __new__(cls, input: Optional[Union[np.ndarray, RealSequence, Matrix]] = DEFAULT_MATRIX44):
        """Initialize the ``Matrix44`` class."""
        obj = Matrix(input).view(cls)
        if input is DEFAULT_MATRIX44:
            return obj

        if obj.shape != (4, 4):
            raise ValueError("Matrix44 should only be a 2D array of shape (4,4).")

        return obj
