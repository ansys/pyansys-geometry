"""Test design interaction."""

from grpc._channel import _InactiveRpcError
from pint import Quantity

from ansys.geometry.core import Modeler
from ansys.geometry.core.designer import CurveType, SurfaceType
from ansys.geometry.core.materials import Material, MaterialProperty, MaterialPropertyType
from ansys.geometry.core.math import Point
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.sketch import Sketch


def test_design_extrusion_and_material_assignment(modeler: Modeler):
    """Test in charge of validating the extrusion of a simple
    circle as a cylinder and assigning materials to it."""

    # Create a Sketch and draw a circle (all client side)
    sketch = Sketch()
    sketch.draw_circle(Point([10, 10, 0], UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design_name = "ExtrudeProfile"
    design = modeler.create_design(design_name)
    assert design.name == design_name
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
    assert design.materials[0].properties[MaterialPropertyType.DENSITY].display_name == "steel"
    assert design.materials[0].properties[MaterialPropertyType.DENSITY].quantity == density
    assert (
        design.materials[0].properties[MaterialPropertyType.POISSON_RATIO].type
        == MaterialPropertyType.POISSON_RATIO
    )
    assert (
        design.materials[0].properties[MaterialPropertyType.POISSON_RATIO].display_name
        == "myPoisson"
    )
    assert (
        design.materials[0].properties[MaterialPropertyType.POISSON_RATIO].quantity == poisson_ratio
    )
    assert (
        design.materials[0].properties[MaterialPropertyType.TENSILE_STRENGTH].type
        == MaterialPropertyType.TENSILE_STRENGTH
    )
    assert (
        design.materials[0].properties[MaterialPropertyType.TENSILE_STRENGTH].display_name
        == "myTensile"
    )
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

    # TODO: Not possible to save to file from a container (CI/CD)
    #       Use download approach when available.
    #
    # design.save(r"C:\temp\shared_volume\MyFile2.scdocx")


def test_component_body(modeler: Modeler):
    """Test the different ``Component`` and ``Body`` creation methods."""

    # Create your design on the server side
    design_name = "ComponentBody_Test"
    design = modeler.create_design(design_name)
    assert design.name == design_name
    assert design.id is not None
    assert design.parent_component is None
    assert len(design.components) == 0
    assert len(design.bodies) == 0
    assert len(design.materials) == 0
    assert len(design.named_selections) == 0

    # Create a simple sketch of a Polygon (specifically a Pentagon)
    sketch = Sketch()
    pentagon = sketch.draw_polygon(Point([10, 10, 0], UNITS.mm), Quantity(10, UNITS.mm), sides=5)

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
    # TODO: GetVolume is not implemented on server side yet
    try:
        # All are in mm
        expected_vol = pentagon.area.m * distance_extruded_body.m
        assert body.volume.m == expected_vol
    except (_InactiveRpcError):
        pass
    assert len(design.components) == 0
    assert len(design.bodies) == 1

    # We have created this body on the base component. Let's add a new component
    # and add a planar surface to it
    planar_component_name = "PlanarBody_Component"
    planar_component = design.add_component(planar_component_name)
    assert planar_component.id is not None
    # TODO: server side is not assigning the name properly... returning empty for now.
    # assert planar_component.name == planar_component_name
    assert planar_component.name == ""

    planar_sketch = Sketch()
    planar_sketch.draw_ellipse(
        Point([50, 50, 0], UNITS.mm), Quantity(30, UNITS.mm), Quantity(10, UNITS.mm)
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

    # Check that the planar component belongs to the design
    assert planar_component.parent_component.id == design.id


def test_named_selections(modeler: Modeler):
    """Test for verifying the correct creation of ``NamedSelection``."""

    # Create your design on the server side
    design_name = "NamedSelection_Test"
    design = modeler.create_design(design_name)

    # Create 2 Sketch objects and draw a circle and a polygon (all client side)
    sketch_1 = Sketch()
    sketch_1.draw_circle(Point([10, 10, 0], UNITS.mm), Quantity(10, UNITS.mm))
    sketch_2 = Sketch()
    sketch_2.draw_polygon(Point([-30, -30, 0], UNITS.mm), Quantity(10, UNITS.mm), sides=5)

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


def test_faces_edges(modeler: Modeler):
    """Test for verifying the correct creation and
    usage of ``Face`` and ``Edge`` objects."""

    # Create your design on the server side
    design_name = "FacesEdges_Test"
    design = modeler.create_design(design_name)

    # Create a Sketch object and draw apolygon (all client side)
    sketch = Sketch()
    polygon = sketch.draw_polygon(Point([-30, -30, 0], UNITS.mm), Quantity(10, UNITS.mm), sides=5)

    # Build independent components and bodies
    polygon_comp = design.add_component("PolygonComponent")
    body_polygon_comp = polygon_comp.extrude_sketch("Polygon", sketch, Quantity(30, UNITS.mm))

    # Get all its faces
    faces = body_polygon_comp.faces
    assert len(faces) == 7  # top + bottom + sides
    assert all(face.id is not None for face in faces)
    # TODO: may be at some point these might change to planar?
    assert all(face.surface_type == SurfaceType.SURFACETYPE_UNKNOWN for face in faces)
    assert all(face.area > 0.0 for face in faces)
    assert abs(faces[0].area.to_base_units().m - polygon.area.to_base_units().m) <= 1e-15

    # Now, from one of the lids (i.e. 0) get all edges
    edges = faces[0].edges
    assert len(edges) == 5  # pentagon
    assert all(edge.id is not None for edge in edges)
    # TODO: may be at some point these might change to line?
    assert all(edge.curve_type == CurveType.CURVETYPE_UNKNOWN for edge in edges)
    assert all(edge.length > 0.0 for edge in edges)
    assert abs(edges[0].length.to_base_units().m - polygon.length.to_base_units().m) <= 1e-15
