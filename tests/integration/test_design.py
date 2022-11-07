"""Test design interaction."""

from pint import Quantity
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.designer import (
    CurveType,
    DesignFileFormat,
    SharedTopologyType,
    SurfaceType,
)
from ansys.geometry.core.designer.face import FaceLoopType
from ansys.geometry.core.materials import Material, MaterialProperty, MaterialPropertyType
from ansys.geometry.core.math import (
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    UNITVECTOR3D_Z,
    Frame,
    Plane,
    Point2D,
    Point3D,
    UnitVector3D,
)
from ansys.geometry.core.misc import UNIT_LENGTH, UNITS, Distance
from ansys.geometry.core.sketch import Sketch


def test_design_extrusion_and_material_assignment(modeler: Modeler):
    """Test in charge of validating the extrusion of a simple
    circle as a cylinder and assigning materials to it."""

    # Create a Sketch and draw a circle (all client side)
    sketch = Sketch()
    sketch.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))

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
    assert longest_body.volume.m == pytest.approx(
        Quantity(3e-6, UNITS.m**3).m, rel=1e-6, abs=1e-8
    )

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

    # Test creating a named selection out of beams
    circle_profile_1 = design.add_beam_circular_profile(
        "CircleProfile1", Quantity(10, UNITS.mm), Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_Y
    )
    beam_1 = design.create_beam(
        Point3D([9, 99, 999], UNITS.mm), Point3D([8, 88, 888], UNITS.mm), circle_profile_1
    )
    design.create_named_selection("CircleProfile", beams=[beam_1])
    assert len(design.named_selections) == 5
    assert design.named_selections[0].name == "OnlyCircle"
    assert design.named_selections[1].name == "OnlyPolygon"
    assert design.named_selections[2].name == "CircleAndPolygon"
    assert design.named_selections[3].name == "OnlyPolygonFaces"
    assert design.named_selections[4].name == "CircleProfile"

    # Test creating a named selection out of design_points
    point_set_1 = Point3D([10, 10, 0], UNITS.m)
    design_points_1 = design.add_design_point("FirstPointSet", point_set_1)
    design.create_named_selection("FirstPointSet", design_points=[design_points_1])
    assert len(design.named_selections) == 6
    assert design.named_selections[0].name == "OnlyCircle"
    assert design.named_selections[1].name == "OnlyPolygon"
    assert design.named_selections[2].name == "CircleAndPolygon"
    assert design.named_selections[3].name == "OnlyPolygonFaces"
    assert design.named_selections[4].name == "CircleProfile"
    assert design.named_selections[5].name == "FirstPointSet"


def test_faces_edges(modeler: Modeler):
    """Test for verifying the correct creation and
    usage of ``Face`` and ``Edge`` objects."""

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
    # TODO: may be at some point these might change to planar?
    assert all(face.surface_type == SurfaceType.SURFACETYPE_UNKNOWN for face in faces)
    assert all(face.area > 0.0 for face in faces)
    assert abs(faces[0].area.to_base_units().m - sketch.faces[0].area.to_base_units().m) <= 1e-15
    assert all(face.body.id == body_polygon_comp.id for face in faces)

    # Get the normal to some of the faces
    assert faces[0].face_normal() == UnitVector3D(-UNITVECTOR3D_Z)  # Bottom
    assert faces[1].face_normal() == UNITVECTOR3D_Z  # Top

    # Get the central point of some of the surfaces
    assert faces[0].face_point(u=-0.03, v=-0.03) == Point3D([-30, -30, 0], UNITS.mm)
    assert faces[1].face_point(u=-0.03, v=-0.03) == Point3D([-30, -30, 30], UNITS.mm)

    loops = faces[0].loops
    assert len(loops) == 1
    assert loops[0].type == FaceLoopType.OUTER_LOOP
    assert loops[0].length is not None  # TODO : To be tested properly at some point
    assert loops[0].min_bbox is not None  # TODO : To be tested properly at some point
    assert loops[0].max_bbox is not None  # TODO : To be tested properly at some point
    assert len(loops[0].edges) == 5  # TODO : To be tested properly at some point

    # Now, from one of the lids (i.e. 0 - bottom) get all edges
    edges = faces[0].edges
    assert len(edges) == 5  # pentagon
    assert all(edge.id is not None for edge in edges)
    # TODO: may be at some point these might change to line?
    assert all(edge.curve_type == CurveType.CURVETYPE_UNKNOWN for edge in edges)
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
        [body_circle_comp, body_polygon_comp], UnitVector3D([1, 0, 0]), Quantity(48, UNITS.mm)
    )
    design.translate_bodies(
        [body_circle_comp, body_polygon_comp], UnitVector3D([0, -1, 1]), Quantity(88, UNITS.mm)
    )

    # Try translating a body that does not belong to this component - no error thrown,
    # but no operation performed either.
    circle_comp.translate_bodies(
        [body_polygon_comp], UnitVector3D([0, -1, 1]), Quantity(88, UNITS.mm)
    )


