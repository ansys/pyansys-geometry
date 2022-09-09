import pytest

from ansys.geometry.core.math import Point, UnitVector3D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.primitives import Cone, Cylinder, Sphere, Torus


def test_cylinder():
    """``Cylinder`` construction and equivalency."""

    # Create two Cylinder objects
    origin = Point([42, 99, 13])
    radius = 100
    height = 200
    c_1 = Cylinder(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), radius, height)
    c_1_duplicate = Cylinder(
        origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), radius, height
    )
    c_2 = Cylinder(Point([5, 8, 9]), UnitVector3D([55, 16, 73]), UnitVector3D([23, 67, 45]), 88, 76)
    c_with_array_definitions = Cylinder([5, 8, 9], [55, 16, 73], [23, 67, 45], 88, 76)

    # Check that the equals operator works
    assert c_1 == c_1_duplicate
    assert c_1 != c_2
    assert c_2 == c_with_array_definitions

    # Check cylinder definition
    assert c_1.origin.x == origin.x
    assert c_1.origin.y == origin.y
    assert c_1.origin.z == origin.z
    assert c_1.radius == radius
    assert c_1.height == height

    c_1.origin = new_origin = Point([42, 88, 99])
    c_1.radius = new_radius = 1000
    c_1.height = new_height = 2000

    assert c_1.origin.x == new_origin.x
    assert c_1.origin.y == new_origin.y
    assert c_1.origin.z == new_origin.z
    assert c_1.radius == new_radius
    assert c_1.height == new_height

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

    with pytest.raises(
        TypeError,
        match="origin is invalid, type",
    ):
        c_1.origin = "A"

    with pytest.raises(TypeError, match=f"Provided type {str} is invalid,"):
        Cylinder(origin, "A", UnitVector3D([25, 39, 82]), 100, 200)

    with pytest.raises(TypeError, match=f"Provided type {str} is invalid,"):
        Cylinder(origin, UnitVector3D([12, 31, 99]), "A", 100, 200)


def test_cylinder_units():
    """``Cylinder`` units validation."""

    origin = Point([42, 99, 13])
    radius = 100
    height = 200
    unit = UNITS.mm
    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        Cylinder(
            origin,
            UnitVector3D([12, 31, 99]),
            UnitVector3D([25, 39, 82]),
            radius,
            height,
            UNITS.celsius,
        )

    c_1 = Cylinder(
        origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), radius, height, unit
    )

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        c_1.unit = UNITS.celsius

    # Check that the units are correctly in place
    assert c_1.unit == unit

    # Request for radius/height and ensure they are in mm
    assert c_1.radius == radius
    assert c_1.height == height

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert c_1._radius == (c_1.radius * c_1.unit).to_base_units().magnitude
    assert c_1._height == (c_1.height * c_1.unit).to_base_units().magnitude

    # Set unit to cm now... and check if the values changed
    c_1.unit = new_unit = UNITS.cm
    assert c_1.radius == UNITS.convert(radius, unit, new_unit)
    assert c_1.height == UNITS.convert(height, unit, new_unit)


def test_sphere():
    """``Sphere`` construction and equivalency."""

    # Create two Sphere objects
    origin = Point([42, 99, 13])
    radius = 100
    s_1 = Sphere(origin, 100)
    s_1_duplicate = Sphere(origin, 100)
    s_2 = Sphere(Point([5, 8, 9]), 88)
    s_with_array_definitions = Sphere([5, 8, 9], 88)

    # Check that the equals operator works
    assert s_1 == s_1_duplicate
    assert s_1 != s_2
    assert s_2 == s_with_array_definitions

    # Check sphere definition
    assert s_1.origin.x == origin.x
    assert s_1.origin.y == origin.y
    assert s_1.origin.z == origin.z
    assert s_1.radius == radius

    s_1.origin = new_origin = Point([42, 88, 99])
    s_1.radius = new_radius = 1000

    assert s_1.origin.x == new_origin.x
    assert s_1.origin.y == new_origin.y
    assert s_1.origin.z == new_origin.z
    assert s_1.radius == new_radius

    s_2.origin = new_origin
    s_2.radius = new_radius
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

    with pytest.raises(
        TypeError,
        match="origin is invalid, type",
    ):
        s_1.origin = "A"


