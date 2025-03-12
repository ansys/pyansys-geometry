# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from typing import TYPE_CHECKING, Union

from beartype import beartype as check_input_types
import numpy as np

from ansys.geometry.core.misc.checks import check_ndarray_is_float_int, check_type
from ansys.geometry.core.typing import Real, RealSequence

if TYPE_CHECKING:
    from ansys.geometry.core.math.frame import Frame
    from ansys.geometry.core.math.vector import Vector3D  # For type hints

DEFAULT_MATRIX33 = np.identity(3)
"""Default value of the 3x3 identity matrix for the ``Matrix33`` class."""

DEFAULT_MATRIX44 = np.identity(4)
"""Default value of the 4x4 identity matrix for the ``Matrix44`` class."""


class Matrix(np.ndarray):
    """Provides matrix representation.

    Parameters
    ----------
    input : ~numpy.ndarray | RealSequence
        Matrix arguments as a :class:`np.ndarray <numpy.ndarray>` class.
    """

    def __new__(cls, input: np.ndarray | RealSequence):
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
    """Provides 3x3 matrix representation.

    Parameters
    ----------
    input : ~numpy.ndarray | RealSequence | Matrix, default: DEFAULT_MATRIX33
        Matrix arguments as a :class:`np.ndarray <numpy.ndarray>` class.
    """

    def __new__(cls, input: np.ndarray | RealSequence | Matrix = DEFAULT_MATRIX33):
        """Initialize the ``Matrix33`` class."""
        obj = Matrix(input).view(cls)
        if input is DEFAULT_MATRIX33:
            return obj

        if obj.shape != (3, 3):
            raise ValueError("Matrix33 should only be a 2D array of shape (3,3).")

        return obj


