"""Test design interaction."""

from grpc._channel import _InactiveRpcError
from pint import Quantity
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.designer import CurveType, SharedTopologyType, SurfaceType
from ansys.geometry.core.materials import Material, MaterialProperty, MaterialPropertyType
from ansys.geometry.core.math import Frame, Point, UnitVector
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

    # TODO: Not possible to save to file from a container (CI/CD)
    #       Use download approach when available.
    #
    # design.save(r"C:\temp\shared_volume\MyFile2.scdocx")


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
        expected_vol = pentagon.area.m * distance_extruded_body.m * 1e-9  # factor to m**3
        assert body.volume.m == pytest.approx(expected_vol)
    except (_InactiveRpcError):
        pass
    assert len(design.components) == 0
    assert len(design.bodies) == 1

    # We have created this body on the base component. Let's add a new component
    # and add a planar surface to it
    planar_component_name = "PlanarBody_Component"
    planar_component = design.add_component(planar_component_name)
    assert planar_component.id is not None
    assert planar_component.name == planar_component_name

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
    design = modeler.create_design("NamedSelection_Test")

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
    design = modeler.create_design("FacesEdges_Test")

    # Create a Sketch object and draw a polygon (all client side)
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


def test_coordinate_system_creation(modeler: Modeler):
    """Test for verifying the correct creation of ``CoordinateSystem``."""

    # Create your design on the server side
    design = modeler.create_design("CoordinateSystem_Test")

    # Build independent component
    nested_comp = design.add_component("NestedComponent")

    frame1 = Frame(Point([10, 200, 3000], UNITS.mm), UnitVector([1, 1, 0]), UnitVector([1, -1, 0]))
    frame2 = Frame(Point([40, 80, 120], UNITS.mm), UnitVector([0, -1, 1]), UnitVector([0, 1, 1]))

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
    sketch.draw_circle(Point([-30, -30, 0], UNITS.mm), Quantity(10, UNITS.mm))
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
    nested_1_comp_2 = comp_2.add_component("Nested_1_Component_2")

    # Create the bodies
    body_1 = comp_3.extrude_sketch(name="comp_3_circle", sketch=sketch, distance=distance)
    body_2 = nested_2_comp_1.extrude_sketch(
        name="nested_2_comp_1_circle", sketch=sketch, distance=distance
    )
    body_3 = nested_1_nested_1_comp_1.extrude_sketch(
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
    assert not comp_1.components[1].bodies[0].is_alive
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
    assert not design.components[0].components[1].bodies[0].is_alive
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
    assert not comp_1.components[0].components[0].bodies[0].is_alive
    assert not comp_1.components[1].is_alive
    assert not comp_1.components[1].bodies[0].is_alive
    assert not comp_2.is_alive
    assert not comp_2.components[0].is_alive
    assert comp_3.is_alive
    assert comp_3.bodies[0].is_alive

    # Do the same checks but calling them from the design object
    assert design.is_alive
    assert not design.components[0].is_alive
    assert not design.components[0].components[0].is_alive
    assert not design.components[0].components[0].components[0].is_alive
    assert not design.components[0].components[0].components[0].bodies[0].is_alive
    assert not design.components[0].components[1].is_alive
    assert not design.components[0].components[1].bodies[0].is_alive
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
    assert not design.components[0].components[0].components[0].bodies[0].is_alive
    assert not design.components[0].components[1].is_alive
    assert not design.components[0].components[1].bodies[0].is_alive
    assert not design.components[1].is_alive
    assert not design.components[1].components[0].is_alive
    assert not design.components[2].is_alive
    assert not design.components[2].bodies[0].is_alive

    # Try deleting the Design object itself - this is forbidden
    with pytest.raises(ValueError, match="The Design object itself cannot be deleted."):
        design.delete_component(design)


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
    sketch.draw_circle(Point([-30, -30, 0], UNITS.mm), Quantity(10, UNITS.mm))
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
    with pytest.raises(ValueError, match="The Design object itself cannot have a shared topology."):
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
    sketch_1.draw_circle(Point([10, 10, 0], UNITS.mm), Quantity(10, UNITS.mm))
    sketch_2 = Sketch()
    sketch_2.draw_polygon(Point([-30, -30, 0], UNITS.mm), Quantity(10, UNITS.mm), sides=5)

    # Build 2 independent components and bodies
    circle_comp = design.add_component("CircleComponent")
    body_circle_comp = circle_comp.extrude_sketch("Circle", sketch_1, Quantity(50, UNITS.mm))
    polygon_comp = design.add_component("PolygonComponent")
    body_polygon_comp = polygon_comp.extrude_sketch("Polygon", sketch_2, Quantity(30, UNITS.mm))

    body_circle_comp.translate(UnitVector([1, 0, 0]), Quantity(50, UNITS.mm))
    body_polygon_comp.translate(UnitVector([-1, 1, -1]), Quantity(88, UNITS.mm))


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
    sketch_1.draw_circle(Point([10, 10, 0], UNITS.mm), Quantity(10, UNITS.mm))
    sketch_2 = Sketch()
    sketch_2.draw_polygon(Point([-30, -30, 0], UNITS.mm), Quantity(10, UNITS.mm), sides=5)

    # Build 2 independent components and bodies
    circle_comp = design.add_component("CircleComponent")
    body_circle_comp = circle_comp.extrude_sketch("Circle", sketch_1, Quantity(50, UNITS.mm))
    polygon_comp = design.add_component("PolygonComponent")
    body_polygon_comp = polygon_comp.extrude_sketch("Polygon", sketch_2, Quantity(30, UNITS.mm))

    design.translate_bodies(
        [body_circle_comp, body_polygon_comp], UnitVector([1, 0, 0]), Quantity(48, UNITS.mm)
    )
    design.translate_bodies(
        [body_circle_comp, body_polygon_comp], UnitVector([0, -1, 1]), Quantity(88, UNITS.mm)
    )
