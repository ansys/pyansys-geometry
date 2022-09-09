from io import UnsupportedOperation

import numpy as np
import pytest

from ansys.geometry.core.math import (
    UNIT_VECTOR_X,
    UNIT_VECTOR_Y,
    UNIT_VECTOR_Z,
    ZERO_VECTOR3D,
    Frame,
    Matrix,
    Matrix33,
    Matrix44,
    Plane,
    Point,
    QuantityVector,
    UnitVector,
    Vector,
)
from ansys.geometry.core.misc import UNITS

DOUBLE_EPS = np.finfo(float).eps


def test_point():
    """Simple test to create a ``Point``."""

    # Test the default Point
    p_default = Point()
    assert len(p_default) == 3
    assert all(x == np.Inf for x in p_default)
    assert p_default.is_3d
    assert not p_default.is_2d
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

    # Create two Point objects
    p_1 = Point([0, 1, 3], UNITS.cm)
    p_1_copy = Point([0, 1, 3], UNITS.cm)
    p_2 = Point([0, 4, 7], UNITS.cm)

    # Check that the equals operator works
    assert p_1 == p_1_copy
    assert p_1 != p_2

    # Check its X, Y, Z components
    assert p_1.x == 0 * UNITS.cm
    assert p_1.y == 1 * UNITS.cm
    assert p_1.z == 3 * UNITS.cm

    # Check that the setter works properly in p_1_copy
    p_1_copy.x = p_1_copy.y = p_1_copy.z = 3 * UNITS.cm

    # Check that the equals operator works (p_1 and p_1_copy should no longer be equal)
    assert p_1 != p_1_copy
    assert p_1 != p_2

    # Create a 2D Point
    point_2d = Point([1, 2], UNITS.cm)
    assert point_2d.x == 1 * UNITS.cm
    assert point_2d.y == 2 * UNITS.cm
    assert point_2d.unit == UNITS.cm
    _, base_unit = UNITS.get_base_units(UNITS.cm)
    assert point_2d.base_unit == base_unit
    assert point_2d.is_2d
    assert not point_2d.is_3d


def test_point_errors():
    """Testing multiple ``Point`` errors."""

    with pytest.raises(
        ValueError,
        match="Point class can only receive 2 or 3 arguments, creating a 2D or 3D point, respectively.",  # noqa: E501
    ):
        Point([1, 4, 3, 5])

    with pytest.raises(
        ValueError,
        match="Point class can only receive 2 or 3 arguments, creating a 2D or 3D point, respectively.",  # noqa: E501
    ):
        Point([1])

    with pytest.raises(
        TypeError, match="The numpy.ndarray 'input' should contain float or integer values."
    ):
        Point(["a", "b", "c"])

    # Create a point
    point = Point([1, 4, 4])

    # Test setter error checks
    with pytest.raises(TypeError, match="Provided type"):
        point.x = "a"

    with pytest.raises(TypeError, match="Provided type"):
        point.y = "a"

    with pytest.raises(TypeError, match="Provided type"):
        point.z = "a"

    with pytest.raises(
        TypeError, match=r"The pint.Unit provided as input should be a \[length\] quantity."
    ):
        point.z = 10 * UNITS.degrees

    # Build a 2D Point and try to compare against it
    point_2d = Point([1, 4])
    assert not point == point_2d

    with pytest.raises(ValueError, match="Instance is not 3D. Z component not accessible."):
        point_2d.z = 10 * UNITS.cm


def test_point_units():
    """``Point`` units testing."""

    # Create a Point with some units
    p_cm_to_mm = Point([10, 20, 30], UNITS.cm)

    # Check that the units are correctly in place
    assert p_cm_to_mm.unit == UNITS.cm

    # Request for X, Y, Z and ensure they are in cm
    assert p_cm_to_mm.x == 10 * UNITS.cm
    assert p_cm_to_mm.y == 20 * UNITS.cm
    assert p_cm_to_mm.z == 30 * UNITS.cm

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
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


