from math import cos, sin
from typing import Optional

import numpy as np
from pint import Unit

from ansys.geometry.core import UNIT_ANGLE
from ansys.geometry.core.misc import check_pint_unit_compatibility
from ansys.geometry.core.primitives.vector import Vector2D, Vector3D


class Matrix33(np.ndarray):
    def __new__(cls, input: np.ndarray):
        """Constructor for ``Point3D``."""

        obj = np.asarray(input).view(cls)

        if obj is None or obj.ndim != 2 or obj.shape != (3, 3):
            raise ValueError("Matrix33 should only be a 2D array of shape (3,3).")

        if not np.issubdtype(obj.dtype, np.number) or not isinstance(obj, (np.ndarray)):
            raise ValueError("The input parameters should be integer or float.")

        return obj

    def inverse(self):
        det = np.linalg.det(self)
        if det == 0:
            raise ValueError("The determinent of matrix is zero, cannot be inversed")
        return np.linalg.inv(self)


class Matrix44(np.ndarray):
    def __new__(cls, input):
        """Constructor for ``Point3D``."""

        obj = np.asarray(input).view(cls)

        if obj is None or obj.ndim != 2 or obj.shape != (4, 4):
            raise ValueError("Matrix44 shouldonly be a 2D array of shape (4,4).")

        if not np.issubdtype(obj.dtype, np.number) or not isinstance(obj, (np.ndarray)):
            raise ValueError("The input parameters should be integer or float.")

        return obj

    def inverse(self):
        det = np.linalg.det(self)
        if det == 0:
            raise ValueError("The determinent of matrix is zero, cannot be inversed")
        return np.linalg.inv(self)

    def rotateX(self, angle, unit: Optional[Unit] = UNIT_ANGLE):
        if unit is not UNIT_ANGLE:
            angle = (angle * unit).to_base_units().magnitude

        check_pint_unit_compatibility(unit, UNIT_ANGLE)
        s = sin(angle)
        c = cos(angle)
        rot = np.identity(4)
        rot[1, 1] = rot[2, 2] = c
        rot[1, 2] = -s
        rot[2, 1] = s
        return np.matmul(self, rot)

    def rotateY(self, angle, unit: Optional[Unit] = UNIT_ANGLE):
        if unit is not UNIT_ANGLE:
            angle = (angle * unit).to_base_units().magnitude

        check_pint_unit_compatibility(unit, UNIT_ANGLE)
        s = sin(angle)
        c = cos(angle)
        rot = np.identity(4)
        rot[0, 0] = rot[3, 3] = c
        rot[3, 1] = -s
        rot[1, 3] = s
        return np.matmul(self, rot)

    def rotateZ(self, angle, unit: Optional[Unit] = UNIT_ANGLE):
        if unit is not UNIT_ANGLE:
            angle = (angle * unit).to_base_units().magnitude

        check_pint_unit_compatibility(unit, UNIT_ANGLE)

        s = sin(angle)
        c = cos(angle)
        rot = np.identity(4)
        rot[0, 0] = rot[1, 1] = c
        rot[0, 1] = -s
        rot[1, 0] = s
        return np.matmul(self, rot)


class RotationMatrix(Matrix33):
    def __new__(cls, input, angle, unit: Optional[Unit] = UNIT_ANGLE):
        if unit is not UNIT_ANGLE:
            angle = (angle * unit).to_base_units().magnitude

        check_pint_unit_compatibility(unit, UNIT_ANGLE)
        obj = Matrix33(input)
        rotation_matrix = np.array(
            [[cos(angle), -sin(angle), 0], [sin(angle), cos(angle), 0], [0, 0, 1]]
        )
        return np.matmul(obj, rotation_matrix)


class TranslationMatrix2D(Matrix33):
    def __new__(cls, input, v: Vector2D):
        obj = Matrix33(input)
        translate = np.array([[1, 0, v.x], [0, 1, v.y], [0, 0, 1]])
        return np.matmul(obj, translate)


class TranslationMatrix3D(Matrix44):
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
