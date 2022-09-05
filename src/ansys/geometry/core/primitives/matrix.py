from math import cos, sin
from typing import Optional, Union

import numpy as np
from pint import Unit

from ansys.geometry.core import UNIT_ANGLE, Real
from ansys.geometry.core.misc import check_pint_unit_compatibility
from ansys.geometry.core.primitives.vector import Vector2D, Vector3D
from ansys.geometry.core.typing import Real, RealSequence

DEFAULT_MATRIX33 = np.identity(3)
"""Default value for ``Matrix33``."""

DEFAULT_MATRIX44 = np.identity(4)
"""Default value for ``Matrix44``."""


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

        if not np.issubdtype(obj.dtype, np.number) or not isinstance(obj, (np.ndarray)):
            raise ValueError("The input parameters should be integer or float.")

        return obj

    def inverse(self: "Matrix33") -> "Matrix33":
        """Provides the inverse of 3x3 matrix."""
        det = np.linalg.det(self)
        if det <= 0:
            raise ValueError("The determinant of the matrix is zero, cannot be inversed.")
        return np.linalg.inv(self)


class Matrix44(np.ndarray):
    """A 4x4 matrix for working with 3D affine transformations.

    Parameters
    ----------
    input : numpy.ndarray, optional
        The matrix arguments as a :class:`np.ndarray`.
        By default, ``DEFAULT_MATRIX44``.
    """

    def __new__(cls, input: Union[np.ndarray, List[Real]] = DEFAULT_MATRIX44):
        """Constructor for ``Matrix44``."""
        if input is DEFAULT_MATRIX44:
            obj = np.asarray(DEFAULT_MATRIX44).view(cls)

        obj = np.asarray(input).view(cls)

        if obj is None or obj.ndim != 2 or obj.shape != (4, 4):
            raise ValueError("Matrix44 should only be a 2D array of shape (4,4).")

        if not np.issubdtype(obj.dtype, np.number) or not isinstance(obj, (np.ndarray)):
            raise ValueError("The input parameters should be integer or float.")

        return obj

    def inverse(self) -> "Matrix44":
        """Provides the inverse of 3x3 matrix."""
        det = np.linalg.det(self)
        if det == 0:
            raise ValueError("The determinant of the matrix is zero, cannot be inversed.")
        return np.linalg.inv(self)

    def rotate_x(self, angle: Real, unit: Optional[Unit] = UNIT_ANGLE) -> "Matrix44":
        """Rotate the 4x4 matrix in X axis in a counter-clockwise direction.

        Parameters
        ----------
        angle : Real
            The angle in which the X-axis rotates.
        unit : Unit, optional
           Unit for the angle, by default ``UNIT_ANGLE``."""
        if unit is not UNIT_ANGLE:
            angle = (angle * unit).to_base_units().magnitude

        check_pint_unit_compatibility(unit, UNIT_ANGLE)
        sin_angle = round(sin(angle))
        cos_angle = round(cos(angle))
        rotation_matrix = np.asarray(
            [
                [1, 0, 0, 0],
                [0, cos_angle, -sin_angle, 0],
                [0, sin_angle, cos_angle, 0],
                [0, 0, 0, 1],
            ]
        )
        return np.matmul(rotation_matrix, self)

    def rotate_y(self, angle, unit: Optional[Unit] = UNIT_ANGLE) -> "Matrix44":
        """Rotate the 4x4 matrix in Y axis in a counter-clockwise direction.

        Parameters
        ----------
        angle : Real
            The angle in which the Y-axis rotates.
        unit : Unit, optional
           Unit for the angle, by default ``UNIT_ANGLE``."""
        if unit is not UNIT_ANGLE:
            angle = (angle * unit).to_base_units().magnitude

        check_pint_unit_compatibility(unit, UNIT_ANGLE)
        sin_angle = round(sin(angle))
        cos_angle = round(cos(angle))
        rotation_matrix = np.asarray(
            [
                [cos_angle, 0, sin_angle, 0],
                [0, 1, 0, 0],
                [0, -sin_angle, cos_angle, 0],
                [0, 0, 0, 1],
            ]
        )
        return np.matmul(rotation_matrix, self)

    def rotate_z(self, angle, unit: Optional[Unit] = UNIT_ANGLE) -> "Matrix44":
        """Rotate the 4x4 matrix in Z axis in a counter-clockwise direction.

        Parameters
        ----------
        angle : Real
            The angle in which the Z-axis rotates.
        unit : Unit, optional
           Unit for the angle, by default ``UNIT_ANGLE``."""
        if unit is not UNIT_ANGLE:
            angle = (angle * unit).to_base_units().magnitude

        check_pint_unit_compatibility(unit, UNIT_ANGLE)

        sin_angle = round(sin(angle))
        cos_angle = round(cos(angle))
        rotation_matrix = np.asarray(
            [
                [cos_angle, -sin_angle, 0, 0],
                [sin_angle, cos_angle, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )
        return np.matmul(rotation_matrix, self)


class RotationMatrix(Matrix33):
    """Rotate the 3x3 matrix in a counter-clockwise direction.

    Parameters
    ----------
    angle : Real
        The angle in which the object rotates
    unit : Unit, optional
       Unit for the angle, by default ``UNIT_ANGLE``
    """

    def __new__(cls, input, angle, unit: Optional[Unit] = UNIT_ANGLE):
        if unit is not UNIT_ANGLE:
            angle = (angle * unit).to_base_units().magnitude

        check_pint_unit_compatibility(unit, UNIT_ANGLE)
        obj = Matrix33(input)
        rotation_matrix = np.array(
            [[cos(angle), -sin(angle), 0], [sin(angle), cos(angle), 0], [0, 0, 1]]
        )
        return np.matmul(rotation_matrix, obj)


class TranslationMatrix2D(Matrix33):
    """Translate the 3x3 matrix on 2D vector space."""

    def __new__(cls, input, v: Vector2D):
        obj = Matrix33(input)
        translate = np.array([[1, 0, v.x], [0, 1, v.y], [0, 0, 1]])
        return np.matmul(obj, translate)


class TranslationMatrix3D(Matrix44):
    """Translate the 4x4 matrix on 2D vector space."""

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