def test_vector():
    """Simple test to create a ``Vector``."""

    # Define the tolerance for the QuantityVector tests
    TOLERANCE = 5e-15

    # Create two Vector objects
    v1 = Vector([0, 1, 3])
    v1_copy = Vector([0, 1, 3])
    v2 = Vector([0, 4, 7])

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

    # Check the cross product value of v1 with v2
    v_cross = v1.cross(v2)
    assert v_cross.x == -5
    assert v_cross.y == 0
    assert v_cross.z == 0

    assert Vector([1, 0, 0]).is_perpendicular_to(Vector([0, 1, 0]))
    assert Vector([1, 0, 0]).is_perpendicular_to(Vector([0, 0, 1]))
    assert not Vector([1, 0, 0]).is_perpendicular_to(Vector([1, 1, 1]))
    assert not Vector([1, 0, 0]).is_perpendicular_to(Vector([-1, 0, 0]))
    assert Vector([1, 1, 1]).is_perpendicular_to(Vector([0, -1, 1]))
    assert not Vector([0, 0, 0]).is_perpendicular_to(Vector([0, -1, 1]))
    assert not Vector([0, -1, 1]).is_perpendicular_to(Vector([0, 0, 0]))

    assert Vector([0, 0, 0]).is_zero
    assert not Vector([0, 1, 0]).is_zero

    # Check that the dot and cross product overload is fine
    assert abs(round(v1 * v2 - 25)) <= DOUBLE_EPS
    v_cross_overload = v1 % v2
    assert v_cross_overload == v_cross

    # Checking that scalar times vector also works
    v1_x_3 = Vector([0, 3, 9])
    assert all(
        [
            abs(round(v1_comp * 3 - v1_x_3_comp)) <= DOUBLE_EPS
            for v1_comp, v1_x_3_comp in zip(v1, v1_x_3)
        ]
    )

    # Create a 3D vector from 2 points
    point_a = Point([1, 2, 3])
    point_b = Point([1, 6, 3])
    vector_from_points = Vector.from_points(point_a, point_b)
    assert vector_from_points.x == 0
    assert vector_from_points.y == 4
    assert vector_from_points.z == 0

    # Create a 3D vector from 2 points
    point_a = Point([1, 2, 3], UNITS.mm)
    point_b = Point([1, 6, 3], UNITS.cm)
    vector_from_points = Vector.from_points(point_a, point_b)
    assert abs(vector_from_points.x - 0.009) <= DOUBLE_EPS
    assert abs(vector_from_points.y - 0.058) <= DOUBLE_EPS
    assert abs(vector_from_points.z - 0.027) <= DOUBLE_EPS

    # Create a 2D vector from 2 points
    point_a = Point([1, 2])
    point_b = Point([1, 6])
    vector_from_points = Vector.from_points(point_a, point_b)
    assert vector_from_points.x == 0
    assert vector_from_points.y == 4

    # Create a 2D vector from 2 points
    point_a = Point([1, 2], UNITS.mm)
    point_b = Point([1, 6], UNITS.cm)

    vector_from_points = Vector.from_points(point_a, point_b)
    assert abs(vector_from_points.x - 0.009) <= DOUBLE_EPS
    assert abs(vector_from_points.y - 0.058) <= DOUBLE_EPS


def test_unit_vector():
    """Simple test to create a ``UnitVector``."""

    # Create UnitVector objects from Vector
    v1 = Vector([0, 1, 3])
    v2 = UnitVector(v1)
    assert abs(round(v2.x, 3) - 0.0) <= DOUBLE_EPS
    assert abs(round(v2.y, 3) - 0.316) <= DOUBLE_EPS
    assert abs(round(v2.z, 3) - 0.949) <= DOUBLE_EPS

    # Create UnitVector objects from numpy.ndarray
    v3 = UnitVector([1, 2, 3])
    assert abs(round(v3.x, 3) - 0.267) <= DOUBLE_EPS
    assert abs(round(v3.y, 3) - 0.535) <= DOUBLE_EPS
    assert abs(round(v3.z, 3) - 0.802) <= DOUBLE_EPS

    assert not UnitVector([1, 1, 1]).is_perpendicular_to(UnitVector([1, 1, -1]))
    assert UnitVector([1, 1, 1]).is_perpendicular_to(UnitVector([0, -1, 1]))

    # Check that UnitVector2D is immutable
    with pytest.raises(UnsupportedOperation, match="UnitVector is immutable."):
        v2.x = 3
    with pytest.raises(UnsupportedOperation, match="UnitVector is immutable."):
        v2.y = 3
    with pytest.raises(UnsupportedOperation, match="UnitVector is immutable."):
        v2.z = 3


