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
"""Test design interaction."""

import os

import matplotlib.colors as mcolors
import numpy as np
from pint import Quantity
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection import BackendType
from ansys.geometry.core.designer import (
    CurveType,
    DesignFileFormat,
    MidSurfaceOffsetType,
    SharedTopologyType,
    SurfaceType,
)
from ansys.geometry.core.designer.body import CollisionType, FillStyle, MasterBody
from ansys.geometry.core.designer.face import FaceLoopType
from ansys.geometry.core.designer.part import MasterComponent, Part
from ansys.geometry.core.errors import GeometryExitedError
from ansys.geometry.core.materials import Material, MaterialProperty, MaterialPropertyType
from ansys.geometry.core.math import (
    IDENTITY_MATRIX44,
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    UNITVECTOR3D_Z,
    Frame,
    Plane,
    Point2D,
    Point3D,
    UnitVector3D,
    Vector3D,
)
from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Accuracy, Angle, Distance
from ansys.geometry.core.misc.auxiliary import DEFAULT_COLOR
from ansys.geometry.core.modeler import Modeler
from ansys.geometry.core.parameters.parameter import ParameterType, ParameterUpdateStatus
from ansys.geometry.core.shapes import (
    Circle,
    Cone,
    Cylinder,
    Ellipse,
    Line,
    ParamUV,
    Sphere,
    Torus,
)
from ansys.geometry.core.shapes.box_uv import BoxUV
from ansys.geometry.core.shapes.parameterization import (
    Interval,
)
from ansys.geometry.core.sketch import Sketch

from ..conftest import are_graphics_available
from .conftest import FILES_DIR


def test_design_selection(modeler: Modeler):
    """Test to validate the designer selection for edges and __repr__ method."""
    sketch = Sketch()
    sketch.box(Point2D([0, 0]), 10, 10)
    design = modeler.create_design("Box")
    body = design.extrude_sketch("Box", sketch, Quantity(2, UNITS.m))
    ns_edge = design.create_named_selection("The Edges", body.edges[0:2])
    assert ns_edge.edges[0].start == Point3D([-5, -5, 2])
    assert ns_edge.edges[0].end == Point3D([5, -5, 2])
    assert ns_edge.edges[1].start == Point3D([-5, -5, 0])
    assert ns_edge.edges[1].end == Point3D([-5, -5, 2])
    assert ns_edge.__repr__()[0:54] == "ansys.geometry.core.designer.selection.NamedSelection "


def test_design_part(modeler: Modeler):
    """Test to validate the designer part id, name, and setter for components and bodies."""
    body1 = MasterBody(id="body1", name="First Only Body", grpc_client=modeler.client)
    body2 = MasterBody(id="body2", name="Second Body in Component", grpc_client=modeler.client)
    bodies = [body1]
    part = Part(id="IDPart", name="NamePart", components=[], bodies=bodies)
    masterPart = MasterComponent(id="PartMaster", name="Part Master", part=part)
    assert masterPart.id == "PartMaster"
    assert masterPart.name == "Part Master"
    assert masterPart.__repr__()[0:50] == "MasterComponent(id=PartMaster, name=Part Master, t"
    assert part.id == "IDPart"
    assert part.name == "NamePart"
    part.components = [body2]
    assert part.components[0].name == "Second Body in Component"
    part.bodies = body1
    assert part.bodies.name == "First Only Body"


def test_design_extrusion_and_material_assignment(modeler: Modeler):
    """Test to validate the extrusion of a simple circle as a cylinder and the
    assignment of materials to it.
    """
    # Create a Sketch and draw a circle (all client side)
    sketch = Sketch()
    sketch.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design_name = "ExtrudeProfile"
    design = modeler.create_design(design_name)
    assert design.name == design_name
    assert design.design_id is not None
    assert design.id is not None
    assert design.parent_component is None
    assert len(design.components) == 0
    assert len(design.bodies) == 0
    assert len(design.materials) == 0
    assert len(design.named_selections) == 0

    # Add a material to your design
    density = Quantity(125, 1000 * UNITS.kg / (UNITS.m * UNITS.m * UNITS.m))
    poisson_ratio = Quantity(0.33, UNITS.dimensionless)
    tensile_strength = Quantity(45)
    material = Material(
        "steel",
        density,
        [MaterialProperty(MaterialPropertyType.POISSON_RATIO, "myPoisson", poisson_ratio)],
    )
    material.add_property(MaterialPropertyType.TENSILE_STRENGTH, "myTensile", Quantity(45))
    design.add_material(material)

    assert len(design.materials) == 1
    assert len(design.materials[0].properties) == 3
    assert (
        design.materials[0].properties[MaterialPropertyType.DENSITY].type
        == MaterialPropertyType.DENSITY
    )
    assert design.materials[0].name == "steel"
    assert design.materials[0].properties[MaterialPropertyType.DENSITY].name == "Density"
    assert design.materials[0].properties[MaterialPropertyType.DENSITY].quantity == density
    assert (
        design.materials[0].properties[MaterialPropertyType.POISSON_RATIO].type
        == MaterialPropertyType.POISSON_RATIO
    )
    assert design.materials[0].properties[MaterialPropertyType.POISSON_RATIO].name == "myPoisson"
    assert (
        design.materials[0].properties[MaterialPropertyType.POISSON_RATIO].quantity == poisson_ratio
    )
    assert (
        design.materials[0].properties[MaterialPropertyType.TENSILE_STRENGTH].type
        == MaterialPropertyType.TENSILE_STRENGTH
    )
    assert design.materials[0].properties[MaterialPropertyType.TENSILE_STRENGTH].name == "myTensile"
    assert (
        design.materials[0].properties[MaterialPropertyType.TENSILE_STRENGTH].quantity
        == tensile_strength
    )

    # Extrude the sketch to create a Body
    body = design.extrude_sketch("JustACircle", sketch, Quantity(10, UNITS.mm))
    assert len(design.components) == 0
    assert len(design.bodies) == 1

    # Assign a material to a Body
    body.assign_material(material)

    # Not possible to save to file from a container (CI/CD)
    # Use download approach when available.
    #
    # design.save(r"C:\temp\shared_volume\MyFile2.scdocx")


def test_assigning_and_getting_material(modeler: Modeler):
    """Test the assignment and retrieval of materials from a design."""
    # Create a Sketch and draw a circle (all client side)
    sketch = Sketch()
    sketch.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design_name = "ExtrudeProfile"
    design = modeler.create_design(design_name)

    # Add a material to body
    density = Quantity(125, 1000 * UNITS.kg / (UNITS.m**3))
    poisson_ratio = Quantity(0.33, UNITS.dimensionless)
    tensile_strength = Quantity(45.0, UNITS.pascal)
    material = Material(
        "steel",
        density,
        [MaterialProperty(MaterialPropertyType.POISSON_RATIO, "myPoisson", poisson_ratio)],
    )
    material.add_property(MaterialPropertyType.TENSILE_STRENGTH, "myTensile", Quantity(45))
    design.add_material(material)

    # Extrude the sketch to create a Body
    body = design.extrude_sketch("JustACircle", sketch, Quantity(10, UNITS.mm))

    # Assign a material to a Body
    body.material = material
    mat_service = body.material

    # Test material and property retrieval
    assert mat_service.name == "steel"
    assert len(mat_service.properties) == 3
    assert mat_service.properties[MaterialPropertyType.DENSITY].type == MaterialPropertyType.DENSITY
    assert mat_service.properties[MaterialPropertyType.DENSITY].name == "Density"
    assert mat_service.properties[MaterialPropertyType.DENSITY].quantity == density
    assert (
        mat_service.properties[MaterialPropertyType.POISSON_RATIO].type
        == MaterialPropertyType.POISSON_RATIO
    )
    assert mat_service.properties[MaterialPropertyType.POISSON_RATIO].name == "myPoisson"
    assert mat_service.properties[MaterialPropertyType.POISSON_RATIO].quantity == poisson_ratio
    assert (
        mat_service.properties[MaterialPropertyType.TENSILE_STRENGTH].type
        == MaterialPropertyType.TENSILE_STRENGTH
    )
    assert mat_service.properties[MaterialPropertyType.TENSILE_STRENGTH].name == "myTensile"
    assert (
        mat_service.properties[MaterialPropertyType.TENSILE_STRENGTH].quantity == tensile_strength
    )


def test_get_empty_material(modeler: Modeler):
    # Create a Sketch and draw a circle (all client side)
    sketch = Sketch()
    sketch.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design_name = "ExtrudeProfile"
    design = modeler.create_design(design_name)

    # Extrude the sketch to create a Body
    body = design.extrude_sketch("JustACircle", sketch, Quantity(10, UNITS.mm))

    # Assign a material to a Body
    mat_service = body.material
    assert mat_service.name == ""
    assert mat_service.properties[MaterialPropertyType.DENSITY].quantity == Quantity(
        0, UNITS.kg / (UNITS.m**3)
    )
    assert len(mat_service.properties) == 1


