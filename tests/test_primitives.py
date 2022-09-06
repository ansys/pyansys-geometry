import pytest

from ansys.geometry.core import UNITS
from ansys.geometry.core.math import Point3D, UnitVector3D
from ansys.geometry.core.primitives import Cylinder


def test_cylinder():
    """``Cylinder`` construction and equivalency."""

    # Create two Cylinder objects
    origin = Point3D([42, 99, 13])
    c_1 = Cylinder(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, 200)
    c_1_duplicate = Cylinder(
        origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, 200
    )
    c_2 = Cylinder(
        Point3D([5, 8, 9]), UnitVector3D([55, 16, 73]), UnitVector3D([23, 67, 45]), 88, 76
    )

    # Check that the equals operator works
    assert c_1 == c_1_duplicate
    assert c_1 != c_2

    # Check cylinder definition
    assert c_1.origin.x == origin.x
    assert c_1.origin.y == origin.y
    assert c_1.origin.z == origin.z
    assert c_1.radius == 100
    assert c_1.height == 200

    c_1.radius = 1000
    c_1.height = 2000

    assert c_1.origin.x == origin.x
    assert c_1.origin.y == origin.y
    assert c_1.origin.z == origin.z
    assert c_1.radius == 1000
    assert c_1.height == 2000

    with pytest.raises(
        TypeError,
        match="The parameter 'radius' should be a float or an integer value.",
    ):
        Cylinder(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), "A", 200)

    with pytest.raises(
        TypeError,
        match="The parameter 'height' should be a float or an integer value.",
    ):
        Cylinder(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, "A")

    with pytest.raises(
        TypeError,
        match="The parameter 'radius' should be a float or an integer value.",
    ):
        c_1.radius = "A"

    with pytest.raises(
        TypeError,
        match="The parameter 'height' should be a float or an integer value.",
    ):
        c_1.height = "A"

    with pytest.raises(TypeError, match=f"direction_x is invalid, type {UnitVector3D} expected."):
        Cylinder(origin, "A", UnitVector3D([25, 39, 82]), 100, 200)

    with pytest.raises(TypeError, match=f"direction_y is invalid, type {UnitVector3D} expected."):
        Cylinder(origin, UnitVector3D([12, 31, 99]), "A", 100, 200)


def test_cylinder_units():
    """``Cylinder`` units validation."""

    origin = Point3D([42, 99, 13])

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match="The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        Cylinder(
            origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, 200, UNITS.celsius
        )

    c_1 = Cylinder(
        origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, 200, UNITS.mm
    )

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match="The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        c_1.unit = UNITS.celsius

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


def test_quantity_vector_3d():
    """Simple tests to create ``QuantityVector3D``."""

    # Define the tolerance for the QuantityVector3D tests
    TOLERANCE = 5e-15

    # Create QuantityVector3D from a Vector3D
    vec = Vector3D([1, 2, 3])
    quantity_vec = QuantityVector3D(vec, UNITS.mm)
    assert abs(quantity_vec.x - vec.x) <= TOLERANCE
    assert abs(quantity_vec.y - vec.y) <= TOLERANCE
    assert abs(quantity_vec.z - vec.z) <= TOLERANCE
    assert quantity_vec.unit == UNITS.mm
    assert abs(quantity_vec.norm - vec.norm) <= TOLERANCE

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert quantity_vec[0] == (quantity_vec.x * quantity_vec.unit).to_base_units().magnitude
    assert quantity_vec[1] == (quantity_vec.y * quantity_vec.unit).to_base_units().magnitude
    assert quantity_vec[2] == (quantity_vec.z * quantity_vec.unit).to_base_units().magnitude

    # Change the values using the setters
    vec_end_mm = Vector3D([70, 80, 90])
    vec_end_cm = Vector3D([7, 8, 9])
    quantity_vec.unit = UNITS.mm
    quantity_vec.x = 70
    quantity_vec.y = 80
    quantity_vec.z = 90
    assert abs(quantity_vec.x - vec_end_mm.x) <= TOLERANCE
    assert abs(quantity_vec.y - vec_end_mm.y) <= TOLERANCE
    assert abs(quantity_vec.z - vec_end_mm.z) <= TOLERANCE
    assert quantity_vec.unit == UNITS.mm
    assert abs(quantity_vec.norm - vec_end_mm.norm) <= TOLERANCE
    assert quantity_vec[0] == (quantity_vec.x * quantity_vec.unit).to_base_units().magnitude
    assert quantity_vec[1] == (quantity_vec.y * quantity_vec.unit).to_base_units().magnitude
    assert quantity_vec[2] == (quantity_vec.z * quantity_vec.unit).to_base_units().magnitude

    # Change back to cm and check that the values are modified according to units
    quantity_vec.unit = UNITS.cm
    assert abs(quantity_vec.x - vec_end_cm.x) <= TOLERANCE
    assert abs(quantity_vec.y - vec_end_cm.y) <= TOLERANCE
    assert abs(quantity_vec.z - vec_end_cm.z) <= TOLERANCE
    assert quantity_vec.unit == UNITS.cm

    # Check that two quantity vectors with the same input vector
    # and different units are not the same
    quantity_vec_cm = QuantityVector3D([1, 2, 3], UNITS.cm)
    quantity_vec_mm_eq = QuantityVector3D([10, 20, 30], UNITS.mm)
    quantity_vec_mm_ne = QuantityVector3D([1, 2, 3], UNITS.mm)
    assert quantity_vec_cm != quantity_vec_mm_ne
    assert quantity_vec_cm == quantity_vec_mm_eq

    # Let's do some vector operations with the below
    quantity_vec_a = QuantityVector3D([1, 2, 3], UNITS.cm)
    quantity_vec_b = QuantityVector3D([70, 0, 10], UNITS.mm)
    dot_a_b = quantity_vec_a * quantity_vec_b
    assert dot_a_b == 0.001

    cross_a_x_b = quantity_vec_a % quantity_vec_b  # Resulting vector: [2, 20, -14] cm
    assert abs(cross_a_x_b.x - 2) <= TOLERANCE
    assert abs(cross_a_x_b.y - 20) <= TOLERANCE
    assert abs(cross_a_x_b.z - (-14)) <= TOLERANCE
    assert cross_a_x_b.unit == UNITS.cm

    normalized_b = quantity_vec_b.normalize()
    vec_b_normalized = Vector3D([70, 0, 10]).normalize()
    assert abs(normalized_b.x - vec_b_normalized.x) <= TOLERANCE
    assert abs(normalized_b.y - vec_b_normalized.y) <= TOLERANCE
    assert abs(normalized_b.z - vec_b_normalized.z) <= TOLERANCE


