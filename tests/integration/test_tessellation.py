"""Test tessellation and plotting."""
from ansys.geometry.core import Modeler
from ansys.geometry.core.math import Plane, Point2D, Point3D
from ansys.geometry.core.misc.units import UNITS as u
from ansys.geometry.core.sketch import Sketch


def test_tessellate(modeler: Modeler):
    origin = Point3D([0, 0, 0])
    plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 0, 1])
    sketch = Sketch(plane)
    box = sketch.box(Point2D([2, 0]), 4, 4)
    design = modeler.create_design("my-design")
    my_comp = design.add_component("my-comp")
    body = my_comp.extrude_sketch("my-sketch", sketch, 1 * u.m)
    blocks = body.tessellate()
    assert "MultiBlock" in str(blocks)
    assert blocks.n_blocks == 6
    mesh = body.tessellate(merge=True)
    assert "PolyData" in str(mesh)
    assert mesh.n_cells == 12
    assert mesh.n_points == 24
    assert mesh.n_arrays == 0
