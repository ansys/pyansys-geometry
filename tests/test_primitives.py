# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from beartype.roar import BeartypeCallHintParamViolation
import geomdl
import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core.math import (
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    UNITVECTOR3D_Z,
    Matrix44,
    Point3D,
    UnitVector3D,
    Vector3D,
)
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Accuracy, Distance
from ansys.geometry.core.shapes import (
    Circle,
    Cone,
    Cylinder,
    Ellipse,
    Line,
    NURBSCurve,
    ParamUV,
    Sphere,
    Torus,
)
from ansys.geometry.core.shapes.parameterization import (
    Parameterization,
    ParamForm,
    ParamType,
)
from ansys.geometry.core.shapes.surfaces.nurbs import NURBSSurface, NURBSSurfaceEvaluation
from ansys.geometry.core.shapes.surfaces.sphere import SphereEvaluation


def test_cylinder():
    """``Cylinder`` construction and equivalency."""
    # Create two Cylinder objects
    origin = Point3D([0, 0, 0])
    radius = 1
    c_1 = Cylinder(origin, radius)
    duplicate = Cylinder(origin, radius)
    c_2 = Cylinder(origin, 2)

    # Check that the equals operator works
    assert c_1 == duplicate
    assert c_1 != c_2

    # Check cylinder definition
    assert c_1.origin.x == origin.x
    assert c_1.origin.y == origin.y
    assert c_1.origin.z == origin.z
    assert c_1.radius.m == radius
    assert c_1.radius.u == "meter"
    assert isinstance(c_1.radius, Quantity)
    assert np.allclose(c_1.dir_x, UNITVECTOR3D_X)
    assert np.allclose(c_1.dir_y, UNITVECTOR3D_Y)
    assert np.allclose(c_1.dir_z, UNITVECTOR3D_Z)

    assert Accuracy.length_is_equal(c_1.surface_area(1).m, 12.5663706)
    assert c_1.surface_area(1).u == "meter ** 2"
    assert isinstance(c_1.surface_area(1), Quantity)
    assert Accuracy.length_is_equal(c_1.volume(1).m, 3.14159265)
    assert c_1.volume(1).u == "meter ** 3"
    assert isinstance(c_1.volume(1), Quantity)

    with pytest.raises(BeartypeCallHintParamViolation):
        Cylinder(origin, "A")

    with pytest.raises(BeartypeCallHintParamViolation):
        Cylinder(origin, 100, "A", UnitVector3D([25, 39, 82]))

    with pytest.raises(BeartypeCallHintParamViolation):
        Cylinder(origin, 100, UnitVector3D([12, 31, 99]), "A")

    with pytest.raises(ValueError):
        Cylinder(origin, 1, UnitVector3D([1, 0, 0]), UnitVector3D([1, 1, 1]))

    origin = Point3D([42, 99, 13])
    radius = 200
    cylinder_2 = Cylinder(
        origin,
        radius,
        UnitVector3D([12, 31, 99]),
        UnitVector3D([0, 99, -31]),
    )
    rotation_matrix = Matrix44([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    cylinder_transformation = cylinder_2.transformed_copy(matrix=rotation_matrix)
    assert np.allclose(cylinder_transformation._origin, Point3D([-99, 42, 13]))
    assert np.allclose(cylinder_transformation._reference, UnitVector3D([-31, 12, 99]))
    assert np.allclose(cylinder_transformation._axis, UnitVector3D([-99, 0, -31]))
    cylinder_mirror = cylinder_2.mirrored_copy()
    assert np.allclose(cylinder_mirror._origin, Point3D([42, 99, 13]))
    assert np.allclose(
        cylinder_mirror._reference, UnitVector3D([-0.11490753, -0.29684446, -0.94798714])
    )
    assert np.allclose(cylinder_mirror._axis, UnitVector3D([0, -0.9543083, 0.29882381]))


def test_cylinder_units():
    """``Cylinder`` units validation."""
    origin = Point3D([42, 99, 13])
    radius = 100
    unit = UNITS.mm

    c_1 = Cylinder(origin, Quantity(radius, unit))

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as an input should be a \[length\] quantity.",
    ):
        Cylinder(origin, Quantity(radius, UNITS.celsius))

    # Check that the units are correctly in place
    assert c_1.radius.u == unit

    # Request for radius/height and ensure they are in mm
    assert c_1.radius == Quantity(radius, unit)

    # Set unit to cm now... and check if the values changed
    c_1._radius.unit = new_unit = UNITS.cm
    assert c_1.radius.m == UNITS.convert(radius, unit, new_unit)


def test_cylinder_evaluation():
    origin = Point3D([0, 0, 0])
    radius = 1
    cylinder = Cylinder(origin, radius)

    eval = cylinder.evaluate(ParamUV(0, 0))

    # with pytest.raises(AttributeError, match="can't set attribute"):
    #    eval.cylinder = Cylinder()
    # Test base evaluation at (0, 0)
    assert eval.cylinder == cylinder
    with pytest.raises(AttributeError):
        eval.cylinder = Cylinder(Point3D([0, 0, 0]), 3)
        eval.parameter = ParamUV(np.pi / 2, np.pi / 2)
    assert np.allclose(eval.position, Point3D([1, 0, 0]))
    assert isinstance(eval.position, Point3D)
    assert np.allclose(eval.normal, UnitVector3D([1, 0, 0]))
    assert isinstance(eval.normal, UnitVector3D)
    assert np.allclose(eval.u_derivative, Vector3D([0, 1, 0]))
    assert isinstance(eval.u_derivative, Vector3D)
    assert np.allclose(eval.v_derivative, Vector3D([0, 0, 1]))
    assert isinstance(eval.v_derivative, Vector3D)
    assert np.allclose(eval.uu_derivative, Vector3D([-1, 0, 0]))
    assert isinstance(eval.uu_derivative, Vector3D)
    assert np.allclose(eval.uv_derivative, Vector3D([0, 0, 0]))
    assert isinstance(eval.uv_derivative, Vector3D)
    assert np.allclose(eval.vv_derivative, Vector3D([0, 0, 0]))
    assert isinstance(eval.vv_derivative, Vector3D)
    assert eval.min_curvature == 0
    assert np.allclose(eval.min_curvature_direction, UnitVector3D([0, 0, 1]))
    assert isinstance(eval.min_curvature_direction, UnitVector3D)
    assert eval.max_curvature == 1.0
    assert np.allclose(eval.max_curvature_direction, UnitVector3D([0, 1, 0]))
    assert isinstance(eval.max_curvature_direction, UnitVector3D)

    # # Test evaluation by projecting a point onto the cylinder
    eval2 = cylinder.project_point(Point3D([3, 3, 3]))
    assert eval2.cylinder == cylinder
    assert np.allclose(eval2.position, Point3D([0.70710678, 0.70710678, 3]))
    assert np.allclose(eval2.normal, UnitVector3D([1, 1, 0]))
    assert np.allclose(eval2.u_derivative.normalize(), UnitVector3D([-1, 1, 0]))
    assert np.allclose(eval2.v_derivative, Vector3D([0, 0, 1]))


def test_cylinder_radius_not_positive():
    """Test that a ValueError is raised when the radius is not positive."""
    origin = Point3D([0, 0, 0])
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Test with zero radius
    with pytest.raises(ValueError, match="Radius must be a real positive value."):
        Cylinder(origin, 0, reference, axis)

    # Test with negative radius
    with pytest.raises(ValueError, match="Radius must be a real positive value."):
        Cylinder(origin, -5, reference, axis)


def test_cylinder_surface_area_height_not_positive():
    """Test that a ValueError is raised when the height is not positive in surface_area."""
    origin = Point3D([0, 0, 0])
    radius = 10.0
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a cylinder instance
    cylinder = Cylinder(origin, radius, reference, axis)

    # Test with zero height
    with pytest.raises(ValueError, match="Height must be a real positive value."):
        cylinder.surface_area(0)

    # Test with negative height
    with pytest.raises(ValueError, match="Height must be a real positive value."):
        cylinder.surface_area(-5)


def test_cylinder_volume_height_not_positive():
    """Test that a ValueError is raised when the height is not positive in volume."""
    origin = Point3D([0, 0, 0])
    radius = 10.0
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a cylinder instance
    cylinder = Cylinder(origin, radius, reference, axis)

    # Test with zero height
    with pytest.raises(ValueError, match="Height must be a real positive value."):
        cylinder.volume(0)

    # Test with negative height
    with pytest.raises(ValueError, match="Height must be a real positive value."):
        cylinder.volume(-5)


def test_cylinder_parameterization():
    """Test the parameterization method of the Cylinder class."""
    # Define valid inputs for the cylinder
    origin = Point3D([0, 0, 0])
    radius = 10.0
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a cylinder instance
    cylinder = Cylinder(origin, radius, reference, axis)

    # Call the parameterization method
    u, v = cylinder.parameterization()

    # Validate the u parameterization
    assert isinstance(u, Parameterization)
    assert u.form == ParamForm.PERIODIC
    assert u.type == ParamType.CIRCULAR
    assert u.interval.start == 0
    assert u.interval.end == 2 * np.pi

    # Validate the v parameterization
    assert isinstance(v, Parameterization)
    assert v.form == ParamForm.OPEN
    assert v.type == ParamType.LINEAR
    assert v.interval.start == -np.inf
    assert v.interval.end == np.inf


def test_cylinder_contains_param_not_implemented():
    """Test that contains_param raises NotImplementedError."""
    # Define valid inputs for the cylinder
    origin = Point3D([0, 0, 0])
    radius = 10.0
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a cylinder instance
    cylinder = Cylinder(origin, radius, reference, axis)

    # Define a parameter
    param_uv = ParamUV(0.5, 0.5)

    # Assert that contains_param raises NotImplementedError
    with pytest.raises(NotImplementedError, match="contains_param\\(\\) is not implemented."):
        cylinder.contains_param(param_uv)


def test_cylinder_contains_point_not_implemented():
    """Test that contains_point raises NotImplementedError."""
    # Define valid inputs for the cylinder
    origin = Point3D([0, 0, 0])
    radius = 10.0
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a cylinder instance
    cylinder = Cylinder(origin, radius, reference, axis)

    # Define a point
    point = Point3D([5, 5, 5])

    # Assert that contains_point raises NotImplementedError
    with pytest.raises(NotImplementedError, match="contains_point\\(\\) is not implemented."):
        cylinder.contains_point(point)


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

    with pytest.raises(BeartypeCallHintParamViolation):
        Sphere(origin, "A")

    origin = Point3D([42, 99, 13])
    radius = 200
    sphere_2 = Sphere(
        origin,
        radius,
        UnitVector3D([12, 31, 99]),
        UnitVector3D([0, 99, -31]),
    )
    rotation_matrix = Matrix44([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    sphere_transformation = sphere_2.transformed_copy(matrix=rotation_matrix)
    assert np.allclose(sphere_transformation._origin, Point3D([-99, 42, 13]))
    assert np.allclose(sphere_transformation._reference, UnitVector3D([-31, 12, 99]))
    assert np.allclose(sphere_transformation._axis, UnitVector3D([-99, 0, -31]))
    sphere_mirror = sphere_2.mirrored_copy()
    assert np.allclose(sphere_mirror._origin, Point3D([42, 99, 13]))
    assert np.allclose(
        sphere_mirror._reference, UnitVector3D([-0.11490753, -0.29684446, -0.94798714])
    )
    assert np.allclose(sphere_mirror._axis, UnitVector3D([0, -0.9543083, 0.29882381]))


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
    with pytest.raises(AttributeError):
        eval.sphere = Sphere(Point3D([0, 0, 0]), Distance(1))
        eval.parameter = ParamUV(np.pi / 2, np.pi / 2)
    assert np.allclose(eval.position, Point3D([1, 0, 0]))
    assert np.allclose(eval.normal, UnitVector3D([1, 0, 0]))
    assert np.allclose(eval.u_derivative, Vector3D([0, 1, 0]))
    assert np.allclose(eval.v_derivative, Vector3D([0, 0, 1]))
    assert np.allclose(eval.uu_derivative, Vector3D([-1, 0, 0]))
    assert np.allclose(eval.uv_derivative, Vector3D([0, 0, 0]))
    assert np.allclose(eval.vv_derivative, Vector3D([-1, 0, 0]))
    assert eval.min_curvature == 1.0
    assert np.allclose(eval.min_curvature_direction, Vector3D([0, -1, 0]))
    assert eval.max_curvature == 1.0
    assert np.allclose(eval.max_curvature_direction, Vector3D([0, 0, 1]))

    # Test evaluation by projecting a point onto the sphere
    eval2 = sphere.project_point(Point3D([1, 1, 1]))
    assert eval2.sphere == sphere
    assert np.allclose(eval2.position, Point3D([0.57735027, 0.57735027, 0.57735027]))
    assert np.allclose(eval2.normal, UnitVector3D([1, 1, 1]))
    assert np.allclose(eval2.u_derivative.normalize(), UnitVector3D([-1, 1, 0]))
    assert np.allclose(eval2.v_derivative.normalize(), UnitVector3D([-1, -1, 2]))


def test_sphere_reference_and_axis_not_perpendicular():
    """Test that a ValueError is raised when the reference and axis are not perpendicular."""
    origin = Point3D([0, 0, 0])
    radius = 10.0
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([1, 0, 0])  # Same direction as reference

    with pytest.raises(
        ValueError, match="Circle reference \\(dir_x\\) and axis \\(dir_z\\) must be perpendicular."
    ):
        Sphere(origin, radius, reference, axis)


def test_sphere_radius_not_positive():
    """Test that a ValueError is raised when the radius is not positive."""
    origin = Point3D([0, 0, 0])
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Test with zero radius
    with pytest.raises(ValueError, match="Radius must be a real positive value."):
        Sphere(origin, 0, reference, axis)

    # Test with negative radius
    with pytest.raises(ValueError, match="Radius must be a real positive value."):
        Sphere(origin, -5, reference, axis)


def test_sphere_project_point_origin():
    """Test the project_point method when the point is at the sphere's origin."""
    # Define valid inputs for the sphere
    origin = Point3D([0, 0, 0])
    radius = 10.0
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a sphere instance
    sphere = Sphere(origin, radius, reference, axis)

    # Define a point at the sphere's origin
    point = Point3D([0, 0, 0])

    # Call the project_point method
    evaluation = sphere.project_point(point)

    # Validate the result
    assert isinstance(evaluation, SphereEvaluation)
    assert evaluation.parameter.u == 0
    assert evaluation.parameter.v == np.pi / 2


def test_sphere_parameterization():
    """Test the parameterization method of the Sphere class."""
    # Define valid inputs for the sphere
    origin = Point3D([0, 0, 0])
    radius = 10.0
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a sphere instance
    sphere = Sphere(origin, radius, reference, axis)

    # Call the parameterization method
    u, v = sphere.parameterization()

    # Validate the u parameterization
    assert isinstance(u, Parameterization)
    assert u.form == ParamForm.PERIODIC
    assert u.type == ParamType.CIRCULAR
    assert u.interval.start == 0
    assert u.interval.end == 2 * np.pi

    # Validate the v parameterization
    assert isinstance(v, Parameterization)
    assert v.form == ParamForm.CLOSED
    assert v.type == ParamType.OTHER
    assert v.interval.start == -np.pi / 2
    assert v.interval.end == np.pi / 2


def test_sphere_contains_param_not_implemented():
    """Test that contains_param raises NotImplementedError."""
    # Define valid inputs for the sphere
    origin = Point3D([0, 0, 0])
    radius = 10.0
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a sphere instance
    sphere = Sphere(origin, radius, reference, axis)

    # Define a parameter
    param_uv = ParamUV(0.5, 0.5)

    # Assert that contains_param raises NotImplementedError
    with pytest.raises(NotImplementedError, match="contains_param\\(\\) is not implemented."):
        sphere.contains_param(param_uv)


def test_sphere_contains_point_not_implemented():
    """Test that contains_point raises NotImplementedError."""
    # Define valid inputs for the sphere
    origin = Point3D([0, 0, 0])
    radius = 10.0
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a sphere instance
    sphere = Sphere(origin, radius, reference, axis)

    # Define a point
    point = Point3D([5, 5, 5])

    # Assert that contains_point raises NotImplementedError
    with pytest.raises(NotImplementedError, match="contains_point\\(\\) is not implemented."):
        sphere.contains_point(point)


def test_cone():
    """``Cone`` construction and equivalency."""
    origin = Point3D([0, 0, 0])
    radius = 1
    half_angle = np.pi / 4
    cone = Cone(origin, radius, half_angle)

    assert np.allclose(cone.origin, origin)
    assert cone.radius.m == radius
    assert isinstance(cone.radius, Quantity)
    assert cone.half_angle.m == half_angle
    assert isinstance(cone.half_angle, Quantity)
    assert np.allclose(cone.dir_x, UNITVECTOR3D_X)
    assert np.allclose(cone.dir_y, UNITVECTOR3D_Y)
    assert np.allclose(cone.dir_z, UNITVECTOR3D_Z)
    assert Accuracy.length_is_equal(cone.height.m, 1)
    assert cone.height.u == "meter"
    assert isinstance(cone.height, Quantity)
    assert Accuracy.length_is_equal(cone.surface_area.m, 7.58447559)
    assert cone.surface_area.u == "meter ** 2"
    assert isinstance(cone.surface_area, Quantity)
    assert Accuracy.length_is_equal(cone.volume.m, 1.04719755)
    assert cone.volume.u == "meter ** 3"
    assert isinstance(cone.volume, Quantity)
    assert np.allclose(cone.apex, Point3D([0, 0, -1]))

    duplicate = Cone(origin, radius, half_angle)
    assert cone == duplicate

    # Same cone, but opens the opposite way since half_angle will be negative
    neg_cone = Cone(origin, radius, -half_angle)

    assert np.allclose(neg_cone.origin, origin)
    assert neg_cone.radius.m == radius
    assert neg_cone.half_angle.m == -half_angle
    assert np.allclose(neg_cone.dir_x, UNITVECTOR3D_X)
    assert np.allclose(neg_cone.dir_y, UNITVECTOR3D_Y)
    assert np.allclose(neg_cone.dir_z, UNITVECTOR3D_Z)
    assert Accuracy.length_is_equal(neg_cone.height.m, 1)
    assert Accuracy.length_is_equal(neg_cone.surface_area.m, 7.58447559)
    assert Accuracy.length_is_equal(neg_cone.volume.m, 1.04719755)
    assert np.allclose(neg_cone.apex, Point3D([0, 0, 1]))

    with pytest.raises(BeartypeCallHintParamViolation):
        Cone(origin, "A", 200)

    with pytest.raises(BeartypeCallHintParamViolation):
        Cone(origin, 100, "A")

    with pytest.raises(BeartypeCallHintParamViolation):
        Cone(origin, 100, 200, "A", UnitVector3D([25, 39, 82]))

    with pytest.raises(BeartypeCallHintParamViolation):
        Cone(origin, 100, 200, UnitVector3D([12, 31, 99]), "A")

    with pytest.raises(ValueError):
        Cone(origin, 1, 1, UnitVector3D([1, 0, 0]), UnitVector3D([1, 1, 1]))

    origin = Point3D([42, 99, 13])
    radius = 200
    half_angle = np.pi / 4
    cone_2 = Cone(
        origin,
        radius,
        half_angle,
        UnitVector3D([12, 31, 99]),
        UnitVector3D([0, 99, -31]),
    )
    rotation_matrix = Matrix44([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    cone_transformation = cone_2.transformed_copy(matrix=rotation_matrix)
    assert np.allclose(cone_transformation._origin, Point3D([-99, 42, 13]))
    assert np.allclose(cone_transformation._reference, UnitVector3D([-31, 12, 99]))
    assert np.allclose(cone_transformation._axis, UnitVector3D([-99, 0, -31]))
    cone_mirror = cone_2.mirrored_copy()
    assert np.allclose(cone_mirror._origin, Point3D([42, 99, 13]))
    assert np.allclose(
        cone_mirror._reference, UnitVector3D([-0.11490753, -0.29684446, -0.94798714])
    )
    assert np.allclose(cone_mirror._axis, UnitVector3D([0, -0.9543083, 0.29882381]))


def test_cone_units():
    """``Cone`` units validation."""
    origin = Point3D([42, 99, 13])
    radius = 100
    radius_unit = UNITS.mm
    half_angle = 45
    angle_unit = UNITS.degrees

    cone = Cone(origin, Quantity(radius, radius_unit), Quantity(half_angle, angle_unit))

    # Verify rejection of invalid base unit type
    with pytest.raises(
        TypeError,
        match=r"The pint.Unit provided as an input should be a \[length\] quantity.",
    ):
        Cone(
            origin,
            Quantity(radius, UNITS.celsius),
            half_angle,
        )

    with pytest.raises(
        TypeError,
        match="The pint.Unit provided as an input should be a dimensionless quantity.",
    ):
        Cone(origin, Quantity(radius, UNITS.mm), Quantity(half_angle, UNITS.celsius))

    # Check that the units are correctly in place
    assert cone.radius.u == radius_unit
    assert cone.half_angle.u == angle_unit

    # Request for radius and half angle are in expected units
    assert cone.radius == Quantity(radius, UNITS.mm)
    assert cone.half_angle == Quantity(half_angle, UNITS.degrees)

    # Change units to and check if the values changed
    cone._radius.unit = new_unit_radius = UNITS.cm
    cone._half_angle.unit = new_unit_angle = UNITS.radian
    assert cone.radius.m == UNITS.convert(radius, radius_unit, new_unit_radius)
    assert Accuracy.angle_is_zero(
        cone.half_angle - UNITS.convert(half_angle, angle_unit, new_unit_angle)
    )


def test_cone_evaluation():
    origin = Point3D([0, 0, 0])
    radius = 1
    half_angle = np.pi / 4
    cone = Cone(origin, radius, half_angle)

    eval = cone.evaluate(ParamUV(0, 0))

    # Test base evaluation at (0, 0)
    assert eval.cone == cone
    with pytest.raises(AttributeError):
        eval.cone = Cone(Point3D([0, 0, 0]), 1, np.pi / 4)
        eval.parameter = ParamUV(np.pi / 2, np.pi / 2)
    assert np.allclose(eval.position, Point3D([1, 0, 0]))
    assert isinstance(eval.position, Point3D)
    assert np.allclose(eval.normal, UnitVector3D([1, 0, -1]))
    assert isinstance(eval.normal, UnitVector3D)
    assert np.allclose(eval.u_derivative, Vector3D([0, 1, 0]))
    assert isinstance(eval.u_derivative, Vector3D)
    assert np.allclose(eval.v_derivative, Vector3D([1, 0, 1]))
    assert isinstance(eval.v_derivative, Vector3D)
    assert np.allclose(eval.uu_derivative, Vector3D([-1, 0, 0]))
    assert isinstance(eval.uu_derivative, Vector3D)
    assert np.allclose(eval.uv_derivative, Vector3D([0, 1, 0]))
    assert isinstance(eval.uv_derivative, Vector3D)
    assert np.allclose(eval.vv_derivative, Vector3D([0, 0, 0]))
    assert isinstance(eval.vv_derivative, Vector3D)
    assert eval.min_curvature == 0
    assert np.allclose(eval.min_curvature_direction, UnitVector3D([1, 0, 1]))
    assert isinstance(eval.min_curvature_direction, UnitVector3D)
    assert eval.max_curvature == 1.0
    assert np.allclose(eval.max_curvature_direction, UnitVector3D([0, 1, 0]))
    assert isinstance(eval.max_curvature_direction, UnitVector3D)

    # # Test evaluation by projecting a point onto the cone
    eval2 = cone.project_point(Point3D([1, 1, 1]))
    assert eval2.cone == cone
    assert np.allclose(eval2.position, Point3D([1.20710678, 1.20710678, 0.70710678]))
    assert np.allclose(eval2.normal, UnitVector3D([0.5, 0.5, -0.70710678]))
    assert np.allclose(eval2.u_derivative.normalize(), UnitVector3D([-1, 1, 0]))
    assert np.allclose(eval2.v_derivative, Vector3D([0.70710678, 0.70710678, 1]))


def test_cone_radius_not_positive():
    """Test that a ValueError is raised when the radius is not positive."""
    origin = Point3D([0, 0, 0])
    half_angle = 45.0  # Valid half angle
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Test with zero radius
    with pytest.raises(ValueError, match="Radius must be a real positive value."):
        Cone(origin, 0, half_angle, reference, axis)

    # Test with negative radius
    with pytest.raises(ValueError, match="Radius must be a real positive value."):
        Cone(origin, -5, half_angle, reference, axis)


def test_cone_project_point_u_normalization():
    """Test the normalization of the u parameter in the project_point method."""
    # Define valid inputs for the cone
    origin = Point3D([0, 0, 0])
    radius = 10.0
    half_angle = 45.0  # Valid half angle
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a cone instance
    cone = Cone(origin, radius, half_angle, reference, axis)

    # Define a point to project onto the cone that results in u < 0
    point_negative_u = Point3D([-5, -5, 5])
    evaluation_negative_u = cone.project_point(point_negative_u)
    assert 0 <= evaluation_negative_u.parameter.u <= 2 * np.pi, (
        "u parameter is not normalized within [0, 2*pi]"
    )

    # Define a point to project onto the cone that results in u > 2 * np.pi
    point_large_u = Point3D([100, 100, 5])
    evaluation_large_u = cone.project_point(point_large_u)
    assert 0 <= evaluation_large_u.parameter.u <= 2 * np.pi, (
        "u parameter is not normalized within [0, 2*pi]"
    )


def test_cone_parameterization():
    """Test the parameterization method of the Cone class."""
    # Define valid inputs for the cone
    origin = Point3D([0, 0, 0])
    radius = 10.0
    half_angle = 45.0  # Valid half angle
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a cone instance
    cone = Cone(origin, radius, half_angle, reference, axis)

    # Call the parameterization method
    u, v = cone.parameterization()

    # Validate the u parameterization
    assert isinstance(u, Parameterization)
    assert u.form == ParamForm.PERIODIC
    assert u.type == ParamType.CIRCULAR
    assert u.interval.start == 0
    assert u.interval.end == 2 * np.pi

    # Validate the v parameterization
    assert isinstance(v, Parameterization)
    assert v.form == ParamForm.OPEN
    assert v.type == ParamType.LINEAR
    assert v.interval.start == cone.apex_param
    assert v.interval.end == np.inf if cone.apex_param < 0 else cone.apex_param


def test_cone_contains_param_not_implemented():
    """Test that contains_param raises NotImplementedError."""
    # Define valid inputs for the cone
    origin = Point3D([0, 0, 0])
    radius = 10.0
    half_angle = 45.0  # Valid half angle
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a cone instance
    cone = Cone(origin, radius, half_angle, reference, axis)

    # Define a parameter
    param_uv = ParamUV(0.5, 0.5)

    # Assert that contains_param raises NotImplementedError
    with pytest.raises(NotImplementedError, match="contains_param\\(\\) is not implemented."):
        cone.contains_param(param_uv)


def test_cone_contains_point_not_implemented():
    """Test that contains_point raises NotImplementedError."""
    # Define valid inputs for the cone
    origin = Point3D([0, 0, 0])
    radius = 10.0
    half_angle = 45.0  # Valid half angle
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a cone instance
    cone = Cone(origin, radius, half_angle, reference, axis)

    # Define a point
    point = Point3D([5, 5, 5])

    # Assert that contains_point raises NotImplementedError
    with pytest.raises(NotImplementedError, match="contains_point\\(\\) is not implemented."):
        cone.contains_point(point)


def test_torus():
    """``Torus`` construction and equivalency."""
    # Create two Torus objects
    origin = Point3D([42, 99, 13])
    major_radius = 200
    minor_radius = 100
    t_1 = Torus(
        origin,
        major_radius,
        minor_radius,
        UnitVector3D([12, 31, 99]),
        UnitVector3D([0, 99, -31]),
    )
    t_1_duplicate = Torus(
        origin,
        major_radius,
        minor_radius,
        UnitVector3D([12, 31, 99]),
        UnitVector3D([0, 99, -31]),
    )
    t_2 = Torus(Point3D([5, 8, 9]), 88, 76, UnitVector3D([55, 16, 73]), UnitVector3D([73, 0, -55]))
    t_with_array_definitions = Torus([5, 8, 9], 88, 76, [55, 16, 73], [73, 0, -55])

    rotation_matrix = Matrix44([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    _ = t_1.transformed_copy(rotation_matrix)

    # Check that the equals operator works
    assert t_1 == t_1_duplicate
    assert t_1 != t_2
    assert t_2 == t_with_array_definitions

    # Check torus definition
    assert t_1.origin.x == origin.x
    assert t_1.origin.y == origin.y
    assert t_1.origin.z == origin.z
    assert t_1.major_radius == major_radius * DEFAULT_UNITS.LENGTH
    assert t_1.minor_radius == minor_radius * DEFAULT_UNITS.LENGTH

    with pytest.raises(BeartypeCallHintParamViolation):
        Torus(
            origin,
            "A",
            200,
            UnitVector3D([12, 31, 99]),
            UnitVector3D([0, 99, -31]),
        )

    with pytest.raises(BeartypeCallHintParamViolation):
        Torus(
            origin,
            100,
            "A",
            UnitVector3D([12, 31, 99]),
            UnitVector3D([0, 99, -31]),
        )

    with pytest.raises(BeartypeCallHintParamViolation):
        Torus(
            origin,
            100,
            200,
            "A",
            UnitVector3D([0, 99, -31]),
        )

    with pytest.raises(BeartypeCallHintParamViolation):
        Torus(
            origin,
            100,
            200,
            UnitVector3D([12, 31, 99]),
            "A",
        )
    origin = Point3D([42, 99, 13])
    major_radius = 200
    minor_radius = 100
    t_2 = Torus(
        origin,
        major_radius,
        minor_radius,
        UnitVector3D([12, 31, 99]),
        UnitVector3D([0, 99, -31]),
    )
    rotation_matrix = Matrix44([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    torus_transformation = t_2.transformed_copy(matrix=rotation_matrix)
    assert np.allclose(torus_transformation._origin, Point3D([-99, 42, 13]))
    assert np.allclose(torus_transformation._reference, UnitVector3D([-31, 12, 99]))
    assert np.allclose(torus_transformation._axis, UnitVector3D([-99, 0, -31]))
    torus_mirror = t_2.mirrored_copy()
    assert np.allclose(torus_mirror._origin, Point3D([42, 99, 13]))
    assert np.allclose(
        torus_mirror._reference, UnitVector3D([-0.11490753, -0.29684446, -0.94798714])
    )
    assert np.allclose(torus_mirror._axis, UnitVector3D([0, -0.9543083, 0.29882381]))
    # Attempt to create a Torus and expect a ValueError
    with pytest.raises(
        ValueError, match=r"Torus reference \(dir_x\) and axis \(dir_z\) must be perpendicular."
    ):
        Torus(origin, major_radius, minor_radius, UnitVector3D([1, 0, 0]), UnitVector3D([1, 0, 0]))


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
            Quantity(major_radius, UNITS.celsius),
            Quantity(minor_radius, UNITS.celsius),
            UnitVector3D([12, 31, 99]),
            UnitVector3D([0, 99, -31]),
        )

    t_1 = Torus(
        origin,
        Quantity(major_radius, unit),
        Quantity(minor_radius, unit),
        UnitVector3D([12, 31, 99]),
        UnitVector3D([0, 99, -31]),
    )

    # Check that the units are correctly in place
    assert t_1.major_radius.u == unit
    assert t_1.minor_radius.u == unit

    # Request for radii and ensure they are in mm
    assert t_1.major_radius.m == major_radius
    assert t_1.minor_radius.m == minor_radius


def test_torus_evaluation():
    origin = Point3D([0, 0, 0])
    major_radius = 2
    unit = UNITS.mm
    minor_radius = 1
    t1 = Torus(
        origin,
        Quantity(major_radius, unit),
        Quantity(minor_radius, unit),
        UnitVector3D([1, 0, 0]),
        UnitVector3D([0, 0, 1]),
    )
    assert Accuracy.length_is_equal(t1.surface_area.m, 78.9568352087)
    assert Accuracy.length_is_equal(t1.volume.m, 39.4784176044)
    eval = t1.evaluate(ParamUV(np.pi / 2, 0))
    assert eval.torus == t1
    with pytest.raises(AttributeError):
        eval.torus = Torus(
            Point3D([0, 0, 0]), 3, 1, UnitVector3D([1, 0, 0]), UnitVector3D([0, 0, 1])
        )
        eval.parameter = ParamUV(np.pi / 2, np.pi / 2)
    assert np.allclose(eval.position, Point3D([0, 3, 0]))
    assert isinstance(eval.position, Point3D)
    assert np.allclose(eval.normal, UnitVector3D([0, 1, 0]))
    assert isinstance(eval.normal, UnitVector3D)
    assert np.allclose(eval.u_derivative, Vector3D([-3, 0, 0]))
    assert isinstance(eval.u_derivative, Vector3D)
    assert np.allclose(eval.v_derivative, Vector3D([0, 0, 1]))
    assert isinstance(eval.v_derivative, Vector3D)
    assert np.allclose(eval.uu_derivative, Vector3D([0, -3, 0]))
    assert isinstance(eval.uu_derivative, Vector3D)
    assert np.allclose(eval.uv_derivative, Vector3D([0, 0, 0]))
    assert isinstance(eval.uv_derivative, Vector3D)
    assert np.allclose(eval.vv_derivative, Vector3D([0, -1, 0]))
    assert isinstance(eval.vv_derivative, Vector3D)
    assert eval.min_curvature == 0.3333333333333333
    assert np.allclose(eval.min_curvature_direction, UnitVector3D([-1, 0, 0]))
    assert isinstance(eval.min_curvature_direction, UnitVector3D)
    assert eval.max_curvature == 1.0
    assert np.allclose(eval.max_curvature_direction, UnitVector3D([0, 0, 1]))
    assert isinstance(eval.max_curvature_direction, UnitVector3D)

    # # Test evaluation by projecting a point onto the Torus
    eval2 = t1.project_point(Point3D([1, 1, 0]))
    assert eval2.torus == t1
    assert np.allclose(eval2.position, Point3D([0.707106781186548, 0.707106781186547, 0]))
    assert np.allclose(eval2.normal, UnitVector3D([-0.707106781186548, -0.707106781186547, 0]))
    assert np.allclose(eval2.u_derivative, UnitVector3D([-1, 1, 0]))
    assert np.allclose(eval2.v_derivative, Vector3D([0, 0, -1]))

    x = Vector3D([95, -35, 5])
    z = Vector3D([1, 2, -5])
    t2 = Torus(Point3D([-18, 7, -9]), 2, 1, x, z)
    eval3 = t2.evaluate(ParamUV(np.pi, 0))
    assert np.allclose(
        eval3.position, Point3D([-20.8116026549018, 8.03585360970068, -9.1479790871001])
    )
    assert isinstance(eval3.position, Point3D)
    assert np.allclose(
        eval3.normal, UnitVector3D([-0.937200884967281, 0.345284536566893, -0.0493263623666991])
    )
    assert isinstance(eval3.normal, UnitVector3D)
    assert np.allclose(
        eval3.u_derivative, Vector3D([0.891566324481193, 2.59364748939984, 1.21577226065617])
    )
    assert isinstance(eval3.u_derivative, Vector3D)
    assert np.allclose(
        eval3.v_derivative, Vector3D([0.182574185835055, 0.365148371670111, -0.912870929175277])
    )
    assert isinstance(eval3.v_derivative, Vector3D)
    assert np.allclose(
        eval3.uu_derivative, Vector3D([2.81160265490184, -1.03585360970068, 0.147979087100097])
    )
    assert isinstance(eval3.uu_derivative, Vector3D)
    assert np.allclose(eval3.uv_derivative, Vector3D([0, 0, 0]))
    assert isinstance(eval3.uv_derivative, Vector3D)
    assert np.allclose(
        eval3.vv_derivative, Vector3D([0.937200884967281, -0.345284536566893, 0.0493263623666991])
    )
    assert isinstance(eval3.vv_derivative, Vector3D)
    assert np.allclose(eval3.min_curvature, 0.3333333333333333)
    assert np.allclose(
        eval3.min_curvature_direction,
        UnitVector3D([0.297188774827064, 0.864549163133279, 0.405257420218724]),
    )
    assert isinstance(eval3.min_curvature_direction, UnitVector3D)
    assert eval3.max_curvature == 1.0
    assert np.allclose(
        eval3.max_curvature_direction,
        UnitVector3D([0.182574185835055, 0.365148371670111, -0.912870929175277]),
    )
    assert isinstance(eval3.max_curvature_direction, UnitVector3D)


def test_torus_parameterization():
    """Test the parameterization method of the Torus class."""
    # Define valid inputs for the torus
    origin = Point3D([0, 0, 0])
    major_radius = 10.0
    minor_radius = 5.0
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a torus instance
    torus = Torus(origin, major_radius, minor_radius, reference, axis)

    # Call the parameterization method
    u, v = torus.parameterization()

    # Validate the u parameterization
    assert isinstance(u, Parameterization)
    assert u.form == ParamForm.PERIODIC
    assert u.type == ParamType.CIRCULAR
    assert u.interval.start == 0
    assert u.interval.end == 2 * np.pi

    # Validate the v parameterization
    assert isinstance(v, Parameterization)
    assert v.form == ParamForm.PERIODIC
    assert v.type == ParamType.CIRCULAR
    assert v.interval.start == -np.pi / 2
    assert v.interval.end == np.pi / 2


def test_torus_contains_param_not_implemented():
    """Test that contains_param raises NotImplementedError."""
    # Define valid inputs for the torus
    origin = Point3D([0, 0, 0])
    major_radius = 10.0
    minor_radius = 5.0
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a torus instance
    torus = Torus(origin, major_radius, minor_radius, reference, axis)

    # Define a parameter
    param_uv = ParamUV(0.5, 0.5)

    # Assert that contains_param raises NotImplementedError
    with pytest.raises(NotImplementedError, match="contains_param\\(\\) is not implemented."):
        torus.contains_param(param_uv)


def test_torus_contains_point_not_implemented():
    """Test that contains_point raises NotImplementedError."""
    # Define valid inputs for the torus
    origin = Point3D([0, 0, 0])
    major_radius = 10.0
    minor_radius = 5.0
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])

    # Create a torus instance
    torus = Torus(origin, major_radius, minor_radius, reference, axis)

    # Define a point
    point = Point3D([5, 5, 5])

    # Assert that contains_point raises NotImplementedError
    with pytest.raises(NotImplementedError, match="contains_point\\(\\) is not implemented."):
        torus.contains_point(point)


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
        _ = Circle(origin, radius, reference=UNITVECTOR3D_X, axis=UnitVector3D([1, 1, 1]))

    origin = Point3D([42, 99, 13])
    radius = 200
    circle_2 = Circle(
        origin,
        radius,
        UnitVector3D([12, 31, 99]),
        UnitVector3D([0, 99, -31]),
    )
    rotation_matrix = Matrix44([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    circle_transformation = circle_2.transformed_copy(matrix=rotation_matrix)
    assert np.allclose(circle_transformation._origin, Point3D([-99, 42, 13]))
    assert np.allclose(circle_transformation._reference, UnitVector3D([-31, 12, 99]))
    assert np.allclose(circle_transformation._axis, UnitVector3D([-99, 0, -31]))
    circle_mirror = circle_2.mirrored_copy()
    assert np.allclose(circle_mirror._origin, Point3D([42, 99, 13]))
    assert np.allclose(
        circle_mirror._reference, UnitVector3D([-0.11490753, -0.29684446, -0.94798714])
    )
    assert np.allclose(circle_mirror._axis, UnitVector3D([0, -0.9543083, 0.29882381]))


def test_circle_evaluation():
    """``CircleEvaluation`` construction and equivalency."""
    origin = Point3D([0, 0, 0])
    radius = Distance(1)

    # Test evaluation at 0
    circle = Circle(origin, radius)
    eval = circle.evaluate(0)
    assert eval.circle == circle
    with pytest.raises(AttributeError):
        eval.circle = Circle(Point3D([0, 0, 0]), Distance(1))
        eval.parameter = ParamUV(np.pi / 2)
    assert eval.position == Point3D([1, 0, 0])
    assert eval.tangent == UNITVECTOR3D_Y
    assert eval.normal == UNITVECTOR3D_X
    assert eval.first_derivative == UNITVECTOR3D_Y
    assert eval.second_derivative == UnitVector3D([-1, 0, 0])
    assert eval.curvature == 1

    # Test evaluation at (.785) by projecting a point
    eval2 = circle.project_point(Point3D([1, 1, 0]))

    assert np.allclose(eval2.position, Point3D([np.sqrt(2) / 2, np.sqrt(2) / 2, 0]))
    assert np.allclose(eval2.tangent, UnitVector3D([-np.sqrt(2) / 2, np.sqrt(2) / 2, 0]))
    assert np.allclose(eval2.normal, UnitVector3D([1, 1, 0]))
    assert np.allclose(eval2.first_derivative, UnitVector3D([-np.sqrt(2) / 2, np.sqrt(2) / 2, 0]))
    assert np.allclose(eval2.second_derivative, UnitVector3D([-np.sqrt(2) / 2, -np.sqrt(2) / 2, 0]))
    assert eval2.curvature == 1


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

    origin = Point3D([42, 99, 13])
    line_2 = Line(
        origin,
        UnitVector3D([0, 99, -31]),
    )
    rotation_matrix = Matrix44([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    line_transformation = line_2.transformed_copy(matrix=rotation_matrix)
    assert np.allclose(line_transformation._origin, Point3D([-99, 42, 13]))
    assert np.allclose(line_transformation._direction, UnitVector3D([-99, 0, -31]))


def test_line_evaluation():
    """``LineEvaluation`` construction and equivalency."""
    origin = Point3D([0, 0, 0])
    direction = UnitVector3D([0.5, 0.5, 0])

    # Test evaluation at 0
    line = Line(origin, direction)
    eval = line.evaluate(0)

    assert eval.line == line
    with pytest.raises(AttributeError):
        eval.line = Line(Point3D([0, 0, 0]), UnitVector3D([0.5, 0.5, 0.5]))
        eval.parameter = 0
    assert eval.position == origin
    assert eval.tangent == UnitVector3D([0.5, 0.5, 0])
    assert eval.first_derivative == UnitVector3D([0.5, 0.5, 0])
    assert eval.second_derivative == Vector3D([0, 0, 0])
    assert eval.curvature == 0

    # Test evaluation at (.707) by projecting a point
    eval2 = line.project_point(Point3D([1, 0, 0]))

    diff = Vector3D.from_points(eval2.position, Point3D([0.5, 0.5, 0]))
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
        _ = Ellipse(
            origin,
            major_radius,
            minor_radius,
            reference=UNITVECTOR3D_X,
            axis=UnitVector3D([1, 1, 1]),
        )

    origin = Point3D([42, 99, 13])
    major_radius = 200
    minor_radius = 100
    ellipse_2 = Ellipse(
        origin,
        major_radius,
        minor_radius,
        UnitVector3D([12, 31, 99]),
        UnitVector3D([0, 99, -31]),
    )
    rotation_matrix = Matrix44([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    ellipse_transformation = ellipse_2.transformed_copy(matrix=rotation_matrix)
    assert np.allclose(ellipse_transformation._origin, Point3D([-99, 42, 13]))
    assert np.allclose(ellipse_transformation._reference, UnitVector3D([-31, 12, 99]))
    assert np.allclose(ellipse_transformation._axis, UnitVector3D([-99, 0, -31]))
    ellipse_mirror = ellipse_2.mirrored_copy()
    assert np.allclose(ellipse_mirror._origin, Point3D([42, 99, 13]))
    assert np.allclose(
        ellipse_mirror._reference, UnitVector3D([-0.11490753, -0.29684446, -0.94798714])
    )
    assert np.allclose(ellipse_mirror._axis, UnitVector3D([0, -0.9543083, 0.29882381]))


def test_ellipse_evaluation():
    """``EllipseEvaluation`` construction and equivalency."""
    origin = Point3D([0, 0, 0])
    major_radius = Distance(3)
    minor_radius = Distance(2)

    # Test evaluation at 0
    ellipse = Ellipse(origin, major_radius, minor_radius)
    eval = ellipse.evaluate(0)

    assert eval.ellipse == ellipse
    with pytest.raises(AttributeError):
        eval.ellipse = Ellipse(Point3D([0, 0, 0]), Distance(3), Distance(1))
        eval.parameter = 0
    assert eval.position == Point3D([3, 0, 0])
    assert eval.tangent == UNITVECTOR3D_Y
    assert eval.normal == UNITVECTOR3D_X
    assert eval.first_derivative.normalize() == UNITVECTOR3D_Y
    assert eval.second_derivative.normalize() == UnitVector3D([-1, 0, 0])
    assert eval.curvature == 0.75

    # Test evaluation at (t) by projecting a point
    eval2 = ellipse.project_point(Point3D([3, 3, 0]))

    np.allclose(eval2.position, Point3D([1.66410059, 1.66410059, 0]))

    np.allclose(eval2.normal, UnitVector3D([1, 1, 0]))

    np.allclose(eval2.tangent, UnitVector3D([-0.91381155, 0.40613847, 0]))

    np.allclose(eval2.first_derivative.normalize(), UnitVector3D([-0.91381155, 0.40613847, 0]))

    np.allclose(
        eval2.second_derivative.normalize(), UnitVector3D([-np.sqrt(2) / 2, -np.sqrt(2) / 2, -0])
    )

    assert Accuracy.length_is_equal(eval2.curvature, 0.31540327)


def test_nurbs_curve_from_control_points():
    """Test ``NURBSCurve`` construction from control points."""
    control_points = [
        Point3D([0, 0, 0]),
        Point3D([1, 1, 0]),
        Point3D([2, 0, 0]),
    ]
    degree = 2
    knots = [0, 0, 0, 1, 1, 1]
    nurbs_curve = NURBSCurve.from_control_points(
        control_points=control_points, degree=degree, knots=knots
    )
    assert nurbs_curve.degree == 2
    assert nurbs_curve.knots == [0, 0, 0, 1, 1, 1]
    assert nurbs_curve.control_points == control_points
    assert nurbs_curve.weights == [1, 1, 1]

    # Test with a different weight vector
    weights = [1, 2, 1]
    nurbs_curve_weights = NURBSCurve.from_control_points(
        control_points=control_points, degree=degree, knots=knots, weights=weights
    )

    assert nurbs_curve_weights.degree == 2
    assert nurbs_curve_weights.knots == [0, 0, 0, 1, 1, 1]
    assert nurbs_curve_weights.control_points == control_points
    assert nurbs_curve_weights.weights == weights

    # Verify that the curves are different
    assert nurbs_curve != nurbs_curve_weights


def test_nurbs_curve_fitting():
    """Test ``NURBSCurve`` fitting."""
    points = [
        Point3D([0, 0, 0]),
        Point3D([1, 1, 0]),
        Point3D([2, 0, 0]),
        Point3D([5, 2, 0]),
    ]
    degree = 3
    nurbs_curve = NURBSCurve.fit_curve_from_points(points=points, degree=degree)

    # Verify degree, knots, and control points
    assert nurbs_curve.degree == degree

    assert len(nurbs_curve.knots) == 8

    assert len(nurbs_curve.control_points) == 4
    assert np.allclose(nurbs_curve.control_points[0], Point3D([0, 0, 0]))
    assert np.allclose(
        nurbs_curve.control_points[1], Point3D([1.54969033497753, 4.03483016710592, 0])
    )
    assert np.allclose(
        nurbs_curve.control_points[2], Point3D([2.87290323505786, -5.66639579939497, 0])
    )
    assert np.allclose(nurbs_curve.control_points[3], Point3D([5, 2, 0]))


def test_nurbs_curve_evaluation():
    """Test ``NURBSCurve`` evaluation."""
    control_points = [
        Point3D([0, 0, 0]),
        Point3D([1, 1, 0]),
        Point3D([2, 0, 0]),
    ]
    degree = 2
    knots = [0, 0, 0, 1, 1, 1]
    nurbs_curve = NURBSCurve.from_control_points(
        control_points=control_points, degree=degree, knots=knots
    )

    # Test evaluation at 0
    eval = nurbs_curve.evaluate(0)
    assert eval is not None
    assert eval.is_set() is True
    assert eval.parameter == 0
    assert eval.position == Point3D([0, 0, 0])
    assert eval.first_derivative == Vector3D([2, 2, 0])
    assert eval.second_derivative == Vector3D([0, -4, 0])
    assert np.isclose(eval.curvature, 0.3535533905932737)

    # Test evaluation at 0.5
    eval = nurbs_curve.evaluate(0.5)
    assert eval is not None
    assert eval.is_set() is True
    assert eval.parameter == 0.5
    assert eval.position == Point3D([1, 0.5, 0])
    assert eval.first_derivative == Vector3D([2, 0, 0])
    assert eval.second_derivative == Vector3D([0, -4, 0])
    assert np.isclose(eval.curvature, 1)

    # Test evaluation at 1
    eval = nurbs_curve.evaluate(1)
    assert eval is not None
    assert eval.is_set() is True
    assert eval.parameter == 1
    assert eval.position == Point3D([2, 0, 0])
    assert eval.first_derivative == Vector3D([2, -2, 0])
    assert eval.second_derivative == Vector3D([0, -4, 0])
    assert np.isclose(eval.curvature, 0.3535533905932737)


def test_nurbs_curve_point_projection():
    """Test projection of a point onto a NURBS curve."""
    # Define the NUTBS curve
    control_points = [
        Point3D([0, 0, 0]),
        Point3D([1, 1, 0]),
        Point3D([2, 0, 0]),
    ]
    degree = 2
    knots = [0, 0, 0, 1, 1, 1]
    nurbs_curve = NURBSCurve.from_control_points(
        control_points=control_points, degree=degree, knots=knots
    )

    # Test projection of a point on the curve
    point = Point3D([1, 3, 0])
    projection = nurbs_curve.project_point(point, initial_guess=0.1)

    assert projection is not None
    assert projection.is_set() is True
    assert np.allclose(projection.position, Point3D([1, 0.5, 0]))
    assert np.isclose(projection.parameter, 0.5)


def test_nurbs_curve_equality_with_non_nurbs_object():
    """Test that __eq__ returns False when comparing with a non-NURBSCurve object."""
    # Create a valid NURBSCurve instance
    control_points = [Point3D([0, 0, 0]), Point3D([1, 1, 1]), Point3D([2, 2, 2])]
    degree = 2
    knots = [0, 0, 0, 1, 1, 1]
    nurbs_curve = NURBSCurve.from_control_points(control_points, degree, knots)

    # Compare with a non-NURBSCurve object
    non_nurbs_object = "Not a NURBSCurve"
    assert nurbs_curve != non_nurbs_object, (
        "__eq__ should return False when comparing with a non-NURBSCurve object."
    )


def test_nurbs_curve_parameterization():
    """Test the parameterization method of the NURBSCurve class."""
    # Define valid inputs for the NURBS curve
    control_points = [Point3D([0, 0, 0]), Point3D([1, 1, 1]), Point3D([2, 2, 2])]
    degree = 2
    knots = [0, 0, 0, 1, 1, 1]

    # Create a NURBS curve instance
    nurbs_curve = NURBSCurve.from_control_points(control_points, degree, knots)

    # Call the parameterization method
    parameterization = nurbs_curve.parameterization()

    # Validate the parameterization
    assert isinstance(parameterization, Parameterization)
    assert parameterization.form == ParamForm.OTHER
    assert parameterization.type == ParamType.OTHER
    assert parameterization.interval.start == nurbs_curve.geomdl_nurbs_curve.domain[0]
    assert parameterization.interval.end == nurbs_curve.geomdl_nurbs_curve.domain[1]


def test_nurbs_curve_transformed_copy():
    """Test the transformed_copy method of the NURBSCurve class."""
    # Define valid inputs for the NURBS curve
    control_points = [Point3D([0, 0, 0]), Point3D([1, 1, 1]), Point3D([2, 2, 2])]
    degree = 2
    knots = [0, 0, 0, 1, 1, 1]

    # Create a NURBS curve instance
    nurbs_curve = NURBSCurve.from_control_points(control_points, degree, knots)

    # Define a transformation matrix (e.g., rotation + translation)
    transformation_matrix = Matrix44(
        [
            [1, 0, 0, 10],  # Translate x by 10
            [0, 1, 0, 20],  # Translate y by 20
            [0, 0, 1, 30],  # Translate z by 30
            [0, 0, 0, 1],
        ]
    )

    # Call the transformed_copy method
    transformed_curve = nurbs_curve.transformed_copy(transformation_matrix)
    assert isinstance(transformed_curve, NURBSCurve)


def test_nurbs_curve_contains_param_not_implemented():
    """Test that contains_param raises NotImplementedError."""
    # Define valid inputs for the NURBS curve
    control_points = [Point3D([0, 0, 0]), Point3D([1, 1, 1]), Point3D([2, 2, 2])]
    degree = 2
    knots = [0, 0, 0, 1, 1, 1]

    # Create a NURBS curve instance
    nurbs_curve = NURBSCurve.from_control_points(control_points, degree, knots)

    # Define a parameter
    param = 0.5

    # Assert that contains_param raises NotImplementedError
    with pytest.raises(NotImplementedError, match="contains_param\\(\\) is not implemented."):
        nurbs_curve.contains_param(param)


def test_nurbs_curve_contains_point_not_implemented():
    """Test that contains_point raises NotImplementedError."""
    # Define valid inputs for the NURBS curve
    control_points = [Point3D([0, 0, 0]), Point3D([1, 1, 1]), Point3D([2, 2, 2])]
    degree = 2
    knots = [0, 0, 0, 1, 1, 1]

    # Create a NURBS curve instance
    nurbs_curve = NURBSCurve.from_control_points(control_points, degree, knots)

    # Define a point
    point = Point3D([1, 1, 1])

    # Assert that contains_point raises NotImplementedError
    with pytest.raises(NotImplementedError, match="contains_point\\(\\) is not implemented."):
        nurbs_curve.contains_point(point)


def test_nurbs_length_calculation():
    """Test the length calculation of a NURBS curve."""
    points = [Point3D([0, 0, 0]), Point3D([2, 2, 0]), Point3D([-2, 4, 0]), Point3D([2, 6, 0])]
    degree = 3
    nurbs_curve = NURBSCurve.fit_curve_from_points(points, degree)

    # Calculate the length of the NURBS curve
    length = nurbs_curve.length()

    # Verify that the length is calculated correctly
    assert np.isclose(length, 13.3012277924)


def test_nurbs_surface_from_control_points():
    """Test fitting a NURBS surface from points."""
    degree_u = 2
    degree_v = 2

    knots_u = [0, 0, 0, 1, 1, 1]
    knots_v = [0, 0, 0, 1, 1, 1]

    control_points = [
        Point3D([0, 0, 0]),
        Point3D([0, 1, 1]),
        Point3D([0, 2, 0]),
        Point3D([1, 0, 1]),
        Point3D([1, 1, 2]),
        Point3D([1, 2, 1]),
        Point3D([2, 0, 0]),
        Point3D([2, 1, 1]),
        Point3D([2, 2, 0]),
    ]

    surface = NURBSSurface.from_control_points(
        degree_u=degree_u,
        degree_v=degree_v,
        knots_u=knots_u,
        knots_v=knots_v,
        control_points=control_points,
    )

    assert isinstance(surface._nurbs_surface, geomdl.NURBS.Surface)
    assert surface.degree_u == degree_u
    assert surface.degree_v == degree_v
    assert surface.knotvector_u == knots_u
    assert surface.knotvector_v == knots_v
    assert surface.control_points == control_points
    assert surface.weights == [1.0] * len(control_points)


def test_nurbs_surface_fitting():
    """Test fitting a NURBS surface from points."""
    points = [
        Point3D([0, 0, 0]),
        Point3D([0, 1, 1]),
        Point3D([0, 2, 0]),
        Point3D([1, 0, 1]),
        Point3D([1, 1, 2]),
        Point3D([1, 2, 1]),
        Point3D([2, 0, 0]),
        Point3D([2, 1, 1]),
        Point3D([2, 2, 0]),
    ]
    degree_u = 2
    degree_v = 2

    surface = NURBSSurface.fit_surface_from_points(
        points=points, size_u=3, size_v=3, degree_u=degree_u, degree_v=degree_v
    )

    assert isinstance(surface._nurbs_surface, geomdl.NURBS.Surface)
    assert surface.degree_u == degree_u
    assert surface.degree_v == degree_v
    assert len(surface.knotvector_u) == 6
    assert len(surface.knotvector_v) == 6
    assert len(surface.control_points) == 9


def test_nurbs_surface_equality():
    """Test if two NURBSSurface instances are equal."""
    points = [
        Point3D([0, 0, 0]),
        Point3D([0, 1, 1]),
        Point3D([0, 2, 0]),
        Point3D([1, 0, 1]),
        Point3D([1, 1, 2]),
        Point3D([1, 2, 1]),
        Point3D([2, 0, 0]),
        Point3D([2, 1, 1]),
        Point3D([2, 2, 0]),
    ]
    degree_u = 2
    degree_v = 2

    surface = NURBSSurface.fit_surface_from_points(
        points=points, size_u=3, size_v=3, degree_u=degree_u, degree_v=degree_v
    )
    other_surface = NURBSSurface.fit_surface_from_points(
        points=points, size_u=3, size_v=3, degree_u=degree_u, degree_v=degree_v
    )

    assert surface == other_surface

    # Test with a different, non-equivalent, surface
    different_points = [
        Point3D([0, 0, 0]),
        Point3D([0, 1, 1]),
        Point3D([0, 2, 0]),
        Point3D([2, 0, 1]),
        Point3D([2, 1, 2]),
        Point3D([2, 2, 1]),
        Point3D([4, 0, 0]),
        Point3D([4, 1, 1]),
        Point3D([4, 2, 0]),
    ]
    different_surface = NURBSSurface.fit_surface_from_points(
        points=different_points, size_u=3, size_v=3, degree_u=degree_u, degree_v=degree_v
    )

    assert surface != different_surface

    # Test comparison with a non-NURBSSurface object
    non_nurbs_object = "Not a NURBSSurface"
    assert surface != non_nurbs_object


def test_nurbs_surface_parameterization():
    """Test the parameterization method of the NURBSSurface class."""
    # Define valid inputs for the NURBS surface
    degree_u = 2
    degree_v = 2
    knots_u = [0, 0, 0, 1, 1, 1]
    knots_v = [0, 0, 0, 1, 1, 1]
    control_points = [
        Point3D([0, 0, 0]),
        Point3D([0, 1, 1]),
        Point3D([0, 2, 0]),
        Point3D([1, 0, 1]),
        Point3D([1, 1, 2]),
        Point3D([1, 2, 1]),
        Point3D([2, 0, 0]),
        Point3D([2, 1, 1]),
        Point3D([2, 2, 0]),
    ]

    # Create a NURBS surface instance
    nurbs_surface = NURBSSurface.from_control_points(
        degree_u=degree_u,
        degree_v=degree_v,
        knots_u=knots_u,
        knots_v=knots_v,
        control_points=control_points,
    )

    # Call the parameterization method
    u_param, v_param = nurbs_surface.parameterization()

    # Validate the u parameterization
    assert isinstance(u_param, Parameterization)
    assert u_param.form == ParamForm.OTHER
    assert u_param.type == ParamType.OTHER
    assert u_param.interval.start == nurbs_surface._nurbs_surface.domain[0][0]
    assert u_param.interval.end == nurbs_surface._nurbs_surface.domain[0][1]

    # Validate the v parameterization
    assert isinstance(v_param, Parameterization)
    assert v_param.form == ParamForm.OTHER
    assert v_param.type == ParamType.OTHER
    assert v_param.interval.start == nurbs_surface._nurbs_surface.domain[1][0]
    assert v_param.interval.end == nurbs_surface._nurbs_surface.domain[1][1]


def test_nurbs_surface_simple_evaluation():
    """Test NURBSSurface evaluation."""
    degree_u = 2
    degree_v = 2
    knots_u = [0, 0, 0, 1, 1, 1]
    knots_v = [0, 0, 0, 1, 1, 1]
    control_points = [
        Point3D([0, 0, 0]),
        Point3D([0, 1, 1]),
        Point3D([0, 2, 0]),
        Point3D([1, 0, 1]),
        Point3D([1, 1, 2]),
        Point3D([1, 2, 1]),
        Point3D([2, 0, 0]),
        Point3D([2, 1, 1]),
        Point3D([2, 2, 0]),
    ]

    nurbs_surface = NURBSSurface.from_control_points(
        degree_u=degree_u,
        degree_v=degree_v,
        knots_u=knots_u,
        knots_v=knots_v,
        control_points=control_points,
    )

    # Test invalid evaluation at (-1,0)
    with pytest.raises(ValueError):
        _ = nurbs_surface.evaluate(ParamUV(-1, 0))

    # Test evaluation at (0,0)
    eval = nurbs_surface.evaluate(ParamUV(0.5, 0.5))

    assert isinstance(eval, NURBSSurfaceEvaluation)
    assert eval.parameter.u == 0.5
    assert eval.parameter.v == 0.5
    assert eval.position == Point3D([1, 1, 1])
    assert isinstance(eval.u_derivative, Vector3D)
    assert isinstance(eval.v_derivative, Vector3D)
    assert isinstance(eval.uu_derivative, Vector3D)
    assert isinstance(eval.uv_derivative, Vector3D)
    assert isinstance(eval.vv_derivative, Vector3D)
    assert isinstance(eval.normal, UnitVector3D)
    assert isinstance(eval.surface, NURBSSurface)
