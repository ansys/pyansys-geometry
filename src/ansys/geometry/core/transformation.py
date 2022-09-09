from typing import Optional, Union

import numpy as np
from scipy.spatial.transform import Rotation as spatial_rot

from ansys.geometry.core.math import Vector3D
from ansys.geometry.core.math.vector import Vector2D
from ansys.geometry.core.misc.checks import check_ndarray_is_float_int
from ansys.geometry.core.typing import Real


class Rotation(np.ndarray):
    def __new__(
        cls, input: object, angle: Union[Real, np.ndarray], axis: Optional[str] = "x"
    ) -> object:
        """Constructor for ``Rotation``."""
        obj = np.asarray(input).view(cls)
        check_ndarray_is_float_int(obj)
        ang = np.asarray(angle).view(cls)
        obj_type = type(input)
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
        obj._angle = ang
        obj._axis = axis
        rotated_obj = spatial_rot.from_euler(obj._axis, obj._angle)
        obj_rot = rotated_obj.apply(obj)
        return obj_rot.view(obj_type)


class Translation(np.ndarray):
    def __new__(cls, input: object, v: Union[Vector2D, Vector3D]):
        obj = np.asarray(input).view(cls)
        translate = np.array(
            [
                [1, 0, 0, v.x],
                [0, 1, 0, v.y],
                [0, 0, 1, v.z],
                [0, 0, 0, 1],
            ]
        )
        return np.multiply(translate, obj)


class Scale(np.ndarray):
    def __new__(cls, input: object, v: Vector3D):
        obj = np.asarray(input).view(cls)
        scalar_matrix = np.array(
            [
                [v.x, 0, 0, 0],
                [0, v.y, 0, 0],
                [0, 0, v.z, 0],
                [0, 0, 0, 1],
            ]
        )
        return np.matmul(scalar_matrix, input)
