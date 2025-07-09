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

from pint import Quantity
import pytest

from ansys.api.geometry.v0.models_pb2 import (
    CurveGeometry as GRPCCurve,
    Material as GRPCMaterial,
    MaterialProperty as GRPCMaterialProperty,
)
from ansys.geometry.core.connection.conversions import (
    curve_to_grpc_curve,
    grpc_curve_to_curve,
    grpc_material_property_to_material_property,
    grpc_material_to_material,
    grpc_surface_to_surface,
    sketch_shapes_to_grpc_geometries,
)
from ansys.geometry.core.designer.face import SurfaceType
from ansys.geometry.core.materials.material import MaterialPropertyType
from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
from ansys.geometry.core.misc.measurements import DEFAULT_UNITS, UNITS
from ansys.geometry.core.shapes.curves import Circle, Ellipse, Line
from ansys.geometry.core.shapes.surfaces import Cone, Cylinder, PlaneSurface, Sphere, Torus
from ansys.geometry.core.sketch import Arc, Polygon, SketchCircle, SketchEdge, SketchEllipse


def test_sketch_shapes_to_grpc_geometries_multiple_faces():
    """Test that multiple face types are converted and added to geometries."""
    # Mock data
    plane = Plane()
    circle = SketchCircle(Point2D([0, 0]), radius=1)
    ellipse = SketchEllipse(Point2D([0, 0]), major_radius=2, minor_radius=1, angle=0)
    polygon = Polygon(Point2D([0, 0]), inner_radius=1, sides=6, angle=0)
    faces = [circle, ellipse, polygon]

    # Call the function
    geometries = sketch_shapes_to_grpc_geometries(plane, edges=[], faces=faces)

    # Assert that the circle, ellipse, and polygon were converted and added
    assert len(geometries.circles) == 1
    assert len(geometries.ellipses) == 1
    assert len(geometries.polygons) == 1


def test_sketch_shapes_to_grpc_geometries_one_curve_lines():
    """Test that only one line geometry is selected and added to one_curve_geometry."""
    # Create real data
    plane = Plane()
    edge = SketchEdge()
    edges = [edge]

    # Call the function with only_one_curve=True
    one_curve_geometry = sketch_shapes_to_grpc_geometries(
        plane, edges=edges, faces=[], only_one_curve=True
    )

    # Assert that only one line geometry is selected and added
    assert len(one_curve_geometry.lines) == 0


def test_sketch_shapes_to_grpc_geometries_one_curve_arcs():
    """Test that only one arc geometry is selected and added to one_curve_geometry."""
    # Create real data
    plane = Plane()
    arc = Arc(Point2D([-1.01, 0]), Point2D([1.01, 0]), Point2D([0, 0]), clockwise=True)
    edges = [arc]

    # Call the function with only_one_curve=True
    one_curve_geometry = sketch_shapes_to_grpc_geometries(
        plane, edges=edges, faces=[], only_one_curve=True
    )

    # Assert that only one arc geometry is selected and added
    assert len(one_curve_geometry.arcs) == 1


def test_sketch_shapes_to_grpc_geometries_one_curve_circles():
    """Test that only one circle geometry is selected and added to one_curve_geometry."""
    # Create real data
    plane = Plane()
    circle = SketchCircle(Point2D([0, 0]), radius=1)
    faces = [circle]

    # Call the function with only_one_curve=True
    one_curve_geometry = sketch_shapes_to_grpc_geometries(
        plane, edges=[], faces=faces, only_one_curve=True
    )

    # Assert that only one circle geometry is selected and added
    assert len(one_curve_geometry.circles) == 1
    assert one_curve_geometry.circles[0].center.x == circle.center.x
    assert one_curve_geometry.circles[0].radius == circle.radius.m_as(DEFAULT_UNITS.SERVER_LENGTH)


def test_sketch_shapes_to_grpc_geometries_one_curve_ellipses():
    """Test that only one ellipse geometry is selected and added to one_curve_geometry."""
    # Create real data
    plane = Plane()
    ellipse = SketchEllipse(Point2D([0, 0]), major_radius=2, minor_radius=1, angle=0)
    faces = [ellipse]

    # Call the function with only_one_curve=True
    one_curve_geometry = sketch_shapes_to_grpc_geometries(
        plane, edges=[], faces=faces, only_one_curve=True
    )

    # Assert that only one ellipse geometry is selected and added
    assert len(one_curve_geometry.ellipses) == 1
    assert one_curve_geometry.ellipses[0].center.x == ellipse.center.x
    assert one_curve_geometry.ellipses[0].majorradius == ellipse.major_radius.m_as(
        DEFAULT_UNITS.SERVER_LENGTH
    )
    assert one_curve_geometry.ellipses[0].minorradius == ellipse.minor_radius.m_as(
        DEFAULT_UNITS.SERVER_LENGTH
    )


