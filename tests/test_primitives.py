import pytest

from ansys.geometry.core import UNITS
from ansys.geometry.core.math import Point3D, UnitVector3D
from ansys.geometry.core.primitives import Cone, Cylinder, Sphere, Torus


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

    c_1.origin = Point3D([42, 88, 99])
    c_1.radius = 1000
    c_1.height = 2000

    assert c_1.origin.x == 42
    assert c_1.origin.y == 88
    assert c_1.origin.z == 99
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

    # Request for radius/height and ensure they are in mm
    assert c_1.radius == 100
    assert c_1.height == 200

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert c_1._radius == (c_1.radius * c_1.unit).to_base_units().magnitude
    assert c_1._height == (c_1.height * c_1.unit).to_base_units().magnitude

    # Set unit to cm now... and check if the values changed
    c_1.unit = UNITS.cm
    assert c_1.radius == 10
    assert c_1.height == 20


def test_sphere():
    """``Sphere`` construction and equivalency."""

    # Create two Sphere objects
    origin = Point3D([42, 99, 13])
    s_1 = Sphere(origin, 100)
    s_1_duplicate = Sphere(origin, 100)
    s_2 = Sphere(Point3D([5, 8, 9]), 88)

    # Check that the equals operator works
    assert s_1 == s_1_duplicate
    assert s_1 != s_2

    # Check sphere definition
    assert s_1.origin.x == origin.x
    assert s_1.origin.y == origin.y
    assert s_1.origin.z == origin.z
    assert s_1.radius == 100

    s_1.origin = Point3D([42, 88, 99])
    s_1.radius = 1000

    assert s_1.origin.x == 42
    assert s_1.origin.y == 88
    assert s_1.origin.z == 99
    assert s_1.radius == 1000

    s_2.origin = Point3D([42, 88, 99])
    s_2.radius = 1000
    assert s_1 == s_2

    with pytest.raises(
        TypeError,
        match="The parameter 'radius' should be a float or an integer value.",
    ):
        Sphere(origin, "A")

    with pytest.raises(
        TypeError,
        match="The parameter 'radius' should be a float or an integer value.",
    ):
        s_1.radius = "A"


def test_sphere_units():
    """``Sphere`` units validation."""

    origin = Point3D([42, 99, 13])

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match="The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        Sphere(origin, 100, UNITS.celsius)

    s_1 = Sphere(origin, 100, UNITS.mm)

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match="The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        s_1.unit = UNITS.celsius

    # Check that the units are correctly in place
    assert s_1.unit == UNITS.mm

    # Request for radius and ensure in mm
    assert s_1.radius == 100

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert s_1._radius == (s_1.radius * s_1.unit).to_base_units().magnitude

    # Set unit to cm now... and check if the values changed
    s_1.unit = UNITS.cm
    assert s_1.radius == 10


def test_cone():
    """``Cone`` construction and equivalency."""

    # Create two Cone objects
    origin = Point3D([42, 99, 13])
    c_1 = Cone(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, 0.78539816)
    c_1_duplicate = Cone(
        origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, 0.78539816
    )
    c_2 = Cone(Point3D([5, 8, 9]), UnitVector3D([55, 16, 73]), UnitVector3D([23, 67, 45]), 88, 0.65)

    # Check that the equals operator works
    assert c_1 == c_1_duplicate
    assert c_1 != c_2

    # Check cone definition
    assert c_1.origin.x == origin.x
    assert c_1.origin.y == origin.y
    assert c_1.origin.z == origin.z
    assert c_1.radius == 100
    assert c_1.half_angle == 0.78539816

    c_1.origin = Point3D([42, 88, 99])
    c_1.radius = 1000
    c_1.half_angle = 0.78539816

    assert c_1.origin.x == 42
    assert c_1.origin.y == 88
    assert c_1.origin.z == 99
    assert c_1.radius == 1000
    assert c_1.half_angle == 0.78539816

    with pytest.raises(
        TypeError,
        match="The parameter 'radius' should be a float or an integer value.",
    ):
        Cone(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), "A", 200)

    with pytest.raises(
        TypeError,
        match="The parameter 'half_angle' should be a float or an integer value.",
    ):
        Cone(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, "A")

    with pytest.raises(
        TypeError,
        match="The parameter 'radius' should be a float or an integer value.",
    ):
        c_1.radius = "A"

    with pytest.raises(
        TypeError,
        match="The parameter 'half_angle' should be a float or an integer value.",
    ):
        c_1.half_angle = "A"

    with pytest.raises(TypeError, match=f"direction_x is invalid, type {UnitVector3D} expected."):
        Cone(origin, "A", UnitVector3D([25, 39, 82]), 100, 200)

    with pytest.raises(TypeError, match=f"direction_y is invalid, type {UnitVector3D} expected."):
        Cone(origin, UnitVector3D([12, 31, 99]), "A", 100, 200)


