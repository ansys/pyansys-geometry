# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.

from io import UnsupportedOperation

from beartype.roar import BeartypeCallHintParamViolation
import numpy as np
import pytest

from ansys.geometry.core.math import (
    UNITVECTOR2D_X,
    UNITVECTOR2D_Y,
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    UNITVECTOR3D_Z,
    ZERO_VECTOR2D,
    ZERO_VECTOR3D,
    BoundingBox2D,
    Frame,
    Matrix,
    Matrix33,
    Matrix44,
    Plane,
    Point2D,
    Point3D,
    UnitVector2D,
    UnitVector3D,
    Vector2D,
    Vector3D,
)
from ansys.geometry.core.misc import UNITS

DOUBLE_EPS = np.finfo(float).eps


def test_point():
    """Simple test to create ``Point2D`` and ``Point3D``."""

    # Test the default Point3D
    p_default = Point3D()
    assert len(p_default) == 3
    assert np.isnan(p_default).all()
    assert p_default.unit == UNITS.m
    p_default.unit = UNITS.cm
    p_default.x = new_x = 10 * UNITS.cm
    p_default.y = new_y = 20 * UNITS.cm
    p_default.z = new_z = 30 * UNITS.cm
    assert p_default.x == new_x
    assert p_default.y == new_y
    assert p_default.z == new_z
    assert p_default[0] == new_x.to_base_units().magnitude
    assert p_default[1] == new_y.to_base_units().magnitude
    assert p_default[2] == new_z.to_base_units().magnitude

    # Test the default Point2D
    p_default = Point2D()
    assert len(p_default) == 2
    assert np.isnan(p_default).all()
    assert p_default.unit == UNITS.m
    p_default.unit = UNITS.cm
    p_default.x = new_x = 10 * UNITS.cm
    p_default.y = new_y = 20 * UNITS.cm
    assert p_default.x == new_x
    assert p_default.y == new_y
    assert p_default[0] == new_x.to_base_units().magnitude
    assert p_default[1] == new_y.to_base_units().magnitude

    # Create two Point3D objects
    p3_1 = Point3D([0, 1, 3], UNITS.cm)
    p3_1_copy = Point3D([0, 1, 3], UNITS.cm)
    p3_2 = Point3D([0, 4, 7], UNITS.cm)

    assert p3_1.unit == UNITS.cm

    # Check that the equals operator works
    assert p3_1 == p3_1_copy
    assert p3_1 != p3_2

    # Check its X, Y, Z components
    assert p3_1.x == 0 * UNITS.cm
    assert p3_1.y == 1 * UNITS.cm
    assert p3_1.z == 3 * UNITS.cm

    # Check that the setter works properly in p_1_copy
    p3_1_copy.x = p3_1_copy.y = p3_1_copy.z = 3 * UNITS.cm

    # Check that the equals operator works (p_1 and p_1_copy should no longer be equal)
    assert p3_1 != p3_1_copy
    assert p3_1 != p3_2

    # Create two Point2D objects
    p2_1 = Point2D([1, 3], UNITS.cm)
    p2_1_copy = Point2D([1, 3], UNITS.cm)
    p2_2 = Point2D([4, 7], UNITS.cm)

    assert p2_1.unit == UNITS.cm

    # Check that the equals operator works
    assert p2_1 == p2_1_copy
    assert p2_1 != p2_2

    # Check its X, Y, Z components
    assert p2_1.x == 1 * UNITS.cm
    assert p2_1.y == 3 * UNITS.cm

    # Check that the setter works properly in p_1_copy
    p2_1_copy.x = p2_1_copy.y = 3 * UNITS.cm

    # Check that the equals operator works (p_1 and p_1_copy should no longer be equal)
    assert p2_1 != p2_1_copy
    assert p2_1 != p2_2


def test_point_errors():
    """Testing multiple ``Point3D`` and ``Point2D`` errors."""

    with pytest.raises(
        ValueError,
        match="Point3D class must receive 3 arguments.",
    ):
        Point3D([1, 4, 3, 5])

    with pytest.raises(
        ValueError,
        match="Point2D class must receive two arguments.",
    ):
        Point2D([1, 4, 5])

    with pytest.raises(
        TypeError, match="The numpy.ndarray 'input' should contain float or integer values."
    ):
        Point3D(["a", "b", "c"])

    with pytest.raises(
        TypeError, match="The numpy.ndarray 'input' should contain float or integer values."
    ):
        Point2D(["a", "b", "c"])

    # Create a Point3D
    point3D = Point3D([1, 4, 4])

    # Test setter error checks
    with pytest.raises(BeartypeCallHintParamViolation):
        point3D.x = "a"

    with pytest.raises(BeartypeCallHintParamViolation):
        point3D.y = "a"

    with pytest.raises(BeartypeCallHintParamViolation):
        point3D.z = "a"

    with pytest.raises(
        TypeError, match=r"The pint.Unit provided as an input should be a \[length\] quantity."
    ):
        point3D.z = 10 * UNITS.degrees

    # Create a Point2D
    point2D = Point2D([1, 4])

    # Test setter error checks
    with pytest.raises(BeartypeCallHintParamViolation):
        point2D.x = "a"

    with pytest.raises(BeartypeCallHintParamViolation):
        point2D.y = "a"

    with pytest.raises(
        TypeError, match=r"The pint.Unit provided as an input should be a \[length\] quantity."
    ):
        point2D.y = 10 * UNITS.degrees