def test_quantity_vector():
    """Simple tests to create ``QuantityVector``."""

    # Define the tolerance for the QuantityVector tests
    TOLERANCE = 5e-15

    # Create QuantityVector from a Vector
    vec = Vector([1, 2, 3])
    quantity_vec = QuantityVector(vec, UNITS.mm)
    assert abs(quantity_vec.x.magnitude - vec.x) <= TOLERANCE
    assert abs(quantity_vec.y.magnitude - vec.y) <= TOLERANCE
    assert abs(quantity_vec.z.magnitude - vec.z) <= TOLERANCE
    assert quantity_vec.unit == UNITS.mm
    assert abs(quantity_vec.norm.magnitude - vec.norm) <= TOLERANCE
    _, base_unit = UNITS.get_base_units(UNITS.mm)
    assert quantity_vec.base_unit == base_unit

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert quantity_vec[0] == (quantity_vec.x).to_base_units().magnitude
    assert quantity_vec[1] == (quantity_vec.y).to_base_units().magnitude
    assert quantity_vec[2] == (quantity_vec.z).to_base_units().magnitude

    # Change the values using the setters
    vec_end_mm = Vector([70, 80, 90])
    vec_end_cm = Vector([7, 8, 9])
    quantity_vec.unit = UNITS.mm
    quantity_vec.x = 70 * quantity_vec.unit
    quantity_vec.y = 80 * quantity_vec.unit
    quantity_vec.z = 90 * quantity_vec.unit
    assert abs(quantity_vec.x.magnitude - vec_end_mm.x) <= TOLERANCE
    assert abs(quantity_vec.y.magnitude - vec_end_mm.y) <= TOLERANCE
    assert abs(quantity_vec.z.magnitude - vec_end_mm.z) <= TOLERANCE
    assert quantity_vec.unit == UNITS.mm
    assert abs(quantity_vec.norm.magnitude - vec_end_mm.norm) <= TOLERANCE
    assert quantity_vec[0] == (quantity_vec.x).to_base_units().magnitude
    assert quantity_vec[1] == (quantity_vec.y).to_base_units().magnitude
    assert quantity_vec[2] == (quantity_vec.z).to_base_units().magnitude

    # Change back to cm and check that the values are modified according to units
    quantity_vec.unit = UNITS.cm
    assert abs(quantity_vec.x.magnitude - vec_end_cm.x) <= TOLERANCE
    assert abs(quantity_vec.y.magnitude - vec_end_cm.y) <= TOLERANCE
    assert abs(quantity_vec.z.magnitude - vec_end_cm.z) <= TOLERANCE
    assert quantity_vec.unit == UNITS.cm

    # Check that two quantity vectors with the same input vector
    # and different units are not the same
    quantity_vec_cm = QuantityVector([1, 2, 3], UNITS.cm)
    quantity_vec_mm_eq = QuantityVector([10, 20, 30], UNITS.mm)
    quantity_vec_mm_ne = QuantityVector([1, 2, 3], UNITS.mm)
    assert quantity_vec_cm != quantity_vec_mm_ne
    assert quantity_vec_cm == quantity_vec_mm_eq

    # Let's do some vector operations with the below
    quantity_vec_a = QuantityVector([1, 2, 3], UNITS.cm)
    quantity_vec_b = QuantityVector([70, 0, 10], UNITS.mm)
    dot_a_b = quantity_vec_a * quantity_vec_b
    assert dot_a_b == 0.001

    cross_a_x_b = quantity_vec_a % quantity_vec_b  # Resulting vector: [2, 20, -14] cm
    cross_result = QuantityVector([2, 20, -14], UNITS.cm)
    assert abs(cross_a_x_b.x.magnitude - cross_result.x.to_base_units().magnitude) <= TOLERANCE
    assert abs(cross_a_x_b.y.magnitude - cross_result.y.to_base_units().magnitude) <= TOLERANCE
    assert abs(cross_a_x_b.z.magnitude - cross_result.z.to_base_units().magnitude) <= TOLERANCE
    assert cross_a_x_b.unit == UNITS.cm

    normalized_b = quantity_vec_b.normalize()
    vec_b_normalized = Vector([70, 0, 10]).normalize()
    assert abs(normalized_b.x - vec_b_normalized.x) <= TOLERANCE
    assert abs(normalized_b.y - vec_b_normalized.y) <= TOLERANCE
    assert abs(normalized_b.z - vec_b_normalized.z) <= TOLERANCE

    # Create a QuantityVector3D from 2 points
    point_a = Point([1, 2, 3], UNITS.cm)
    point_b = Point([1, 6, 3], UNITS.cm)
    quantity_vector_from_points = QuantityVector.from_points(point_a, point_b)
    assert abs(quantity_vector_from_points.x.m - (0 * UNITS.cm).to_base_units().m) <= TOLERANCE
    assert abs(quantity_vector_from_points.y.m - (4 * UNITS.cm).to_base_units().m) <= TOLERANCE
    assert abs(quantity_vector_from_points.z.m - (0 * UNITS.cm).to_base_units().m) <= TOLERANCE

    with pytest.raises(
        TypeError,
        match="Provided type <class 'numpy.ndarray'> is invalid",
    ):
        QuantityVector.from_points(np.array([2, 5, 8]), point_b)

    with pytest.raises(
        TypeError,
        match="Provided type <class 'numpy.ndarray'> is invalid",
    ):
        QuantityVector.from_points(point_a, np.array([2, 5, 8]))

    # Create a 2D QuantityVector from 2 points with same units
    point_a = Point([1, 2], UNITS.cm)
    point_b = Point([1, 6], UNITS.cm)
    quantity_vector_from_points = QuantityVector.from_points(point_a, point_b)
    assert abs(quantity_vector_from_points.x.m - (0 * UNITS.cm).to_base_units().m) <= TOLERANCE
    assert abs(quantity_vector_from_points.y.m - (4 * UNITS.cm).to_base_units().m) <= TOLERANCE
    assert quantity_vector_from_points.unit == point_a.base_unit

    # Create a 2D QuantityVector from 2 points with different units
    point_a = Point([1, 2], UNITS.dm)
    point_b = Point([1, 6], UNITS.cm)
    quantity_vector_from_points = QuantityVector.from_points(point_a, point_b)
    assert abs(quantity_vector_from_points.x.m - (-9 * UNITS.cm).to_base_units().m) <= TOLERANCE
    assert abs(quantity_vector_from_points.y.m - (-14 * UNITS.cm).to_base_units().m) <= TOLERANCE
    assert quantity_vector_from_points.unit == point_a.base_unit
    assert quantity_vector_from_points.is_2d

    with pytest.raises(
        TypeError,
        match="Provided type <class 'numpy.ndarray'> is invalid",
    ):
        QuantityVector.from_points(np.array([2, 5]), point_b)

    with pytest.raises(
        TypeError,
        match="Provided type <class 'numpy.ndarray'> is invalid",
    ):
        QuantityVector.from_points(point_a, np.array([2, 5]))


