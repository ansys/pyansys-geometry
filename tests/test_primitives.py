from beartype.roar import BeartypeCallHintParamViolation
import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core.math import (
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    UNITVECTOR3D_Z,
    Point3D,
    UnitVector3D,
    Vector3D,
)
from ansys.geometry.core.misc import UNITS, Accuracy, Distance
from ansys.geometry.core.primitives import Circle, Cone, Cylinder, Ellipse, Line, ParamUV, Sphere, Torus


def test_cylinder():
    """``Cylinder`` construction and equivalency."""

    # Create two Cylinder objects
    origin = Point3D([42, 99, 13])
    radius = 100
    height = 200
    c_1 = Cylinder(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), radius, height)
    c_1_duplicate = Cylinder(
        origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), radius, height
    )
    c_2 = Cylinder(
        Point3D([5, 8, 9]), UnitVector3D([55, 16, 73]), UnitVector3D([23, 67, 45]), 88, 76
    )
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

    c_1.origin = new_origin = Point3D([42, 88, 99])
    c_1.radius = new_radius = 1000
    c_1.height = new_height = 2000

    assert c_1.origin.x == new_origin.x
    assert c_1.origin.y == new_origin.y
    assert c_1.origin.z == new_origin.z
    assert c_1.radius == new_radius
    assert c_1.height == new_height

    with pytest.raises(BeartypeCallHintParamViolation):
        Cylinder(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), "A", 200)

    with pytest.raises(BeartypeCallHintParamViolation):
        Cylinder(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, "A")

    with pytest.raises(BeartypeCallHintParamViolation):
        c_1.radius = "A"

    with pytest.raises(BeartypeCallHintParamViolation):
        c_1.height = "A"

    with pytest.raises(BeartypeCallHintParamViolation):
        c_1.origin = "A"

    with pytest.raises(BeartypeCallHintParamViolation):
        Cylinder(origin, "A", UnitVector3D([25, 39, 82]), 100, 200)

    with pytest.raises(BeartypeCallHintParamViolation):
        Cylinder(origin, UnitVector3D([12, 31, 99]), "A", 100, 200)


def test_cylinder_units():
    """``Cylinder`` units validation."""

    origin = Point3D([42, 99, 13])
    radius = 100
    height = 200
    unit = UNITS.mm
    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as an input should be a \[length\] quantity.",
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
        match=r"The pint.Unit provided as an input should be a \[length\] quantity.",
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
    origin = Point3D([42, 99, 13])
    radius = Distance(100)
    s_1 = Sphere(origin, radius)
    s_1_duplicate = Sphere(origin, radius)
    s_2 = Sphere(Point3D([5, 8, 9]), radius)
    s_with_array_definitions = Sphere([5, 8, 9], radius)

    # Check that the equals operator works
    assert s_1 == s_1_duplicate
    assert s_1 != s_2
    assert s_2 == s_with_array_definitions

    # Check sphere definition
    assert s_1.origin.x == origin.x
    assert s_1.origin.y == origin.y
    assert s_1.origin.z == origin.z
    assert s_1.radius.m == 100
    assert s_1.radius.u == "meter"
    assert Accuracy.length_is_equal(s_1.surface_area.m, 1.25663706e5)
    assert Accuracy.length_is_equal(s_1.volume.m, 4.1887902e6)

    s_1.origin = new_origin = Point3D([42, 88, 99])

    assert s_1.origin.x == new_origin.x
    assert s_1.origin.y == new_origin.y
    assert s_1.origin.z == new_origin.z

    s_2.origin = new_origin
    assert s_1 == s_2

    with pytest.raises(BeartypeCallHintParamViolation):
        Sphere(origin, "A")

    with pytest.raises(BeartypeCallHintParamViolation):
        s_1.origin = "A"


def test_sphere_units():
    """``Sphere`` units validation."""

    origin = Point3D([42, 99, 13])
    radius = 100
    unit = UNITS.mm
    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as an input should be a \[length\] quantity.",
    ):
        Sphere(origin, Quantity(radius, UNITS.celsius))

    s_1 = Sphere(origin, Quantity(radius, unit))

    # Check that the units are correctly in place
    assert s_1.radius.u == unit

    # Request for radius and ensure in mm
    assert s_1.radius.m == radius

    # Set unit to cm now... and check if the values changed
    s_1._radius.unit = new_unit = UNITS.cm
    assert s_1.radius.m == UNITS.convert(radius, unit, new_unit)