def test_sphere_units():
    """``Sphere`` units validation."""

    origin = Point([42, 99, 13])
    radius = 100
    unit = UNITS.mm
    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        Sphere(origin, radius, UNITS.celsius)

    s_1 = Sphere(origin, radius, unit)

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        s_1.unit = UNITS.celsius

    # Check that the units are correctly in place
    assert s_1.unit == unit

    # Request for radius and ensure in mm
    assert s_1.radius == radius

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert s_1._radius == (s_1.radius * s_1.unit).to_base_units().magnitude

    # Set unit to cm now... and check if the values changed
    s_1.unit = new_unit = UNITS.cm
    assert s_1.radius == UNITS.convert(radius, unit, new_unit)


def test_cone():
    """``Cone`` construction and equivalency."""

    # Create two Cone objects
    origin = Point([42, 99, 13])
    radius = 100
    half_angle = 0.78539816
    c_1 = Cone(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), radius, half_angle)
    c_1_duplicate = Cone(
        origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), radius, half_angle
    )
    c_2 = Cone(Point([5, 8, 9]), UnitVector3D([55, 16, 73]), UnitVector3D([23, 67, 45]), 88, 0.65)
    c_with_array_definitions = Cone([5, 8, 9], [55, 16, 73], [23, 67, 45], 88, 0.65)

    # Check that the equals operator works
    assert c_1 == c_1_duplicate
    assert c_1 != c_2
    assert c_2 == c_with_array_definitions

    # Check cone definition
    assert c_1.origin.x == origin.x
    assert c_1.origin.y == origin.y
    assert c_1.origin.z == origin.z
    assert c_1.radius == radius
    assert c_1.half_angle == half_angle

    c_1.origin = new_origin = Point([42, 88, 99])
    c_1.radius = new_radius = 1000
    c_1.half_angle = new_half_angle = 0.78539816

    assert c_1.origin.x == new_origin.x
    assert c_1.origin.y == new_origin.y
    assert c_1.origin.z == new_origin.z
    assert c_1.radius == new_radius
    assert c_1.half_angle == new_half_angle

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

    with pytest.raises(
        TypeError,
        match="origin is invalid, type",
    ):
        c_1.origin = "A"

    with pytest.raises(TypeError, match=f"Provided type {str} is invalid,"):
        Cone(origin, "A", UnitVector3D([25, 39, 82]), 100, 200)

    with pytest.raises(TypeError, match=f"Provided type {str} is invalid,"):
        Cone(origin, UnitVector3D([12, 31, 99]), "A", 100, 200)


def test_cone_units():
    """``Cone`` units validation."""

    origin = Point([42, 99, 13])
    radius = 100
    half_angle = 45
    unit_radius = UNITS.mm
    unit_angle = UNITS.degree
    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        Cone(
            origin,
            UnitVector3D([12, 31, 99]),
            UnitVector3D([25, 39, 82]),
            radius,
            half_angle,
            UNITS.celsius,
        )

    with pytest.raises(
        TypeError,
        match="The pint.Unit provided as input should be a dimensionless quantity.",
    ):
        Cone(
            origin,
            UnitVector3D([12, 31, 99]),
            UnitVector3D([25, 39, 82]),
            radius,
            half_angle,
            unit_radius,
            UNITS.celsius,
        )

    c_1 = Cone(
        origin,
        UnitVector3D([12, 31, 99]),
        UnitVector3D([25, 39, 82]),
        radius,
        half_angle,
        unit_radius,
        unit_angle,
    )

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        c_1.length_unit = UNITS.celsius

    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as input should be a dimensionless quantity.",
    ):
        c_1.angle_unit = UNITS.celsius

    # Check that the units are correctly in place
    assert c_1.length_unit == unit_radius
    assert c_1.angle_unit == unit_angle

    # Request for radius and half angle are in expected units
    assert c_1.radius == radius
    assert c_1.half_angle == half_angle

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert c_1._radius == (c_1.radius * c_1.length_unit).to_base_units().magnitude
    assert c_1._half_angle == (c_1.half_angle * c_1.angle_unit).to_base_units().magnitude

    # Change units to and check if the values changed
    c_1.length_unit = new_unit_radius = UNITS.cm
    c_1.angle_unit = new_unit_angle = UNITS.radian
    assert c_1.radius == UNITS.convert(radius, unit_radius, new_unit_radius)
    assert c_1.half_angle == UNITS.convert(half_angle, unit_angle, new_unit_angle)