def test_face_to_body_creation(modeler: Modeler):
    """Test in charge of validating the extrusion of an existing face."""
    # Create a Sketch and draw a circle (all client side)
    sketch = Sketch()
    sketch.box(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design_name = "BoxExtrusions"
    design = modeler.create_design(design_name)

    # Extrude the sketch to create a Body
    box_body = design.extrude_sketch("JustABox", sketch, Quantity(10, UNITS.mm))

    assert len(design.components) == 0
    assert len(design.bodies) == 1

    longer_body = design.extrude_face(
        "LongerBoxFromFace", box_body.faces[0], Quantity(20, UNITS.mm)
    )

    assert len(design.components) == 0
    assert len(design.bodies) == 2
    assert longer_body.volume.m == pytest.approx(Quantity(2e-6, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    longest_body = design.extrude_face(
        "LongestBoxFromFace", box_body.faces[0], Distance(30, UNITS.mm)
    )

    assert len(design.components) == 0
    assert len(design.bodies) == 3
    assert longest_body.volume.m == pytest.approx(Quantity(3e-6, UNITS.m**3).m, rel=1e-6, abs=1e-8)

    nested_component = design.add_component("NestedComponent")
    surface_body = nested_component.create_surface_from_face(
        "SurfaceFromFace", longer_body.faces[2]
    )

    assert len(design.components) == 1
    assert len(design.bodies) == 3
    assert len(nested_component.components) == 0
    assert len(nested_component.bodies) == 1
    assert surface_body.volume.m == Quantity(0, UNITS.m**3).m
    assert surface_body.faces[0].area.m == pytest.approx(
        Quantity(2e-4, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )


def test_extrude_negative_sketch(modeler: Modeler):
    """Test to check the extrusion of a sketch in the negative direction."""
    # Create a sketch of a rectangle
    sk = Sketch()
    sk.box(Point2D([0, 0]), 10, 20)

    # Create a design
    design = modeler.create_design("mydes")

    # Create a positive extrusion and a negative one
    pos = design.extrude_sketch("positive", sk, 10)
    neg = design.extrude_sketch("negative", sk, 10, direction="-")

    # Verify that the negative extrusion is in the negative direction
    assert neg.faces[0].normal() != pos.faces[0].normal()
    assert np.isclose(neg.faces[0].normal().dot(pos.faces[0].normal()), -1.0)

    # If an invalid direction is given, it should default to the positive direction
    invalid_neg = design.extrude_sketch("invalid", sk, 10, direction="z")
    assert invalid_neg.faces[0].normal() == pos.faces[0].normal()
    assert np.isclose(invalid_neg.faces[0].normal().dot(pos.faces[0].normal()), 1.0)


def test_extrude_negative_sketch_face(modeler: Modeler):
    """Test to check the extrusion of a face in the negative direction."""
    # Create a sketch of a rectangle
    sk = Sketch()
    sk.box(Point2D([0, 0]), 10, 20)

    # Create a design
    design = modeler.create_design("mydes")

    # Create a positive extrusion and a negative one
    body = design.extrude_sketch("positive", sk, 10)
    pos = design.extrude_face("positive_face", body.faces[0], 10)
    neg = design.extrude_face("negative_face", body.faces[0], 10, direction="-")

    # Verify that the negative extrusion is in the negative direction
    assert neg.faces[0].normal() != pos.faces[0].normal()
    assert np.isclose(neg.faces[0].normal().dot(pos.faces[0].normal()), -1.0)

    # If an invalid direction is given, it should default to the positive direction
    invalid_neg = design.extrude_face("invalid_negative_face", body.faces[0], 10, direction="z")
    assert invalid_neg.faces[0].normal() == pos.faces[0].normal()
    assert np.isclose(invalid_neg.faces[0].normal().dot(pos.faces[0].normal()), 1.0)


def test_modeler(modeler: Modeler):
    """Test the ``Modeler`` methods."""
    # Get the modeler's string representation and check it
    repr = str(modeler)
    assert "Ansys Geometry Modeler (" in repr

    design = modeler.create_design("MyNewDesign")
    assert design is not None


def test_component_body(modeler: Modeler):
    """Test the different ``Component`` and ``Body`` creation methods."""
    # Create your design on the server side
    design_name = "ComponentBody_Test"
    design = modeler.create_design(design_name)
    assert design.name == design_name
    assert design.design_id is not None
    assert design.id is not None
    assert design.parent_component is None
    assert len(design.components) == 0
    assert len(design.bodies) == 0
    assert len(design.materials) == 0
    assert len(design.named_selections) == 0
    assert len(design.coordinate_systems) == 0

    # Create a simple sketch of a Polygon (specifically a Pentagon)
    sketch = Sketch()
    sketch.polygon(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), sides=5)

    # In the "root/base" Component (i.e. Design object) let's extrude the sketch
    name_extruded_body = "ExtrudedPolygon"
    distance_extruded_body = Quantity(50, UNITS.mm)
    body = design.extrude_sketch(
        name=name_extruded_body, sketch=sketch, distance=distance_extruded_body
    )

    assert body.name == name_extruded_body
    assert body.id is not None
    assert body.is_surface is False
    assert len(body.faces) == 7  # 5 sides + top + bottom
    expected_vol = sketch.faces[0].area.m * distance_extruded_body.m * 1e-9  # In mm -factor to m**3
    assert body.volume.m == pytest.approx(expected_vol)
    assert len(design.components) == 0
    assert len(design.bodies) == 1
    assert len(body.edges) == 15  # 5 top + 5 bottom + 5 sides

    # We have created this body on the base component. Let's add a new component
    # and add a planar surface to it
    planar_component_name = "PlanarBody_Component"
    planar_component = design.add_component(planar_component_name)
    assert planar_component.id is not None
    assert planar_component.name == planar_component_name

    planar_sketch = Sketch()
    planar_sketch.ellipse(
        Point2D([50, 50], UNITS.mm), Quantity(30, UNITS.mm), Quantity(10, UNITS.mm)
    )
    planar_component_surface_name = "PlanarBody_Component_Surface"
    planar_body = planar_component.create_surface(planar_component_surface_name, planar_sketch)

    assert planar_body.name == planar_component_surface_name
    assert planar_body.id is not None
    assert planar_body.is_surface is True
    assert len(planar_body.faces) == 1  # top + bottom merged into a single face
    assert planar_body.volume == 0.0
    assert len(planar_component.components) == 0
    assert len(planar_component.bodies) == 1
    assert len(design.components) == 1
    assert len(design.bodies) == 1
    assert (
        len(planar_body.edges) == 1
    )  # top + bottom merged into a single face + ellipse is a single curve

    # Check that the planar component belongs to the design
    assert planar_component.parent_component.id == design.id

    # Let's test the repr method for a component
    comp_str = repr(planar_component)
    assert "ansys.geometry.core.designer.Component" in comp_str
    assert "Exists               : True" in comp_str
    assert "N Bodies             : 1" in comp_str
    assert "N Components         : 0" in comp_str
    assert "N Coordinate Systems : 0" in comp_str


def test_named_selections(modeler: Modeler):
    """Test for verifying the correct creation of ``NamedSelection``."""
    # Create your design on the server side
    design = modeler.create_design("NamedSelection_Test")

    # Create 2 Sketch objects and draw a circle and a polygon (all client side)
    sketch_1 = Sketch()
    sketch_1.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))
    sketch_2 = Sketch()
    sketch_2.polygon(Point2D([-30, -30], UNITS.mm), Quantity(10, UNITS.mm), sides=5)

    # Build 2 independent components and bodies
    circle_comp = design.add_component("CircleComponent")
    body_circle_comp = circle_comp.extrude_sketch("Circle", sketch_1, Quantity(50, UNITS.mm))
    polygon_comp = design.add_component("PolygonComponent")
    body_polygon_comp = polygon_comp.extrude_sketch("Polygon", sketch_2, Quantity(30, UNITS.mm))

    # Create the NamedSelection
    design.create_named_selection("OnlyCircle", bodies=[body_circle_comp])
    design.create_named_selection("OnlyPolygon", bodies=[body_polygon_comp])
    design.create_named_selection("CircleAndPolygon", bodies=[body_circle_comp, body_polygon_comp])
    dupl_named_selection = design.create_named_selection(
        "CircleAndPolygon_2", bodies=[body_circle_comp, body_polygon_comp]
    )

    # Check that the named selections are available
    assert len(design.named_selections) == 4
    assert all(entry.id is not None for entry in design.named_selections)
    assert design.named_selections[0].name == "OnlyCircle"
    assert design.named_selections[1].name == "OnlyPolygon"
    assert design.named_selections[2].name == "CircleAndPolygon"
    assert design.named_selections[3].name == "CircleAndPolygon_2"

    # Try deleting a non-existing named selection
    design.delete_named_selection("MyInventedNamedSelection")
    assert len(design.named_selections) == 4

    # Now, let's delete the duplicated entry CircleAndPolygon_2
    design.delete_named_selection(dupl_named_selection)
    assert len(design.named_selections) == 3
    assert design.named_selections[0].name == "OnlyCircle"
    assert design.named_selections[1].name == "OnlyPolygon"
    assert design.named_selections[2].name == "CircleAndPolygon"

    # Test also that you can create a named selection out of faces only
    design.create_named_selection("OnlyPolygonFaces", faces=body_polygon_comp.faces)
    assert len(design.named_selections) == 4
    assert design.named_selections[0].name == "OnlyCircle"
    assert design.named_selections[1].name == "OnlyPolygon"
    assert design.named_selections[2].name == "CircleAndPolygon"
    assert design.named_selections[3].name == "OnlyPolygonFaces"

    # Try deleting a named selection by name
    design.delete_named_selection("OnlyCircle")
    assert len(design.named_selections) == 3


def test_named_selection_contents(modeler: Modeler):
    """Test for verifying the correct contents of a ``NamedSelection``."""
    # Create your design on the server side
    design = modeler.create_design("NamedSelection_Test")

    # Create objects to add to the named selection
    box = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    box_2 = design.extrude_sketch("box_2", Sketch().box(Point2D([0, 0]), 5, 5), 5)
    face = box_2.faces[2]
    edge = box_2.edges[0]

    circle_profile_1 = design.add_beam_circular_profile(
        "CircleProfile1", Quantity(10, UNITS.mm), Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_Y
    )
    beam = design.create_beam(
        Point3D([9, 99, 999], UNITS.mm), Point3D([8, 88, 888], UNITS.mm), circle_profile_1
    )

    # Create the NamedSelection
    ns = design.create_named_selection(
        "MyNamedSelection", bodies=[box, box_2], faces=[face], edges=[edge], beams=[beam]
    )

    # Check that the named selection has everything
    assert len(ns.bodies) == 2
    assert np.isin([box.id, box_2.id], [body.id for body in ns.bodies]).all()

    assert len(ns.faces) == 1
    assert ns.faces[0].id == face.id

    assert len(ns.edges) == 1
    assert ns.edges[0].id == edge.id

    assert len(ns.beams) == 1
    assert ns.beams[0].id == beam.id

    assert len(ns.design_points) == 0


def test_add_component_with_instance_name(modeler: Modeler):
    design = modeler.create_design("DesignHierarchyExample")
    circle_sketch = Sketch()
    circle_sketch.circle(Point2D([10, 10], UNITS.mm), Distance(10, UNITS.mm))

    slot_sketch = Sketch()
    slot_sketch.slot(Point2D([40, 10], UNITS.mm), Distance(20, UNITS.mm), Distance(10, UNITS.mm))

    nested_component = design.add_component("NestedComponent")
    nested_component2 = design.add_component("NestedComponent2", instance_name="first instance")

    assert nested_component.name == "NestedComponent"
    assert nested_component.instance_name == ""

    assert nested_component2.name == "NestedComponent2"
    assert nested_component2.instance_name == "first instance"


def test_faces_edges(modeler: Modeler):
    """Test for verifying the correct creation and usage of ``Face`` and
    ``Edge`` objects.
    """
    # Create your design on the server side
    design = modeler.create_design("FacesEdges_Test")

    # Create a Sketch object and draw a polygon (all client side)
    sketch = Sketch()
    sketch.polygon(Point2D([-30, -30], UNITS.mm), Quantity(10, UNITS.mm), sides=5)

    # Build independent components and bodies
    polygon_comp = design.add_component("PolygonComponent")
    body_polygon_comp = polygon_comp.extrude_sketch("Polygon", sketch, Quantity(30, UNITS.mm))

    # Get all its faces
    faces = body_polygon_comp.faces
    assert len(faces) == 7  # top + bottom + sides
    assert all(face.id is not None for face in faces)
    assert all(face.surface_type == SurfaceType.SURFACETYPE_PLANE for face in faces)
    assert all(face.area > 0.0 for face in faces)
    assert abs(faces[0].area.to_base_units().m - sketch.faces[0].area.to_base_units().m) <= 1e-15
    assert all(face.body.id == body_polygon_comp.id for face in faces)

    # Get the normal to some of the faces
    assert faces[0].normal() == UnitVector3D(-UNITVECTOR3D_Z)  # Bottom
    assert faces[1].normal() == UNITVECTOR3D_Z  # Top

    # Get the central point of some of the surfaces
    assert faces[0].point(0.4472135954999579, 0.5) == Point3D([-30, -30, 0], UNITS.mm)
    u, v = faces[1].shape.get_proportional_parameters(ParamUV(-0.03, -0.03))
    assert faces[1].point(u, v) == Point3D([-30, -30, 30], UNITS.mm)

    loops = faces[0].loops
    assert len(loops) == 1
    assert loops[0].type == FaceLoopType.OUTER_LOOP
    assert loops[0].length is not None
    assert loops[0].min_bbox is not None
    assert loops[0].max_bbox is not None
    assert len(loops[0].edges) == 5

    # Now, from one of the lids (i.e. 0 - bottom) get all edges
    edges = faces[0].edges
    assert len(edges) == 5  # pentagon
    assert all(edge.id is not None for edge in edges)
    assert all(edge.curve_type == CurveType.CURVETYPE_LINE for edge in edges)
    assert all(edge.length > 0.0 for edge in edges)
    assert (
        abs(edges[0].length.to_base_units().m - sketch.faces[0].length.to_base_units().m) <= 1e-15
    )

    # Get the faces to which the edge belongs
    faces_of_edge = edges[0].faces
    assert len(faces_of_edge) == 2
    assert any(
        [face.id == faces[0].id for face in faces_of_edge]
    )  # The bottom face must be one of them


def test_coordinate_system_creation(modeler: Modeler):
    """Test for verifying the correct creation of ``CoordinateSystem``."""
    # Create your design on the server side
    design = modeler.create_design("CoordinateSystem_Test")

    # Build independent component
    nested_comp = design.add_component("NestedComponent")

    frame1 = Frame(
        Point3D([10, 200, 3000], UNITS.mm), UnitVector3D([1, 1, 0]), UnitVector3D([1, -1, 0])
    )
    frame2 = Frame(
        Point3D([40, 80, 120], UNITS.mm), UnitVector3D([0, -1, 1]), UnitVector3D([0, 1, 1])
    )

    # Create the CoordinateSystem
    design.create_coordinate_system("DesignCS1", frame1)
    nested_comp.create_coordinate_system("CompCS1", frame1)
    nested_comp.create_coordinate_system("CompCS2", frame2)

    # Check that the named selections are available
    assert len(design.coordinate_systems) == 1
    assert all(entry.id is not None for entry in design.coordinate_systems)
    design_cs = design.coordinate_systems[0]
    assert design_cs.name == "DesignCS1"
    assert design_cs.frame.origin == frame1.origin
    for dir, dir_ref in zip(
        [design_cs.frame.direction_x, design_cs.frame.direction_y, design_cs.frame.direction_z],
        [frame1.direction_x, frame1.direction_y, frame1.direction_z],
    ):
        assert dir.x == pytest.approx(dir_ref.x, rel=1e-8, abs=1e-14)
        assert dir.y == pytest.approx(dir_ref.y, rel=1e-8, abs=1e-14)
        assert dir.z == pytest.approx(dir_ref.z, rel=1e-8, abs=1e-14)
    assert design_cs.parent_component.id == design.id

    assert len(nested_comp.coordinate_systems) == 2
    assert all(entry.id is not None for entry in nested_comp.coordinate_systems)
    nested_comp_cs1 = nested_comp.coordinate_systems[0]
    nested_comp_cs2 = nested_comp.coordinate_systems[1]
    assert nested_comp_cs1.name == "CompCS1"
    for dir, dir_ref in zip(
        [
            nested_comp_cs1.frame.direction_x,
            nested_comp_cs1.frame.direction_y,
            nested_comp_cs1.frame.direction_z,
        ],
        [frame1.direction_x, frame1.direction_y, frame1.direction_z],
    ):
        assert dir.x == pytest.approx(dir_ref.x, rel=1e-8, abs=1e-14)
        assert dir.y == pytest.approx(dir_ref.y, rel=1e-8, abs=1e-14)
        assert dir.z == pytest.approx(dir_ref.z, rel=1e-8, abs=1e-14)
    assert nested_comp_cs1.parent_component.id == nested_comp.id

    assert nested_comp_cs2.name == "CompCS2"
    for dir, dir_ref in zip(
        [
            nested_comp_cs2.frame.direction_x,
            nested_comp_cs2.frame.direction_y,
            nested_comp_cs2.frame.direction_z,
        ],
        [frame2.direction_x, frame2.direction_y, frame2.direction_z],
    ):
        assert dir.x == pytest.approx(dir_ref.x, rel=1e-8, abs=1e-14)
        assert dir.y == pytest.approx(dir_ref.y, rel=1e-8, abs=1e-14)
        assert dir.z == pytest.approx(dir_ref.z, rel=1e-8, abs=1e-14)
    assert nested_comp_cs2.parent_component.id == nested_comp.id

    # Let's check the representation of the coordinate system
    nested_comp_cs1_str = str(nested_comp_cs1)
    assert "ansys.geometry.core.designer.CoordinateSystem" in nested_comp_cs1_str
    assert "  Name                 : CompCS1" in nested_comp_cs1_str
    assert "  Exists               : True" in nested_comp_cs1_str
    assert "  Parent component     : NestedComponent" in nested_comp_cs1_str
    assert "  Frame origin         : [0.01,0.2,3.0] in meters" in nested_comp_cs1_str
    assert "  Frame X-direction    : " in nested_comp_cs1_str
    assert "  Frame Y-direction    : " in nested_comp_cs1_str
    assert "  Frame Z-direction    : " in nested_comp_cs1_str


def test_delete_body_component(modeler: Modeler):
    """Test for verifying the deletion of ``Component`` and ``Body`` objects.

    Notes
    -----
    Requires storing scdocx file and checking manually (for now).
    """
    # Create your design on the server side
    design = modeler.create_design("Deletion_Test")

    # Create a Sketch object and draw a circle (all client side)
    sketch = Sketch()
    sketch.circle(Point2D([-30, -30], UNITS.mm), Quantity(10, UNITS.mm))
    distance = Quantity(30, UNITS.mm)

    #  The following component hierarchy is made
    #
    #           |---> comp_1 ---|---> nested_1_comp_1 ---> nested_1_nested_1_comp_1
    #           |               |
    #           |               |---> nested_2_comp_1
    #           |
    # DESIGN ---|---> comp_2 -------> nested_1_comp_2
    #           |
    #           |
    #           |---> comp_3
    #
    #
    # Now, only "comp_3", "nested_2_comp_1" and "nested_1_nested_1_comp_1"
    # will have a body associated...
    #
    #

    # Create the components
    comp_1 = design.add_component("Component_1")
    comp_2 = design.add_component("Component_2")
    comp_3 = design.add_component("Component_3")
    nested_1_comp_1 = comp_1.add_component("Nested_1_Component_1")
    nested_1_nested_1_comp_1 = nested_1_comp_1.add_component("Nested_1_Nested_1_Component_1")
    nested_2_comp_1 = comp_1.add_component("Nested_2_Component_1")
    _ = comp_2.add_component("Nested_1_Component_2")

    # Create the bodies
    body_1 = comp_3.extrude_sketch(name="comp_3_circle", sketch=sketch, distance=distance)
    body_2 = nested_2_comp_1.extrude_sketch(
        name="nested_2_comp_1_circle", sketch=sketch, distance=distance
    )
    _ = nested_1_nested_1_comp_1.extrude_sketch(
        name="nested_1_nested_1_comp_1_circle", sketch=sketch, distance=distance
    )

    # Let's start by doing something impossible - trying to delete body_1 from comp_1
    comp_1.delete_body(body_1)

    # Check that all the underlying objects are still alive
    assert comp_1.is_alive
    assert comp_1.components[0].is_alive
    assert comp_1.components[0].components[0].is_alive
    assert comp_1.components[0].components[0].bodies[0].is_alive
    assert comp_1.components[1].is_alive
    assert comp_1.components[1].bodies[0].is_alive
    assert comp_2.is_alive
    assert comp_2.components[0].is_alive
    assert comp_3.is_alive
    assert comp_3.bodies[0].is_alive

    # Do the same checks but calling them from the design object
    assert design.is_alive
    assert design.components[0].is_alive
    assert design.components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].bodies[0].is_alive
    assert design.components[0].components[1].is_alive
    assert design.components[0].components[1].bodies[0].is_alive
    assert design.components[1].is_alive
    assert design.components[1].components[0].is_alive
    assert design.components[2].is_alive
    assert design.components[2].bodies[0].is_alive

    # Let's do another impossible thing - trying to delete comp_3 from comp_1
    comp_1.delete_component(comp_3)

    # Check that all the underlying objects are still alive
    assert comp_1.is_alive
    assert comp_1.components[0].is_alive
    assert comp_1.components[0].components[0].is_alive
    assert comp_1.components[0].components[0].bodies[0].is_alive
    assert comp_1.components[1].is_alive
    assert comp_1.components[1].bodies[0].is_alive
    assert comp_2.is_alive
    assert comp_2.components[0].is_alive
    assert comp_3.is_alive
    assert comp_3.bodies[0].is_alive

    # Do the same checks but calling them from the design object
    assert design.is_alive
    assert design.components[0].is_alive
    assert design.components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].bodies[0].is_alive
    assert design.components[0].components[1].is_alive
    assert design.components[0].components[1].bodies[0].is_alive
    assert design.components[1].is_alive
    assert design.components[1].components[0].is_alive
    assert design.components[2].is_alive
    assert design.components[2].bodies[0].is_alive

    # Let's delete now the entire comp_2 component
    comp_2.delete_component(comp_2)

    # Check that all the underlying objects are still alive except for comp_2
    assert comp_1.is_alive
    assert comp_1.components[0].is_alive
    assert comp_1.components[0].components[0].is_alive
    assert comp_1.components[0].components[0].bodies[0].is_alive
    assert comp_1.components[1].is_alive
    assert comp_1.components[1].bodies[0].is_alive
    assert not comp_2.is_alive
    assert not comp_2.components[0].is_alive
    assert comp_3.is_alive
    assert comp_3.bodies[0].is_alive

    # Do the same checks but calling them from the design object
    assert design.is_alive
    assert design.components[0].is_alive
    assert design.components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].bodies[0].is_alive
    assert design.components[0].components[1].is_alive
    assert design.components[0].components[1].bodies[0].is_alive
    assert not design.components[1].is_alive
    assert not design.components[1].components[0].is_alive
    assert design.components[2].is_alive
    assert design.components[2].bodies[0].is_alive

    # Let's delete now the body_2 object
    design.delete_body(body_2)

    # Check that all the underlying objects are still alive except for comp_2 and body_2
    assert comp_1.is_alive
    assert comp_1.components[0].is_alive
    assert comp_1.components[0].components[0].is_alive
    assert comp_1.components[0].components[0].bodies[0].is_alive
    assert comp_1.components[1].is_alive
    assert not body_2.is_alive
    assert not comp_2.is_alive
    assert not comp_2.components[0].is_alive
    assert comp_3.is_alive

    # Do the same checks but calling them from the design object
    assert design.is_alive
    assert design.components[0].is_alive
    assert design.components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].is_alive
    assert design.components[0].components[0].components[0].bodies[0].is_alive
    assert design.components[0].components[1].is_alive
    assert not design.components[1].is_alive
    assert not design.components[1].components[0].is_alive
    assert design.components[2].is_alive
    assert design.components[2].bodies[0].is_alive

    # Finally, let's delete the most complex one - comp_1
    design.delete_component(comp_1)

    # Check that all the underlying objects are still alive except for comp_2, body_2 and comp_1
    assert not comp_1.is_alive
    assert not comp_1.components[0].is_alive
    assert not comp_1.components[0].components[0].is_alive
    assert not comp_1.components[1].is_alive
    assert not comp_2.is_alive
    assert not comp_2.components[0].is_alive
    assert comp_3.is_alive
    assert comp_3.bodies[0].is_alive

    # Do the same checks but calling them from the design object
    assert design.is_alive
    assert not design.components[0].is_alive
    assert not design.components[0].components[0].is_alive
    assert not design.components[0].components[0].components[0].is_alive
    assert not design.components[0].components[1].is_alive
    assert not design.components[1].is_alive
    assert not design.components[1].components[0].is_alive
    assert design.components[2].is_alive
    assert design.components[2].bodies[0].is_alive

    # Finally, let's delete the entire design
    design.delete_component(comp_3)

    # Check everything is dead
    assert design.is_alive
    assert not design.components[0].is_alive
    assert not design.components[0].components[0].is_alive
    assert not design.components[0].components[0].components[0].is_alive
    assert not design.components[0].components[1].is_alive
    assert not design.components[1].is_alive
    assert not design.components[1].components[0].is_alive
    assert not design.components[2].is_alive

    # Try deleting the Design object itself - this is forbidden
    with pytest.raises(ValueError, match="The design itself cannot be deleted."):
        design.delete_component(design)

    # Let's try out the representation methods
    design_str = str(design)
    assert "ansys.geometry.core.designer.Design" in design_str
    assert "Name                 : Deletion_Test" in design_str
    assert "N Bodies             : 0" in design_str
    assert "N Components         : 0" in design_str
    assert "N Coordinate Systems : 0" in design_str
    assert "N Named Selections   : 0" in design_str
    assert "N Materials          : 0" in design_str
    assert "N Beam Profiles      : 0" in design_str
    assert "N Design Points      : 0" in design_str

    comp_1_str = str(comp_1)
    assert "ansys.geometry.core.designer.Component" in comp_1_str
    assert "Name                 : Component_1" in comp_1_str
    assert "Exists               : False" in comp_1_str
    assert "Parent component     : Deletion_Test" in comp_1_str
    assert "N Bodies             : 0" in comp_1_str
    assert "N Beams              : 0" in comp_1_str
    assert "N Components         : 0" in comp_1_str
    assert "N Design Points      : 0" in comp_1_str
    assert "N Coordinate Systems : 0" in comp_1_str

    body_1_str = str(body_1)
    assert "ansys.geometry.core.designer.Body" in body_1_str
    assert "Name                 : comp_3_circle" in body_1_str
    assert "Exists               : False" in body_1_str
    assert "Surface body         : False" in body_1_str
    assert "Parent component     : Component_3" in body_1_str
    assert "Color                : None" in body_1_str


