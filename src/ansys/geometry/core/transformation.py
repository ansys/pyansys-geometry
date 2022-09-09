from typing import Optional, Union

import numpy as np
from scipy.spatial.transform import Rotation as spatial_rot

from ansys.geometry.core.misc.checks import check_ndarray_is_float_int
from ansys.geometry.core.typing import Real


class Rotation:
    def __new__(
        cls, input: object, angle: Union[Real, np.ndarray], axis: Optional[str] = "x"
    ) -> object:
        """Constructor for ``Rotation``."""
        obj = np.asarray(input).view(cls)
        check_ndarray_is_float_int(obj)
        type = type(obj)
        if len(axis) > 3:
            raise ValueError("The rotation is possible only in three dimensions at a time")
        if len(axis) != len(angle) + 1:
            raise ValueError("Axis and angle are not matching")
        obj._angle = angle
        obj._axis = axis
        rotated_obj = spatial_rot.from_euler(obj._axis, obj._angle)
        obj_rot = rotated_obj.apply(obj)
        return obj_rot.view(type)