def test_sphere_evaluation():
    origin = Point3D([0, 0, 0])
    radius = Distance(1)
    sphere = Sphere(origin, radius)
    eval = sphere.evaluate(ParamUV(0, 0))

    # Test base evaluation at (0, 0)
    assert eval.sphere == sphere
    assert np.allclose(eval.position(), Point3D([1, 0, 0]))
    assert np.allclose(eval.normal(), UnitVector3D([1, 0, 0]))
    assert np.allclose(eval.cylinder_normal(), Vector3D([1, 0, 0]))
    assert np.allclose(eval.cylinder_tangent(), Vector3D([0, 1, 0]))
    assert np.allclose(eval.u_derivative(), Vector3D([0, 1, 0]))
    assert np.allclose(eval.v_derivative(), Vector3D([0, 0, 1]))
    assert np.allclose(eval.uu_derivative(), Vector3D([-1, 0, 0]))
    assert np.allclose(eval.uv_derivative(), Vector3D([0, 0, 0]))
    assert np.allclose(eval.vv_derivative(), Vector3D([-1, 0, 0]))
    assert eval.min_curvature() == 1.0
    assert np.allclose(eval.min_curvature_direction(), Vector3D([0, -1, 0]))
    assert eval.max_curvature() == 1.0
    assert np.allclose(eval.max_curvature_direction(), Vector3D([0, 0, 1]))

    # Test evaluation by projecting a point onto the sphere
    eval2 = sphere.project_point(Point3D([1, 1, 1]))
    assert eval2.sphere == sphere
    assert np.allclose(eval2.position(), Point3D([0.57735027, 0.57735027, 0.57735027]))
    assert np.allclose(eval2.normal(), UnitVector3D([1, 1, 1]))
    assert np.allclose(eval2.u_derivative().normalize(), UnitVector3D([-1, 1, 0]))
    assert np.allclose(eval2.v_derivative().normalize(), UnitVector3D([-1, -1, 2]))


def test_cone():
    """``Cone`` construction and equivalency."""

    # Create two Cone objects
    origin = Point3D([42, 99, 13])
    radius = 100
    half_angle = 0.78539816
    c_1 = Cone(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), radius, half_angle)
    c_1_duplicate = Cone(
        origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), radius, half_angle
    )
    c_2 = Cone(Point3D([5, 8, 9]), UnitVector3D([55, 16, 73]), UnitVector3D([23, 67, 45]), 88, 0.65)
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

    c_1.origin = new_origin = Point3D([42, 88, 99])
    c_1.radius = new_radius = 1000
    c_1.half_angle = new_half_angle = 0.78539816

    assert c_1.origin.x == new_origin.x
    assert c_1.origin.y == new_origin.y
    assert c_1.origin.z == new_origin.z
    assert c_1.radius == new_radius
    assert c_1.half_angle == new_half_angle

    with pytest.raises(BeartypeCallHintParamViolation):
        Cone(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), "A", 200)

    with pytest.raises(BeartypeCallHintParamViolation):
        Cone(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, "A")

    with pytest.raises(BeartypeCallHintParamViolation):
        c_1.radius = "A"

    with pytest.raises(BeartypeCallHintParamViolation):
        c_1.half_angle = "A"

    with pytest.raises(BeartypeCallHintParamViolation):
        c_1.origin = "A"

    with pytest.raises(BeartypeCallHintParamViolation):
        Cone(origin, "A", UnitVector3D([25, 39, 82]), 100, 200)

    with pytest.raises(BeartypeCallHintParamViolation):
        Cone(origin, UnitVector3D([12, 31, 99]), "A", 100, 200)


def test_cone_units():
    """``Cone`` units validation."""

    origin = Point3D([42, 99, 13])
    radius = 100
    half_angle = 45
    unit_radius = UNITS.mm
    unit_angle = UNITS.degree
    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as an input should be a \[length\] quantity.",
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
        match="The pint.Unit provided as an input should be a dimensionless quantity.",
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
        match=r"The pint.Unit provided as an input should be a \[length\] quantity.",
    ):
        c_1.length_unit = UNITS.celsius

    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as an input should be a dimensionless quantity.",
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
    origin = Point3D([42, 99, 13])
    major_radius = 200
    minor_radius = 100
    t_1 = Torus(
        origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), major_radius, minor_radius
    )
    t_1_duplicate = Torus(
        origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), major_radius, minor_radius
    )
    t_2 = Torus(Point3D([5, 8, 9]), UnitVector3D([55, 16, 73]), UnitVector3D([23, 67, 45]), 88, 76)
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

    t_1.origin = new_origin = Point3D([42, 88, 99])
    assert t_1.origin.x == new_origin.x
    assert t_1.origin.y == new_origin.y
    assert t_1.origin.z == new_origin.z
    assert t_1.major_radius == new_major_radius
    assert t_1.minor_radius == new_minor_radius

    with pytest.raises(BeartypeCallHintParamViolation):
        Torus(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), "A", 200)

    with pytest.raises(BeartypeCallHintParamViolation):
        Torus(origin, UnitVector3D([12, 31, 99]), UnitVector3D([25, 39, 82]), 100, "A")

    with pytest.raises(BeartypeCallHintParamViolation):
        t_1.major_radius = "A"

    with pytest.raises(BeartypeCallHintParamViolation):
        t_1.minor_radius = "A"

    with pytest.raises(BeartypeCallHintParamViolation):
        t_1.origin = "A"

    with pytest.raises(BeartypeCallHintParamViolation):
        Torus(origin, "A", UnitVector3D([25, 39, 82]), 100, 200)

    with pytest.raises(BeartypeCallHintParamViolation):
        Torus(origin, UnitVector3D([12, 31, 99]), "A", 100, 200)


