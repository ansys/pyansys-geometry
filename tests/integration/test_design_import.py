"""Test design import."""

from pint import Quantity

from ansys.geometry.core import Modeler
from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.sketch import Sketch


def test_design_import_simple_case(modeler: Modeler):
    # With the given session let's create a the following Design
    #
    # Create your design on the server side
    design = modeler.create_design("ReadDesign")

    # Create a Sketch object and draw a circle (all client side)
    sketch = Sketch()
    sketch.circle(Point2D([-30, -30], UNITS.mm), Quantity(10, UNITS.mm))
    distance = Quantity(30, UNITS.mm)

    #  The following component hierarchy is made
    #
    #           |---> comp_1 ---|---> nested_1_comp_1 ---> nested_1_nested_1_comp_1 X
    #           |               |                              X BODY X
    #           |               |---> nested_2_comp_1
    #           |                         X BODY X
    #           |
    # DESIGN ---|---> comp_2 -------> nested_1_comp_2
    #           |
    #           |
    #           |---> comp_3
    #                X BODY X
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
    comp_2.add_component("Nested_1_Component_2")

    # Create the bodies
    comp_3.extrude_sketch(name="comp_3_circle", sketch=sketch, distance=distance)
    nested_2_comp_1.extrude_sketch(name="nested_2_comp_1_circle", sketch=sketch, distance=distance)
    nested_1_nested_1_comp_1.extrude_sketch(
        name="nested_1_nested_1_comp_1_circle", sketch=sketch, distance=distance
    )

    # Now, let's create a new client session
    new_client = Modeler()
    read_design = new_client.read_existing_design()
    #
    # TODO: And now assert all its elements
    assert read_design is None
    assert len(new_client._designs) == 1