def test_vector_errors():
    """Testing multiple ``Vector`` errors."""

    with pytest.raises(
        ValueError,
        match="Vector class can only receive 2 or 3 arguments, creating a 2D or 3D vector, respectively.",  # noqa: E501
    ):
        Vector([1])

    with pytest.raises(
        ValueError,
        match="Vector class can only receive 2 or 3 arguments, creating a 2D or 3D vector, respectively.",  # noqa: E501
    ):
        Vector([1, 2, 3, 4])

    with pytest.raises(
        TypeError, match="The numpy.ndarray 'input' should contain float or integer values."
    ):
        Vector(["a", "b", "c"])

    # Create a Vector
    v1 = Vector([1, 2, 3])

    # Test setter error checks
    with pytest.raises(TypeError, match="The parameter 'x' should be a float or an integer value."):
        v1.x = "x"

    with pytest.raises(TypeError, match="The parameter 'y' should be a float or an integer value."):
        v1.y = "y"

    with pytest.raises(TypeError, match="The parameter 'z' should be a float or an integer value."):
        v1.z = "z"

    # Build a 2D Vector and try to compare against it
    v2 = Vector([1, 2])
    assert not v1 == v2

    # Try to normalize a 0-value vector
    with pytest.raises(ValueError, match="The norm of the Vector is not valid."):
        v2 = ZERO_VECTOR3D
        v2.normalize()

    # Having V1 and V2 - let's try to do a cross product
    v2 = Vector([1, 2])
    with pytest.raises(ValueError, match="Invalid Vector dimensions for cross product."):
        v1 % v2

    # Having V1 and V2 - let's try to do a dot product
    with pytest.raises(ValueError, match="Invalid Vector dimensions for dot product."):
        v1 * v2

    with pytest.raises(
        ValueError,
        match="Vector class can only receive 2 or 3 arguments, creating a 2D or 3D vector, respectively.",  # noqa: E501
    ):
        QuantityVector([1], UNITS.cm)

    with pytest.raises(
        ValueError,
        match="Vector class can only receive 2 or 3 arguments, creating a 2D or 3D vector, respectively.",  # noqa: E501
    ):
        QuantityVector([1, 2, 3, 4], UNITS.cm)

    with pytest.raises(
        ValueError,
        match="The norm of the Vector is not valid.",
    ):
        QuantityVector(ZERO_VECTOR3D, UNITS.cm).normalize()