def test_download_file(modeler: Modeler, tmp_path_factory: pytest.TempPathFactory):
    """Test for downloading a design in multiple modes and verifying the correct download."""

    # Create your design on the server side
    design = modeler.create_design("MultipleBodyTranslation_Test")

    # Create a Sketch object and draw a circle
    sketch = Sketch()
    sketch.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))

    # Extrude the sketch
    design.extrude_sketch(name="MyCylinder", sketch=sketch, distance=Quantity(50, UNITS.mm))

    # Download the design
    file = tmp_path_factory.mktemp("scdoc_files_download") / "cylinder.scdocx"
    file_stream = tmp_path_factory.mktemp("scdoc_files_download") / "cylinder_stream.scdocx"
    design.download(file, as_stream=False)
    design.download(file_stream, as_stream=True)

    # Check that both files exist
    assert file.exists()
    assert file_stream.exists()

    # Check that we can also save it (even if it is not accessible on the server)
    file_save = tmp_path_factory.mktemp("scdoc_files_save") / "cylinder.scdocx"
    design.save(file_location=file_save)

    # Check for parasolid exports
    binary_parasolid_file = tmp_path_factory.mktemp("scdoc_files_download") / "cylinder.x_b"
    text_parasolid_file = tmp_path_factory.mktemp("scdoc_files_download") / "cylinder_stream.x_t"
    design.download(binary_parasolid_file, format=DesignFileFormat.PARASOLID_BIN, as_stream=True)
    design.download(text_parasolid_file, format=DesignFileFormat.PARASOLID_TEXT)
    assert binary_parasolid_file.exists()
    assert text_parasolid_file.exists()

    # Check also the invalid format is not supported - no download performed
    invalid_file = tmp_path_factory.mktemp("scdoc_files_download") / "invalid.file"
    design.download(invalid_file, format=DesignFileFormat.INVALID, as_stream=True)
    assert not invalid_file.exists()


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

    # Create a Sketch object and draw a couple of slots
    imprint_sketch = Sketch()
    imprint_sketch.slot(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm), Quantity(5, UNITS.mm))
    imprint_sketch.slot(Point2D([50, 50], UNITS.mm), Quantity(10, UNITS.mm), Quantity(5, UNITS.mm))

    # Extrude the sketch
    sketch = Sketch()
    sketch.box(Point2D([0, 0], UNITS.mm), Quantity(150, UNITS.mm), Quantity(150, UNITS.mm))
    body = design.extrude_sketch(name="MyBox", sketch=sketch, distance=Quantity(50, UNITS.mm))
    body_faces = body.faces

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

    # Now once the previous curves have been projected, let's try imprinting our sketch
    #
    # It should generate two additional faces to our box = 6 + 2
    _, new_faces = body.imprint_curves(faces=faces, sketch=imprint_sketch_2)

    assert len(new_faces) == 2
    assert len(body.faces) == 8


def test_beams(modeler: Modeler):
    """Test beam creation."""
    # Create your design on the server side
    design = modeler.create_design("BeamCreation")

    circle_profile_1 = design.add_beam_circular_profile(
        "CircleProfile1", Quantity(10, UNITS.mm), Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_Y
    )

    assert circle_profile_1.id is not None
    assert circle_profile_1.center == Point3D([0, 0, 0])
    assert circle_profile_1.radius.value.m_as(UNIT_LENGTH) == 0.01
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

    beam_1 = design.create_beam(
        Point3D([9, 99, 999], UNITS.mm), Point3D([8, 88, 888], UNITS.mm), circle_profile_1
    )

    assert beam_1.id is not None
    assert beam_1.start == Point3D([9, 99, 999], UNITS.mm)
    assert beam_1.end == Point3D([8, 88, 888], UNITS.mm)
    assert beam_1.profile == circle_profile_1
    assert beam_1.parent_component.id == design.id
    assert len(design.beams) == 1
    assert design.beams[0] == beam_1

    beam_1_str = str(beam_1)
    assert "ansys.geometry.core.designer.Beam" in beam_1_str
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

    nested_component = design.add_component("NestedComponent")

    beam_2 = nested_component.create_beam(
        Point3D([7, 77, 777], UNITS.mm), Point3D([6, 66, 666], UNITS.mm), circle_profile_2
    )

    assert beam_2.id is not None
    assert beam_2.profile == circle_profile_2
    assert beam_2.parent_component.id == nested_component.id
    assert len(nested_component.beams) == 1
    assert nested_component.beams[0] == beam_2


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
    assert design_points_1.design_point == point

    # Create another set of design points
    point_set_2 = [Point3D([10, 10, 10], UNITS.m), Point3D([20, 20, 20], UNITS.m)]
    design_points_2 = design.add_design_points("SecondPointSet", point_set_2)

    assert len(design.design_points) == 3

    nested_component = design.add_component("NestedComponent")

    design_point_3 = nested_component.add_design_point("Nested", Point3D([7, 77, 777], UNITS.mm))

    assert design_point_3.id is not None
    assert design_point_3.design_point == Point3D([7, 77, 777], UNITS.mm)
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