def test_shared_topology(modeler: Modeler):
    """Test for checking the correct setting of shared topology on the server.

    Notes
    -----
    Requires storing scdocx file and checking manually (for now).
    """
    # Create your design on the server side
    design = modeler.create_design("SharedTopology_Test")

    # Create a Sketch object and draw a circle (all client side)
    sketch = Sketch()
    sketch.circle(Point2D([-30, -30], UNITS.mm), Quantity(10, UNITS.mm))
    distance = Quantity(30, UNITS.mm)

    # Create a component
    comp_1 = design.add_component("Component_1")
    comp_1.extrude_sketch(name="Body_1", sketch=sketch, distance=distance)

    # Now that the component is created, let's try to assign a SharedTopology
    assert comp_1.shared_topology is None

    # Set the shared topology
    comp_1.set_shared_topology(SharedTopologyType.SHARETYPE_SHARE)
    assert comp_1.shared_topology == SharedTopologyType.SHARETYPE_SHARE

    # Try to assign it to the entire design
    assert design.shared_topology is None
    with pytest.raises(ValueError, match="The design itself cannot have a shared topology."):
        design.set_shared_topology(SharedTopologyType.SHARETYPE_NONE)


def test_single_body_translation(modeler: Modeler):
    """Test for verifying the correct translation of a ``Body``.

    Notes
    -----
    Requires storing scdocx file and checking manually (for now).
    """
    # Create your design on the server side
    design = modeler.create_design("SingleBodyTranslation_Test")

    # Create 2 Sketch objects and draw a circle and a polygon (all client side)
    sketch_1 = Sketch()
    sketch_1.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))
    sketch_2 = Sketch()
    sketch_2.polygon(Point2D([-30, -30], UNITS.mm), Quantity(10, UNITS.mm), sides=5)

    # Build 2 independent components and bodies
    circle_comp = design.add_component("CircleComponent")
    body_circle_comp = circle_comp.extrude_sketch("Circle", sketch_1, Quantity(50, UNITS.mm))
    polygon_comp = design.add_component("PolygonComponent")
    body_polygon_comp = polygon_comp.extrude_sketch("Polygon", sketch_2, Quantity(30, UNITS.mm))

    body_circle_comp.translate(UnitVector3D([1, 0, 0]), Distance(50, UNITS.mm))
    body_polygon_comp.translate(UnitVector3D([-1, 1, -1]), Quantity(88, UNITS.mm))
    body_polygon_comp.translate(UnitVector3D([-1, 1, -1]), 101)


def test_bodies_translation(modeler: Modeler):
    """Test for verifying the correct translation of list of ``Body``.

    Notes
    -----
    Requires storing scdocx file and checking manually (for now).
    """
    # Create your design on the server side
    design = modeler.create_design("MultipleBodyTranslation_Test")

    # Create 2 Sketch objects and draw a circle and a polygon (all client side)
    sketch_1 = Sketch()
    sketch_1.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))
    sketch_2 = Sketch()
    sketch_2.polygon(Point2D([-30, -30], UNITS.mm), Quantity(10, UNITS.mm), sides=5)

    # Build 2 independent components and bodies
    circle_comp = design.add_component("CircleComponent")
    body_circle_comp = circle_comp.extrude_sketch("Circle", sketch_1, Quantity(50, UNITS.mm))
    polygon_comp = design.add_component("PolygonComponent")
    body_polygon_comp = polygon_comp.extrude_sketch("Polygon", sketch_2, Quantity(30, UNITS.mm))

    design.translate_bodies(
        [body_circle_comp, body_polygon_comp], UnitVector3D([1, 0, 0]), Distance(48, UNITS.mm)
    )
    design.translate_bodies(
        [body_circle_comp, body_polygon_comp], UnitVector3D([0, -1, 1]), Quantity(88, UNITS.mm)
    )
    design.translate_bodies([body_circle_comp, body_polygon_comp], UnitVector3D([0, -1, 1]), 101)

    # Try translating a body that does not belong to this component - no error thrown,
    # but no operation performed either.
    circle_comp.translate_bodies(
        [body_polygon_comp], UnitVector3D([0, -1, 1]), Quantity(88, UNITS.mm)
    )


def test_body_rotation(modeler: Modeler):
    """Test for verifying the correct rotation of a ``Body``."""
    # Create your design on the server side
    design = modeler.create_design("BodyRotation_Test")

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    original_vertices = []
    for edge in body.edges:
        original_vertices.extend([edge.shape.start, edge.shape.end])

    body.rotate(Point3D([0, 0, 0]), UnitVector3D([0, 0, 1]), np.pi / 4)

    new_vertices = []
    for edge in body.edges:
        new_vertices.extend([edge.shape.start, edge.shape.end])

    # Make sure no vertices are in the same position as in before rotation
    for old_vertex, new_vertex in zip(original_vertices, new_vertices):
        assert not np.allclose(old_vertex, new_vertex)


def test_download_file(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test for downloading a design in multiple modes and verifying the
    correct download.
    """
    # Create your design on the server side
    design = modeler.create_design("MultipleBodyTranslation_Test")

    # Create a Sketch object and draw a circle
    sketch = Sketch()
    sketch.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))

    # Extrude the sketch
    design.extrude_sketch(name="MyCylinder", sketch=sketch, distance=Quantity(50, UNITS.mm))

    # Download the design
    file = tmp_path_factory.mktemp("scdoc_files_download") / "dummy_folder" / "cylinder.scdocx"
    design.download(file)

    # Check that the file exists
    assert file.exists()

    # Check that we can also save it (even if it is not accessible on the server)
    if BackendType.is_linux_service(modeler.client.backend_type):
        file_save = "/tmp/cylinder-temp.scdocx"
    else:
        file_save = tmp_path_factory.mktemp("scdoc_files_save") / "cylinder.scdocx"

    design.save(file_location=file_save)

    # Check for other exports - Windows backend...
    if not BackendType.is_core_service(modeler.client.backend_type):
        binary_parasolid_file = tmp_path_factory.mktemp("scdoc_files_download") / "cylinder.x_b"
        text_parasolid_file = tmp_path_factory.mktemp("scdoc_files_download") / "cylinder.x_t"

        # Windows-only HOOPS exports for now
        step_file = tmp_path_factory.mktemp("scdoc_files_download") / "cylinder.stp"
        design.download(step_file, format=DesignFileFormat.STEP)
        assert step_file.exists()

        iges_file = tmp_path_factory.mktemp("scdoc_files_download") / "cylinder.igs"
        design.download(iges_file, format=DesignFileFormat.IGES)
        assert iges_file.exists()

    # Linux backend...
    else:
        binary_parasolid_file = tmp_path_factory.mktemp("scdoc_files_download") / "cylinder.xmt_bin"
        text_parasolid_file = tmp_path_factory.mktemp("scdoc_files_download") / "cylinder.xmt_txt"

    # FMD
    fmd_file = tmp_path_factory.mktemp("scdoc_files_download") / "cylinder.fmd"
    design.download(fmd_file, format=DesignFileFormat.FMD)
    assert fmd_file.exists()

    # PMDB
    pmdb_file = tmp_path_factory.mktemp("scdoc_files_download") / "cylinder.pmdb"

    design.download(binary_parasolid_file, format=DesignFileFormat.PARASOLID_BIN)
    design.download(text_parasolid_file, format=DesignFileFormat.PARASOLID_TEXT)
    design.download(pmdb_file, format=DesignFileFormat.PMDB)

    assert binary_parasolid_file.exists()
    assert text_parasolid_file.exists()
    assert pmdb_file.exists()


def test_upload_file(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test uploading a file to the server."""
    file = tmp_path_factory.mktemp("test_design") / "upload_example.scdocx"
    file_size = 1024

    # Write random bytes
    with file.open(mode="wb") as fout:
        fout.write(os.urandom(file_size))

    assert file.exists()

    # Upload file
    path_on_server = modeler._upload_file(file)
    assert path_on_server is not None


def test_stream_upload_file(tmp_path_factory: pytest.TempPathFactory):
    """Test uploading a file to the server."""
    # Define a new maximum message length
    import ansys.geometry.core.connection.defaults as pygeom_defaults

    old_value = pygeom_defaults.MAX_MESSAGE_LENGTH
    try:
        # Set the new maximum message length
        pygeom_defaults.MAX_MESSAGE_LENGTH = 1024**2  # 1 MB

        file = tmp_path_factory.mktemp("test_design") / "upload_stream_example.scdocx"
        file_size = 5 * 1024**2  # stream five messages

        # Write random bytes
        with file.open(mode="wb") as fout:
            fout.write(os.urandom(file_size))
        assert file.exists()

        # Upload file - necessary to import the Modeler class and create an instance
        from ansys.geometry.core import Modeler

        modeler = Modeler()
        path_on_server = modeler._upload_file_stream(file)
        assert path_on_server is not None
    finally:
        pygeom_defaults.MAX_MESSAGE_LENGTH = old_value


def test_slot_extrusion(modeler: Modeler):
    """Test the extrusion of a slot."""
    # Create your design on the server side
    design = modeler.create_design("ExtrudeSlot")

    # Create a Sketch object and draw a slot
    sketch = Sketch()
    sketch.slot(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(5, UNITS.mm))

    # Extrude the sketch
    body = design.extrude_sketch(name="MySlot", sketch=sketch, distance=Distance(50, UNITS.mm))

    # A slot has 6 faces and 12 edges
    assert len(body.faces) == 6
    assert len(body.edges) == 12


def test_project_and_imprint_curves(modeler: Modeler):
    """Test the projection of a set of curves on a body."""
    # Create your design on the server side
    design = modeler.create_design("ExtrudeSlot")
    comp = design.add_component("Comp1")

    # Create a Sketch object and draw a couple of slots
    imprint_sketch = Sketch()
    imprint_sketch.slot(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(5, UNITS.mm))
    imprint_sketch.slot(Point2D([50, 50], UNITS.mm), Quantity(10, UNITS.mm), Quantity(5, UNITS.mm))

    # Extrude the sketch
    sketch = Sketch()
    sketch.box(Point2D([0, 0], UNITS.mm), Quantity(150, UNITS.mm), Quantity(150, UNITS.mm))
    body = comp.extrude_sketch(name="MyBox", sketch=sketch, distance=Quantity(50, UNITS.mm))
    body_faces = body.faces

    body_copy = body.copy(design, "copy")

    # Project the curves on the box
    faces = body.project_curves(direction=UNITVECTOR3D_Z, sketch=imprint_sketch, closest_face=True)
    assert len(faces) == 1
    # With the previous dir, the curves will be imprinted on the
    # bottom face (closest one), i.e. the first one.
    assert faces[0].id == body_faces[0].id

    # If we now draw our curves on a higher plane, the upper face should be selected
    imprint_sketch_2 = Sketch(plane=Plane(Point3D([0, 0, 50], UNITS.mm)))
    imprint_sketch_2.slot(
        Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(5, UNITS.mm)
    )
    imprint_sketch_2.slot(
        Point2D([50, 50], UNITS.mm), Quantity(10, UNITS.mm), Quantity(5, UNITS.mm)
    )
    faces = body.project_curves(
        direction=UNITVECTOR3D_Z, sketch=imprint_sketch_2, closest_face=True
    )
    assert len(faces) == 1
    # With the previous dir, the curves will be imprinted on the
    # top face (closest one), i.e. the first one.
    assert faces[0].id == body_faces[1].id

    # Now, let's try projecting only a single curve (i.e. one of the slots only)
    faces = body.project_curves(
        direction=UNITVECTOR3D_Z, sketch=imprint_sketch_2, closest_face=True, only_one_curve=True
    )
    assert len(faces) == 1
    # With the previous dir, the curves will be imprinted on the
    # top face (closest one), i.e. the first one.
    assert faces[0].id == body_faces[1].id

    # Verify that the surface and curve types are of the correct type - related to PR
    # https://github.com/ansys/pyansys-geometry/pull/1096
    assert isinstance(faces[0].surface_type, SurfaceType)

    # Now once the previous curves have been projected, let's try imprinting our sketch
    #
    # It should generate two additional faces to our box = 6 + 2
    new_edges, new_faces = body.imprint_curves(faces=faces, sketch=imprint_sketch_2)

    assert len(new_faces) == 2
    assert len(body.faces) == 8

    # Verify that the surface and curve types are of the correct type - related to PR
    # https://github.com/ansys/pyansys-geometry/pull/1096
    assert isinstance(new_faces[0].surface_type, SurfaceType)
    assert isinstance(new_edges[0].curve_type, CurveType)

    # Make sure we have occurrence faces, not master
    assert faces[0].id not in [face.id for face in body._template.faces]
    assert new_faces[0].id not in [face.id for face in body._template.faces]

    faces = body_copy.imprint_projected_curves(
        direction=UNITVECTOR3D_Z, sketch=imprint_sketch, closest_face=True
    )
    assert len(faces) == 2
    assert len(body_copy.faces) == 8


def test_imprint_trimmed_curves(modeler: Modeler):
    """
    Test the imprinting of trimmed curves onto a specified face of a body.
    """
    unit = DEFAULT_UNITS.LENGTH

    wx = 1
    wy = 1
    wz = 1
    design = modeler.create_design("test imprint")

    # create box
    start_at = Point3D([wx / 2, wy / 2, 0.0], unit=unit)

    plane = Plane(
        start_at,
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )

    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0], unit=unit), width=wx, height=wy)
    box = design.extrude_sketch("box", box_plane, wz)

    assert len(box.faces) == 6
    assert len(box.edges) == 12

    # create cylinder
    point = Point3D([0.5, 0.5, 0.5])
    ortho_1, ortho_2 = UNITVECTOR3D_X, UNITVECTOR3D_Y
    plane = Plane(point, ortho_1, ortho_2)
    sketch_cylinder = Sketch(plane)
    sketch_cylinder.circle(Point2D([0.0, 0.0], unit=unit), radius=0.1)
    cylinder = design.extrude_sketch("cylinder", sketch_cylinder, 0.5)

    edges = cylinder.faces[1].edges
    trimmed_curves = [edges[0].shape]
    new_edges, new_faces = box.imprint_curves(faces=[box.faces[1]], trimmed_curves=trimmed_curves)

    # the new edge is coming from the circular top edge of the cylinder.
    assert new_edges[0].start == new_edges[0].end
    # verify that there is one new edge coming from the circle.
    assert len(new_faces) == 1
    # verify that there is one new face coming from the circle.
    assert len(new_edges) == 1
    # verify that there are 7 faces in total.
    assert len(box.faces) == 7
    # verify that there are 14 edges in total.
    assert len(box.edges) == 13