def test_torus_units():
    """``Torus`` units validation."""

    origin = Point3D([42, 99, 13])
    major_radius = 200
    minor_radius = 100
    unit = UNITS.mm

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as an input should be a \[length\] quantity.",
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
        match=r"The pint.Unit provided as an input should be a \[length\] quantity.",
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


def test_circle():
    """``Circle`` construction and equivalency."""
    origin = Point3D([0, 0, 0])
    radius = Distance(10)
    origin_circle = Circle(origin, radius)
    origin_duplicate_circle = Circle(origin, radius)
    bigger_circle = Circle(origin, Distance(20))
    tilted_circle = Circle(
        origin, radius, reference=UnitVector3D([1, 0, 1]), axis=UnitVector3D([-1, 2, 1])
    )

    # Test attributes
    assert origin_circle.origin.x == origin.x
    assert origin_circle.origin.y == origin.y
    assert origin_circle.origin.z == origin.z
    assert origin_circle.radius.m == 10
    assert origin_circle.dir_x == UNITVECTOR3D_X
    assert origin_circle.dir_y == UNITVECTOR3D_Y
    assert origin_circle.dir_z == UNITVECTOR3D_Z
    assert tilted_circle.dir_y == Vector3D([2, 2, -2]).normalize()

    # Test comparisons
    assert origin_circle == origin_duplicate_circle
    assert origin_circle.is_coincident_circle(origin_duplicate_circle)
    assert origin_circle != bigger_circle

    # Test expected errors
    with pytest.raises(ValueError):
        invalid_axis_circle = Circle(
            origin, radius, reference=UNITVECTOR3D_X, axis=UnitVector3D([1, 1, 1])
        )


def test_circle_evaluation():
    """``CircleEvaluation`` construction and equivalency."""
    origin = Point3D([0, 0, 0])
    radius = Distance(1)

    # Test evaluation at 0
    circle = Circle(origin, radius)
    eval = circle.evaluate(0)

    assert eval.circle == circle
    assert eval.position() == Point3D([1, 0, 0])
    assert eval.tangent() == UNITVECTOR3D_Y
    assert eval.first_derivative() == UNITVECTOR3D_Y
    assert eval.second_derivative() == UnitVector3D([-1, 0, 0])
    assert eval.curvature() == 1

    # Test evaluation at (.785) by projecting a point
    eval2 = circle.project_point(Point3D([1, 1, 0]))

    # TODO: enforce Accuracy in Point3D __eq__ ? want to be able to say:
    assert eval2.position() == Point3D([np.sqrt(2) / 2, np.sqrt(2) / 2, 0])
    assert eval2.tangent() == UnitVector3D([-np.sqrt(2) / 2, np.sqrt(2) / 2, 0])
    assert eval2.first_derivative() == UnitVector3D([-np.sqrt(2) / 2, np.sqrt(2) / 2, 0])
    assert eval2.second_derivative() == UnitVector3D([-np.sqrt(2) / 2, -np.sqrt(2) / 2, 0])
    assert eval2.curvature() == 1


def test_line():
    """``Line`` construction and equivalency."""

    origin = Point3D([0, 0, 0])
    direction = UnitVector3D([0.5, 0.5, 0])

    line = Line(origin, direction)
    line_duplicate = Line(origin, direction)
    coincident_line = Line(Point3D([-1, -1, 0]), direction)
    x_line = Line(origin, UNITVECTOR3D_X)
    opposite_x_line = Line(origin, UnitVector3D([-1, 0, 0]))

    # Test attributes
    assert line.origin.x == origin.x
    assert line.origin.y == origin.y
    assert line.origin.z == origin.z

    # Test comparisons
    assert line == line_duplicate
    assert line != x_line
    assert line.is_coincident_line(line_duplicate)
    assert line.is_coincident_line(coincident_line)
    assert x_line.is_opposite_line(opposite_x_line)