def test_point2d_units():
    """``Point2D`` units testing."""

    # Create a Point2D with some units
    p_cm_to_mm = Point2D([10, 20], UNITS.cm)

    # Check that the units are correctly in place
    assert p_cm_to_mm.unit == UNITS.cm

    # Request for X, Y and ensure they are in cm
    assert p_cm_to_mm.x == 10 * UNITS.cm
    assert p_cm_to_mm.y == 20 * UNITS.cm

    # Check that the actual values are in base units (i.e. DEFAULT_UNITS.LENGTH)
    assert p_cm_to_mm[0] == p_cm_to_mm.x.to_base_units().magnitude
    assert p_cm_to_mm[1] == p_cm_to_mm.y.to_base_units().magnitude

    # Store the numpy array values
    (raw_x, raw_y) = p_cm_to_mm[0:3]

    # Set unit to mm now... and check if the values changed
    p_cm_to_mm.unit = UNITS.mm
    assert p_cm_to_mm.x == 100 * UNITS.mm
    assert p_cm_to_mm.y == 200 * UNITS.mm

    # Check that the values are still the same in the array
    assert raw_x == p_cm_to_mm[0]
    assert raw_y == p_cm_to_mm[1]

    # Now change the value of a X being in millimeters
    p_cm_to_mm.x = 20 * p_cm_to_mm.unit  # Basically 1/5 of original x
    assert not raw_x == p_cm_to_mm[0]
    assert raw_x == p_cm_to_mm[0] * 5

    # Now change the value of a Y being in millimeters
    p_cm_to_mm.y = 10 * p_cm_to_mm.unit  # Basically 1/20 of original y
    assert not raw_y == p_cm_to_mm[1]
    assert raw_y == p_cm_to_mm[1] * 20


def test_point3d_units():
    """``Point3D`` units testing."""

    # Create a Point with some units
    p_cm_to_mm = Point3D([10, 20, 30], UNITS.cm)

    # Check that the units are correctly in place
    assert p_cm_to_mm.unit == UNITS.cm

    # Request for X, Y, Z and ensure they are in cm
    assert p_cm_to_mm.x == 10 * UNITS.cm
    assert p_cm_to_mm.y == 20 * UNITS.cm
    assert p_cm_to_mm.z == 30 * UNITS.cm

    # Check that the actual values are in base units (i.e. DEFAULT_UNITS.LENGTH)
    assert p_cm_to_mm[0] == p_cm_to_mm.x.to_base_units().magnitude
    assert p_cm_to_mm[1] == p_cm_to_mm.y.to_base_units().magnitude
    assert p_cm_to_mm[2] == p_cm_to_mm.z.to_base_units().magnitude

    # Store the numpy array values
    (raw_x, raw_y, raw_z) = p_cm_to_mm[0:3]

    # Set unit to mm now... and check if the values changed
    p_cm_to_mm.unit = UNITS.mm
    assert p_cm_to_mm.x == 100 * UNITS.mm
    assert p_cm_to_mm.y == 200 * UNITS.mm
    assert p_cm_to_mm.z == 300 * UNITS.mm

    # Check that the values are still the same in the array
    assert raw_x == p_cm_to_mm[0]
    assert raw_y == p_cm_to_mm[1]
    assert raw_z == p_cm_to_mm[2]

    # Now change the value of a X being in millimeters
    p_cm_to_mm.x = 20 * p_cm_to_mm.unit  # Basically 1/5 of original x
    assert not raw_x == p_cm_to_mm[0]
    assert raw_x == p_cm_to_mm[0] * 5

    # Now change the value of a Y being in millimeters
    p_cm_to_mm.y = 10 * p_cm_to_mm.unit  # Basically 1/20 of original y
    assert not raw_y == p_cm_to_mm[1]
    assert raw_y == p_cm_to_mm[1] * 20

    # Now change the value of a Z being in millimeters
    p_cm_to_mm.z = 30 * p_cm_to_mm.unit  # Basically 1/10 of original z
    assert not raw_z == p_cm_to_mm[2]
    assert raw_z == p_cm_to_mm[2] * 10