def test_copy_body(modeler: Modeler):
    """Test copying a body."""
    # Create your design on the server side
    design = modeler.create_design("Design")

    sketch_1 = Sketch().circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))
    body = design.extrude_sketch("Original", sketch_1, Distance(1, UNITS.mm))

    # Copy body at same design level
    copy = body.copy(design, "Copy")
    assert len(design.bodies) == 2
    assert design.bodies[-1].id == copy.id

    # Bodies should be distinct
    assert body.id != copy.id
    assert body != copy

    # Copy body into sub-component
    comp1 = design.add_component("comp1")
    copy2 = body.copy(comp1, "Subcopy")
    assert len(comp1.bodies) == 1
    assert comp1.bodies[-1].id == copy2.id

    # Bodies should be distinct
    assert body.id != copy2.id
    assert body != copy2

    # Copy a copy
    comp2 = comp1.add_component("comp2")
    copy3 = copy2.copy(comp2, "Copy3")
    assert len(comp2.bodies) == 1
    assert comp2.bodies[-1].id == copy3.id

    # Bodies should be distinct
    assert copy2.id != copy3.id
    assert copy2 != copy3

    # Ensure deleting original doesn't affect the copies
    design.delete_body(body)
    assert not body.is_alive
    assert copy.is_alive


def test_beams(modeler: Modeler):
    """Test beam creation."""
    # Create your design on the server side
    design = modeler.create_design("BeamCreation")

    circle_profile_1 = design.add_beam_circular_profile(
        "CircleProfile1", Quantity(10, UNITS.mm), Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_Y
    )

    assert circle_profile_1.id is not None
    assert circle_profile_1.center == Point3D([0, 0, 0])
    assert circle_profile_1.radius.value.m_as(DEFAULT_UNITS.LENGTH) == 0.01
    assert circle_profile_1.direction_x == UNITVECTOR3D_X
    assert circle_profile_1.direction_y == UNITVECTOR3D_Y

    circle_profile_2 = design.add_beam_circular_profile(
        "CircleProfile2",
        Distance(20, UNITS.mm),
        Point3D([10, 20, 30], UNITS.mm),
        UnitVector3D([1, 1, 1]),
        UnitVector3D([0, -1, 1]),
    )

    assert circle_profile_2.id is not None
    assert circle_profile_2.id is not circle_profile_1.id

    with pytest.raises(ValueError, match="Radius must be a real positive value."):
        design.add_beam_circular_profile(
            "InvalidProfileRadius",
            Quantity(-10, UNITS.mm),
            Point3D([0, 0, 0]),
            UNITVECTOR3D_X,
            UNITVECTOR3D_Y,
        )

    with pytest.raises(ValueError, match="Direction X and direction Y must be perpendicular."):
        design.add_beam_circular_profile(
            "InvalidUnitVectorAlignment",
            Quantity(10, UNITS.mm),
            Point3D([0, 0, 0]),
            UNITVECTOR3D_X,
            UnitVector3D([-1, -1, -1]),
        )

    # Create a beam at the root component level
    beam_1 = design.create_beam(
        Point3D([9, 99, 999], UNITS.mm), Point3D([8, 88, 888], UNITS.mm), circle_profile_1
    )

    assert beam_1.id is not None
    assert beam_1.start == Point3D([9, 99, 999], UNITS.mm)
    assert beam_1.end == Point3D([8, 88, 888], UNITS.mm)
    assert beam_1.profile == circle_profile_1
    assert beam_1.parent_component.id == design.id
    assert beam_1.is_alive
    assert len(design.beams) == 1
    assert design.beams[0] == beam_1

    beam_1_str = str(beam_1)
    assert "ansys.geometry.core.designer.Beam" in beam_1_str
    assert "  Exists               : True" in beam_1_str
    assert "  Start                : [0.009" in beam_1_str
    assert "  End                  : [0.008" in beam_1_str
    assert "  Parent component     : BeamCreation" in beam_1_str
    assert "  Beam Profile info" in beam_1_str
    assert "  -----------------" in beam_1_str
    assert "ansys.geometry.core.designer.BeamCircularProfile " in beam_1_str
    assert "  Name                 : CircleProfile1" in beam_1_str
    assert "  Radius               : 10.0 millimeter" in beam_1_str
    assert "  Center               : [0.0,0.0,0.0] in meters" in beam_1_str
    assert "  Direction x          : [1.0,0.0,0.0]" in beam_1_str
    assert "  Direction y          : [0.0,1.0,0.0]" in beam_1_str

    # Now, let's create two beams at a nested component, with the same profile
    nested_component = design.add_component("NestedComponent")
    beam_2 = nested_component.create_beam(
        Point3D([7, 77, 777], UNITS.mm), Point3D([6, 66, 666], UNITS.mm), circle_profile_2
    )
    beam_3 = nested_component.create_beam(
        Point3D([8, 88, 888], UNITS.mm), Point3D([7, 77, 777], UNITS.mm), circle_profile_2
    )

    assert beam_2.id is not None
    assert beam_2.profile == circle_profile_2
    assert beam_2.parent_component.id == nested_component.id
    assert beam_2.is_alive
    assert beam_3.id is not None
    assert beam_3.profile == circle_profile_2
    assert beam_3.parent_component.id == nested_component.id
    assert beam_3.is_alive
    assert beam_2.id != beam_3.id
    assert len(nested_component.beams) == 2
    assert nested_component.beams[0] == beam_2
    assert nested_component.beams[1] == beam_3

    # Once the beams are created, let's try deleting it.
    # For example, we shouldn't be able to delete beam_1 from the nested component.
    nested_component.delete_beam(beam_1)

    assert beam_2.is_alive
    assert nested_component.beams[0].is_alive
    assert beam_3.is_alive
    assert nested_component.beams[1].is_alive
    assert beam_1.is_alive
    assert design.beams[0].is_alive

    # Let's try deleting one of the beams from the nested component
    nested_component.delete_beam(beam_2)
    assert not beam_2.is_alive
    assert not nested_component.beams[0].is_alive
    assert beam_3.is_alive
    assert nested_component.beams[1].is_alive
    assert beam_1.is_alive
    assert design.beams[0].is_alive

    # Now, let's try deleting it from the design directly - this should be possible
    design.delete_beam(beam_3)
    assert not beam_2.is_alive
    assert not nested_component.beams[0].is_alive
    assert not beam_3.is_alive
    assert not nested_component.beams[1].is_alive
    assert beam_1.is_alive
    assert design.beams[0].is_alive

    # Finally, let's delete the beam from the root component
    design.delete_beam(beam_1)
    assert not beam_2.is_alive
    assert not nested_component.beams[0].is_alive
    assert not beam_3.is_alive
    assert not nested_component.beams[1].is_alive
    assert not beam_1.is_alive
    assert not design.beams[0].is_alive

    # Now, let's try deleting the beam profiles!
    assert len(design.beam_profiles) == 2
    design.delete_beam_profile("MyInventedBeamProfile")
    assert len(design.beam_profiles) == 2
    design.delete_beam_profile(circle_profile_1)
    assert len(design.beam_profiles) == 1
    design.delete_beam_profile(circle_profile_2)
    assert len(design.beam_profiles) == 0


def test_midsurface_properties(modeler: Modeler):
    """Test mid-surface properties assignment."""
    # Create your design on the server side
    design = modeler.create_design("MidSurfaceProperties")

    # Create a Sketch object and draw a slot
    sketch = Sketch()
    sketch.slot(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(5, UNITS.mm))

    # Create an actual body from the slot, and translate it
    slot_body = design.extrude_sketch("MySlot", sketch, Quantity(10, UNITS.mm))
    slot_body.translate(UNITVECTOR3D_X, Quantity(40, UNITS.mm))

    # Create a surface body as well
    slot_surf = design.create_surface("MySlotSurface", sketch)

    surf_repr = str(slot_surf)
    assert "ansys.geometry.core.designer.Body" in surf_repr
    assert "Name                 : MySlotSurface" in surf_repr
    assert "Exists               : True" in surf_repr
    assert "Parent component     : MidSurfaceProperties" in surf_repr
    assert "Surface body         : True" in surf_repr
    assert "Surface thickness    : None" in surf_repr
    assert "Surface offset       : None" in surf_repr
    assert f"Color                : {DEFAULT_COLOR}" in surf_repr

    # Let's assign a thickness to both bodies
    design.add_midsurface_thickness(
        thickness=Quantity(10, UNITS.mm),
        bodies=[slot_body, slot_surf],
    )

    # Let's also assign a mid-surface offset to both bodies
    design.add_midsurface_offset(
        offset_type=MidSurfaceOffsetType.TOP, bodies=[slot_body, slot_surf]
    )

    # Let's check the values now
    assert slot_body.surface_thickness is None
    assert slot_body.surface_offset is None
    assert slot_surf.surface_thickness == Quantity(10, UNITS.mm)
    assert slot_surf.surface_offset == MidSurfaceOffsetType.TOP

    # Let's check that the design-stored values are also updated
    assert design.bodies[0].surface_thickness is None
    assert design.bodies[0].surface_offset is None
    assert design.bodies[1].surface_thickness == Quantity(10, UNITS.mm)
    assert design.bodies[1].surface_offset == MidSurfaceOffsetType.TOP

    surf_repr = str(slot_surf)
    assert "ansys.geometry.core.designer.Body" in surf_repr
    assert "Name                 : MySlotSurface" in surf_repr
    assert "Exists               : True" in surf_repr
    assert "Parent component     : MidSurfaceProperties" in surf_repr
    assert "Surface body         : True" in surf_repr
    assert "Surface thickness    : 10 millimeter" in surf_repr
    assert "Surface offset       : MidSurfaceOffsetType.TOP" in surf_repr
    assert f"Color                : {DEFAULT_COLOR}" in surf_repr

    # Let's try reassigning values directly to slot_body - this shouldn't do anything
    slot_body.add_midsurface_thickness(Quantity(10, UNITS.mm))
    slot_body.add_midsurface_offset(MidSurfaceOffsetType.TOP)

    body_repr = str(slot_body)
    assert "ansys.geometry.core.designer.Body" in body_repr
    assert "Name                 : MySlot" in body_repr
    assert "Exists               : True" in body_repr
    assert "Parent component     : MidSurfaceProperties" in body_repr
    assert "Surface body         : False" in body_repr
    assert f"Color                : {DEFAULT_COLOR}" in surf_repr
    assert slot_body.surface_thickness is None
    assert slot_body.surface_offset is None

    # Let's try reassigning values directly to slot_surf - this should work
    # TODO :  at the moment the server does not allow to reassign - put in try/catch block
    # https://github.com/ansys/pyansys-geometry/issues/1146
    try:
        slot_surf.add_midsurface_thickness(Quantity(30, UNITS.mm))
        slot_surf.add_midsurface_offset(MidSurfaceOffsetType.BOTTOM)

        surf_repr = str(slot_surf)
        assert "ansys.geometry.core.designer.Body" in surf_repr
        assert "Name                 : MySlotSurface" in surf_repr
        assert "Exists               : True" in surf_repr
        assert "Parent component     : MidSurfaceProperties" in surf_repr
        assert "Surface body         : True" in surf_repr
        assert "Surface thickness    : 30 millimeter" in surf_repr
        assert "Surface offset       : MidSurfaceOffsetType.BOTTOM" in surf_repr
        assert f"Color                : {DEFAULT_COLOR}" in surf_repr
    except GeometryExitedError:
        pass

    # Let's create a new surface body and assign them from body methods directly
    slot_surf2 = design.create_surface("MySlotSurface2", sketch)

    slot_surf2.add_midsurface_thickness(Quantity(30, UNITS.mm))
    slot_surf2.add_midsurface_offset(MidSurfaceOffsetType.BOTTOM)

    surf_repr = str(slot_surf2)
    assert "ansys.geometry.core.designer.Body" in surf_repr
    assert "Name                 : MySlotSurface2" in surf_repr
    assert "Exists               : True" in surf_repr
    assert "Parent component     : MidSurfaceProperties" in surf_repr
    assert "Surface body         : True" in surf_repr
    assert "Surface thickness    : 30 millimeter" in surf_repr
    assert "Surface offset       : MidSurfaceOffsetType.BOTTOM" in surf_repr
    assert f"Color                : {DEFAULT_COLOR}" in surf_repr