def test_quantity_vector_2d():
    """Simple tests to create ``QuantityVector2D``."""

    # Define the tolerance for the QuantityVector2D tests
    TOLERANCE = 5e-15

    # Create QuantityVector2D from a Vector3D
    vec = Vector2D([1, 2])
    quantity_vec = QuantityVector2D(vec, UNITS.mm)
    assert abs(quantity_vec.x - vec.x) <= TOLERANCE
    assert abs(quantity_vec.y - vec.y) <= TOLERANCE
    assert quantity_vec.unit == UNITS.mm
    assert abs(quantity_vec.norm - vec.norm) <= TOLERANCE

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert quantity_vec[0] == (quantity_vec.x * quantity_vec.unit).to_base_units().magnitude
    assert quantity_vec[1] == (quantity_vec.y * quantity_vec.unit).to_base_units().magnitude

    # Change the values using the setters
    vec_end_mm = Vector2D([70, 80])
    vec_end_cm = Vector2D([7, 8])
    quantity_vec.unit = UNITS.mm
    quantity_vec.x = 70
    quantity_vec.y = 80
    assert abs(quantity_vec.x - vec_end_mm.x) <= TOLERANCE
    assert abs(quantity_vec.y - vec_end_mm.y) <= TOLERANCE
    assert quantity_vec.unit == UNITS.mm
    assert abs(quantity_vec.norm - vec_end_mm.norm) <= TOLERANCE
    assert quantity_vec[0] == (quantity_vec.x * quantity_vec.unit).to_base_units().magnitude
    assert quantity_vec[1] == (quantity_vec.y * quantity_vec.unit).to_base_units().magnitude

    # Change back to cm and check that the values are modified according to units
    quantity_vec.unit = UNITS.cm
    assert abs(quantity_vec.x - vec_end_cm.x) <= TOLERANCE
    assert abs(quantity_vec.y - vec_end_cm.y) <= TOLERANCE
    assert quantity_vec.unit == UNITS.cm

    # Check that two quantity vectors with the same input vector
    # and different units are not the same
    quantity_vec_cm = QuantityVector2D([1, 2], UNITS.cm)
    quantity_vec_mm_eq = QuantityVector2D([10, 20], UNITS.mm)
    quantity_vec_mm_ne = QuantityVector2D([1, 2], UNITS.mm)
    assert quantity_vec_cm != quantity_vec_mm_ne
    assert quantity_vec_cm == quantity_vec_mm_eq

    # Let's do some vector operations with the below
    quantity_vec_a = QuantityVector2D([1, 2], UNITS.cm)
    quantity_vec_b = QuantityVector2D([70, 10], UNITS.mm)
    dot_a_b = quantity_vec_a * quantity_vec_b
    assert round(dot_a_b, 4) == 0.0009

    normalized_b = quantity_vec_b.normalize()
    vec_b_normalized = Vector2D([70, 10]).normalize()
    assert abs(normalized_b.x - vec_b_normalized.x) <= TOLERANCE
    assert abs(normalized_b.y - vec_b_normalized.y) <= TOLERANCE
