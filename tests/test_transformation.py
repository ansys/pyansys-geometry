import numpy as np

from ansys.geometry.core.math import Matrix33, Point, Vector
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.transformation import Rotation, Translation

DOUBLE_EPS = np.finfo(float).eps * 2


def test_transformation_rotation():
    v_1 = Vector([1, 2, 3])
    rot_x = Rotation(v_1, np.pi / 2, "x")
    test_vector = Vector([1, -3, 2])
    assert rot_x.x - test_vector.x <= DOUBLE_EPS
    assert rot_x.y - test_vector.y <= DOUBLE_EPS
    assert rot_x.z - test_vector.z <= DOUBLE_EPS

    # Rotation along x axis in degree
    rot_x_degree = Rotation(v_1, 90, "x", unit=UNITS.degree)
    assert rot_x_degree.x - test_vector.x <= DOUBLE_EPS
    assert rot_x_degree.y - test_vector.y <= DOUBLE_EPS
    assert rot_x_degree.z - test_vector.z <= DOUBLE_EPS
    m = Matrix33()
    rot_x = Rotation(m, [np.pi / 2, np.pi / 2], "xy")
    test = np.array([[0, 0, -1], [1.0, 0, 0], [0.0, -1, 0]])


def test_translation():
    point = Point([1, 2, 3])
    v = Vector([1, 1, 1])
    trans = Translation(point, v)