def test_design_points(modeler: Modeler):
    """Test for verifying the ``DesignPoints``"""
    # Create your design on the server side
    design = modeler.create_design("DesignPoints")
    point = Point3D([6, 66, 666], UNITS.mm)
    design_points_1 = design.add_design_point("FirstPointSet", point)

    # Check the design points
    assert len(design.design_points) == 1
    assert design_points_1.id is not None
    assert design_points_1.name == "FirstPointSet"
    assert design_points_1.value == point

    # Create another set of design points
    point_set_2 = [Point3D([10, 10, 10], UNITS.m), Point3D([20, 20, 20], UNITS.m)]
    design_points_2 = design.add_design_points("SecondPointSet", point_set_2)

    assert len(design.design_points) == 3

    nested_component = design.add_component("NestedComponent")
    design_point_3 = nested_component.add_design_point("Nested", Point3D([7, 77, 777], UNITS.mm))

    assert design_point_3.id is not None
    assert design_point_3.value == Point3D([7, 77, 777], UNITS.mm)
    assert design_point_3.parent_component.id == nested_component.id
    assert len(nested_component.design_points) == 1
    assert nested_component.design_points[0] == design_point_3

    design_point_1_str = str(design_points_1)
    assert "ansys.geometry.core.designer.DesignPoint" in design_point_1_str
    assert "  Name                 : FirstPointSet" in design_point_1_str
    assert "  Design Point         : [0.006 0.066 0.666]" in design_point_1_str

    design_point_2_str = str(design_points_2)
    assert "ansys.geometry.core.designer.DesignPoint" in design_point_2_str
    assert "  Name                 : SecondPointSet" in design_point_2_str
    assert "  Design Point         : [10. 10. 10.]" in design_point_2_str
    assert "ansys.geometry.core.designer.DesignPoint" in design_point_2_str
    assert "  Name                 : SecondPointSet" in design_point_2_str
    assert "  Design Point         : [20. 20. 20.]" in design_point_2_str

    # SKIPPING IF GRAPHICS REQUIRED
    if are_graphics_available():
        # make sure it can create polydata
        pd = design_points_1._to_polydata()

        import pyvista as pv

        assert isinstance(pd, pv.PolyData)


def test_named_selections_beams(modeler: Modeler):
    """Test for verifying the correct creation of ``NamedSelection`` with
    beams.
    """
    # Create your design on the server side
    design = modeler.create_design("NamedSelectionBeams_Test")

    # Test creating a named selection out of beams
    circle_profile_1 = design.add_beam_circular_profile(
        "CircleProfile1", Quantity(10, UNITS.mm), Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_Y
    )
    beam_1 = design.create_beam(
        Point3D([9, 99, 999], UNITS.mm), Point3D([8, 88, 888], UNITS.mm), circle_profile_1
    )
    ns_beams = design.create_named_selection("CircleProfile", beams=[beam_1])
    assert len(design.named_selections) == 1
    assert design.named_selections[0].name == "CircleProfile"

    # Try deleting this named selection
    design.delete_named_selection(ns_beams)
    assert len(design.named_selections) == 0


def test_named_selections_design_points(modeler: Modeler):
    """Test for verifying the correct creation of ``NamedSelection`` with
    design points.
    """
    # Create your design on the server side
    design = modeler.create_design("NamedSelectionDesignPoints_Test")

    # Test creating a named selection out of design_points
    point_set_1 = Point3D([10, 10, 0], UNITS.m)
    design_points_1 = design.add_design_point("FirstPointSet", point_set_1)
    ns_despoint = design.create_named_selection("FirstPointSet", design_points=[design_points_1])
    assert len(design.named_selections) == 1
    assert design.named_selections[0].name == "FirstPointSet"

    # Try deleting this named selection
    design.delete_named_selection(ns_despoint)
    assert len(design.named_selections) == 0


def test_component_instances(modeler: Modeler):
    """Test creation of ``Component`` instances and the effects this has."""
    design_name = "ComponentInstance_Test"
    design = modeler.create_design(design_name)

    # Create a car
    car1 = design.add_component("Car1")
    comp1 = car1.add_component("A")
    comp2 = car1.add_component("B")
    wheel1 = comp2.add_component("Wheel1")

    # Create car base frame
    sketch = Sketch().box(Point2D([5, 10]), 10, 20)
    comp2.extrude_sketch("Base", sketch, 5)

    # Create first wheel
    sketch = Sketch(Plane(direction_x=Vector3D([0, 1, 0]), direction_y=Vector3D([0, 0, 1])))
    sketch.circle(Point2D([0, 0]), 5)
    wheel1.extrude_sketch("Wheel", sketch, -5)

    # Create 3 other wheels and move them into position
    rotation_origin = Point3D([0, 0, 0])
    rotation_direction = UnitVector3D([0, 0, 1])

    wheel2 = comp2.add_component("Wheel2", wheel1)
    wheel2.modify_placement(Vector3D([0, 20, 0]))

    wheel3 = comp2.add_component("Wheel3", wheel1)
    wheel3.modify_placement(Vector3D([10, 0, 0]), rotation_origin, rotation_direction, np.pi)

    wheel4 = comp2.add_component("Wheel4", wheel1)
    wheel4.modify_placement(Vector3D([10, 20, 0]), rotation_origin, rotation_direction, np.pi)

    # Assert all components have unique IDs
    comp_ids = [wheel1.id, wheel2.id, wheel3.id, wheel4.id]
    assert len(comp_ids) == len(set(comp_ids))

    # Assert all bodies have unique IDs
    body_ids = [wheel1.bodies[0].id, wheel2.bodies[0].id, wheel3.bodies[0].id, wheel4.bodies[0].id]
    assert len(body_ids) == len(set(body_ids))

    # Assert all instances have unique MasterComponents
    comp_templates = [wheel2._master_component, wheel3._master_component, wheel4._master_component]
    assert len(comp_templates) == len(set(comp_templates))

    # Assert all instances have the same Part
    comp_parts = [
        wheel2._master_component.part,
        wheel3._master_component.part,
        wheel4._master_component.part,
    ]
    assert len(set(comp_parts)) == 1

    assert wheel1.get_world_transform() == IDENTITY_MATRIX44
    assert wheel2.get_world_transform() != IDENTITY_MATRIX44

    # Create 2nd car
    car2 = design.add_component("Car2", car1)
    car2.modify_placement(Vector3D([30, 0, 0]))

    # Create top of car - applies to BOTH cars
    sketch = Sketch(Plane(Point3D([0, 5, 5]))).box(Point2D([5, 2.5]), 10, 5)
    comp1.extrude_sketch("Top", sketch, 5)

    # Show the body also got added to Car2, and they are distinct, but
    # not independent
    assert car1.components[0].bodies[0].id != car2.components[0].bodies[0].id

    # If monikers were formatted properly, you should be able to use them
    assert len(car2.components[1].components[1].bodies[0].faces) > 0


