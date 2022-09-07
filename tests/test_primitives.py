import pytest

from ansys.geometry.core import UNITS
from ansys.geometry.core.math import Point3D, UnitVector3D
from ansys.geometry.core.primitives import Cylinder, Plane


def test_plane():
    """``Plane`` construction and equivalency."""

    origin = Point3D([42, 99, 13])
    p_1 = Plane(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]))
    p_1_duplicate = Plane(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]))
    p_2 = Plane(Point3D([5, 8, 9]), UnitVector3D([55, 16, 73]), UnitVector3D([23, 67, 45]))

    # Check that the equals operator works
    assert p_1 == p_1_duplicate
    assert p_1 != p_2

    # Check plane definition
    assert p_1.origin.x == origin.x
    assert p_1.origin.y == origin.y
    assert p_1.origin.z == origin.z

    with pytest.raises(TypeError, match=f"direction_x is invalid, type {UnitVector3D} expected."):
        Plane(origin, "A", UnitVector3D([25, 39, 82]))

    with pytest.raises(TypeError, match=f"direction_y is invalid, type {UnitVector3D} expected."):
        Plane(origin, UnitVector3D([12, 31, 99]), "A")


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
