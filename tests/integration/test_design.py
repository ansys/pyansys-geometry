"""Test design interaction."""

from pint import Quantity

from ansys.geometry.core import Modeler
from ansys.geometry.core.materials import Material, MaterialProperty, MaterialPropertyType
from ansys.geometry.core.math import Point
from ansys.geometry.core.misc import Distance, UNITS
from ansys.geometry.core.sketch import Sketch


def test_design_extrusion_and_material_assignment(modeler: Modeler):
    """Test in charge of validating the extrusion of a simple
    circle as a cylinder and assigning materials to it."""

    # Create a Sketch and draw a circle (all client side)
    sketch = Sketch()
    sketch.draw_circle(Point([10, 10, 0], UNITS.mm), Distance(10, UNITS.mm))

    # Create your design on the server side
    design = modeler.create_design("ExtrudeProfile")

    # Add a material to your design
    material = Material(
        "steel",
        Quantity(125, 1000 * UNITS.kg / (UNITS.m * UNITS.m * UNITS.m)),
        [
            MaterialProperty(
                MaterialPropertyType.POISSON_RATIO, "myPoisson", Quantity(0.33, UNITS.dimensionless)
            )
        ],
    )
    material.add_property(MaterialPropertyType.TENSILE_STRENGTH, "myTensile", Quantity(45))
    design.add_material(material)

    # Extrude the sketch to create a Body
    body = design.extrude_sketch("JustACircle", sketch, Quantity(10, UNITS.mm))

    # Assign a material to a Body
    body.assign_material(material)

    # Not possible to save to file from a container (CI/CD)
    #
    # design.save("C:/ExtrudeProfile.scdocx")