def test_boolean_body_operations(modeler: Modeler):
    """
    Test cases:

    1) master/master
        a) intersect
            i) normal
                x) identity
                y) transform
            ii) empty failure
        b) subtract
            i) normal
                x) identity
                y) transform
            ii) empty failure
            iii) disjoint
        c) unite
            i) normal
                x) identity
                y) transform
            ii) disjoint
    2) instance/instance
        a) intersect
            i) normal
                x) identity
                y) transform
            ii) empty failure
        b) subtract
            i) normal
                x) identity
                y) transform
            ii) empty failure
        c) unite
            i) normal
                x) identity
                y) transform
    """
    design = modeler.create_design("TestBooleanOperations")

    comp1 = design.add_component("Comp1")
    comp2 = design.add_component("Comp2")
    comp3 = design.add_component("Comp3")

    body1 = comp1.extrude_sketch("Body1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    body2 = comp2.extrude_sketch("Body2", Sketch().box(Point2D([0.5, 0]), 1, 1), 1)
    body3 = comp3.extrude_sketch("Body3", Sketch().box(Point2D([5, 0]), 1, 1), 1)

    # 1.a.i.x
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy1.intersect(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

    # 1.a.i.y
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.intersect(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.25)

    # 1.a.ii
    copy1 = body1.copy(comp1, "Copy1")
    copy3 = body3.copy(comp3, "Copy3")
    with pytest.raises(ValueError, match="bodies do not intersect"):
        copy1.intersect(copy3)

    assert copy1.is_alive
    assert copy3.is_alive

    # 1.b.i.x
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy1.subtract(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

    # 1.b.i.y
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.subtract(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.75)

    # 1.b.ii
    copy1 = body1.copy(comp1, "Copy1")
    copy1a = body1.copy(comp1, "Copy1a")
    with pytest.raises(ValueError):
        copy1.subtract(copy1a)

    assert copy1.is_alive
    assert copy1a.is_alive

    # 1.b.iii
    copy1 = body1.copy(comp1, "Copy1")
    copy3 = body3.copy(comp3, "Copy3")
    copy1.subtract(copy3)

    assert Accuracy.length_is_equal(copy1.volume.m, 1)
    assert copy1.volume
    assert not copy3.is_alive

    # 1.c.i.x
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy1.unite(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1.5)

    # 1.c.i.y
    copy1 = body1.copy(comp1, "Copy1")
    copy2 = body2.copy(comp2, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.unite(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1.75)

    # 1.c.ii
    copy1 = body1.copy(comp1, "Copy1")
    copy3 = body3.copy(comp3, "Copy3")
    copy1.unite(copy3)

    assert not copy3.is_alive
    assert body3.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1)

    # Test instance/instance
    comp1_i = design.add_component("Comp1_i", comp1)
    comp2_i = design.add_component("Comp2_i", comp2)
    comp3_i = design.add_component("Comp3_i", comp3)

    comp1_i.modify_placement(
        Vector3D([52, 61, -43]), Point3D([-4, 26, 66]), UnitVector3D([-21, 20, 87]), np.pi / 4
    )
    comp2_i.modify_placement(
        Vector3D([52, 61, -43]), Point3D([-4, 26, 66]), UnitVector3D([-21, 20, 87]), np.pi / 4
    )
    comp3_i.modify_placement(
        Vector3D([52, 61, -43]), Point3D([-4, 26, 66]), UnitVector3D([-21, 20, 87]), np.pi / 4
    )

    body1 = comp1_i.bodies[0]
    body2 = comp2_i.bodies[0]
    body3 = comp3_i.bodies[0]

    # 2.a.i.x
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy1.intersect(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

    # 2.a.i.y
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.intersect(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.25)

    # 2.a.ii
    copy1 = body1.copy(comp1_i, "Copy1")
    copy3 = body3.copy(comp3_i, "Copy3")
    with pytest.raises(ValueError, match="bodies do not intersect"):
        copy1.intersect(copy3)

    assert copy1.is_alive
    assert copy3.is_alive

    # 2.b.i.x
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy1.subtract(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

    # 2.b.i.y
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.subtract(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 0.75)

    # 2.b.ii
    copy1 = body1.copy(comp1_i, "Copy1")
    copy1a = body1.copy(comp1_i, "Copy1a")
    with pytest.raises(ValueError):
        copy1.subtract(copy1a)

    assert copy1.is_alive
    assert copy1a.is_alive

    # 2.b.iii
    copy1 = body1.copy(comp1_i, "Copy1")
    copy3 = body3.copy(comp3_i, "Copy3")
    copy1.subtract(copy3)

    assert Accuracy.length_is_equal(copy1.volume.m, 1)
    assert copy1.volume
    assert not copy3.is_alive

    # 2.c.i.x
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy1.unite(copy2)

    assert not copy2.is_alive
    assert body2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1.5)

    # 2.c.i.y
    copy1 = body1.copy(comp1_i, "Copy1")
    copy2 = body2.copy(comp2_i, "Copy2")
    copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
    copy1.unite(copy2)

    assert not copy2.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1.75)

    # 2.c.ii
    copy1 = body1.copy(comp1_i, "Copy1")
    copy3 = body3.copy(comp3_i, "Copy3")
    copy1.unite(copy3)

    assert not copy3.is_alive
    assert body3.is_alive
    assert Accuracy.length_is_equal(copy1.volume.m, 1)


def test_multiple_bodies_boolean_operations(modeler: Modeler):
    """Test boolean operations with multiple bodies."""
    design = modeler.create_design("TestBooleanOperationsMultipleBodies")

    comp1 = design.add_component("Comp1")
    comp2 = design.add_component("Comp2")
    comp3 = design.add_component("Comp3")

    body1 = comp1.extrude_sketch("Body1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    body2 = comp2.extrude_sketch("Body2", Sketch().box(Point2D([0.5, 0]), 1, 1), 1)
    body3 = comp3.extrude_sketch("Body3", Sketch().box(Point2D([5, 0]), 1, 1), 1)

    ################# Check subtract operation #################
    copy1_sub = body1.copy(comp1, "Copy1_subtract")
    copy2_sub = body2.copy(comp2, "Copy2_subtract")
    copy3_sub = body3.copy(comp3, "Copy3_subtract")
    copy1_sub.subtract([copy2_sub, copy3_sub])

    assert not copy2_sub.is_alive
    assert not copy3_sub.is_alive
    assert body2.is_alive
    assert body3.is_alive
    assert len(comp1.bodies) == 2
    assert len(comp2.bodies) == 1
    assert len(comp3.bodies) == 1

    # Cleanup previous subtest
    comp1.delete_body(copy1_sub)
    assert len(comp1.bodies) == 1

    ################# Check unite operation #################
    copy1_uni = body1.copy(comp1, "Copy1_unite")
    copy2_uni = body2.copy(comp2, "Copy2_unite")
    copy3_uni = body3.copy(comp3, "Copy3_unite")
    copy1_uni.unite([copy2_uni, copy3_uni])

    assert not copy2_uni.is_alive
    assert not copy3_uni.is_alive
    assert body2.is_alive
    assert body3.is_alive
    assert len(comp1.bodies) == 2
    assert len(comp2.bodies) == 1
    assert len(comp3.bodies) == 1

    # Cleanup previous subtest
    comp1.delete_body(copy1_uni)
    assert len(comp1.bodies) == 1

    ################# Check intersect operation #################
    copy1_int = body1.copy(comp1, "Copy1_intersect")
    copy2_int = body2.copy(comp2, "Copy2_intersect")
    copy3_int = body3.copy(comp3, "Copy3_intersect")  # Body 3 does not intersect them
    copy1_int.intersect([copy2_int])

    assert not copy2_int.is_alive
    assert copy3_int.is_alive
    assert body2.is_alive
    assert body3.is_alive
    assert len(comp1.bodies) == 2
    assert len(comp2.bodies) == 1
    assert len(comp3.bodies) == 2

    # Cleanup previous subtest
    comp1.delete_body(copy1_int)
    comp3.delete_body(copy3_int)
    assert len(comp1.bodies) == 1
    assert len(comp3.bodies) == 1


def test_bool_operations_with_keep_other(modeler: Modeler):
    """Test boolean operations with keep other option."""
    # Create the design and bodies
    design = modeler.create_design("TestBooleanOperationsWithKeepOther")

    comp1 = design.add_component("Comp1")
    comp2 = design.add_component("Comp2")
    comp3 = design.add_component("Comp3")

    body1 = comp1.extrude_sketch("Body1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    body2 = comp2.extrude_sketch("Body2", Sketch().box(Point2D([0.5, 0]), 1, 1), 1)
    body3 = comp3.extrude_sketch("Body3", Sketch().box(Point2D([5, 0]), 1, 1), 1)

    # ---- Verify subtract operation ----
    body1.subtract([body2, body3], keep_other=True)

    assert body2.is_alive
    assert body3.is_alive
    assert len(comp1.bodies) == 1
    assert len(comp2.bodies) == 1
    assert len(comp3.bodies) == 1

    # ---- Verify unite operation ----
    body1.unite([body2, body3], keep_other=True)

    assert body2.is_alive
    assert body3.is_alive
    assert len(comp1.bodies) == 1
    assert len(comp2.bodies) == 1
    assert len(comp3.bodies) == 1

    # ---- Verify intersect operation ----
    body1.intersect(body2, keep_other=True)

    assert body1.is_alive
    assert body2.is_alive
    assert body3.is_alive
    assert len(comp1.bodies) == 1
    assert len(comp2.bodies) == 1
    assert len(comp3.bodies) == 1


def test_child_component_instances(modeler: Modeler):
    """Test creation of child ``Component`` instances and check the data model
    reflects that.
    """
    design_name = "ChildComponentInstances_Test"
    design = modeler.create_design(design_name)
    # Create a base component
    base1 = design.add_component("Base1")
    comp1 = base1.add_component("A")
    comp2 = base1.add_component("B")

    # Create the solid body for the base
    sketch = Sketch().box(Point2D([5, 10]), 10, 20)
    comp2.extrude_sketch("Bottom", sketch, 5)

    # Create the 2nd base
    base2 = design.add_component("Base2", base1)
    base2.modify_placement(Vector3D([30, 0, 0]))

    # Create top part (applies to both Base1 and Base2)
    sketch = Sketch(Plane(Point3D([0, 5, 5]))).box(Point2D([5, 2.5]), 10, 5)
    comp1.extrude_sketch("Top", sketch, 5)

    # create the first child component
    comp1.add_component("Child1")
    comp1.extrude_sketch("Child1_body", Sketch(Plane([5, 7.5, 10])).box(Point2D([0, 0]), 1, 1), 1)

    assert len(comp1.components) == 1
    assert len(base2.components[0].components) == 1
    assert len(comp1.components) == len(base2.components[0].components)

    # create the second child component
    comp1.add_component("Child2")
    comp1.extrude_sketch("Child2_body", Sketch(Plane([5, 7.5, 10])).box(Point2D([0, 0]), 1, 1), -1)

    assert len(comp1.components) == 2
    assert len(base2.components[0].components) == 2
    assert len(comp1.components) == len(base2.components[0].components)


def test_multiple_designs(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Generate multiple designs, make sure they are all separate, and once
    a design is deactivated, the next one is activated.
    """
    # Initiate expected output images
    scshot_dir = tmp_path_factory.mktemp("test_multiple_designs")
    scshot_1 = scshot_dir / "design1.png"
    scshot_2 = scshot_dir / "design2.png"

    # Create your design on the server side
    design1 = modeler.create_design("Design1")

    # Create a Sketch object and draw a slot
    sketch1 = Sketch()
    sketch1.slot(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(5, UNITS.mm))

    # Extrude the sketch to create a body
    design1.extrude_sketch("MySlot", sketch1, Quantity(10, UNITS.mm))

    # SKIPPING IF GRAPHICS REQUIRED
    if are_graphics_available():
        # Request plotting and store images
        design1.plot(screenshot=scshot_1)

    # Create a second design
    design2 = modeler.create_design("Design2")

    # Create a Sketch object and draw a rectangle
    sketch2 = Sketch()
    sketch2.box(Point2D([-30, -30], UNITS.mm), 5 * UNITS.mm, 8 * UNITS.mm)

    # Extrude the sketch to create a body
    design2.extrude_sketch("MyRectangle", sketch2, Quantity(10, UNITS.mm))

    # SKIPPING IF GRAPHICS REQUIRED
    if are_graphics_available():
        # Request plotting and store images
        design2.plot(screenshot=scshot_2)

        # Check that the images are different
        assert scshot_1.exists()
        assert scshot_2.exists()

        from pyvista.plotting.utilities.regression import compare_images as pv_compare_images

        err = pv_compare_images(str(scshot_1), str(scshot_2))
        assert not err < 0.1

    # Check that design1 is not active and design2 is active
    assert not design1.is_active
    assert design2.is_active


def test_get_active_design(modeler: Modeler):
    """Return the active design from the designs dictionary of the modeler."""
    design1 = modeler.create_design("Design1")
    d1_id = design1.design_id
    active_design = modeler.get_active_design()
    assert active_design.design_id == d1_id


def test_get_collision(modeler: Modeler):
    """Test the collision state between two bodies."""
    design = modeler.open_file(FILES_DIR / "MixingTank.scdocx")
    body1 = design.bodies[0]
    body2 = design.bodies[1]
    body3 = design.bodies[2]

    assert body1.get_collision(body2) == CollisionType.TOUCH
    assert body2.get_collision(body3) == CollisionType.NONE


def test_set_body_name(modeler: Modeler):
    """Test the setting the name of a body."""
    design = modeler.create_design("simple_cube")
    unit = DEFAULT_UNITS.LENGTH
    plane = Plane(
        Point3D([1 / 2, 1 / 2, 0.0], unit=unit),
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )
    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0]), width=1 * unit, height=1 * unit)
    box = design.extrude_sketch("first_name", box_plane, 1 * unit)
    assert box.name == "first_name"
    box.set_name("updated_name")
    assert box.name == "updated_name"
    box.name = "updated_name2"
    assert box.name == "updated_name2"


def test_set_fill_style(modeler: Modeler):
    """Test the setting the fill style of a body."""
    design = modeler.create_design("RVE")
    unit = DEFAULT_UNITS.LENGTH

    plane = Plane(
        Point3D([1 / 2, 1 / 2, 0.0], unit=unit),
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )

    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0]), width=1 * unit, height=1 * unit)
    box = design.extrude_sketch("Matrix", box_plane, 1 * unit)

    assert box.fill_style == FillStyle.DEFAULT
    box.set_fill_style(FillStyle.TRANSPARENT)
    assert box.fill_style == FillStyle.TRANSPARENT
    box.fill_style = FillStyle.OPAQUE
    assert box.fill_style == FillStyle.OPAQUE


def test_body_suppression(modeler: Modeler):
    """Test the suppression of a body."""

    design = modeler.create_design("RVE")
    unit = DEFAULT_UNITS.LENGTH

    plane = Plane(
        Point3D([1 / 2, 1 / 2, 0.0], unit=unit),
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )

    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0]), width=1 * unit, height=1 * unit)
    box = design.extrude_sketch("Matrix", box_plane, 1 * unit)

    assert box.is_suppressed is False
    box.set_suppressed(True)
    assert box.is_suppressed is True
    box.is_suppressed = False
    assert box.is_suppressed is False


def test_set_body_color(modeler: Modeler):
    """Test the getting and setting of body color."""

    design = modeler.create_design("RVE2")
    unit = DEFAULT_UNITS.LENGTH

    plane = Plane(
        Point3D([1 / 2, 1 / 2, 0.0], unit=unit),
        UNITVECTOR3D_X,
        UNITVECTOR3D_Y,
    )
    box_plane = Sketch(plane)
    box_plane.box(Point2D([0.0, 0.0]), width=1 * unit, height=1 * unit)
    box = design.extrude_sketch("Block", box_plane, 1 * unit)

    # Default body color is if it is not set on server side.
    assert box.color == DEFAULT_COLOR

    # Set the color of the body using hex code.
    box.color = "#0000ff"
    assert box.color[0:7] == "#0000ff"

    box.color = "#ffc000"
    assert box.color[0:7] == "#ffc000"

    # Set the color of the body using color name.
    box.set_color("green")
    box.color[0:7] == "#008000"

    # Set the color of the body using RGB values between (0,1) as floats.
    box.set_color((1.0, 0.0, 0.0))
    box.color[0:7] == "#ff0000"

    # Set the color of the body using RGB values between (0,255) as integers).
    box.set_color((0, 255, 0))
    box.color[0:7] == "#00ff00"

    # Assigning color object directly
    blue_color = mcolors.to_rgba("#0000FF")
    box.color = blue_color
    assert box.color[0:7] == "#0000ff"

    # Test an RGBA color
    box.color = "#ff00003c"
    assert box.color == "#ff00003c"

    # Test setting the opacity separately
    box.opacity = 0.8
    assert box.color == "#ff0000cc"

    # Try setting the opacity to an invalid value
    with pytest.raises(
        ValueError, match="Invalid color value: Opacity value must be between 0 and 1."
    ):
        box.opacity = 255


def test_body_scale(modeler: Modeler):
    """Verify the correct scaling of a body."""
    design = modeler.create_design("BodyScale_Test")

    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    assert Accuracy.length_is_equal(body.volume.m, 1)

    body.scale(2)
    assert Accuracy.length_is_equal(body.volume.m, 8)

    body.scale(0.25)
    assert Accuracy.length_is_equal(body.volume.m, 1 / 8)


def test_body_mapping(modeler: Modeler):
    """Verify the correct mapping of a body."""
    design = modeler.create_design("BodyMap_Test")

    # non-symmetric shape to allow determination of mirroring
    body = design.extrude_sketch(
        "box",
        Sketch()
        .segment(Point2D([1, 1]), Point2D([-1, 1]))
        .segment_to_point(Point2D([0, 0.5]))
        .segment_to_point(Point2D([-1, -1]))
        .segment_to_point(Point2D([1, -1]))
        .segment_to_point(Point2D([1, 1])),
        1,
    )

    # Test 1: identity mapping - everything should be the same
    copy = body.copy(body.parent_component, "copy")
    copy.map(Frame(Point3D([0, 0, 0]), UnitVector3D([1, 0, 0]), UnitVector3D([0, 1, 0])))

    vertices = []
    for edge in body.edges:
        vertices.extend([edge.shape.start, edge.shape.end])

    copy_vertices = []
    for edge in copy.edges:
        copy_vertices.extend([edge.shape.start, edge.shape.end])

    assert np.allclose(vertices, copy_vertices)

    # Test 2: mirror the body - flips only the x direction
    copy = body.copy(body.parent_component, "copy")
    copy.map(Frame(Point3D([-4, 0, 1]), UnitVector3D([-1, 0, 0]), UnitVector3D([0, 1, 0])))

    copy_vertices = []
    for edge in copy.edges:
        copy_vertices.extend([edge.shape.start, edge.shape.end])

    # expected vertices from confirmed mirror
    expected_vertices = [
        Point3D([-3.0, -1.0, 0.0]),
        Point3D([-5.0, -1.0, 0.0]),
        Point3D([-3.0, -1.0, 1.0]),
        Point3D([-3.0, -1.0, 0.0]),
        Point3D([-4.0, 0.5, 0.0]),
        Point3D([-3.0, -1.0, 0.0]),
        Point3D([-4.0, 0.5, 1.0]),
        Point3D([-4.0, 0.5, 0.0]),
        Point3D([-3.0, 1.0, 0.0]),
        Point3D([-4.0, 0.5, 0.0]),
        Point3D([-3.0, 1.0, 1.0]),
        Point3D([-3.0, 1.0, 0.0]),
        Point3D([-5.0, 1.0, 0.0]),
        Point3D([-3.0, 1.0, 0.0]),
        Point3D([-5.0, 1.0, 1.0]),
        Point3D([-5.0, 1.0, 0.0]),
        Point3D([-5.0, -1.0, 0.0]),
        Point3D([-5.0, 1.0, 0.0]),
        Point3D([-5.0, -1.0, 1.0]),
        Point3D([-5.0, -1.0, 0.0]),
        Point3D([-3.0, -1.0, 1.0]),
        Point3D([-5.0, -1.0, 1.0]),
        Point3D([-4.0, 0.5, 1.0]),
        Point3D([-3.0, -1.0, 1.0]),
        Point3D([-3.0, 1.0, 1.0]),
        Point3D([-4.0, 0.5, 1.0]),
        Point3D([-5.0, 1.0, 1.0]),
        Point3D([-3.0, 1.0, 1.0]),
        Point3D([-5.0, -1.0, 1.0]),
        Point3D([-5.0, 1.0, 1.0]),
    ]

    assert np.allclose(expected_vertices, copy_vertices)

    # Test 3: rotate body 180 degrees - flip x and y direction
    map_copy = body.copy(body.parent_component, "copy")
    map_copy.map(Frame(Point3D([0, 0, 0]), UnitVector3D([-1, 0, 0]), UnitVector3D([0, -1, 0])))

    rotate_copy = body.copy(body.parent_component, "copy")
    rotate_copy.rotate(Point3D([0, 0, 0]), UnitVector3D([0, 0, 1]), np.pi)

    map_vertices = []
    for edge in map_copy.edges:
        map_vertices.extend([edge.shape.start, edge.shape.end])

    rotate_vertices = []
    for edge in rotate_copy.edges:
        rotate_vertices.extend([edge.shape.start, edge.shape.end])

    assert np.allclose(map_vertices, rotate_vertices)


def test_sphere_creation(modeler: Modeler):
    """Test the creation of a sphere body with a given radius."""
    design = modeler.create_design("Spheretest")
    center_point = Point3D([10, 10, 10], UNITS.m)
    radius = Distance(1, UNITS.m)
    spherebody = design.create_sphere("testspherebody", center_point, radius)
    assert spherebody.name == "testspherebody"
    assert len(spherebody.faces) == 1
    assert round(spherebody.volume._magnitude, 3) == round(4.1887902, 3)


def test_body_mirror(modeler: Modeler):
    """Test the mirroring of a body."""
    design = modeler.create_design("Design1")

    # Create shape with no lines of symmetry in any axis
    body = design.extrude_sketch(
        "box",
        Sketch()
        .segment(Point2D([1, 1]), Point2D([-1, 1]))
        .segment_to_point(Point2D([0, 0.5]))
        .segment_to_point(Point2D([-1, -1]))
        .segment_to_point(Point2D([1, -1]))
        .segment_to_point(Point2D([1, 1])),
        1,
    )
    top = design.extrude_sketch(
        "top", Sketch(Plane(Point3D([0, 0, 1]))).box(Point2D([0.5, 0.5]), 0.1, 0.1), 0.1
    )
    body.unite(top)

    # Mirror across YZ plane
    copy1 = body.copy(body.parent_component, "box2")
    copy1.mirror(Plane(Point3D([2, 0, 0]), UnitVector3D([0, 0, 1]), UnitVector3D([0, 1, 0])))

    # results from SpaceClaim
    expected_vertices = [
        Point3D([5.0, -1.0, 1.0]),
        Point3D([5.0, -1.0, 0.0]),
        Point3D([4.0, 0.5, 1.0]),
        Point3D([4.0, 0.5, 0.0]),
        Point3D([5.0, 1.0, 1.0]),
        Point3D([5.0, 1.0, 0.0]),
        Point3D([3.0, 1.0, 1.0]),
        Point3D([3.0, 1.0, 0.0]),
        Point3D([3.0, -1.0, 1.0]),
        Point3D([3.0, -1.0, 0.0]),
        Point3D([3.55, 0.45, 1.1]),
        Point3D([3.55, 0.45, 1.0]),
        Point3D([3.55, 0.55, 1.1]),
        Point3D([3.55, 0.55, 1.0]),
        Point3D([3.45, 0.55, 1.1]),
        Point3D([3.45, 0.55, 1.0]),
        Point3D([3.45, 0.45, 1.1]),
        Point3D([3.45, 0.45, 1.0]),
    ]

    copy_vertices = []
    for edge in copy1.edges:
        if edge.shape.start not in copy_vertices:
            copy_vertices.append(edge.shape.start)
    assert np.allclose(expected_vertices, copy_vertices)

    # Mirror across XY plane
    copy2 = body.copy(body.parent_component, "box3")
    copy2.mirror(Plane(Point3D([0, 0, -5]), UnitVector3D([1, 0, 0]), UnitVector3D([0, 1, 0])))

    # results from SpaceClaim
    expected_vertices = [
        Point3D([-1.0, -1.0, -11.0]),
        Point3D([-1.0, -1.0, -10.0]),
        Point3D([0.0, 0.5, -11.0]),
        Point3D([0.0, 0.5, -10.0]),
        Point3D([-1.0, 1.0, -11.0]),
        Point3D([-1.0, 1.0, -10.0]),
        Point3D([1.0, 1.0, -11.0]),
        Point3D([1.0, 1.0, -10.0]),
        Point3D([1.0, -1.0, -11.0]),
        Point3D([1.0, -1.0, -10.0]),
        Point3D([0.45, 0.45, -11.1]),
        Point3D([0.45, 0.45, -11.0]),
        Point3D([0.45, 0.55, -11.1]),
        Point3D([0.45, 0.55, -11.0]),
        Point3D([0.55, 0.55, -11.1]),
        Point3D([0.55, 0.55, -11.0]),
        Point3D([0.55, 0.45, -11.1]),
        Point3D([0.55, 0.45, -11.0]),
    ]

    copy_vertices = []
    for edge in copy2.edges:
        if edge.shape.start not in copy_vertices:
            copy_vertices.append(edge.shape.start)
    assert np.allclose(expected_vertices, copy_vertices)

    # Mirror across XZ plane
    copy3 = body.copy(body.parent_component, "box4")
    copy3.mirror(Plane(Point3D([0, 3, 0]), UnitVector3D([1, 0, 0]), UnitVector3D([0, 0, 1])))

    # results from SpaceClaim
    expected_vertices = [
        Point3D([-1.0, 7.0, 1.0]),
        Point3D([-1.0, 7.0, 0.0]),
        Point3D([0.0, 5.5, 1.0]),
        Point3D([0.0, 5.5, 0.0]),
        Point3D([-1.0, 5.0, 1.0]),
        Point3D([-1.0, 5.0, 0.0]),
        Point3D([1.0, 5.0, 1.0]),
        Point3D([1.0, 5.0, 0.0]),
        Point3D([1.0, 7.0, 1.0]),
        Point3D([1.0, 7.0, 0.0]),
        Point3D([0.45, 5.55, 1.1]),
        Point3D([0.45, 5.55, 1.0]),
        Point3D([0.45, 5.45, 1.1]),
        Point3D([0.45, 5.45, 1.0]),
        Point3D([0.55, 5.45, 1.1]),
        Point3D([0.55, 5.45, 1.0]),
        Point3D([0.55, 5.55, 1.1]),
        Point3D([0.55, 5.55, 1.0]),
    ]

    copy_vertices = []
    for edge in copy3.edges:
        if edge.shape.start not in copy_vertices:
            copy_vertices.append(edge.shape.start)
    assert np.allclose(expected_vertices, copy_vertices)


def test_sweep_sketch(modeler: Modeler):
    """Test revolving a circle profile around a circular axis to make a
    donut.
    """
    design_sketch = modeler.create_design("donut")

    path_radius = 5
    profile_radius = 2

    # create a circle on the XZ-plane centered at (5, 0, 0) with radius 2
    profile = Sketch(plane=Plane(direction_x=[1, 0, 0], direction_y=[0, 0, 1])).circle(
        Point2D([path_radius, 0]), profile_radius
    )

    # create a circle on the XY-plane centered at (0, 0, 0) with radius 5
    path = [Circle(Point3D([0, 0, 0]), path_radius).trim(Interval(0, 2 * np.pi))]

    body = design_sketch.sweep_sketch("donutsweep", profile, path)

    assert body.is_surface is False

    # check edges
    assert len(body.edges) == 0

    # check faces
    assert len(body.faces) == 1

    # check area of face
    # compute expected area (torus with r < R) where r2 is inner radius and r1 is outer radius
    r1 = path_radius + profile_radius
    r2 = path_radius - profile_radius
    expected_face_area = (np.pi**2) * (r1**2 - r2**2)
    assert body.faces[0].area.m == pytest.approx(expected_face_area)

    assert Accuracy.length_is_equal(body.volume.m, 394.7841760435743)


def test_sweep_chain(modeler: Modeler):
    """Test revolving a semi-elliptical profile around a circular axis to make
    a bowl.
    """
    design_chain = modeler.create_design("bowl")

    radius = 10

    # create quarter-ellipse profile with major radius = 10, minor radius = 5
    profile = [
        Ellipse(
            Point3D([0, 0, radius / 2]), radius, radius / 2, reference=[1, 0, 0], axis=[0, 1, 0]
        ).trim(Interval(0, np.pi / 2))
    ]

    # create circle on the plane parallel to the XY-plane but moved up by 5 units with radius 10
    path = [Circle(Point3D([0, 0, radius / 2]), radius).trim(Interval(0, 2 * np.pi))]

    # create the bowl body
    body = design_chain.sweep_chain("bowlsweep", path, profile)

    assert body.is_surface is True

    # check edges
    assert len(body.edges) == 1

    # check length of edge
    # compute expected circumference (circle with radius 10)
    expected_edge_cirumference = 2 * np.pi * 10
    assert body.edges[0].length.m == pytest.approx(expected_edge_cirumference)

    # check faces
    assert len(body.faces) == 1

    # check area of face
    # compute expected area (half a spheroid)
    minor_rad = radius / 2
    e_squared = 1 - (minor_rad**2 / radius**2)
    e = np.sqrt(e_squared)
    expected_face_area = (
        2 * np.pi * radius**2 + (minor_rad**2 / e) * np.pi * np.log((1 + e) / (1 - e))
    ) / 2
    assert body.faces[0].area.m == pytest.approx(expected_face_area)

    # check volume of body
    # expected is 0 since it's not a closed surface
    assert body.volume.m == 0


def test_create_body_from_loft_profile(modeler: Modeler):
    """Test the ``create_body_from_loft_profile()`` method to create a vase
    shape.
    """
    design_sketch = modeler.create_design("loftprofile")

    profile1 = Circle(origin=[0, 0, 0], radius=8).trim(Interval(0, 2 * np.pi))
    profile2 = Circle(origin=[0, 0, 10], radius=10).trim(Interval(0, 2 * np.pi))
    profile3 = Circle(origin=[0, 0, 20], radius=5).trim(Interval(0, 2 * np.pi))

    # Call the method
    result = design_sketch.create_body_from_loft_profile(
        "vase", [[profile1], [profile2], [profile3]], False, False
    )

    # Assert that the resulting body has only one face.
    assert len(result.faces) == 1

    # check volume of body
    # expected is 0 since it's not a closed surface
    assert result.volume.m == 0


def test_revolve_sketch(modeler: Modeler):
    """Test revolving a circular profile for a quarter donut."""
    # Initialize the donut sketch design
    design = modeler.create_design("quarter-donut")

    # Donut parameters
    path_radius = 5
    profile_radius = 2

    # Create the circular profile on the XZ plane centered at (5, 0, 0)
    # with a radius of 2
    plane_profile = Plane(
        origin=Point3D([path_radius, 0, 0]), direction_x=UNITVECTOR3D_X, direction_y=UNITVECTOR3D_Z
    )
    profile = Sketch(plane=plane_profile)
    profile.circle(Point2D([0, 0]), profile_radius)

    # Revolve the profile around the Z axis and center in the absolute origin
    # for an angle of 90 degrees
    body = design.revolve_sketch(
        "donut-body",
        sketch=profile,
        axis=UNITVECTOR3D_Z,
        angle=Angle(90, unit=UNITS.degrees),
        rotation_origin=Point3D([0, 0, 0]),
    )

    assert body.is_surface is False
    assert body.name == "donut-body"
    assert np.isclose(body.volume.m, np.pi**2 * 2 * 5, rtol=1e-3)  # quarter of a torus volume


def test_revolve_sketch_coincident_origins(modeler: Modeler):
    """Test demonstrating revolving a sketch when it is located
    in the same origin does not fail.
    """
    # Initialize a sphere sketch design given a semicircle profile
    design = modeler.create_design("revolve-coincident-origins")

    # Create an XZ plane centered at (0, 0, 0)
    plane_profile = Plane(
        origin=Point3D([0, 0, 0]), direction_x=UNITVECTOR3D_X, direction_y=UNITVECTOR3D_Z
    )
    profile = Sketch(plane=plane_profile)
    (
        profile.segment_to_point(Point2D([1, 0]))
        .arc_to_point(Point2D([-1, 0]), Point2D([0, 0]))
        .segment_to_point(Point2D([0, 0]))
    )

    # Try revolving the profile... coincident origins is not a problem anymore
    body = design.revolve_sketch(
        "cross-section-sphere",
        sketch=profile,
        axis=UNITVECTOR3D_X,
        angle=Angle(90, unit=UNITS.degrees),
        rotation_origin=Point3D([0, 0, 0]),
    )

    assert body.is_surface is False
    assert body.name == "cross-section-sphere"
    assert np.isclose(
        body.volume.m, np.pi / 3, rtol=1e-3
    )  # quarter of a sphere volume (4/3 * pi * r^3) / 4
    # 1/3 * pi * r^3 --> r = 1 --> 1/3 * pi


def test_revolve_sketch_fail_invalid_path(modeler: Modeler):
    """Test demonstrating the failure of revolving a sketch when an invalid path is provided."""
    # Initialize the donut sketch design
    design = modeler.create_design("revolve-fail")

    # Create an XZ plane centered at (0, 0, 0)
    plane_profile = Plane(
        origin=Point3D([0, 0, 0]), direction_x=UNITVECTOR3D_X, direction_y=UNITVECTOR3D_Z
    )
    profile = Sketch(plane=plane_profile)
    profile.circle(Point2D([0, 0]), 1)

    # Try revolving the profile...
    with pytest.raises(
        GeometryExitedError, match="The path is invalid, or it is unsuitable for the profile."
    ):
        design.revolve_sketch(
            "cross-section-sphere",
            sketch=profile,
            axis=UNITVECTOR3D_Z,
            angle=Angle(90, unit=UNITS.degrees),
            rotation_origin=Point3D([0, 0, 0]),
        )


def test_component_tree_print(modeler: Modeler):
    """Test for verifying the tree print for ``Component`` objects."""

    def check_list_equality(lines, expected_lines):
        # By doing "a in b" rather than "a == b", we can check for substrings
        # which, in the case of beam ids, is necessary since they are unique
        # and will not be the same in different runs.
        return all([expected_line in line for line, expected_line in zip(lines, expected_lines)])

    # Create your design on the server side
    design = modeler.create_design("TreePrintComponent")

    # Create a Sketch object and draw a circle (all client side)
    sketch = Sketch()
    sketch.circle(Point2D([-30, -30], UNITS.mm), Quantity(10, UNITS.mm))
    distance = Quantity(30, UNITS.mm)
    #  The following component hierarchy is made
    #
    #           |---> comp_1 ---|---> nested_1_comp_1 ---> nested_1_nested_1_comp_1
    #           |               |
    #           |               |---> nested_2_comp_1
    #           |
    # DESIGN ---|---> comp_2 -------> nested_1_comp_2
    #           |
    #           |
    #           |---> comp_3
    #
    #
    # Now, only "comp_3", "nested_2_comp_1" and "nested_1_nested_1_comp_1"
    # will have a body associated.
    #

    # Create the components
    comp_1 = design.add_component("Component_1")
    comp_2 = design.add_component("Component_2")
    comp_3 = design.add_component("Component_3")
    nested_1_comp_1 = comp_1.add_component("Nested_1_Component_1")
    nested_1_nested_1_comp_1 = nested_1_comp_1.add_component("Nested_1_Nested_1_Component_1")
    nested_2_comp_1 = comp_1.add_component("Nested_2_Component_1")
    _ = comp_2.add_component("Nested_1_Component_2")

    # Create the bodies
    _ = comp_3.extrude_sketch(name="comp_3_circle", sketch=sketch, distance=distance)
    _ = nested_2_comp_1.extrude_sketch(
        name="nested_2_comp_1_circle", sketch=sketch, distance=distance
    )
    _ = nested_1_nested_1_comp_1.extrude_sketch(
        name="nested_1_nested_1_comp_1_circle", sketch=sketch, distance=distance
    )

    # Create beams (in design)
    circle_profile_1 = design.add_beam_circular_profile(
        "CircleProfile1", Quantity(10, UNITS.mm), Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_Y
    )
    _ = design.create_beam(
        Point3D([9, 99, 999], UNITS.mm), Point3D([8, 88, 888], UNITS.mm), circle_profile_1
    )

    # Test the tree print - by default
    ##################################
    lines = design.tree_print(return_list=True)
    ref = [
        ">>> Tree print view of component 'TreePrintComponent'",
        "",
        "Location",
        "--------",
        "Root component (Design)",
        "",
        "Subtree",
        "-------",
        "(comp) TreePrintComponent",
        "|---(beam) 0:",
        "|---(comp) Component_1",
        ":   |---(comp) Nested_1_Component_1",
        ":   :   |---(comp) Nested_1_Nested_1_Component_1",
        ":   :       |---(body) nested_1_nested_1_comp_1_circle",
        ":   |---(comp) Nested_2_Component_1",
        ":       |---(body) nested_2_comp_1_circle",
        "|---(comp) Component_2",
        ":   |---(comp) Nested_1_Component_2",
        "|---(comp) Component_3",
        "    |---(body) comp_3_circle",
    ]
    assert check_list_equality(lines, ref) is True

    # Test - request depth 1, and show only components
    ##################################################
    lines = design.tree_print(
        return_list=True, depth=1, consider_bodies=False, consider_beams=False
    )
    ref = [
        ">>> Tree print view of component 'TreePrintComponent'",
        "",
        "Location",
        "--------",
        "Root component (Design)",
        "",
        "Subtree",
        "-------",
        "(comp) TreePrintComponent",
        "|---(comp) Component_1",
        "|---(comp) Component_2",
        "|---(comp) Component_3",
    ]
    assert check_list_equality(lines, ref) is True

    # Test - request depth 2, indent 1 (which will default to 2)
    # and sort the components alphabetically
    ############################################################
    lines = design.tree_print(return_list=True, depth=2, indent=1, sort_keys=True)
    ref = [
        ">>> Tree print view of component 'TreePrintComponent'",
        "",
        "Location",
        "--------",
        "Root component (Design)",
        "",
        "Subtree",
        "-------",
        "(comp) TreePrintComponent",
        "|-(beam) 0:",
        "|-(comp) Component_1",
        ": |-(comp) Nested_1_Component_1",
        ": |-(comp) Nested_2_Component_1",
        "|-(comp) Component_2",
        ": |-(comp) Nested_1_Component_2",
        "|-(comp) Component_3",
        "  |-(body) comp_3_circle",
    ]
    assert check_list_equality(lines, ref) is True

    # Test - request from Nested_1_Component_1
    ##########################################
    lines = nested_1_comp_1.tree_print(return_list=True)
    ref = [
        ">>> Tree print view of component 'Nested_1_Component_1'",
        "",
        "Location",
        "--------",
        "TreePrintComponent > Component_1 > Nested_1_Component_1",
        "",
        "Subtree",
        "-------",
        "(comp) Nested_1_Component_1",
        "|---(comp) Nested_1_Nested_1_Component_1",
        "    |---(body) nested_1_nested_1_comp_1_circle",
    ]
    assert check_list_equality(lines, ref) is True


def test_surface_body_creation(modeler: Modeler):
    """Test surface body creation from trimmed surfaces."""
    design = modeler.create_design("Design1")

    # half sphere
    surface = Sphere([0, 0, 0], 1)
    trimmed_surface = surface.trim(BoxUV(Interval(0, np.pi * 2), Interval(0, np.pi / 2)))
    body = design.create_body_from_surface("sphere", trimmed_surface)
    assert len(design.bodies) == 1
    assert body.is_surface
    assert body.faces[0].area.m == pytest.approx(np.pi * 2)

    # cylinder
    surface = Cylinder([0, 0, 0], 1)
    trimmed_surface = surface.trim(BoxUV(Interval(0, np.pi * 2), Interval(0, 1)))
    body = design.create_body_from_surface("cylinder", trimmed_surface)

    assert len(design.bodies) == 2
    assert body.is_surface
    assert body.faces[0].area.m == pytest.approx(np.pi * 2)

    # cone
    surface = Cone([0, 0, 0], 1, np.pi / 4)
    trimmed_surface = surface.trim(BoxUV(Interval(0, np.pi * 2), Interval(surface.apex.z.m, 0)))
    body = design.create_body_from_surface("cone", trimmed_surface)

    assert len(design.bodies) == 3
    assert body.is_surface
    assert body.faces[0].area.m == pytest.approx(4.44288293816)

    # half torus
    surface = Torus([0, 0, 0], 2, 1)
    trimmed_surface = surface.trim(BoxUV(Interval(0, np.pi), Interval(0, np.pi * 2)))
    body = design.create_body_from_surface("torus", trimmed_surface)

    assert len(design.bodies) == 4
    assert body.is_surface
    assert body.faces[0].area.m == pytest.approx(39.4784176044)

    # SOLID BODIES

    # sphere
    surface = Sphere([0, 0, 0], 1)
    trimmed_surface = surface.trim(BoxUV(Interval(0, np.pi * 2), Interval(-np.pi / 2, np.pi / 2)))
    body = design.create_body_from_surface("sphere_solid", trimmed_surface)
    assert len(design.bodies) == 5
    assert not body.is_surface
    assert body.faces[0].area.m == pytest.approx(np.pi * 4)

    # torus
    surface = Torus([0, 0, 0], 2, 1)
    trimmed_surface = surface.trim(BoxUV(Interval(0, np.pi * 2), Interval(0, np.pi * 2)))
    body = design.create_body_from_surface("torus_solid", trimmed_surface)

    assert len(design.bodies) == 6
    assert not body.is_surface
    assert body.faces[0].area.m == pytest.approx(39.4784176044 * 2)


def test_design_parameters(modeler: Modeler):
    """Test the design parameter's functionality."""
    design = modeler.open_file(FILES_DIR / "blockswithparameters.dsco")
    test_parameters = design.parameters

    # Verify the initial parameters
    assert len(test_parameters) == 2
    assert test_parameters[0].name == "p1"
    assert abs(test_parameters[0].dimension_value - 0.00010872999999999981) < 1e-8
    assert test_parameters[0].dimension_type == ParameterType.DIMENSIONTYPE_AREA

    assert test_parameters[1].name == "p2"
    assert abs(test_parameters[1].dimension_value - 0.0002552758322160813) < 1e-8
    assert test_parameters[1].dimension_type == ParameterType.DIMENSIONTYPE_AREA

    # Update the second parameter and verify the status
    test_parameters[1].dimension_value = 0.0006
    status = design.set_parameter(test_parameters[1])
    assert status == ParameterUpdateStatus.SUCCESS

    # Attempt to update the first parameter and expect a constrained status
    test_parameters[0].dimension_value = 0.0006
    status = design.set_parameter(test_parameters[0])
    assert status == ParameterUpdateStatus.CONSTRAINED_PARAMETERS


def test_cached_bodies(modeler: Modeler):
    """Test that bodies are cached correctly.

    Whenever a new body is created, modified etc. we should make sure that the cache is updated.
    """
    design = modeler.create_design("ModelingDemo")

    # Define a sketch
    origin = Point3D([0, 0, 10])
    plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])

    # Create a sketch
    sketch_box = Sketch(plane)
    sketch_box.box(Point2D([20, 20]), 30 * UNITS.m, 30 * UNITS.m)

    sketch_cylinder = Sketch(plane)
    sketch_cylinder.circle(Point2D([20, 20]), 5 * UNITS.m)

    design.extrude_sketch(name="BoxBody", sketch=sketch_box, distance=Distance(30, unit=UNITS.m))
    design.extrude_sketch(
        name="CylinderBody",
        sketch=sketch_cylinder,
        distance=Distance(60, unit=UNITS.m),
    )

    my_bodies = design.bodies
    my_bodies_2 = design.bodies

    # We should make sure that the object memory addresses are the same
    for body1, body2 in zip(my_bodies, my_bodies_2):
        assert body1 is body2  # We are comparing the memory addresses
        assert id(body1) == id(body2)

    design.extrude_sketch(
        name="CylinderBody2",
        sketch=sketch_cylinder,
        distance=Distance(20, unit=UNITS.m),
        direction="-",
    )
    my_bodies_3 = design.bodies

    for body1, body3 in zip(my_bodies, my_bodies_3):
        assert body1 is not body3
        assert id(body1) != id(body3)


def test_extrude_sketch_with_cut_request(modeler: Modeler):
    """Test the cut argument when performing a sketch extrusion.

    This method mimics a cut operation.

    Behind the scenes, a subtraction operation is performed on the bodies. After extruding the
    sketch, the resulting body should be a cut body.
    """
    # Define a sketch
    origin = Point3D([0, 0, 10])
    plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])

    # Create a sketch
    sketch_box = Sketch(plane)
    sketch_box.box(Point2D([20, 20]), 30 * UNITS.m, 30 * UNITS.m)

    sketch_cylinder = Sketch(plane)
    sketch_cylinder.circle(Point2D([20, 20]), 5 * UNITS.m)

    # Create a design
    design = modeler.create_design("ExtrudeSketchWithCut")

    box_body = design.extrude_sketch(
        name="BoxBody", sketch=sketch_box, distance=Distance(30, unit=UNITS.m)
    )
    volume_box = box_body.volume

    design.extrude_sketch(
        name="CylinderBody", sketch=sketch_cylinder, distance=Distance(60, unit=UNITS.m), cut=True
    )

    # Verify there is only one body
    assert len(design.bodies) == 1

    # Verify the volume of the resulting body is less than the volume of the box
    assert design.bodies[0].volume < volume_box


def test_extrude_sketch_with_cut_request_no_collision(modeler: Modeler):
    """Test the cut argument when performing a sketch extrusion (with no collision).

    This method mimics an unsuccessful cut operation.

    The sketch extrusion should not result in a cut body since there is no collision between the
    original body and the extruded body.
    """
    # Define a sketch
    origin = Point3D([0, 0, 10])
    plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])

    # Create a sketch
    sketch_box = Sketch(plane)
    sketch_box.box(Point2D([20, 20]), 30 * UNITS.m, 30 * UNITS.m)

    sketch_cylinder = Sketch(plane)
    sketch_cylinder.circle(Point2D([100, 100]), 5 * UNITS.m)

    # Create a design
    design = modeler.create_design("ExtrudeSketchWithCutNoCollision")

    box_body = design.extrude_sketch(
        name="BoxBody", sketch=sketch_box, distance=Distance(30, unit=UNITS.m)
    )
    volume_box = box_body.volume

    design.extrude_sketch(
        name="CylinderBody", sketch=sketch_cylinder, distance=Distance(60, unit=UNITS.m), cut=True
    )

    # Verify there is only one body... the cut operation should delete it
    assert len(design.bodies) == 1

    # Verify the volume of the resulting body is exactly the same
    assert design.bodies[0].volume == volume_box