def test_vector3D():
    """Simple test to create ``Vector3D``."""

    # Create two Vector3D objects
    v1 = Vector3D([0, 1, 3])
    v1_copy = Vector3D([0, 1, 3])
    v2 = Vector3D([0, 4, 7])

    # Check that the equals operator works
    assert v1 == v1_copy
    assert v1 != v2

    # Check its X, Y, Z components
    assert v1.x == 0
    assert v1.y == 1
    assert v1.z == 3

    # Check that the setter works properly in v1_copy
    v1_copy.x = 3
    v1_copy.y = 3
    v1_copy.z = 3

    # Check that the equals operator works (v1 and v1_copy should no longer be equal)
    assert v1 != v1_copy
    assert v1 != v2

    # Check the norm value of vector v1
    assert abs(round(v1.norm, 3) - 3.162) <= DOUBLE_EPS

    # Check the normalization value of v1
    v1_n = v1.normalize()
    assert abs(round(v1_n.x, 3) - 0.0) <= DOUBLE_EPS
    assert abs(round(v1_n.y, 3) - 0.316) <= DOUBLE_EPS
    assert abs(round(v1_n.z, 3) - 0.949) <= DOUBLE_EPS

    # Check the magnitude
    assert v1.magnitude == 3.1622776601683795
    assert v2.magnitude == 8.06225774829855

    assert (Vector3D([1, 0, 0])).get_angle_between(Vector3D([1, 1, 0])) == np.pi / 4

    # Check the cross product value of v1 with v2
    v_cross = v1.cross(v2)
    assert v_cross.x == -5
    assert v_cross.y == 0
    assert v_cross.z == 0

    assert Vector3D([1, 0, 0]).is_perpendicular_to(Vector3D([0, 1, 0]))
    assert Vector3D([1, 0, 0]).is_perpendicular_to(Vector3D([0, 0, 1]))
    assert not Vector3D([1, 0, 0]).is_perpendicular_to(Vector3D([1, 1, 1]))
    assert not Vector3D([1, 0, 0]).is_perpendicular_to(Vector3D([-1, 0, 0]))
    assert Vector3D([1, 1, 1]).is_perpendicular_to(Vector3D([0, -1, 1]))
    assert not Vector3D([0, 0, 0]).is_perpendicular_to(Vector3D([0, -1, 1]))
    assert not Vector3D([0, -1, 1]).is_perpendicular_to(Vector3D([0, 0, 0]))

    assert Vector3D([0, 0, 0]).is_zero
    assert not Vector3D([0, 1, 0]).is_zero

    # Check that the dot and cross product overload is fine
    assert abs(round(v1 * v2 - 25)) <= DOUBLE_EPS
    v_cross_overload = v1 % v2
    assert v_cross_overload == v_cross

    # Check as well that vector * scalar also works
    assert Vector3D([5, 5, 5]) == Vector3D([1, 1, 1]) * 5
    assert Vector3D([5, 5, 5]) == 5 * Vector3D([1, 1, 1])

    # Checking that scalar times vector also works
    v1_x_3 = Vector3D([0, 3, 9])
    assert all(
        [
            abs(round(v1_comp * 3 - v1_x_3_comp)) <= DOUBLE_EPS
            for v1_comp, v1_x_3_comp in zip(v1, v1_x_3)
        ]
    )

    # Create a 3D vector from 2 points
    point_a = Point3D([1, 2, 3])
    point_b = Point3D([1, 6, 3])
    vector_from_points = Vector3D.from_points(point_a, point_b)
    assert vector_from_points.x == 0
    assert vector_from_points.y == 4
    assert vector_from_points.z == 0

    # Create a 3D vector from 2 points
    point_a = Point3D([1, 2, 3], UNITS.mm)
    point_b = Point3D([1, 6, 3], UNITS.cm)
    vector_from_points = Vector3D.from_points(point_a, point_b)
    assert abs(vector_from_points.x - 0.009) <= DOUBLE_EPS
    assert abs(vector_from_points.y - 0.058) <= DOUBLE_EPS
    assert abs(vector_from_points.z - 0.027) <= DOUBLE_EPS

    # Compute the angle of two vectors when they are parallel
    pos_x = UNITVECTOR3D_X
    neg_x = -UNITVECTOR3D_X
    ang_pi = pos_x.get_angle_between(neg_x)
    ang_0 = pos_x.get_angle_between(pos_x)
    assert ang_pi.m == np.pi
    assert ang_0.m == 0

    # Add two vectors
    vec_res = pos_x + neg_x
    assert vec_res == ZERO_VECTOR3D

    # Subtract two vectors
    vec_res = pos_x - neg_x
    assert vec_res == (UNITVECTOR3D_X + UNITVECTOR3D_X)

    # Parallel vectors
    assert UNITVECTOR3D_X.is_parallel_to(UNITVECTOR3D_X)
    assert not UNITVECTOR3D_X.is_parallel_to(UNITVECTOR3D_Y)

    # Opposite vectors
    assert UNITVECTOR3D_X.is_opposite(Vector3D([-1, 0, 0]))
    assert not UNITVECTOR3D_X.is_opposite(UNITVECTOR3D_X)


def test_vector2D():
    """Simple test to create ``Vector2D``."""

    # Create two Vector2D objects
    v1 = Vector2D([0, 1])
    v1_copy = Vector2D([0, 1])
    v2 = Vector2D([0, 4])

    # Check that the equals operator works
    assert v1 == v1_copy
    assert v1 != v2

    # Check its X, Y components
    assert v1.x == 0
    assert v1.y == 1

    # Check that the setter works properly in v1_copy
    v1_copy.x = 3
    v1_copy.y = 3

    # Check that the equals operator works (v1 and v1_copy should no longer be equal)
    assert v1 != v1_copy
    assert v1 != v2

    # Check the norm value of vector v1
    assert abs(round(v1.norm, 3) - 1) <= DOUBLE_EPS

    # Check the normalization value of v1
    v1_n = v1.normalize()
    assert abs(round(v1_n.x, 3) - 0.0) <= DOUBLE_EPS
    assert abs(round(v1_n.y, 3) - 1) <= DOUBLE_EPS

    # Check the magnitude
    assert v1.magnitude == 1
    assert v2.magnitude == 4

    assert (Vector2D([1, 0])).get_angle_between(Vector2D([1, 1])) == np.pi / 4
    assert (Vector2D([1, 1])).get_angle_between(Vector2D([1, 0])) == 7 * np.pi / 4

    assert Vector2D([1, 0]).is_perpendicular_to(Vector2D([0, 1]))
    assert not Vector2D([1, 0]).is_perpendicular_to(Vector2D([1, 1]))
    assert not Vector2D([1, 0]).is_perpendicular_to(Vector2D([-1, 0]))
    assert not Vector2D([0, 0]).is_perpendicular_to(Vector2D([-1, 0]))

    assert Vector2D([0, 0]).is_zero
    assert not Vector2D([0, 1]).is_zero

    # Check that the dot product overload is fine
    assert abs(round(v1 * v2 - 4)) <= DOUBLE_EPS

    # Checking that scalar times vector also works
    assert abs(round((v1 * 3 - Vector2D([0, 3])).magnitude)) <= DOUBLE_EPS

    # Create a 2D vector from 2 points
    point_a = Point2D([1, 2])
    point_b = Point2D([1, 6])
    vector_from_points = Vector2D.from_points(point_a, point_b)
    assert vector_from_points.x == 0
    assert vector_from_points.y == 4

    # Create a 2D vector from 2 points
    point_a = Point2D([1, 2], UNITS.mm)
    point_b = Point2D([1, 6], UNITS.cm)
    vector_from_points = Vector2D.from_points(point_a, point_b)
    assert abs(vector_from_points.x - 0.009) <= DOUBLE_EPS
    assert abs(vector_from_points.y - 0.058) <= DOUBLE_EPS

    # Add two vectors
    # Compute the angle of two vectors when they are parallel
    pos_x = UNITVECTOR2D_X
    neg_x = -UNITVECTOR2D_X
    vec_res = pos_x + neg_x
    assert vec_res == ZERO_VECTOR2D

    # Subtract two vectors
    vec_res = pos_x - neg_x
    assert vec_res == (UNITVECTOR2D_X + UNITVECTOR2D_X)

    # Parallel vectors
    assert UNITVECTOR2D_X.is_parallel_to(UNITVECTOR2D_X)
    assert not UNITVECTOR2D_X.is_parallel_to(UNITVECTOR2D_Y)

    # Opposite vectors
    assert UNITVECTOR2D_X.is_opposite(Vector2D([-1, 0]))
    assert not UNITVECTOR2D_X.is_opposite(UNITVECTOR2D_X)