def test_matrix():
    """Simple test to create a ``Matrix``."""

    # Create two matrix objects
    m_1 = Matrix([[2, 5], [0, 8]])
    m_1_copy = Matrix([[2, 5], [0, 8]])
    m_2 = Matrix([[3, 2, 0], [1, 3, 0], [0, 6, 4]])

    # Intiate a test matrix using numpy.ndarray
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


def test_matrix_errors():
    """Testing multiple ``Matrix`` errors."""

    with pytest.raises(
        TypeError, match="The numpy.ndarray provided should contain float or integer values."
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
    with pytest.raises(ValueError, match="The matrices dimensions 2 and 3 are not multipliable."):
        m_1 * m_2


def test_matrix_33():
    """Simple test to create a ``Matrix33``."""

    # Create a Matrix33 objects
    m_1 = Matrix33([[2, 0, 0], [0, 3, 0], [0, 0, 4]])

    # Create a null matrix, which is 3x3 identity matrix
    m_null = Matrix33()

    # Intiate a test matrix using numpy.ndarray
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

    with pytest.raises(ValueError) as val:
        Matrix33([[1, 2], [1, 6]])
        assert "Matrix33 should only be a 2D array of shape (3,3)." in str(val.value)

    # Build a Matrix44 and try to compare against it
    with pytest.raises(TypeError, match="Provided type"):
        m_2 = Matrix44([[2, 0, 0, 2], [0, 3, 0, 1], [0, 0, 4, 2], [0, 0, 4, 2]])
        assert m_1 == m_2


def test_matrix_44():
    """Simple test to create a ``Matrix44``."""

    # Create two Matrix44 objects
    m_1 = Matrix44([[2, 0, 0, 0], [0, 3, 0, 0], [0, 0, 4, 0], [0, 0, 0, 1]])

    # Create a null matrix, which is 4x4 identity matrix
    m_null = Matrix44()

    # Intiate a test matrix using numpy.ndarray
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

    # Check error with other than 4x4 matrix
    with pytest.raises(ValueError) as val:
        Matrix44([[1, 2], [1, 6]])
        assert "Matrix44 should only be a 2D array of shape (4,4)." in str(val.value)

    # Build a Matrix44 and try to compare against it
    with pytest.raises(TypeError, match="Provided type"):
        m_2 = Matrix33([[2, 0, 0], [0, 3, 0], [0, 0, 4]])
        assert m_1 == m_2


def test_frame():
    """``Frame`` construction and equivalency."""

    origin = Point([42, 99, 13])
    f_1 = Frame(origin, UnitVector([1, 0, 0]), UnitVector([0, 1, 0]))
    f_1_duplicate = Frame(origin, UnitVector([1, 0, 0]), UnitVector([0, 1, 0]))
    f_2 = Frame(Point([5, 8, 9]), UnitVector([1, 1, 1]), UnitVector([0, -1, 1]))
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
    assert f_defaults.direction_x == UNIT_VECTOR_X
    assert f_defaults.direction_y == UNIT_VECTOR_Y
    assert f_defaults.direction_z == UNIT_VECTOR_Z

    with pytest.raises(TypeError, match=f"Provided type {str} is invalid,"):
        Frame(origin, "A", UnitVector([25, 39, 82]))

    with pytest.raises(TypeError, match=f"Provided type {str} is invalid,"):
        Frame(origin, UnitVector([12, 31, 99]), "A")

    with pytest.raises(TypeError, match=f"Provided type {str} is invalid,"):
        Frame("A", UnitVector([12, 31, 99]), UnitVector([23, 67, 45]))


def test_plane():
    """``Plane`` construction and equivalency."""

    origin = Point([42, 99, 13])
    p_1 = Plane(origin, UnitVector([1, 0, 0]), UnitVector([0, 1, 0]))
    p_1_duplicate = Plane(origin, UnitVector([1, 0, 0]), UnitVector([0, 1, 0]))
    p_2 = Plane(Point([5, 8, 9]), UnitVector([1, 1, 1]), UnitVector([0, -1, 1]))
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
    assert p_defaults.direction_x == UNIT_VECTOR_X
    assert p_defaults.direction_y == UNIT_VECTOR_Y
    assert p_defaults.direction_z == UNIT_VECTOR_Z

    with pytest.raises(TypeError, match=f"Provided type {str} is invalid,"):
        Plane(origin, "A", UnitVector([25, 39, 82]))

    with pytest.raises(TypeError, match=f"Provided type {str} is invalid,"):
        Plane(origin, UnitVector([12, 31, 99]), "A")

    with pytest.raises(TypeError, match=f"Provided type {str} is invalid,"):
        Plane("A", UnitVector([12, 31, 99]), UnitVector([23, 67, 45]))
