from pint import Quantity

from ansys.geometry.core import Modeler
from ansys.geometry.core.math import UNITVECTOR3D_X, UNITVECTOR3D_Y, Point2D, Point3D
from ansys.geometry.core.misc import UNITS
from ansys.geometry.core.sketch import Sketch


def test_bug(modeler: Modeler):
    """Bug test."""

    # Create your design on the server side
    design = modeler.create_design("BugTest")

    sketch_1 = Sketch()
    sketch_1.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))
    circle_comp = design.add_component("CircleComponent")
    body_circle_comp = circle_comp.extrude_sketch("Circle", sketch_1, Quantity(50, UNITS.mm))

    # NAMED SELECTIONS TEST
    # =========================================================================

    # Create the NamedSelection
    design.create_named_selection("OnlyCircle", bodies=[body_circle_comp])
    assert len(design.named_selections) == 1
    assert design.named_selections[0].name == "OnlyCircle"

    # Try deleting a non-existing named selection
    design.delete_named_selection("MyInventedNamedSelection")

    # Now, let's delete the duplicated entry OnlyCircle
    design.delete_named_selection(design.named_selections[0].id)
    # assert len(design.named_selections) == 0

    # CREATE BEAM PART
    # =========================================================================

    circle_profile_1 = design.add_beam_circular_profile(
        "CircleProfile1", Quantity(10, UNITS.mm), Point3D([0, 0, 0]), UNITVECTOR3D_X, UNITVECTOR3D_Y
    )

    design.create_beam(
        Point3D([9, 99, 999], UNITS.mm), Point3D([8, 88, 888], UNITS.mm), circle_profile_1
    )

    # NAMED SELECTIONS TEST AGAIN
    # =========================================================================

    # Create the NamedSelection
    design.create_named_selection("OnlyCircle_2", bodies=[body_circle_comp])
    assert len(design.named_selections) == 1
    assert design.named_selections[0].name == "OnlyCircle_2"

    # Try deleting a non-existing named selection
    design.delete_named_selection("MyInventedNamedSelection")

    # Now, let's delete the duplicated entry OnlyCircle_2
    design.delete_named_selection(design.named_selections[0].id)
    # assert len(design.named_selections) == 0