def test_unitvector3D():
    """Simple test to create a ``UnitVector3D``."""

    # Create UnitVector objects from Vector
    v1 = Vector3D([0, 1, 3])
    v2 = UnitVector3D(v1)
    assert abs(round(v2.x, 3) - 0.0) <= DOUBLE_EPS
    assert abs(round(v2.y, 3) - 0.316) <= DOUBLE_EPS
    assert abs(round(v2.z, 3) - 0.949) <= DOUBLE_EPS

    # Create UnitVector objects from numpy.ndarray
    v3 = UnitVector3D([1, 2, 3])
    assert abs(round(v3.x, 3) - 0.267) <= DOUBLE_EPS
    assert abs(round(v3.y, 3) - 0.535) <= DOUBLE_EPS
    assert abs(round(v3.z, 3) - 0.802) <= DOUBLE_EPS

    assert not UnitVector3D([1, 1, 1]).is_perpendicular_to(UnitVector3D([1, 1, -1]))
    assert UnitVector3D([1, 1, 1]).is_perpendicular_to(UnitVector3D([0, -1, 1]))

    assert UNITVECTOR3D_X.get_angle_between(UNITVECTOR3D_Y) == np.pi / 2

    # Check that UnitVector3D is immutable
    with pytest.raises(UnsupportedOperation, match="UnitVector3D is immutable."):
        v2.x = 3
    with pytest.raises(UnsupportedOperation, match="UnitVector3D is immutable."):
        v2.y = 3
    with pytest.raises(UnsupportedOperation, match="UnitVector3D is immutable."):
        v2.z = 3

    point_a = Point3D([1, 2, 7])
    point_b = Point3D([1, 2, 5])
    vector_from_points = UnitVector3D.from_points(point_a, point_b)
    assert vector_from_points.x == 0
    assert vector_from_points.y == 0
    assert vector_from_points.z == -1


def test_unitvector2D():
    """Simple test to create a ``UnitVector2D``."""

    # Create UnitVector2D objects from Vector
    v1 = Vector2D([0, 1])
    v2 = UnitVector2D(v1)
    assert abs(round(v2.x, 3) - 0.0) <= DOUBLE_EPS
    assert abs(round(v2.y, 3) - 1) <= DOUBLE_EPS

    # Create UnitVector2D objects from numpy.ndarray
    v3 = UnitVector2D([1, 2])
    assert abs(round(v3.x, 3) - 0.447) <= DOUBLE_EPS
    assert abs(round(v3.y, 3) - 0.894) <= DOUBLE_EPS

    assert UnitVector2D([1, 0]).is_perpendicular_to(UnitVector2D([0, 1]))
    assert not UnitVector2D([1, 0]).is_perpendicular_to(UnitVector2D([1, 1]))

    assert UNITVECTOR2D_X.get_angle_between(UNITVECTOR2D_Y) == np.pi / 2

    # Check that UnitVector2D is immutable
    with pytest.raises(UnsupportedOperation, match="UnitVector2D is immutable."):
        v2.x = 3
    with pytest.raises(UnsupportedOperation, match="UnitVector2D is immutable."):
        v2.y = 3

    point_a = Point2D([1, 2])
    point_b = Point2D([1, 5])
    vector_from_points = UnitVector2D.from_points(point_a, point_b)
    assert vector_from_points.x == 0
    assert vector_from_points.y == 1