def test_sketch_shapes_to_grpc_geometries_one_curve_polygons():
    """Test that only one polygon geometry is selected and added to one_curve_geometry."""
    # Create real data
    plane = Plane()
    polygon = Polygon(Point2D([0, 0]), inner_radius=1, sides=6, angle=0)
    faces = [polygon]

    # Call the function with only_one_curve=True
    one_curve_geometry = sketch_shapes_to_grpc_geometries(
        plane, edges=[], faces=faces, only_one_curve=True
    )

    # Assert that only one polygon geometry is selected and added
    assert len(one_curve_geometry.polygons) == 1
    assert one_curve_geometry.polygons[0].center.x == polygon.center.x
    assert one_curve_geometry.polygons[0].radius == polygon.inner_radius.m_as(
        DEFAULT_UNITS.SERVER_LENGTH
    )
    assert one_curve_geometry.polygons[0].numberofsides == polygon.n_sides


@pytest.mark.parametrize(
    "surface_type, surface_data, expected_type",
    [
        (
            SurfaceType.SURFACETYPE_CONE,
            {
                "origin": [0, 0, 0],
                "axis": [0, 0, 1],
                "reference": [1, 0, 0],
                "radius": 5,
                "half_angle": 45,
            },
            Cone,
        ),
        (
            SurfaceType.SURFACETYPE_CYLINDER,
            {"origin": [0, 0, 0], "axis": [0, 0, 1], "reference": [1, 0, 0], "radius": 5},
            Cylinder,
        ),
        (
            SurfaceType.SURFACETYPE_SPHERE,
            {"origin": [0, 0, 0], "axis": [0, 0, 1], "reference": [1, 0, 0], "radius": 5},
            Sphere,
        ),
        (
            SurfaceType.SURFACETYPE_TORUS,
            {
                "origin": [0, 0, 0],
                "axis": [0, 0, 1],
                "reference": [1, 0, 0],
                "major_radius": 10,
                "minor_radius": 2,
            },
            Torus,
        ),
        (
            SurfaceType.SURFACETYPE_PLANE,
            {"origin": [0, 0, 0], "axis": [0, 0, 1], "reference": [1, 0, 0]},
            PlaneSurface,
        ),
        (
            "INVALID_SURFACE_TYPE",
            {"origin": [0, 0, 0], "axis": [0, 0, 1], "reference": [1, 0, 0]},
            None,
        ),
    ],
)
def test_grpc_surface_to_surface(surface_type, surface_data, expected_type):
    """Test grpc_surface_to_surface for various surface types."""
    # Mock surface data
    surface = type(
        "MockSurface",
        (object,),
        {
            "origin": type(
                "MockPoint",
                (object,),
                {
                    "x": surface_data["origin"][0],
                    "y": surface_data["origin"][1],
                    "z": surface_data["origin"][2],
                },
            ),
            "axis": type(
                "MockVector",
                (object,),
                {
                    "x": surface_data["axis"][0],
                    "y": surface_data["axis"][1],
                    "z": surface_data["axis"][2],
                },
            ),
            "reference": type(
                "MockVector",
                (object,),
                {
                    "x": surface_data["reference"][0],
                    "y": surface_data["reference"][1],
                    "z": surface_data["reference"][2],
                },
            ),
            "radius": surface_data.get("radius"),
            "half_angle": surface_data.get("half_angle"),
            "major_radius": surface_data.get("major_radius"),
            "minor_radius": surface_data.get("minor_radius"),
        },
    )()

    # Call the function
    result = grpc_surface_to_surface(surface, surface_type)

    # Assert the result type
    if expected_type is None:
        assert result is None
    else:
        assert isinstance(result, expected_type)


