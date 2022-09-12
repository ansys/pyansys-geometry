import numpy as np

from ansys.geometry.core.math import Matrix33, Vector3D
from ansys.geometry.core.transformation import Rotation, Translation

DOUBLE_EPS = np.finfo(float).eps


def test_transformation_rotation():
    v_1 = Vector3D([1, 2, 3])
    rot_x = Rotation(v_1, np.pi / 2, "x")
    assert abs(all(rot_x - Vector3D([1, -1, 2]))) <= DOUBLE_EPS
    m = Matrix33()
    rot_x = Rotation(m, [np.pi / 2, np.pi / 2], "xy")
    test = np.array([[0, 0, -1], [1.0, 0, 0], [0.0, -1, 0]])


def test_translation():
    v_1 = Vector3D([1, 2, 3])
    v_2 = Vector3D([1, 1, 1])
    trans = Translation(v_1, v_2)