def test_vector3D_errors():
    """Testing multiple ``Vector3D`` errors."""

    with pytest.raises(
        ValueError,
        match="Vector3D class must receive 3 arguments.",  # noqa: E501
    ):
        Vector3D([1, 2])

    with pytest.raises(
        ValueError,
        match="Vector3D class must receive 3 arguments.",  # noqa: E501
    ):
        Vector3D([1, 2, 3, 4])

    with pytest.raises(
        TypeError, match="The numpy.ndarray 'input' should contain float or integer values."
    ):
        Vector3D(["a", "b", "c"])

    # Create a Vector
    v1 = Vector3D([1, 2, 3])

    # Test setter error checks
    with pytest.raises(BeartypeCallHintParamViolation):
        v1.x = "x"

    with pytest.raises(BeartypeCallHintParamViolation):
        v1.y = "y"

    with pytest.raises(BeartypeCallHintParamViolation):
        v1.z = "z"

    # Try to normalize a 0-value vector
    with pytest.raises(ValueError, match="The norm of the 3D vector is not valid."):
        v2 = ZERO_VECTOR3D
        v2.normalize()

    # Try to get the angle of two vectors when one of them is 0-valued
    with pytest.raises(ValueError, match="Vectors cannot be zero-valued."):
        v2 = ZERO_VECTOR3D
        v1.get_angle_between(v2)


def test_vector2D_errors():
    """Testing multiple ``Vector2D`` errors."""

    with pytest.raises(
        ValueError,
        match="Vector2D class must receive 2 arguments.",  # noqa: E501
    ):
        Vector2D([1])

    with pytest.raises(
        ValueError,
        match="Vector2D class must receive 2 arguments.",  # noqa: E501
    ):
        Vector2D([1, 2, 3])

    with pytest.raises(
        TypeError, match="The numpy.ndarray 'input' should contain float or integer values."
    ):
        Vector2D(["a", "b"])

    # Create a Vector
    v1 = Vector2D([1, 2])

    # Test setter error checks
    with pytest.raises(BeartypeCallHintParamViolation):
        v1.x = "x"

    with pytest.raises(BeartypeCallHintParamViolation):
        v1.y = "y"

    # Try to normalize a 0-value vector
    with pytest.raises(ValueError, match="The norm of the 2D vector is not valid."):
        v2 = ZERO_VECTOR2D
        v2.normalize()

    # Try to get the angle of two vectors when one of them is 0-valued
    with pytest.raises(ValueError, match="Vectors cannot be zero-valued."):
        v2 = ZERO_VECTOR2D
        v1.get_angle_between(v2)


def test_matrix():
    """Simple test to create a ``Matrix``."""

    # Create two matrix objects
    m_1 = Matrix([[2, 5], [0, 8]])
    m_1_copy = Matrix([[2, 5], [0, 8]])
    m_2 = Matrix([[3, 2, 0], [1, 3, 0], [0, 6, 4]])

    # Initiate a test matrix using numpy.ndarray
    test_matrix = np.array([[2, 5], [0, 8]])

    # Check inverse of matrix
    m_3 = m_1.inverse()
    test_inverse = np.linalg.inv(test_matrix)
    assert abs(m_3 - test_inverse).all() <= DOUBLE_EPS

    # Check determinant of matrix
    det = m_1.determinant()
    assert abs(round(det, 3) - 16) <= DOUBLE_EPS

    # Check the equals operator
    assert m_1 == m_1_copy
    assert m_1 != m_2

    # Check the multiply operator
    m_4 = Matrix([[2, 5, 3], [0, 8, 3]])
    test_multiply = np.array([[2, 5, 3], [0, 8, 3]])
    assert np.array_equal((m_1 * m_4), np.matmul(test_matrix, test_multiply))

    # Check invalid size
    with pytest.raises(ValueError, match="Matrix should only be a 2D array."):
        Matrix([None, None, None, None, None])


def test_matrix_errors():
    """Testing multiple ``Matrix`` errors."""

    with pytest.raises(
        TypeError, match="The numpy.ndarray should contain float or integer values."
    ):
        Matrix(([[2, 0, "a"], [0, 3, 0], [0, 0, 4]]))

    # Test inverse error with determinent is zero
    with pytest.raises(
        ValueError, match="The matrix cannot be inversed because its determinant is zero."
    ):
        Matrix([[1, 2, 3], [2, 5, 6], [2, 5, 3]]).inverse()

    # Test determinent error of nxm matrix
    with pytest.raises(ValueError, match="The determinant is only defined for square matrices."):
        Matrix([[1, 2, 3, 4], [2, 5, 6, 5], [2, 5, 3, 10]]).determinant()

    m_1 = Matrix([[2, 5], [0, 8]])
    m_2 = Matrix([[2, 5, 6], [0, 8, 6], [1, 2, 3]])

    # Test multiply operator with mismatched dimensions.
    with pytest.raises(
        ValueError, match="The dimensions of the matrices 2 and 3 are not multipliable."
    ):
        m_1 * m_2


def test_matrix_33():
    """Simple test to create a ``Matrix33``."""

    # Create a Matrix33 objects
    m_1 = Matrix33([[2, 0, 0], [0, 3, 0], [0, 0, 4]])

    # Create a null matrix, which is 3x3 identity matrix
    m_null = Matrix33()

    # Initiate a test matrix using numpy.ndarray
    test_matrix = np.array([[2, 0, 0], [0, 3, 0], [0, 0, 4]])
    assert np.array_equal(test_matrix, m_1)

    # Check the default matrix is identity matrix
    assert np.array_equal(np.identity(3), m_null)

    # Check inverse of matrix
    test_inverse = np.linalg.inv(test_matrix)
    m_3 = m_1.inverse()
    assert abs(m_3 - test_inverse).all() <= DOUBLE_EPS

    # Check determinant of matrix
    det = m_1.determinant()
    assert abs(round(det, 3) - 24) <= DOUBLE_EPS

    m_2 = Matrix44([[2, 0, 0, 2], [0, 3, 0, 1], [0, 0, 4, 2], [0, 0, 4, 2]])
    assert m_1 != m_2

    with pytest.raises(ValueError) as val:
        Matrix33([[1, 2], [1, 6]])
        assert "Matrix33 should only be a 2D array of shape (3,3)." in str(val.value)


