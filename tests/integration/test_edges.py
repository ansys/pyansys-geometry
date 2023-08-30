"""Test edges."""

from ansys.geometry.core import Modeler
from ansys.geometry.core.math import Point2D, Vector3D
from ansys.geometry.core.misc.units import UNITS, Quantity
from ansys.geometry.core.sketch import Sketch


def test_edges_startend_box(modeler: Modeler):
    # init modeler
    design = modeler.create_design("Box")

    # define body
    body_sketch = Sketch()
    body_sketch.box(Point2D([10, 10], UNITS.m), Quantity(10, UNITS.m), Quantity(10, UNITS.m))
    box_body = design.extrude_sketch("JustABox", body_sketch, Quantity(10, UNITS.m))
    for edge in box_body.edges:
        vec = Vector3D.from_points(edge.start_point, edge.end_point)
        assert vec.magnitude == edge.length.magnitude