@pytest.mark.parametrize(
    "curve_data, expected_type, expected_attributes",
    [
        # Test for Circle
        (
            {
                "origin": {"x": 0, "y": 0, "z": 0},
                "axis": {"x": 0, "y": 0, "z": 1},
                "reference": {"x": 1, "y": 0, "z": 0},
                "radius": 5,
            },
            Circle,
            {"radius": Quantity(5, UNITS.m)},
        ),
        # Test for Ellipse
        (
            {
                "origin": {"x": 0, "y": 0, "z": 0},
                "axis": {"x": 0, "y": 0, "z": 1},
                "reference": {"x": 1, "y": 0, "z": 0},
                "major_radius": 10,
                "minor_radius": 5,
            },
            Ellipse,
            {"major_radius": Quantity(10, UNITS.m), "minor_radius": Quantity(5, UNITS.m)},
        ),
        # Test for Line
        (
            {"origin": {"x": 0, "y": 0, "z": 0}, "direction": {"x": 1, "y": 0, "z": 0}},
            Line,
            {"direction": {"x": 1, "y": 0, "z": 0}},
        ),
    ],
)
def test_grpc_curve_to_curve(curve_data, expected_type, expected_attributes):
    """Test grpc_curve_to_curve for various curve types."""
    # Create a GRPCCurve object using a dictionary
    grpc_curve = GRPCCurve(
        origin={
            "x": curve_data["origin"]["x"],
            "y": curve_data["origin"]["y"],
            "z": curve_data["origin"]["z"],
        },
        axis={
            "x": curve_data.get("axis", {}).get("x", 1),
            "y": curve_data.get("axis", {}).get("y", 0),
            "z": curve_data.get("axis", {}).get("z", 0),
        },
        reference={
            "x": curve_data.get("reference", {}).get("x", 1),
            "y": curve_data.get("reference", {}).get("y", 0),
            "z": curve_data.get("reference", {}).get("z", 0),
        },
        radius=curve_data.get("radius", 0),
        major_radius=curve_data.get("major_radius", 0),
        minor_radius=curve_data.get("minor_radius", 0),
        direction={
            "x": curve_data.get("direction", {}).get("x", 1),
            "y": curve_data.get("direction", {}).get("y", 0),
            "z": curve_data.get("direction", {}).get("z", 0),
        },
    )

    # Call the function
    result = grpc_curve_to_curve(grpc_curve)

    # Assert the result type
    if expected_type is None:
        assert result is None
    else:
        assert isinstance(result, expected_type)

        # Assert the attributes of the result
        for attr, value in expected_attributes.items():
            if isinstance(value, dict):  # For nested attributes like direction
                for sub_attr, sub_value in value.items():
                    assert getattr(result.direction, sub_attr) == sub_value
            else:
                assert getattr(result, attr) == value


def test_curve_to_grpc_curve_ellipse():
    """Test conversion of an Ellipse to GRPCCurve."""
    # Create an Ellipse object
    origin = Point3D([0, 0, 0])
    reference = UnitVector3D([1, 0, 0])
    axis = UnitVector3D([0, 0, 1])
    major_radius = Quantity(10, UNITS.m)
    minor_radius = Quantity(5, UNITS.m)
    ellipse = Ellipse(origin, major_radius, minor_radius, reference, axis)

    # Call the function
    grpc_curve = curve_to_grpc_curve(ellipse)

    # Assert the GRPCCurve attributes
    assert grpc_curve.origin.x == origin.x.m_as(UNITS.m)
    assert grpc_curve.origin.y == origin.y.m_as(UNITS.m)
    assert grpc_curve.origin.z == origin.z.m_as(UNITS.m)
    assert grpc_curve.reference.x == reference.x
    assert grpc_curve.reference.y == reference.y
    assert grpc_curve.reference.z == reference.z
    assert grpc_curve.axis.x == axis.x
    assert grpc_curve.axis.y == axis.y
    assert grpc_curve.axis.z == axis.z
    assert grpc_curve.major_radius == major_radius.m
    assert grpc_curve.minor_radius == minor_radius.m


def test_grpc_material_to_material():
    """Test conversion of GRPCMaterial to Material."""
    # Create GRPCMaterialProperty objects
    density_property = GRPCMaterialProperty(
        id=MaterialPropertyType.DENSITY.name,
        display_name="Density",
        value=7850,
        units="kg/m^3",
    )
    elasticity_property = GRPCMaterialProperty(
        id=MaterialPropertyType.ELASTIC_MODULUS.name,
        display_name="Elasticity",
        value=200000,
        units="Pa",
    )

    # Create GRPCMaterial object
    grpc_material = GRPCMaterial(
        name="Steel",
        material_properties=[density_property, elasticity_property],
    )

    # Call the function
    material = grpc_material_to_material(grpc_material)

    # Assert the Material attributes
    assert material.name == "Steel"
    assert isinstance(material._density.quantity, Quantity)  # Ensure density is a Quantity object

    # Assert the Material properties
    assert len(material.properties) == 3


def test_grpc_material_property_to_material_property_invalid_units():
    """Test handling of invalid units in GRPCMaterialProperty."""
    # Create a GRPCMaterialProperty with invalid units
    invalid_units_property = GRPCMaterialProperty(
        id=MaterialPropertyType.DENSITY.value,
        display_name="Density",
        value=7850,
        units="invalid_unit",  # Invalid unit
    )

    # Call the function
    material_property = grpc_material_property_to_material_property(invalid_units_property)

    # Assert fallback logic
    assert material_property.type == "Density"
    assert material_property.quantity == 7850  # Fallback to value