def test_cone_units():
    """``Cone`` units validation."""

    origin = Point3D([42, 99, 13])

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match="The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        Cone(
            origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, 200, UNITS.celsius
        )

    with pytest.raises(
        TypeError,
        match="The pint.Unit provided as input should be a dimensionless quantity.",
    ):
        Cone(
            origin,
            UnitVector3D([12, 31, 99]),
            UnitVector3D([25, 39, 82]),
            100,
            200,
            UNITS.mm,
            UNITS.celsius,
        )

    c_1 = Cone(
        origin,
        UnitVector3D([12, 31, 99]),
        UnitVector3D([25, 39, 82]),
        100,
        45,
        UNITS.mm,
        UNITS.degree,
    )

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match="The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        c_1.length_unit = UNITS.celsius

    with pytest.raises(
        TypeError,
        match="The pint.Unit provided as input should be a dimensionless quantity.",
    ):
        c_1.angle_unit = UNITS.celsius

    # Check that the units are correctly in place
    assert c_1.length_unit == UNITS.mm
    assert c_1.angle_unit == UNITS.degree

    # Request for radius and half angle are in expected units
    assert c_1.radius == 100
    assert c_1.half_angle == 45

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert c_1._radius == (c_1.radius * c_1.length_unit).to_base_units().magnitude
    assert c_1._half_angle == (c_1.half_angle * c_1.angle_unit).to_base_units().magnitude

    # Change units to and check if the values changed
    c_1.length_unit = UNITS.cm
    c_1.angle_unit = UNITS.radian
    assert c_1.radius == 10
    assert c_1.half_angle == 0.7853981633974483


def test_torus():
    """``Torus`` construction and equivalency."""

    # Create two Torus objects
    origin = Point3D([42, 99, 13])
    t_1 = Torus(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, 200)
    t_1_duplicate = Torus(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, 200)
    t_2 = Torus(Point3D([5, 8, 9]), UnitVector3D([55, 16, 73]), UnitVector3D([23, 67, 45]), 88, 76)

    # Check that the equals operator works
    assert t_1 == t_1_duplicate
    assert t_1 != t_2

    # Check cylinder definition
    assert t_1.origin.x == origin.x
    assert t_1.origin.y == origin.y
    assert t_1.origin.z == origin.z
    assert t_1.semi_major_radius == 100
    assert t_1.semi_minor_radius == 200

    t_1.semi_major_radius = 1000
    t_1.semi_minor_radius = 2000

    assert t_1.origin.x == origin.x
    assert t_1.origin.y == origin.y
    assert t_1.origin.z == origin.z
    assert t_1.semi_major_radius == 1000
    assert t_1.semi_minor_radius == 2000

    with pytest.raises(
        TypeError,
        match="The parameter 'semi_major_radius' should be a float or an integer value.",
    ):
        Torus(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), "A", 200)

    with pytest.raises(
        TypeError,
        match="The parameter 'semi_minor_radius' should be a float or an integer value.",
    ):
        Torus(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, "A")

    with pytest.raises(
        TypeError,
        match="The parameter 'semi_major_radius' should be a float or an integer value.",
    ):
        t_1.semi_major_radius = "A"

    with pytest.raises(
        TypeError,
        match="The parameter 'semi_minor_radius' should be a float or an integer value.",
    ):
        t_1.semi_minor_radius = "A"

    with pytest.raises(TypeError, match=f"direction_x is invalid, type {UnitVector3D} expected."):
        Torus(origin, "A", UnitVector3D([25, 39, 82]), 100, 200)

    with pytest.raises(TypeError, match=f"direction_y is invalid, type {UnitVector3D} expected."):
        Torus(origin, UnitVector3D([12, 31, 99]), "A", 100, 200)


def test_torus_units():
    """``Torus`` units validation."""

    origin = Point3D([42, 99, 13])

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match="The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        Torus(
            origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, 200, UNITS.celsius
        )

    t_1 = Torus(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, 200, UNITS.mm)

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match="The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        t_1.unit = UNITS.celsius

    # Check that the units are correctly in place
    assert t_1.unit == UNITS.mm

    # Request for radius/height and ensure they are in mm
    assert t_1.semi_major_radius == 100
    assert t_1.semi_minor_radius == 200

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert t_1._semi_major_radius == (t_1.semi_major_radius * t_1.unit).to_base_units().magnitude
    assert t_1._semi_minor_radius == (t_1.semi_minor_radius * t_1.unit).to_base_units().magnitude

    # Set unit to cm now... and check if the values changed
    t_1.unit = UNITS.cm
    assert t_1.semi_major_radius == 10
    assert t_1.semi_minor_radius == 20
