import numpy as np

from ansys.geometry.core.math import Vector3D
from ansys.geometry.core.transformation import Rotation

DOUBLE_EPS = np.finfo(float).eps


def test_transformation_rotation():
    v_1 = Vector3D([1, 2, 3])
    rot_x = Rotation(v_1, np.pi / 2, "x")
    assert abs(all(rot_x - Vector3D([1, -1, 2]))) <= DOUBLE_EPS