def test_torus():
    """``Torus`` construction and equivalency."""

    # Create two Torus objects
    origin = Point([42, 99, 13])
    major_radius = 200
    minor_radius = 100
    t_1 = Torus(
        origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), major_radius, minor_radius
    )
    t_1_duplicate = Torus(
        origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), major_radius, minor_radius
    )
    t_2 = Torus(Point([5, 8, 9]), UnitVector3D([55, 16, 73]), UnitVector3D([23, 67, 45]), 88, 76)
    t_with_array_definitions = Torus([5, 8, 9], [55, 16, 73], [23, 67, 45], 88, 76)

    # Check that the equals operator works
    assert t_1 == t_1_duplicate
    assert t_1 != t_2
    assert t_2 == t_with_array_definitions

    # Check cylinder definition
    assert t_1.origin.x == origin.x
    assert t_1.origin.y == origin.y
    assert t_1.origin.z == origin.z
    assert t_1.major_radius == major_radius
    assert t_1.minor_radius == minor_radius

    t_1.major_radius = new_major_radius = 2000
    t_1.minor_radius = new_minor_radius = 1000

    assert t_1.origin.x == origin.x
    assert t_1.origin.y == origin.y
    assert t_1.origin.z == origin.z
    assert t_1.major_radius == new_major_radius
    assert t_1.minor_radius == new_minor_radius

    t_1.origin = new_origin = Point([42, 88, 99])
    assert t_1.origin.x == new_origin.x
    assert t_1.origin.y == new_origin.y
    assert t_1.origin.z == new_origin.z
    assert t_1.major_radius == new_major_radius
    assert t_1.minor_radius == new_minor_radius

    with pytest.raises(
        TypeError,
        match="The parameter 'major_radius' should be a float or an integer value.",
    ):
        Torus(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), "A", 200)

    with pytest.raises(
        TypeError,
        match="The parameter 'minor_radius' should be a float or an integer value.",
    ):
        Torus(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, "A")

    with pytest.raises(
        TypeError,
        match="The parameter 'major_radius' should be a float or an integer value.",
    ):
        t_1.major_radius = "A"

    with pytest.raises(
        TypeError,
        match="The parameter 'minor_radius' should be a float or an integer value.",
    ):
        t_1.minor_radius = "A"

    with pytest.raises(
        TypeError,
        match="origin is invalid, type",
    ):
        t_1.origin = "A"

    with pytest.raises(TypeError, match=f"Provided type {str} is invalid,"):
        Torus(origin, "A", UnitVector3D([25, 39, 82]), 100, 200)

    with pytest.raises(TypeError, match=f"Provided type {str} is invalid,"):
        Torus(origin, UnitVector3D([12, 31, 99]), "A", 100, 200)


def test_torus_units():
    """``Torus`` units validation."""

    origin = Point([42, 99, 13])
    major_radius = 200
    minor_radius = 100
    unit = UNITS.mm

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        Torus(
            origin,
            UnitVector3D([12, 31, 99]),
            UnitVector3D([25, 39, 82]),
            major_radius,
            minor_radius,
            UNITS.celsius,
        )

    t_1 = Torus(
        origin,
        UnitVector3D([12, 31, 99]),
        UnitVector3D([25, 39, 82]),
        major_radius,
        minor_radius,
        unit,
    )

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as input should be a \[length\] quantity.",
    ):
        t_1.unit = UNITS.celsius

    # Check that the units are correctly in place
    assert t_1.unit == unit

    # Request for radius/height and ensure they are in mm
    assert t_1.major_radius == major_radius
    assert t_1.minor_radius == minor_radius

    # Check that the actual values are in base units (i.e. UNIT_LENGTH)
    assert t_1._major_radius == (t_1.major_radius * t_1.unit).to_base_units().magnitude
    assert t_1._minor_radius == (t_1.minor_radius * t_1.unit).to_base_units().magnitude

    # Set unit to cm now... and check if the values changed
    t_1.unit = new_unit = UNITS.cm
    assert t_1.major_radius == UNITS.convert(major_radius, unit, new_unit)
    assert t_1.minor_radius == UNITS.convert(minor_radius, unit, new_unit)
    assert t_1.unit == new_unit