class Matrix44(Matrix):
    """Provides 4x4 matrix representation.

    Parameters
    ----------
    input : ~numpy.ndarray | RealSequence | Matrix, default: DEFAULT_MATRIX44
        Matrix arguments as a :class:`np.ndarray <numpy.ndarray>` class.
    """

    def __new__(cls, input: np.ndarray | RealSequence | Matrix = DEFAULT_MATRIX44):
        """Initialize the ``Matrix44`` class."""
        obj = Matrix(input).view(cls)
        if input is DEFAULT_MATRIX44:
            return obj

        if obj.shape != (4, 4):
            raise ValueError("Matrix44 should only be a 2D array of shape (4,4).")

        return obj

    @classmethod
    def create_translation(cls, translation: "Vector3D") -> "Matrix44":
        """Create a matrix representing the specified translation.

        Parameters
        ----------
        translation : Vector3D
            The translation vector representing the translation. The components of the vector
            should be in meters.

        Returns
        -------
        Matrix44
            A 4x4 matrix representing the translation.

        Examples
        --------
        >>> translation_vector = Vector3D(1.0, 2.0, 3.0)
        >>> translation_matrix = Matrix44.create_translation(translation_vector)
        >>> print(translation_matrix)
        [[1. 0. 0. 1.]
         [0. 1. 0. 2.]
         [0. 0. 1. 3.]
         [0. 0. 0. 1.]]
        """
        from ansys.geometry.core.math.vector import Vector3D

        # Verify the input
        check_type(translation, Vector3D)

        matrix = cls(
            [
                [1, 0, 0, translation.x],
                [0, 1, 0, translation.y],
                [0, 0, 1, translation.z],
                [0, 0, 0, 1],
            ]
        )
        return matrix

    def is_translation(self, including_identity: bool = False) -> bool:
        """Check if the matrix represents a translation.

        This method checks if the matrix represents a translation transformation.
        A translation matrix has the following form:

            [1 0 0 tx]
            [0 1 0 ty]
            [0 0 1 tz]
            [0 0 0  1]

        Parameters
        ----------
        including_identity : bool, optional
            If ``True``, the method will return ``True`` for the identity matrix as well.
            If ``False``, the method will return ``False`` for the identity matrix.

        Returns
        -------
        bool
            ``True`` if the matrix represents a translation, ``False`` otherwise.

        Examples
        --------
        >>> matrix = Matrix44([[1, 0, 0, 5], [0, 1, 0, 3], [0, 0, 1, 2], [0, 0, 0, 1]])
        >>> matrix.is_translation()
        True
        >>> identity_matrix = Matrix44([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        >>> identity_matrix.is_translation()
        False
        >>> identity_matrix.is_translation(including_identity=True)
        True
        """
        if not (
            self.__is_close(self[0][0], 1)
            and self.__is_close(self[0][1], 0)
            and self.__is_close(self[0][2], 0)
        ):
            return False
        if not (
            self.__is_close(self[1][0], 0)
            and self.__is_close(self[1][1], 1)
            and self.__is_close(self[1][2], 0)
        ):
            return False
        if not (
            self.__is_close(self[2][0], 0)
            and self.__is_close(self[2][1], 0)
            and self.__is_close(self[2][2], 1)
        ):
            return False
        if not self.__is_close(self[2][2], 1):
            return False

        if (
            not including_identity
            and self.__is_close(self[0][3], 0)
            and self.__is_close(self[1][3], 0)
            and self.__is_close(self[2][3], 0)
        ):
            return False

        return True

    def __is_close(self, a, b, tol=1e-9):
        """Check if two values are close to each other within a tolerance."""
        return np.isclose(a, b, atol=tol)

    @classmethod
    def create_rotation(
        cls, direction_x: "Vector3D", direction_y: "Vector3D", direction_z: "Vector3D" = None
    ) -> "Matrix44":
        """Create a matrix representing the specified rotation.

        Parameters
        ----------
        direction_x : Vector3D
            The X direction vector.
        direction_y : Vector3D
            The Y direction vector.
        direction_z : Vector3D, optional
            The Z direction vector. If not provided, it will be calculated
            as the cross product of direction_x and direction_y.

        Returns
        -------
        Matrix44
            A 4x4 matrix representing the rotation.

        Examples
        --------
        >>> direction_x = Vector3D(1.0, 0.0, 0.0)
        >>> direction_y = Vector3D(0.0, 1.0, 0.0)
        >>> rotation_matrix = Matrix44.create_rotation(direction_x, direction_y)
        >>> print(rotation_matrix)
        [[1. 0. 0. 0.]
        [0. 1. 0. 0.]
        [0. 0. 1. 0.]
        [0. 0. 0. 1.]]
        """
        from ansys.geometry.core.math.vector import Vector3D

        # Verify the inputs
        check_type(direction_x, Vector3D)
        check_type(direction_y, Vector3D)
        if direction_z is not None:
            check_type(direction_z, Vector3D)

        if not direction_x.is_perpendicular_to(direction_y):
            raise ValueError("The provided direction vectors are not orthogonal.")

        # Normalize the vectors
        direction_x = direction_x.normalize()
        direction_y = direction_y.normalize()

        # Calculate the third direction vector if not provided
        if direction_z is None:
            direction_z = direction_x.cross(direction_y)
        else:
            if not (
                direction_x.is_perpendicular_to(direction_z)
                and direction_y.is_perpendicular_to(direction_z)
            ):
                raise ValueError("The provided direction vectors are not orthogonal.")
            direction_z = direction_z.normalize()

        matrix = cls(
            [
                [direction_x.x, direction_y.x, direction_z.x, 0],
                [direction_x.y, direction_y.y, direction_z.y, 0],
                [direction_x.z, direction_y.z, direction_z.z, 0],
                [0, 0, 0, 1],
            ]
        )
        return matrix

    @classmethod
    def create_matrix_from_rotation_about_axis(cls, axis: "Vector3D", angle: float) -> "Matrix44":
        """
        Create a matrix representing a rotation about a given axis.

        Parameters
        ----------
        axis : Vector3D
            The axis of rotation.
        angle : float
            The angle of rotation in radians.

        Returns
        -------
        Matrix44
            A 4x4 matrix representing the rotation.
        """
        axis_dir = axis.normalize()
        x, y, z = axis_dir[0], axis_dir[1], axis_dir[2]

        k = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])

        identity = np.eye(3)
        cos_theta = np.cos(angle)
        sin_theta = np.sin(angle)

        # Rodrigues' rotation formula
        rotation_3x3 = identity + sin_theta * k + (1 - cos_theta) * (k @ k)

        # Convert to a 4x4 homogeneous matrix
        rotation_matrix = np.eye(4)
        rotation_matrix[:3, :3] = rotation_3x3

        return cls(rotation_matrix)

    @classmethod
    def create_matrix_from_mapping(cls, frame: "Frame") -> "Matrix44":
        """
        Create a matrix representing the specified mapping.

        Parameters
        ----------
        frame : Frame
            The frame containing the origin and direction vectors.

        Returns
        -------
        Matrix44
            A 4x4 matrix representing the translation and rotation defined by the frame.
        """
        from ansys.geometry.core.math.vector import Vector3D

        translation_matrix = Matrix44.create_translation(
            Vector3D([frame.origin[0], frame.origin[1], frame.origin[2]])
        )
        rotation_matrix = Matrix44.create_rotation(frame.direction_x, frame.direction_y)
        return translation_matrix * rotation_matrix
