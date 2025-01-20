a = 1
from ansys.geometry.core import Modeler
from ansys.geometry.core.sketch import Sketch
#from ansys.geometry.core import launch_modeler_with_discovery
#modeler = launch_modeler_with_discovery()
from ansys.geometry.core.math import (
    IDENTITY_MATRIX44,
    UNITVECTOR3D_X,
    UNITVECTOR3D_Y,
    UNITVECTOR3D_Z,
    Frame,
    Plane,
    Point2D,
    Point3D,
    UnitVector3D,
    Vector3D,
)
modeler = Modeler(host="localhost", port= 50051)

design = modeler.create_design("TestBooleanOperations")

comp1 = design.add_component("Comp1")
comp2 = design.add_component("Comp2")
comp3 = design.add_component("Comp3")

body1 = comp1.extrude_sketch("Body1", Sketch().box(Point2D([0, 0]), 1, 1), 1)
body2 = comp2.extrude_sketch("Body2", Sketch().box(Point2D([0.5, 0]), 1, 1), 1)
body3 = comp3.extrude_sketch("Body3", Sketch().box(Point2D([5, 0]), 1, 1), 1)

    # 1.c.i.x
copy1 = body1.copy(comp1, "Copy1")
copy2 = body2.copy(comp2, "Copy2")
copy1.unite(copy2)

assert not copy2.is_alive
assert body2.is_alive
b = 1