def test_matrix_44():
    """Simple test to create a ``Matrix44``."""

    # Create two Matrix44 objects
    m_1 = Matrix44([[2, 0, 0, 0], [0, 3, 0, 0], [0, 0, 4, 0], [0, 0, 0, 1]])

    # Create a null matrix, which is 4x4 identity matrix
    m_null = Matrix44()

    # Initiate a test matrix using numpy.ndarray
    test_matrix = np.array([[2, 0, 0, 0], [0, 3, 0, 0], [0, 0, 4, 0], [0, 0, 0, 1]])
    assert np.array_equal(test_matrix, m_1)

    # Check the default matrix is identity matrix
    assert np.array_equal(np.identity(4), m_null)

    # Check inverse of matrix
    test_inverse = np.linalg.inv(test_matrix)
    m_3 = m_1.inverse()
    assert abs(m_3 - test_inverse).all() <= DOUBLE_EPS

    # Check determinant of matrix
    det = m_1.determinant()
    assert abs(round(det, 3) - 24) <= DOUBLE_EPS

    m_2 = Matrix33([[2, 0, 0], [0, 3, 0], [0, 0, 4]])
    assert m_1 != m_2

    # Check error with other than 4x4 matrix
    with pytest.raises(ValueError) as val:
        Matrix44([[1, 2], [1, 6]])
        assert "Matrix44 should only be a 2D array of shape (4,4)." in str(val.value)


def test_frame():
    """``Frame`` construction and equivalency."""

    origin = Point3D([42, 99, 13])
    f_1 = Frame(origin, UnitVector3D([1, 0, 0]), UnitVector3D([0, 1, 0]))
    f_1_duplicate = Frame(origin, UnitVector3D([1, 0, 0]), UnitVector3D([0, 1, 0]))
    f_2 = Frame(Point3D([5, 8, 9]), UnitVector3D([1, 1, 1]), UnitVector3D([0, -1, 1]))
    f_with_array_definitions = Frame([5, 8, 9], [1, 1, 1], [0, -1, 1])
    f_defaults = Frame()

    assert f_1 == f_1_duplicate
    assert f_1 != f_2
    assert f_2 == f_with_array_definitions

    assert f_1.origin.x == origin.x
    assert f_1.origin.y == origin.y
    assert f_1.origin.z == origin.z

    assert f_defaults.origin.x == 0
    assert f_defaults.origin.y == 0
    assert f_defaults.origin.z == 0
    assert f_defaults.direction_x == UNITVECTOR3D_X
    assert f_defaults.direction_y == UNITVECTOR3D_Y
    assert f_defaults.direction_z == UNITVECTOR3D_Z

    # Test transformation matrix of frame
    transformed_matrix = Matrix44([[1, 0, 0, 42.0], [0, 1, 0, 99], [0, 0, 1, 13], [0, 0, 0, 1]])
    assert np.array_equal(f_1.transformation_matrix, transformed_matrix)

    with pytest.raises(ValueError, match="Direction x and direction y must be perpendicular."):
        Frame(origin, UnitVector3D([1, 0, 0]), UnitVector3D([1, 1, 0]))

    with pytest.raises(BeartypeCallHintParamViolation):
        Frame(origin, "A", UnitVector3D([25, 39, 82]))

    with pytest.raises(BeartypeCallHintParamViolation):
        Frame(origin, UnitVector3D([12, 31, 99]), "A")

    with pytest.raises(BeartypeCallHintParamViolation):
        Frame("A", UnitVector3D([12, 31, 99]), UnitVector3D([23, 67, 45]))


def test_frame_local_to_global_point_transformation():
    """``Frame`` transform_point_global_to_local implementation tests."""
    origin = Point3D([42, 99, 13])
    frame_xy = Frame(origin, UnitVector3D([1, 0, 0]), UnitVector3D([0, 1, 0]))
    transformed_xy_origin = frame_xy.transform_point2d_local_to_global(Point2D([0, 0]))
    assert transformed_xy_origin == origin

    global_to_local_mat = Matrix33(
        [UNITVECTOR3D_X.tolist(), UNITVECTOR3D_Y.tolist(), UNITVECTOR3D_Z.tolist()]
    )
    transformation_mat = Matrix44(
        [
            UNITVECTOR3D_X.tolist() + [0],
            UNITVECTOR3D_Y.tolist() + [0],
            UNITVECTOR3D_Z.tolist() + [0],
            origin.tolist() + [1],
        ]
    ).T
    assert frame_xy.global_to_local_rotation == global_to_local_mat
    assert frame_xy.local_to_global_rotation == global_to_local_mat.T

    # In this case, since the rotation is an identity matrix, they will be identical
    assert not frame_xy.local_to_global_rotation != global_to_local_mat

    assert frame_xy.transformation_matrix == transformation_mat
    assert frame_xy.transformation_matrix != transformation_mat.T

    frame_xz = Frame(origin, UnitVector3D([1, 0, 0]), UnitVector3D([0, 0, 1]))
    transformed_xz = frame_xz.transform_point2d_local_to_global(Point2D([0, 12]))
    assert transformed_xz == Point3D([42, 99, 25])

    frame_tilted = Frame(Point3D([0, 0, 0]), UnitVector3D([1, 1, 1]), UnitVector3D([0, -1, 1]))
    transformed_tilted = frame_tilted.transform_point2d_local_to_global(Point2D([0, 10]))
    assert transformed_tilted == Point3D([0, -7.071067811865475, 7.071067811865475])

    assert transformed_xy_origin == origin

    frame_xz = Frame(origin, UnitVector3D([1, 0, 0]), UnitVector3D([0, 0, 1]))
    transformed_xz = frame_xz.transform_point2d_local_to_global(Point2D([0, 12]))
    assert transformed_xz == Point3D([42, 99, 25])

    frame_tilted = Frame(Point3D([0, 0, 0]), UnitVector3D([1, 1, 1]), UnitVector3D([0, -1, 1]))
    transformed_tilted = frame_tilted.transform_point2d_local_to_global(Point2D([0, 10]))
    assert transformed_tilted == Point3D([0, -7.071067811865475, 7.071067811865475])


