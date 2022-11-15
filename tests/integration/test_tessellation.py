"""Test tessellation and plotting."""
from ansys.geometry.core import Modeler
from ansys.geometry.core.math import Plane, Point2D
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.sketch import Sketch


def test_body_tessellate(modeler: Modeler):
    """Test the body tessellation"""
    sketch = Sketch()
    sketch.box(Point2D([2, 0]), 4, 4)
    design = modeler.create_design("Design1")
    my_comp = design.add_component("Component1")
    body = my_comp.extrude_sketch("Sketch1", sketch, 1 * UNITS.m)

    # Tessellate the body without merging the individual faces
    blocks = body.tessellate()
    assert "MultiBlock" in str(blocks)
    assert blocks.n_blocks == 6
    assert (blocks.center == ([2, 0, 0.5])).all()

    # Tessellate the body without merging the individual faces
    mesh = body.tessellate(merge=True)
    assert "PolyData" in str(mesh)
    assert mesh.n_cells == 12
    assert mesh.n_points == 24
    assert mesh.n_arrays == 0


def test_component_tessellate(modeler: Modeler):
    """Test the component tessellation"""
    sketch_1 = Sketch()
    sketch_1.box(Point2D([10, 10]), width=10, height=5)
    sketch_1.circle(Point2D([0, 0]), radius=25 * UNITS.m)
    design = modeler.create_design("Design")
    comp = design.add_component("Component")
    comp.extrude_sketch("Body", sketch=sketch_1, distance=10 * UNITS.m)
    sketch_2 = Sketch(Plane([0, 0, 10]))
    sketch_2.box(Point2D([10, 10]), width=10, height=5)
    sketch_2.circle(Point2D([0, 0]), radius=25 * UNITS.m)
    comp.extrude_sketch("Body", sketch=sketch_2, distance=10 * UNITS.m)
    dataset = comp.tessellate(merge_bodies=True)
    assert "MultiBlock" in str(dataset)
    assert dataset.n_blocks == 1
    mesh = comp.tessellate(merge_component=True)
    assert mesh.n_cells == 3280
    assert mesh.n_arrays == 0
    assert mesh.n_points == 3300
