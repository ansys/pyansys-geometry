"""``Matrix`` Class Module."""
from math import cos, sin
from typing import Optional, Union

import numpy as np
from pint import Unit

from ansys.geometry.core import UNIT_ANGLE
from ansys.geometry.core.misc import check_pint_unit_compatibility
from ansys.geometry.core.misc.checks import check_ndarray_is_float_int, check_type_equivalence
from ansys.geometry.core.primitives.vector import Vector2D, Vector3D
from ansys.geometry.core.typing import Real, RealSequence

DEFAULT_MATRIX33 = np.identity(3)
"""Default value of 3x3 identity matrix for ``Matrix33``."""

DEFAULT_MATRIX44 = np.identity(4)
"""Default value of 4x4 identity matrix for ``Matrix44``."""


class Matrix33(np.ndarray):
    """A 3x3 matrix for working with 2D affine transformations.

    Parameters
    ----------
    input : Union[numpy.ndarray, List[Real]], optional
        The matrix arguments as a :class:`np.ndarray`.
        By default, ``DEFAULT_MATRIX33``.
    """

    def __new__(cls, input: Optional[Union[np.ndarray, RealSequence]] = DEFAULT_MATRIX33):
        """Constructor for ``Matrix33``."""

        if input is DEFAULT_MATRIX33:
            obj = np.asarray(DEFAULT_MATRIX33).view(cls)

        obj = np.asarray(input).view(cls)

        if obj is None or obj.ndim != 2 or obj.shape != (3, 3):
            raise ValueError("Matrix33 should only be a 2D array of shape (3,3).")

        check_ndarray_is_float_int(obj)

        return obj

    def inverse(self) -> "Matrix33":
        """Provides the inverse of 3x3 matrix."""
        det = np.linalg.det(self)
        if det <= 0:
            raise ValueError("The determinant of the matrix is zero, cannot be inversed.")
        return np.linalg.inv(self)

    def determinant(self) -> float:
        """Provides the determinent of 3x3 matrix."""
        return np.linalg.det(self)

    def __eq__(self, other: "Matrix33") -> bool:
        """Equals operator for ``Matrix33``."""
        check_type_equivalence(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Matrix33") -> bool:
        """Not equals operator for ``Matrix33``."""
        return not self == other


class Matrix44(np.ndarray):
    """A 4x4 matrix for working with 3D affine transformations.

    Parameters
    ----------
    input : numpy.ndarray, optional
        The matrix arguments as a :class:`np.ndarray`.
        By default, ``DEFAULT_MATRIX44``.
    """

    def __new__(cls, input: Optional[Union[np.ndarray, RealSequence]] = DEFAULT_MATRIX44):
        """Constructor for ``Matrix44``."""
        if input is DEFAULT_MATRIX44:
            obj = np.asarray(DEFAULT_MATRIX44).view(cls)

        obj = np.asarray(input).view(cls)

        if obj is None or obj.ndim != 2 or obj.shape != (4, 4):
            raise ValueError("Matrix44 should only be a 2D array of shape (4,4).")

        check_ndarray_is_float_int(obj)

        return obj

    def inverse(self) -> "Matrix44":
        """Provides the inverse of 4x4 matrix."""
        det = np.linalg.det(self)
        if det == 0:
            raise ValueError("The determinant of the matrix is zero, cannot be inversed.")
        return np.linalg.inv(self)

    def determinant(self) -> float:
        """Provides the determinent of 4x4 matrix."""
        return np.linalg.det(self)

    def rotate_x(self, angle: Real, unit: Optional[Unit] = UNIT_ANGLE) -> "Matrix44":
        """Rotate the 4x4 matrix in X axis in a counter-clockwise direction.

        Parameters
        ----------
        angle : Real
            The angle in which the X-axis rotates.
        unit : ~pint.Unit, optional
           Unit for the angle, by default ``UNIT_ANGLE``.

        Notes
        -----
        The default unit of angle is radian.
        """
        if unit is not UNIT_ANGLE:
            angle = (angle * unit).to_base_units().magnitude

        check_pint_unit_compatibility(unit, UNIT_ANGLE)
        rotation_matrix = np.asarray(
            [
                [1, 0, 0, 0],
                [0, cos(angle), -sin(angle), 0],
                [0, sin(angle), cos(angle), 0],
                [0, 0, 0, 1],
            ]
        )
        return np.matmul(rotation_matrix, self)

    def rotate_y(self, angle: Real, unit: Optional[Unit] = UNIT_ANGLE) -> "Matrix44":
        """Rotate the 4x4 matrix in Y axis in a counter-clockwise direction.

        Parameters
        ----------
        angle : Real
            The angle in which the Y-axis rotates.
        unit : ~pint.Unit, optional
           Unit for the angle, by default ``UNIT_ANGLE``.

        Notes
        -----
        The default unit of angle is radian.
        """
        if unit is not UNIT_ANGLE:
            angle = (angle * unit).to_base_units().magnitude

        check_pint_unit_compatibility(unit, UNIT_ANGLE)
        rotation_matrix = np.asarray(
            [
                [cos(angle), 0, sin(angle), 0],
                [0, 1, 0, 0],
                [-sin(angle), 0, cos(angle), 0],
                [0, 0, 0, 1],
            ]
        )
        return np.matmul(rotation_matrix, self)

    def rotate_z(self, angle: Real, unit: Optional[Unit] = UNIT_ANGLE) -> "Matrix44":
        """Rotate the 4x4 matrix in Z axis in a counter-clockwise direction.

        Parameters
        ----------
        angle : Real
            The angle in which the Z-axis rotates.
        unit : ~pint.Unit, optional
           Unit for the angle, by default ``UNIT_ANGLE``.

        Notes
        -----
        The default unit of angle is radian.
        """
        if unit is not UNIT_ANGLE:
            angle = (angle * unit).to_base_units().magnitude

        check_pint_unit_compatibility(unit, UNIT_ANGLE)
        rotation_matrix = np.asarray(
            [
                [cos(angle), -sin(angle), 0, 0],
                [sin(angle), cos(angle), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )
        return np.matmul(rotation_matrix, self)

    def __eq__(self, other: "Matrix44") -> bool:
        """Equals operator for ``Matrix44``."""
        check_type_equivalence(other, self)
        return np.array_equal(self, other)

    def __ne__(self, other: "Matrix44") -> bool:
        """Not equals operator for ``Matrix44``."""
        return not self == other


class RotationMatrix(Matrix33):
    """Rotate the 3x3 matrix in a counter-clockwise direction.

    Parameters
    ----------
    angle : Real
        The angle in which the object rotates
    unit : ~pint.Unit, optional
       Unit for the angle, by default ``UNIT_ANGLE``

    Returns
    -------
    Matrix33
        The Rotated 3x3 Matrix

    Notes
    -----
    The default unit of angle is ``radian``.
    """

    def __new__(cls, input, angle: Real, unit: Optional[Unit] = UNIT_ANGLE):
        if unit is not UNIT_ANGLE:
            angle = (angle * unit).to_base_units().magnitude

        check_pint_unit_compatibility(unit, UNIT_ANGLE)
        obj = Matrix33(input)
        rotation_matrix = np.array(
            [[cos(angle), -sin(angle), 0], [sin(angle), cos(angle), 0], [0, 0, 1]]
        )
        return np.matmul(rotation_matrix, obj)


class TranslationMatrix2D(Matrix33):
    """Translate the 3x3 matrix on 2D vector space.

    Parameters
    ----------
    input : ``Matrix33`` or numpy.ndarray
        A :class:``Matrix33`` or the matrix arguments as a :class:`np.ndarray`.
    vector : ``Vector2D``
        A :class:``Vector2D`` representing the translation vector in
        which the matrix to get translate

    Returns
    -------
    Matrix33
        The translated matrix
    """

    def __new__(cls, input, vector: Vector2D):
        obj = Matrix33(input)
        translate = np.array([[1, 0, vector.x], [0, 1, vector.y], [0, 0, 1]])
        return np.matmul(obj, translate)


class TranslationMatrix3D(Matrix44):
    """Translate the 4x4 matrix on 3D vector space.

    Parameters
    ----------
    input : ``Matrix44`` or numpy.ndarray
        A :class:`Matrix44` or the matrix arguments as a :class:`np.ndarray`.
    vector : ``Vector3D``
        A :class:`Vector3D` representing the translation vector in
        which the matrix to get translate

    Returns
    -------
    Matrix44
        The translated matrix
    """

    def __new__(cls, input, v: Vector3D):
        obj = Matrix44(input)
        translate = np.array(
            [
                [1, 0, 0, v.x],
                [0, 1, 0, v.y],
                [0, 0, 1, v.z],
                [0, 0, 0, 1],
            ]
        )
        return np.matmul(obj, translate)