def test_line_evaluation():
    """``LineEvaluation`` construction and equivalency."""
    origin = Point3D([0, 0, 0])
    direction = UnitVector3D([0.5, 0.5, 0])

    # Test evaluation at 0
    line = Line(origin, direction)
    eval = line.evaluate(0)

    assert eval.line == line
    assert eval.position() == origin
    assert eval.tangent() == UnitVector3D([0.5, 0.5, 0])
    assert eval.first_derivative() == UnitVector3D([0.5, 0.5, 0])
    assert eval.second_derivative() == Vector3D([0, 0, 0])
    assert eval.curvature() == 0

    # Test evaluation at (.707) by projecting a point
    eval2 = line.project_point(Point3D([1, 0, 0]))

    # TODO: enforce Accuracy in Point3D __eq__ ? want to be able to say:
    # assert eval2.position() == Point3D([.5,.5,0])
    diff = Vector3D.from_points(eval2.position(), Point3D([0.5, 0.5, 0]))
    assert Accuracy.length_is_zero(diff.x)
    assert Accuracy.length_is_zero(diff.y)
    assert Accuracy.length_is_zero(diff.z)


def test_ellipse():
    """``Ellipse`` construction and equivalency."""
    origin = Point3D([0, 0, 0])
    major_radius = Distance(10)
    minor_radius = Distance(5)
    origin_ellipse = Ellipse(origin, major_radius, minor_radius)
    origin_duplicate_ellipse = Ellipse(origin, major_radius, minor_radius)
    bigger_ellipse = Ellipse(origin, Distance(20), Distance(10))
    tilted_ellipse = Ellipse(
        origin,
        major_radius,
        minor_radius,
        reference=UnitVector3D([1, 0, 1]),
        axis=UnitVector3D([-1, 2, 1]),
    )

    # Test attributes
    assert origin_ellipse.origin.x == origin.x
    assert origin_ellipse.origin.y == origin.y
    assert origin_ellipse.origin.z == origin.z
    assert origin_ellipse.major_radius.m == 10
    assert origin_ellipse.minor_radius.m == 5
    assert origin_ellipse.dir_x == UNITVECTOR3D_X
    assert origin_ellipse.dir_y == UNITVECTOR3D_Y
    assert origin_ellipse.dir_z == UNITVECTOR3D_Z
    assert tilted_ellipse.dir_y == Vector3D([2, 2, -2]).normalize()

    # Test comparisons
    assert origin_ellipse == origin_duplicate_ellipse
    assert origin_ellipse.is_coincident_ellipse(origin_duplicate_ellipse)
    assert origin_ellipse != bigger_ellipse

    # Test expected errors
    with pytest.raises(ValueError):
        invalid_axis = Ellipse(
            origin,
            major_radius,
            minor_radius,
            reference=UNITVECTOR3D_X,
            axis=UnitVector3D([1, 1, 1]),
        )


def test_ellipse_evaluation():
    """``EllipseEvaluation`` construction and equivalency."""
    origin = Point3D([0, 0, 0])
    major_radius = Distance(3)
    minor_radius = Distance(2)

    # Test evaluation at 0
    ellipse = Ellipse(origin, major_radius, minor_radius)
    eval = ellipse.evaluate(0)

    assert eval.ellipse == ellipse
    assert eval.position() == Point3D([3, 0, 0])
    assert eval.tangent() == UNITVECTOR3D_Y
    assert eval.first_derivative().normalize() == UNITVECTOR3D_Y
    assert eval.second_derivative().normalize() == UnitVector3D([-1, 0, 0])
    assert eval.curvature() == 0.75

    # Test evaluation at (t) by projecting a point
    eval2 = ellipse.project_point(Point3D([3, 3, 0]))

    # TODO: enforce Accuracy in Point3D __eq__ ? want to be able to say:
    diff = Vector3D.from_points(eval2.position(), Point3D([1.66410059, 1.66410059, 0]))
    assert Accuracy.length_is_zero(diff.x)
    assert Accuracy.length_is_zero(diff.y)
    assert Accuracy.length_is_zero(diff.z)

    # TODO: enforce Accuracy in Vector3D __eq__ ? want to be able to say:
    diff = Vector3D.from_points(eval2.tangent(), UnitVector3D([-0.91381155, 0.40613847, 0]))
    assert Accuracy.length_is_zero(diff.x)
    assert Accuracy.length_is_zero(diff.y)
    assert Accuracy.length_is_zero(diff.z)

    diff = Vector3D.from_points(
        eval2.first_derivative().normalize(), UnitVector3D([-0.91381155, 0.40613847, 0])
    )
    assert Accuracy.length_is_zero(diff.x)
    assert Accuracy.length_is_zero(diff.y)
    assert Accuracy.length_is_zero(diff.z)

    diff = Vector3D.from_points(
        eval2.second_derivative().normalize(), UnitVector3D([-np.sqrt(2) / 2, -np.sqrt(2) / 2, -0])
    )
    assert Accuracy.length_is_zero(diff.x)
    assert Accuracy.length_is_zero(diff.y)
    assert Accuracy.length_is_zero(diff.z)

    assert Accuracy.length_is_equal(eval2.curvature(), 0.31540327)
