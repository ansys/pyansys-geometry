from numpy import finfo as np_finfo
import pytest

from ansys.geometry.core import UNITS
from ansys.geometry.core.primitives import (
    Cylinder,
    Point2D,
    Point3D,
    UnitVector2D,
    UnitVector3D,
    Vector2D,
    Vector3D,
)

DOUBLE_EPS = np_finfo(float).eps


def test_point3d():
    """Simple test to create a ``Point3D``."""

    # Test the null Point3D
    p_null = Point3D()
    assert len(p_null) == 3
    assert all(x == None for x in p_null)
    p_null.unit = UNITS.cm
    p_null.x = 10
    p_null.y = 20
    p_null.z = 30
    assert p_null.x == 10
    assert p_null.y == 20
    assert p_null.z == 30
    assert p_null[0] == 0.1
    assert p_null[1] == 0.2
    assert p_null[2] == 0.3

    # Create two Point3D objects
    p_1 = Point3D([0, 1, 3])
    p_1_copy = Point3D([0, 1, 3])
    p_2 = Point3D([0, 4, 7])

    # Check that the equals operator works
    assert p_1 == p_1_copy
    assert p_1 != p_2

    # Check its X, Y, Z components
    assert p_1.x == 0
    assert p_1.y == 1
    assert p_1.z == 3

    # Check that the setter works properly in p_1_copy
    p_1_copy.x = 3
    p_1_copy.y = 3
    p_1_copy.z = 3

    # Check that the equals operator works (p_1 and p_1_copy should no longer be equal)
    assert p_1 != p_1_copy
    assert p_1 != p_2


def test_point2d():
    """Simple test to create a ``Point2D``."""

    # Test the null Point2D
    p_null = Point2D()
    assert len(p_null) == 2
    assert all(x == None for x in p_null)
    p_null.unit = UNITS.cm
    p_null.x = 10
    p_null.y = 20
    assert p_null.x == 10
    assert p_null.y == 20
    assert p_null[0] == 0.1
    assert p_null[1] == 0.2

    # Create two Point2D objects
    p_1 = Point2D([0, 1])
    p_1_copy = Point2D([0, 1])
    p_2 = Point2D([0, 4])

    # Check that the equals operator works
    assert p_1 == p_1_copy
    assert p_1 != p_2

    # Check its X, Y, Z components
    assert p_1.x == 0
    assert p_1.y == 1

    # Check that the setter works properly in p_1_copy
    p_1_copy.x = 3
    p_1_copy.y = 3

    # Check that the equals operator works (p_1 and p_1_copy should no longer be equal)
    assert p_1 != p_1_copy
    assert p_1 != p_2


def test_point3d_errors():
    """Testing multiple ``Point3D`` errors."""

    with pytest.raises(ValueError, match="Point3D must have three coordinates."):
        Point3D([1, 4])

    with pytest.raises(
        TypeError, match="The np.ndarray 'input' should contain float or integer values."
    ):
        Point3D(["a", "b", "c"])

    # Create a point
    point = Point3D([1, 4, 4])

    # Test setter error checks
    with pytest.raises(TypeError, match="The parameter 'x' should be a float or an integer value."):
        point.x = "a"

    with pytest.raises(TypeError, match="The parameter 'y' should be a float or an integer value."):
        point.y = "a"

    with pytest.raises(TypeError, match="The parameter 'z' should be a float or an integer value."):
        point.z = "a"

    # Build a Point2D and try to compare against it
    with pytest.raises(TypeError, match=f"Provided type {Point2D} is invalid"):
        point_2d = Point2D([1, 4])
        assert point == point_2d


def test_point2d_errors():
    """Testing multiple ``Point2D`` errors."""

    with pytest.raises(ValueError, match="Point2D must have two coordinates."):
        Point2D([1, 4, 4])

    with pytest.raises(
        TypeError, match="The np.ndarray 'input' should contain float or integer values."
    ):
        Point2D(["a", "b"])

    # Create a point
    point = Point2D([1, 4])

    # Test setter error checks
    with pytest.raises(TypeError, match="The parameter 'x' should be a float or an integer value."):
        point.x = "a"

    with pytest.raises(TypeError, match="The parameter 'y' should be a float or an integer value."):
        point.y = "a"

    # Build a Point3D and try to compare against it
    with pytest.raises(TypeError, match=f"Provided type {Point3D} is invalid"):
        point_3d = Point3D([1, 4, 4])
        assert point == point_3d


def test_vector3d():
    """Simple test to create a ``Vector3D``."""

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

    # Check the cross product value of v1 with v2
    v_cross = v1.cross(v2)
    assert v_cross.x == -5
    assert v_cross.y == 0
    assert v_cross.z == 0