def test_plane():
    """``Plane`` construction and equivalency."""

    origin = Point3D([42, 99, 13])
    p_1 = Plane(origin, UnitVector3D([1, 0, 0]), UnitVector3D([0, 1, 0]))
    p_1_duplicate = Plane(origin, UnitVector3D([1, 0, 0]), UnitVector3D([0, 1, 0]))
    p_2 = Plane(Point3D([5, 8, 9]), UnitVector3D([1, 1, 1]), UnitVector3D([0, -1, 1]))
    p_with_array_definitions = Plane([5, 8, 9], [1, 1, 1], [0, -1, 1])
    p_defaults = Plane()

    assert p_1 == p_1_duplicate
    assert p_1 != p_2
    assert p_2 == p_with_array_definitions

    assert p_1.origin.x == origin.x
    assert p_1.origin.y == origin.y
    assert p_1.origin.z == origin.z

    assert p_defaults.origin.x == 0
    assert p_defaults.origin.y == 0
    assert p_defaults.origin.z == 0
    assert p_defaults.direction_x == UNITVECTOR3D_X
    assert p_defaults.direction_y == UNITVECTOR3D_Y
    assert p_defaults.direction_z == UNITVECTOR3D_Z

    with pytest.raises(BeartypeCallHintParamViolation):
        Plane(origin, "A", UnitVector3D([25, 39, 82]))

    with pytest.raises(BeartypeCallHintParamViolation):
        Plane(origin, UnitVector3D([12, 31, 99]), "A")

    with pytest.raises(BeartypeCallHintParamViolation):
        Plane("A", UnitVector3D([12, 31, 99]), UnitVector3D([23, 67, 45]))

    assert p_1.is_point_contained(Point3D([42, 99, 13]))
    assert not p_1.is_point_contained(Point3D([42, 99, 14]))

    with pytest.raises(BeartypeCallHintParamViolation):
        p_1.is_point_contained(Point2D([42, 99]))


def test_add_sub_point():
    """Test for adding/subtracting Point3D/2D objects."""

    # Point3D (and Vector3D)
    # =======================================================================

    # Let's create two reference points
    a_3d = Point3D([23, 43, 53], UNITS.mm)
    b_3d = Point3D([1, 3, 7], UNITS.dm)
    c_add_3d = Point3D([123, 343, 753], UNITS.mm)
    a_sub_b_3d = Point3D([-77, -257, -647], UNITS.mm)
    b_sub_a_3d = -a_sub_b_3d

    # Check that the add operation is equal to the ref value
    # and that the units are the same as "a_3d" (first value in add operation)
    c_add_mm_3d = a_3d + b_3d
    assert np.allclose(c_add_mm_3d, c_add_3d)
    assert c_add_mm_3d.unit == a_3d.unit

    # Let's add them the other way around
    c_add_dm_3d = b_3d + a_3d
    assert np.allclose(c_add_dm_3d, c_add_3d)
    assert c_add_dm_3d.unit == b_3d.unit

    # Let's do subtraction operations now with two points
    a_sub_b_mm_3d = a_3d - b_3d
    assert np.allclose(a_sub_b_mm_3d, a_sub_b_3d)
    assert a_sub_b_mm_3d.unit == a_3d.unit

    # Let's add them the other way around
    b_sub_a_dm_3d = b_3d - a_3d
    assert np.allclose(b_sub_a_dm_3d, b_sub_a_3d)
    assert b_sub_a_dm_3d.unit == b_3d.unit

    # Let's try adding a vector now. Vectors are always added as base units.
    vector_3d = Vector3D([1, 2, 3])
    d_3d = a_3d + vector_3d
    d_3d_ref = Point3D([1.023, 2.043, 3.053], UNITS.m)

    assert np.allclose(d_3d, d_3d_ref)
    assert d_3d.unit == a_3d.unit

    # Let's try adding it the other way around
    e_3d = vector_3d + a_3d
    assert np.allclose(e_3d, d_3d_ref)
    assert e_3d.unit == a_3d.unit

    # Let's try subtracting a vector to a point now
    a_sub_vec_3d = a_3d - vector_3d
    a_sub_vec_3d_ref = Point3D([-977, -1957, -2947], UNITS.mm)
    assert np.allclose(a_sub_vec_3d, a_sub_vec_3d_ref)
    assert a_sub_vec_3d.unit == a_3d.unit

    # Point2D (and Vector2D)
    # =======================================================================

    # Let's create two reference points
    a_2d = Point2D([23, 43], UNITS.mm)
    b_2d = Point2D([1, 3], UNITS.dm)
    c_add_2d = Point2D([123, 343], UNITS.mm)
    a_sub_b_2d = Point2D([-77, -257], UNITS.mm)
    b_sub_a_2d = -a_sub_b_2d

    # Check that the add operation is equal to the ref value
    # and that the units are the same as "a_2d" (first value in add operation)
    c_add_mm_2d = a_2d + b_2d
    assert np.allclose(c_add_mm_2d, c_add_2d)
    assert c_add_mm_2d.unit == a_2d.unit
    assert c_add_mm_2d.x == c_add_2d.x
    assert c_add_mm_2d.y == c_add_2d.y

    # Let's add them the other way around
    c_add_dm_2d = b_2d + a_2d
    assert np.allclose(c_add_dm_2d, c_add_2d)
    assert c_add_dm_2d.unit == b_2d.unit

    # Let's do subtraction operations now with two points
    a_sub_b_mm_2d = a_2d - b_2d
    assert np.allclose(a_sub_b_mm_2d, a_sub_b_2d)
    assert a_sub_b_mm_2d.unit == a_2d.unit

    # Let's subtract them the other way around
    b_sub_a_dm_2d = b_2d - a_2d
    assert np.allclose(b_sub_a_dm_2d, b_sub_a_2d)
    assert b_sub_a_dm_2d.unit == b_2d.unit

    # Let's try adding a vector now. Vectors are always added as base units.
    vector_2d = Vector2D([1, 2])
    d_2d = a_2d + vector_2d
    d_2d_ref = Point2D([1.023, 2.043], UNITS.m)

    assert np.allclose(d_2d, d_2d_ref)
    assert d_2d.unit == a_2d.unit

    # Let's try adding it the other way around
    e_2d = vector_2d + a_2d
    assert np.allclose(e_2d, d_2d_ref)
    assert e_2d.unit == a_2d.unit

    # Let's try subtracting a vector to a point now
    a_sub_vec_2d = a_2d - vector_2d
    a_sub_vec_2d_ref = Point2D([-977, -1957], UNITS.mm)
    assert np.allclose(a_sub_vec_2d, a_sub_vec_2d_ref)
    assert a_sub_vec_2d.unit == a_2d.unit

    # Let's try some errors when adding invalid objects to Vectors
    with pytest.raises(BeartypeCallHintParamViolation):
        vector_2d + "a"

    with pytest.raises(BeartypeCallHintParamViolation):
        vector_3d + "a"


