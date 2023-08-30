"""Test edges."""

from ansys.geometry.core import Modeler
from ansys.geometry.core.math import Point2D, Vector3D
from ansys.geometry.core.misc.units import UNITS, Quantity
from ansys.geometry.core.sketch import Sketch


def test_edges_startend_prism(modeler: Modeler):
    # init modeler
    design = modeler.create_design("Prism")

    # define body
    body_sketch = Sketch()
    body_sketch.box(Point2D([10, 10], UNITS.m), Quantity(5, UNITS.m), Quantity(3, UNITS.m))
    prism_body = design.extrude_sketch("JustAPrism", body_sketch, Quantity(13, UNITS.m))
    for edge in prism_body.edges:
        vec = Vector3D.from_points(edge.start_point, edge.end_point)
        assert vec.magnitude == edge.length.magnitude