def test_vector2d():
    """Simple test to create a ``Vector2D``."""

    # Create two Vector2D objects
    v_1 = Vector2D([2, 1])
    v_1_copy = Vector2D([2, 1])
    v_2 = Vector2D([0, 4])

    # Check that the equals operator works
    assert v_1 == v_1_copy
    assert v_1 != v_2

    # Check its X, Y components
    assert v_1.x == 2
    assert v_1.y == 1

    # Check that the setter works properly in v_1_copy
    v_1_copy.x = 3
    v_1_copy.y = 3

    # Check that the equals operator works (v_1 and v_1_copy should no longer be equal)
    assert v_1 != v_1_copy
    assert v_1 != v_2

    # Check the norm value of vector v1
    assert abs(round(v_1.norm, 3) - 2.236) <= DOUBLE_EPS

    v1_n = v_1.normalize()
    assert abs(round(v1_n.x, 3) - 0.894) <= DOUBLE_EPS
    assert abs(round(v1_n.y, 3) - 0.447) <= DOUBLE_EPS


def test_unit_vector_3d():
    """Simple test to create a ``UnitVector3D``."""

    # Create UnitVector3D objects from Vector3D
    v1 = Vector3D([0, 1, 3])
    v2 = UnitVector3D(v1)
    assert abs(round(v2.x, 3) - 0.0) <= DOUBLE_EPS
    assert abs(round(v2.y, 3) - 0.316) <= DOUBLE_EPS
    assert abs(round(v2.z, 3) - 0.949) <= DOUBLE_EPS

    # Create UnitVector3D objects from np.ndarray
    v3 = UnitVector3D([1, 2, 3])
    assert abs(round(v3.x, 3) - 0.267) <= DOUBLE_EPS
    assert abs(round(v3.y, 3) - 0.535) <= DOUBLE_EPS
    assert abs(round(v3.z, 3) - 0.802) <= DOUBLE_EPS


def test_unit_vector_2d():
    """Simple test to create a ``UnitVector2D``."""

    # Create UnitVector2D objects from Vector2D
    v1 = Vector2D([2, 1])
    v2 = UnitVector2D(v1)
    assert abs(round(v2.x, 3) - 0.894) <= DOUBLE_EPS
    assert abs(round(v2.y, 3) - 0.447) <= DOUBLE_EPS

    # Create UnitVector2D objects from np.ndarray
    v3 = UnitVector2D([2, 1])
    assert abs(round(v3.x, 3) - 0.894) <= DOUBLE_EPS
    assert abs(round(v3.y, 3) - 0.447) <= DOUBLE_EPS


def test_vector3d_errors():
    """Testing multiple ``Vector3D`` errors."""

    with pytest.raises(ValueError, match="Vector3D must have three coordinates."):
        Vector3D([1, 2])

    with pytest.raises(
        TypeError, match="The np.ndarray 'input' should contain float or integer values."
    ):
        Vector3D(["a", "b", "c"])

    # Create a Vector3D
    v1 = Vector3D([1, 2, 3])

    # Test setter error checks
    with pytest.raises(TypeError, match="The parameter 'x' should be a float or an integer value."):
        v1.x = "x"

    with pytest.raises(TypeError, match="The parameter 'y' should be a float or an integer value."):
        v1.y = "y"

    with pytest.raises(TypeError, match="The parameter 'z' should be a float or an integer value."):
        v1.z = "z"

    # Build a Vector2D and try to compare against it
    with pytest.raises(TypeError, match=f"Provided type {Vector2D} is invalid"):
        v2 = Vector2D([1, 2])
        assert v1 == v2

    # Try to normalize a 0-value vector
    with pytest.raises(ValueError, match="The norm of the Vector3D is not valid."):
        v2 = Vector3D([0, 0, 0])
        v2.normalize()


def test_vector2d_errors():
    """Testing multiple ``Vector2D`` errors."""

    with pytest.raises(ValueError, match="Vector2D must have two coordinates."):
        Vector2D([1])

    with pytest.raises(
        TypeError, match="The np.ndarray 'input' should contain float or integer values."
    ):
        Vector2D(["a", "b"])

    # Create a Vector2D
    v1 = Vector2D([1, 2])

    # Test setter error checks
    with pytest.raises(TypeError, match="The parameter 'x' should be a float or an integer value."):
        v1.x = "x"

    with pytest.raises(TypeError, match="The parameter 'y' should be a float or an integer value."):
        v1.y = "y"

    # Build a Vector3D and try to compare against it
    with pytest.raises(TypeError, match=f"Provided type {Vector3D} is invalid"):
        v2 = Vector3D([1, 5, 6])
        assert v1 == v2

    # Try to normalize a 0-value vector
    with pytest.raises(ValueError, match="The norm of the Vector2D is not valid."):
        v2 = Vector2D([0, 0])
        v2.normalize()