def test_bounding_box_expands_and_evaluates_bounds_comparisons():
    bounding_box = BoundingBox2D()
    point1X = 1
    point1Y = 5
    point2X = -4
    point2Y = -2
    point3X = 7
    point3Y = 8
    point4X = -100
    point4Y = 100

    bounding_box.add_point_components(point1X, point1Y)
    assert 1 == bounding_box.x_min
    assert 1 == bounding_box.x_max
    assert 5 == bounding_box.y_min
    assert 5 == bounding_box.y_max

    bounding_box.add_point_components(point2X, point2Y)
    assert -4 == bounding_box.x_min
    assert 1 == bounding_box.x_max
    assert -2 == bounding_box.y_min
    assert 5 == bounding_box.y_max

    bounding_box.add_point_components(point3X, point3Y)
    assert -4 == bounding_box.x_min
    assert 7 == bounding_box.x_max
    assert -2 == bounding_box.y_min
    assert 8 == bounding_box.y_max

    bounding_box.add_point(Point2D([point4X, point4Y]))
    assert -100 == bounding_box.x_min
    assert 7 == bounding_box.x_max
    assert -2 == bounding_box.y_min
    assert 100 == bounding_box.y_max

    bounding_box2 = BoundingBox2D(0, 10, 0, 10)
    assert bounding_box2.contains_point_components(5, 5)
    assert not bounding_box2.contains_point_components(100, 100)
    assert bounding_box2.contains_point(Point2D([3, 4]))
    assert not bounding_box2.contains_point(Point2D([3, 14]))

    bounding_box2.add_points([Point2D([-100, -100]), Point2D([100, 100])])
    assert bounding_box2.contains_point(Point2D([100, -100]))
    assert bounding_box2.contains_point(Point2D([-100, 100]))

    copy_bbox_1 = BoundingBox2D(x_min=-100, x_max=7, y_min=-2, y_max=100)
    assert copy_bbox_1 == bounding_box
    assert copy_bbox_1 != bounding_box2


@pytest.mark.parametrize(
    "a,b_ref",
    [
        (Point2D([3, 4], UNITS.cm), Point2D([9, 12], UNITS.cm)),
        (Point3D([3, 4, 5], UNITS.cm), Point3D([9, 12, 15], UNITS.cm)),
    ],
)
def test_mult_operator_point(a, b_ref):
    """Testing the multiplication operator for Point objects."""

    b = 3 * a
    assert np.allclose(b, b_ref)
    assert b.unit
    assert a.unit.is_compatible_with(b.unit)
    assert a.unit.dimensionality == b.unit.dimensionality

    b_2 = a * 3
    assert np.allclose(b_2, b_ref)
    assert b_2.unit
    assert a.unit.is_compatible_with(b_2.unit)
    assert a.unit.dimensionality == b_2.unit.dimensionality


@pytest.mark.parametrize(
    "a,b_ref",
    [
        (Point2D([9, 12], UNITS.cm), Point2D([3, 4], UNITS.cm)),
        (Point3D([9, 12, 15], UNITS.cm), Point3D([3, 4, 5], UNITS.cm)),
    ],
)
def test_div_operator_point(a, b_ref):
    """Testing the division operator for Point objects."""

    b = a / 3
    assert np.allclose(b, b_ref)
    assert b.unit
    assert a.unit.is_compatible_with(b.unit)
    assert a.unit.dimensionality == b.unit.dimensionality
