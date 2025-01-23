a = 1
import numpy as np
import pytest

from ansys.geometry.core import Modeler

# from ansys.geometry.core import launch_modeler_with_discovery
# modeler = launch_modeler_with_discovery()
from ansys.geometry.core.math import (
    Point2D,
    Point3D,
    UnitVector3D,
    Vector3D,
)
from ansys.geometry.core.math.point import Point2D
from ansys.geometry.core.misc.accuracy import Accuracy
from ansys.geometry.core.sketch import Sketch

modeler = Modeler(host="localhost", port=50051)

design = modeler.create_design("TestBooleanOperationsWithKeepOther")

comp1 = design.add_component("Comp1")
comp2 = design.add_component("Comp2")
comp3 = design.add_component("Comp3")

body1 = comp1.extrude_sketch("Body1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
body2 = comp2.extrude_sketch("Body2", Sketch().box(Point2D([0.5, 0]), 1, 1), 1)
body3 = comp3.extrude_sketch("Body3", Sketch().box(Point2D([5, 0]), 1, 1), 1)

# ---- Verify subtract operation ----
body1.subtract([body2, body3], keep_other=True)

assert body2.is_alive
assert body3.is_alive
assert len(comp1.bodies) == 1
assert len(comp2.bodies) == 1
assert len(comp3.bodies) == 1

# ---- Verify unite operation ----
body1.unite([body2, body3], keep_other=True)

assert body1.is_alive
assert not body2.is_alive
assert len(comp1.bodies) == 1
assert len(comp2.bodies) == 0
assert len(comp3.bodies) == 0

# ---- Verify intersect operation ----
comp2 = design.add_component("Comp2")
comp3 = design.add_component("Comp3")
body1 = comp1.extrude_sketch("Body1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
body2 = comp2.extrude_sketch("Body2", Sketch().box(Point2D([0.5, 0]), 1, 1), 1)
body3 = comp3.extrude_sketch("Body3", Sketch().box(Point2D([5, 0]), 1, 1), 1)
body1.intersect([body2, body3], keep_other=True)

assert body1.is_alive
assert body2.is_alive
assert body3.is_alive
assert len(comp1.bodies) == 2
assert len(comp2.bodies) == 1
assert len(comp3.bodies) == 1


design = modeler.create_design("TestBooleanOperations")

comp1 = design.add_component("Comp1")
comp2 = design.add_component("Comp2")
comp3 = design.add_component("Comp3")
body1 = comp1.extrude_sketch("Body1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
body2 = comp2.extrude_sketch("Body2", Sketch().box(Point2D([0.5, 0]), 1, 1), 1)
body3 = comp3.extrude_sketch("Body3", Sketch().box(Point2D([5, 0]), 1, 1), 1)

# 1.a.i.x
copy1 = body1.copy(comp1, "Copy1")
copy2 = body2.copy(comp2, "Copy2")
copy1.intersect(copy2, False)

assert not copy2.is_alive
assert body2.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

# 1.a.i.y
copy1 = body1.copy(comp1, "Copy1")
copy2 = body2.copy(comp2, "Copy2")
copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
copy1.intersect(copy2, False)

assert not copy2.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 0.25)

# 1.a.ii
copy1 = body1.copy(comp1, "Copy1")
copy3 = body3.copy(comp3, "Copy3")
with pytest.raises(ValueError, match="bodies do not intersect"):
    copy1.intersect(copy3)

assert copy1.is_alive
assert copy3.is_alive

# 1.b.i.x
copy1 = body1.copy(comp1, "Copy1")
copy2 = body2.copy(comp2, "Copy2")
copy1.subtract(copy2)

assert not copy2.is_alive
assert body2.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

# 1.b.i.y
copy1 = body1.copy(comp1, "Copy1")
copy2 = body2.copy(comp2, "Copy2")
copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
copy1.subtract(copy2)

assert not copy2.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 0.75)

# 1.b.ii
copy1 = body1.copy(comp1, "Copy1")
copy1a = body1.copy(comp1, "Copy1a")
# with pytest.raises(ValueError):
copy1.subtract(copy1a)
assert copy1.is_alive
assert not copy1a.is_alive

# 1.b.iii
copy1 = body1.copy(comp1, "Copy1")
copy3 = body3.copy(comp3, "Copy3")
with pytest.raises(ValueError):
    copy1.subtract(copy3)

assert Accuracy.length_is_equal(copy1.volume.m, 1)
assert copy1.volume
# assert not copy3.is_alive

# 1.c.i.x
copy1 = body1.copy(comp1, "Copy1")
copy2 = body2.copy(comp2, "Copy2")
copy1.unite(copy2)

assert not copy2.is_alive
assert body2.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 1.5)