def test_point3D_units():
    """``Point3D`` units testing."""

    # Create a Point3D with some units
    p_cm_to_mm = Point3D([10, 20, 30], UNITS.cm)

    # Check that the units are correctly in place
    assert p_cm_to_mm.unit == UNITS.cm

    # Request for X, Y, Z and ensure they are in cm
    assert p_cm_to_mm.x == 10
    assert p_cm_to_mm.y == 20
    assert p_cm_to_mm.z == 30

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert p_cm_to_mm[0] == (p_cm_to_mm.x * p_cm_to_mm.unit).to_base_units().magnitude
    assert p_cm_to_mm[1] == (p_cm_to_mm.y * p_cm_to_mm.unit).to_base_units().magnitude
    assert p_cm_to_mm[2] == (p_cm_to_mm.z * p_cm_to_mm.unit).to_base_units().magnitude

    # Store the numpy array values
    (raw_x, raw_y, raw_z) = p_cm_to_mm[0:3]

    # Set unit to mm now... and check if the values changed
    p_cm_to_mm.unit = UNITS.mm
    assert p_cm_to_mm.x == 100
    assert p_cm_to_mm.y == 200
    assert p_cm_to_mm.z == 300

    # Check that the values are still the same in the array
    assert raw_x == p_cm_to_mm[0]
    assert raw_y == p_cm_to_mm[1]
    assert raw_z == p_cm_to_mm[2]

    # Now change the value of a X being in millimeters
    p_cm_to_mm.x = 20  # Basically 1/5 of original x
    assert not raw_x == p_cm_to_mm[0]
    assert raw_x == p_cm_to_mm[0] * 5

    # Now change the value of a Y being in millimeters
    p_cm_to_mm.y = 10  # Basically 1/20 of original y
    assert not raw_y == p_cm_to_mm[1]
    assert raw_y == p_cm_to_mm[1] * 20

    # Now change the value of a Z being in millimeters
    p_cm_to_mm.z = 30  # Basically 1/10 of original z
    assert not raw_z == p_cm_to_mm[2]
    assert raw_z == p_cm_to_mm[2] * 10


def test_point2D_units():
    """``Point2D`` units testing."""

    # Create a Point2D with some units
    p_cm_to_mm = Point2D([10, 20], UNITS.cm)

    # Check that the units are correctly in place
    assert p_cm_to_mm.unit == UNITS.cm

    # Request for X, Y, Z and ensure they are in cm
    assert p_cm_to_mm.x == 10
    assert p_cm_to_mm.y == 20

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert p_cm_to_mm[0] == (p_cm_to_mm.x * p_cm_to_mm.unit).to_base_units().magnitude
    assert p_cm_to_mm[1] == (p_cm_to_mm.y * p_cm_to_mm.unit).to_base_units().magnitude

    # Store the numpy array values
    (raw_x, raw_y) = p_cm_to_mm[0:2]

    # Set unit to mm now... and check if the values changed
    p_cm_to_mm.unit = UNITS.mm
    assert p_cm_to_mm.x == 100
    assert p_cm_to_mm.y == 200

    # Check that the values are still the same in the array
    assert raw_x == p_cm_to_mm[0]
    assert raw_y == p_cm_to_mm[1]

    # Now change the value of a X being in millimeters
    p_cm_to_mm.x = 20  # Basically 1/5 of original x
    assert not raw_x == p_cm_to_mm[0]
    assert raw_x == p_cm_to_mm[0] * 5

    # Now change the value of a Y being in millimeters
    p_cm_to_mm.y = 10  # Basically 1/20 of original y
    assert not raw_y == p_cm_to_mm[1]
    assert raw_y == p_cm_to_mm[1] * 20


def test_cylinder():
    """``Cylinder`` construction and equivalency."""

    # Create two Cylinder objects
    origin = Point3D([42, 99, 13])
    c_1 = Cylinder(origin, Vector3D([12, 31, 99]), Vector3D([25, 39, 82]), 100, 200)
    c_1_duplicate = Cylinder(origin, Vector3D([12, 31, 99]), Vector3D([25, 39, 82]), 100, 200)
    c_2 = Cylinder(Point3D([5, 8, 9]), Vector3D([55, 16, 73]), Vector3D([23, 67, 45]), 88, 76)

    # Check that the equals operator works
    assert c_1 == c_1_duplicate
    assert c_1 != c_2

    # Check cylinder definition
    assert c_1.origin.x == origin.x
    assert c_1.origin.y == origin.y
    assert c_1.origin.z == origin.z
    assert c_1.radius == 100
    assert c_1.height == 200


def test_cylinder_units():
    """``Cylinder`` units validation."""

    origin = Point3D([42, 99, 13])

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match="The pint.Unit provided as input should be a \[length\] Quantity.",
    ):
        Cylinder(origin, Vector3D([12, 31, 99]), Vector3D([25, 39, 82]), 100, 200, UNITS.celsius)

    # Create a Cylinder with radius and height in mm
    c_1 = Cylinder(origin, Vector3D([12, 31, 99]), Vector3D([25, 39, 82]), 100, 200, UNITS.mm)

    # Check that the units are correctly in place
    assert c_1.unit == UNITS.mm

    # Request for X, Y, Z and ensure they are in mm
    assert c_1.radius == 100
    assert c_1.height == 200

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert c_1._radius == (c_1.radius * c_1.unit).to_base_units().magnitude
    assert c_1._height == (c_1.height * c_1.unit).to_base_units().magnitude

    # Set unit to cm now... and check if the values changed
    c_1.unit = UNITS.cm
    assert c_1.radius == 10
    assert c_1.height == 20
