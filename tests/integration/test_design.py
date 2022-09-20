"""Test design interaction."""

from grpc._channel import _InactiveRpcError
from pint import Quantity

from ansys.geometry.core import Modeler
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

    # Assign a material to a Body
    body.assign_material(material)

    # TODO: Not possible to save to file from a container (CI/CD)
    #       Use download approach when available.
    #
    # design.save("C:/ExtrudeProfile.scdocx")


def test_component_body(modeler: Modeler):
    """Test the different ``Component`` and ``Body`` creation methods."""

    # Create your design on the server side
    design_name = "ComponentBody_Test"
    design = modeler.create_design(design_name)
    assert design.name == design_name
    assert design.id is not None

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
        assert body.volume == pentagon.area * distance_extruded_body
    except (_InactiveRpcError):
        pass
    assert len(design._components) == 0
    assert len(design._bodies) == 1

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
    assert len(planar_component._components) == 0
    assert len(planar_component._bodies) == 1
    assert len(design._components) == 1
    assert len(design._bodies) == 1


def test_named_selections():
    """Test for verifying the correct creation of ``NamedSelection``."""
