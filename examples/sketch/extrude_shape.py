from pint import Quantity

from ansys.geometry.core import Modeler
from ansys.geometry.core.math import Point
from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.sketch import Sketch

sketch = Sketch()

sketch.draw_circle(Point([10, 10, 0], UNITS.mm), Distance(10, UNITS.mm))

modeler = Modeler(host="0.0.0.0", port=50051)

design = modeler.create_design("ExtrudeProfile")

design.extrude_sketch("JustACircle", sketch, Quantity(10, UNITS.mm))

design.save("C:/ExtrudeProfile.scdocx")