# 1.c.i.y
copy1 = body1.copy(comp1, "Copy1")
copy2 = body2.copy(comp2, "Copy2")
copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
copy1.unite(copy2)

assert not copy2.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 1.75)

# 1.c.ii
copy1 = body1.copy(comp1, "Copy1")
copy3 = body3.copy(comp3, "Copy3")
with pytest.raises(ValueError):
    copy1.unite(copy3)

# assert not copy3.is_alive
assert body3.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 1)

# Test instance/instance
comp1_i = design.add_component("Comp1_i", comp1)
comp2_i = design.add_component("Comp2_i", comp2)
comp3_i = design.add_component("Comp3_i", comp3)

comp1_i.modify_placement(
    Vector3D([52, 61, -43]), Point3D([-4, 26, 66]), UnitVector3D([-21, 20, 87]), np.pi / 4
)
comp2_i.modify_placement(
    Vector3D([52, 61, -43]), Point3D([-4, 26, 66]), UnitVector3D([-21, 20, 87]), np.pi / 4
)
comp3_i.modify_placement(
    Vector3D([52, 61, -43]), Point3D([-4, 26, 66]), UnitVector3D([-21, 20, 87]), np.pi / 4
)

body1 = comp1_i.bodies[0]
body2 = comp2_i.bodies[0]
body3 = comp3_i.bodies[0]

# 2.a.i.x
copy1 = body1.copy(comp1_i, "Copy1")
copy2 = body2.copy(comp2_i, "Copy2")
copy1.intersect(copy2, False)

assert not copy2.is_alive
assert body2.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

# 2.a.i.y
copy1 = body1.copy(comp1_i, "Copy1")
copy2 = body2.copy(comp2_i, "Copy2")
copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
copy1.intersect(copy2, False)

assert not copy2.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 0.25)

# 2.a.ii
copy1 = body1.copy(comp1_i, "Copy1")
copy3 = body3.copy(comp3_i, "Copy3")
with pytest.raises(ValueError, match="bodies do not intersect"):
    copy1.intersect(copy3, False)

assert copy1.is_alive
assert copy3.is_alive

# 2.b.i.x
copy1 = body1.copy(comp1_i, "Copy1")
copy2 = body2.copy(comp2_i, "Copy2")
copy1.subtract(copy2)


assert not copy2.is_alive
assert body2.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 0.5)

# 2.b.i.y
copy1 = body1.copy(comp1_i, "Copy1")
copy2 = body2.copy(comp2_i, "Copy2")
copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
copy1.subtract(copy2)

assert not copy2.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 0.75)

# 2.b.ii
copy1 = body1.copy(comp1_i, "Copy1")
copy1a = body1.copy(comp1_i, "Copy1a")
# with pytest.raises(ValueError):
copy1.subtract(copy1a)

assert copy1.is_alive
assert not copy1a.is_alive

# 2.b.iii
copy1 = body1.copy(comp1_i, "Copy1")
copy3 = body3.copy(comp3_i, "Copy3")
with pytest.raises(ValueError):
    copy1.subtract(copy3)
assert Accuracy.length_is_equal(copy1.volume.m, 1)
assert copy1.volume
assert copy3.is_alive
# 2.c.i.x
copy1 = body1.copy(comp1_i, "Copy1")
copy2 = body2.copy(comp2_i, "Copy2")
copy1.unite(copy2)

assert not copy2.is_alive
assert body2.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 1.5)

# 2.c.i.y
copy1 = body1.copy(comp1_i, "Copy1")
copy2 = body2.copy(comp2_i, "Copy2")
copy2.translate(UnitVector3D([1, 0, 0]), 0.25)
copy1.unite(copy2)

assert not copy2.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 1.75)
# 2.c.ii
copy1 = body1.copy(comp1_i, "Copy1")
copy3 = body3.copy(comp3_i, "Copy3")
with pytest.raises(ValueError):
    copy1.unite(copy3)

assert copy3.is_alive
assert body3.is_alive
assert Accuracy.length_is_equal(copy1.volume.m, 1)
