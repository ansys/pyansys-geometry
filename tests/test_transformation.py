import numpy as np

from ansys.geometry.core.math import Matrix33, Matrix44, Point, Vector
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.transformation import Rotation, Scaling, Translation

DOUBLE_EPS = np.finfo(float).eps


def test_transformation_rotation():
    """Simple test to test rotation"""
    v_1 = Vector([1, 2, 3])
    rot_x = Rotation(v_1, np.pi / 2, "x")
    test_vector = Vector([1, -3, 2])
    assert round(rot_x.x) - test_vector.x <= DOUBLE_EPS
    assert round(rot_x.y) - test_vector.y <= DOUBLE_EPS
    assert round(rot_x.z) - test_vector.z <= DOUBLE_EPS

    # Rotation along x axis in degree
    rot_x_degree = Rotation(v_1, 90, "x", unit=UNITS.degree)
    assert round(rot_x_degree.x) - test_vector.x <= DOUBLE_EPS
    assert round(rot_x_degree.y) - test_vector.y <= DOUBLE_EPS
    assert round(rot_x_degree.z) - test_vector.z <= DOUBLE_EPS

    # Test matrix in x = 90, y = 90
    m = Matrix33()
    rot_matrix_xy = Rotation(m, [np.pi / 2, np.pi / 2], "xy")
    test = Matrix33([[0, 0, -1], [1, 0, 0], [0, -1, 0]])
    assert abs(rot_matrix_xy - test).all() <= DOUBLE_EPS

    point = Point([6, 2, 3])
    rot_point = Rotation(point, 60, "x", unit=UNITS.degree)
    rot_point_rad = Rotation(point, np.pi / 3, "x")
    test_point = Point([6, -1.5020666, 3.27777302])
    assert abs(rot_point - test_point).all() <= DOUBLE_EPS
    assert abs(rot_point_rad - test_point).all() <= DOUBLE_EPS


def test_transformation_translation():
    """Simple test for translation"""
    point = Point([1, 2, 3])
    v = Vector([1, 1, 1])
    trans = Translation(point, v)
    assert trans == Point([2, 3, 4])

    # Test matrix translation
    m_1 = Matrix33()
    v_1 = Vector([5, 6])
    trans_matrix = Translation(m_1, v_1)
    test_matrix = Matrix33([[1.0, 0.0, 5.0], [0.0, 1.0, 6.0], [0.0, 0.0, 1.0]])
    assert abs(trans_matrix - test_matrix).all() <= DOUBLE_EPS
    m_2 = Matrix44()
    v_2 = Vector([5, 6, 7])
    trans_matrix = Translation(m_2, v_2)
    test_matrix = Matrix44(
        [[1.0, 0.0, 0, 5.0], [0.0, 1.0, 0, 6.0], [0.0, 0.0, 1.0, 7], [0, 0, 0, 1]]
    )
    assert abs(trans_matrix - test_matrix).all() <= DOUBLE_EPS


def test_transformation_scalar():
    """Simple test for scaling"""
    point = Point([1, 2, 3])
    v = Vector([1, 1 / 2, 1 / 3])
    scale = Scaling(point, v)
    assert scale == Point([1, 1, 1])

    # Test matrix translation
    m = Matrix33()
    v = Vector([5, 6])
    scale_matrix = Scaling(m, v)
    test_matrix = Matrix33([[5.0, 0.0, 0.0], [0.0, 6.0, 0.0], [0.0, 0.0, 1.0]])
    assert abs(scale_matrix - test_matrix).all() <= DOUBLE_EPS
