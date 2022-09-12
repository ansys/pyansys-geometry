from typing import Optional, Union

import numpy as np
from pint import Unit
from scipy.spatial.transform import Rotation as spatial_rotation

from ansys.geometry.core.math import Vector
from ansys.geometry.core.misc import UNIT_ANGLE, check_ndarray_is_float_int
from ansys.geometry.core.misc.units import PhysicalQuantity
from ansys.geometry.core.typing import Real


class Rotation(np.ndarray, PhysicalQuantity):
    def __new__(
        cls,
        input: object,
        angle: Union[Real, np.ndarray],
        axis: str,
        unit: Optional[Unit] = UNIT_ANGLE,
    ) -> object:
        """Constructor for ``Rotation``."""
        obj = np.asarray(input).view(cls)
        check_ndarray_is_float_int(obj)
        ang = np.asarray(angle).view(cls)
        if len(axis) > 3:
            raise ValueError(
                f"Expected axis specification to be a string of up to 3 characters, got{axis}"
            )
        if ang.ndim == 0 and len(axis) != 1:
            raise ValueError("Axis and angle are not matching")
        if ang.ndim == 1 and len(axis) != ang.shape[0]:
            raise ValueError("Axis and angle are not matching")
        if ang.ndim >= 2 and len(axis) != ang.shape[1]:
            raise ValueError("Axis and angle are not matching")
        super().__init__(cls, unit, expected_dimensions=UNIT_ANGLE)
        obj._angle = ang
        obj._axis = axis
        obj_type = type(input)
        rotated_obj = spatial_rotation.from_euler(obj._axis, obj._angle)
        obj_rot = rotated_obj.apply(obj)
        return obj_type(obj_rot)


class Translation(np.ndarray):
    def __new__(cls, input: object, v: Vector):
        obj = np.asarray(input).view(cls)
        obj = np.append(obj, [1])
        if v._is_3d == True:
            translate = np.array(
                [
                    [1, 0, 0, v.x],
                    [0, 1, 0, v.y],
                    [0, 0, 1, v.z],
                    [0, 0, 0, 1],
                ]
            )
        else:
            translate = np.array(
                [
                    [1, 0, v.x],
                    [0, 1, v.y],
                    [0, 0, 1],
                ]
            )
        return np.matmul(translate, obj)[:-1]


class Scale(np.ndarray):
    def __new__(cls, input: object, v: Vector):
        obj = np.asarray(input).view(cls)
        obj = np.append(obj, [1])
        if v._is_3d == True:
            scalar_matrix = np.array(
                [
                    [v.x, 0, 0, 0],
                    [0, v.y, 0, 0],
                    [0, 0, v.z, 0],
                    [0, 0, 0, 1],
                ]
            )
        else:
            scalar_matrix = np.array(
                [
                    [v.x, 0, 0],
                    [0, v.y, 0],
                    [0, 0, 1],
                ]
            )
        return np.matmul(scalar_matrix, input)[:-1]