def test_create_surface_body_from_trimmed_curves(modeler: Modeler):
    design = modeler.create_design("surface")

    # pill shape
    circle1 = Circle(Point3D([0, 0, 0]), 1).trim(Interval(0, np.pi))
    line1 = Line(Point3D([-1, 0, 0]), UnitVector3D([0, -1, 0])).trim(Interval(0, 1))
    circle2 = Circle(Point3D([0, -1, 0]), 1).trim(Interval(np.pi, np.pi * 2))
    line2 = Line(Point3D([1, 0, 0]), UnitVector3D([0, -1, 0])).trim(Interval(0, 1))

    body = design.create_surface_from_trimmed_curves("body", [circle1, line1, line2, circle2])
    assert body.is_surface
    assert body.faces[0].area.m == pytest.approx(
        Quantity(2 + np.pi, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )

    # create from edges (by getting their trimmed curves)
    trimmed_curves_from_edges = [edge.shape for edge in body.edges]
    body = design.create_surface_from_trimmed_curves("body2", trimmed_curves_from_edges)
    assert body.is_surface
    assert body.faces[0].area.m == pytest.approx(
        Quantity(2 + np.pi, UNITS.m**2).m, rel=1e-6, abs=1e-8
    )


def test_shell_body(modeler: Modeler):
    """Test shell command."""
    design = modeler.create_design("shell")
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    assert base.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 6

    # shell
    success = base.shell_body(0.1)
    assert success
    assert base.volume.m == pytest.approx(Quantity(0.728, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 12

    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    success = base.shell_body(-0.1)
    assert success
    assert base.volume.m == pytest.approx(Quantity(0.488, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 12


def test_shell_faces(modeler: Modeler):
    """Test shell commands for a single face."""
    design = modeler.create_design("shell")
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    assert base.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 6

    # shell
    success = base.remove_faces(base.faces[0], 0.1)
    assert success
    assert base.volume.m == pytest.approx(Quantity(0.584, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 11


def test_shell_multiple_faces(modeler: Modeler):
    """Test shell commands for multiple faces."""
    design = modeler.create_design("shell")
    base = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    assert base.volume.m == pytest.approx(Quantity(1, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 6

    # shell
    success = base.remove_faces([base.faces[0], base.faces[2]], 0.1)
    assert success
    assert base.volume.m == pytest.approx(Quantity(0.452, UNITS.m**3).m, rel=1e-6, abs=1e-8)
    assert len(base.faces) == 10


def test_set_face_color(modeler: Modeler):
    """Test the getting and setting of face colors."""

    design = modeler.create_design("FaceColorTest")
    box = design.extrude_sketch("Body1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
    faces = box.faces
    assert len(faces) == 6

    # Default body color is if it is not set on server side.
    assert faces[0].color == DEFAULT_COLOR

    # Set the color of the body using hex code.
    faces[0].color = "#0000ffff"
    assert faces[0].color == "#0000ffff"

    faces[1].color = "#ffc000ff"
    assert faces[1].color == "#ffc000ff"

    # Set the color of the body using color name.
    faces[2].set_color("green")
    assert faces[2].color == "#008000ff"

    # Set the color of the body using RGB values between (0,1) as floats.
    faces[0].set_color((1.0, 0.0, 0.0))
    assert faces[0].color == "#ff0000ff"

    # Set the color of the body using RGB values between (0,255) as integers).
    faces[1].set_color((0, 255, 0))
    assert faces[1].color == "#00ff00ff"

    # Assigning color object directly
    blue_color = mcolors.to_rgba("#0000FF")
    faces[2].color = blue_color
    assert faces[2].color == "#0000ffff"

    # Assign a color with opacity
    faces[3].color = (255, 0, 0, 80)
    assert faces[3].color == "#ff000050"

    # Test setting the opacity separately
    faces[3].opacity = 0.8
    assert faces[3].color == "#ff0000cc"

    # Try setting the opacity to an invalid value
    with pytest.raises(
        ValueError, match="Invalid color value: Opacity value must be between 0 and 1."
    ):
        faces[3].opacity = 255


def test_set_component_name(modeler: Modeler):
    """Test the setting of component names."""

    design = modeler.create_design("ComponentNameTest")
    component = design.add_component("Component1")
    assert component.name == "Component1"

    component.name = "ChangedComponentName"
    assert component.name == "ChangedComponentName"


def test_get_face_bounding_box(modeler: Modeler):
    """Test getting the bounding box of a face."""
    design = modeler.create_design("face_bounding_box")
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    bounding_box = body.faces[0].bounding_box
    assert bounding_box.min_corner.x.m == bounding_box.min_corner.y.m == -0.5
    assert bounding_box.max_corner.x.m == bounding_box.max_corner.y.m == 0.5

    bounding_box = body.faces[1].bounding_box
    assert bounding_box.min_corner.x.m == bounding_box.min_corner.y.m == -0.5
    assert bounding_box.max_corner.x.m == bounding_box.max_corner.y.m == 0.5


def test_get_edge_bounding_box(modeler: Modeler):
    """Test getting the bounding box of an edge."""
    design = modeler.create_design("edge_bounding_box")
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    # Edge 0 goes from (-0.5, -0.5, 1) to (0.5, -0.5, 1)
    bounding_box = body.edges[0].bounding_box
    assert bounding_box.min_corner.x.m == bounding_box.min_corner.y.m == -0.5
    assert bounding_box.min_corner.z.m == 1
    assert bounding_box.max_corner.x.m == 0.5
    assert bounding_box.max_corner.y.m == -0.5
    assert bounding_box.max_corner.z.m == 1

    # Test center
    center = bounding_box.center
    assert center.x.m == 0
    assert center.y.m == -0.5
    assert center.z.m == 1


def test_get_body_bounding_box(modeler: Modeler):
    """Test getting the bounding box of a body."""
    design = modeler.create_design("body_bounding_box")
    body = design.extrude_sketch("box", Sketch().box(Point2D([0, 0]), 1, 1), 1)

    bounding_box = body.bounding_box
    assert bounding_box.min_corner.x.m == bounding_box.min_corner.y.m == -0.5
    assert bounding_box.min_corner.z.m == 0
    assert bounding_box.max_corner.x.m == bounding_box.max_corner.y.m == 0.5
    assert bounding_box.max_corner.z.m == 1

    # Test center
    center = bounding_box.center
    assert center.x.m == 0
    assert center.y.m == 0
    assert center.z.m == 0.5
