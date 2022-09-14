from ansys.geometry.core import launch_modeler
from ansys.geometry.core.math import Point
from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.sketch import Sketch

modeler = launch_modeler()

design = modeler.create_design()

sketch = Sketch()

sketch.draw_circle(Point(0, 0), Distance(10))

design.extrude_sketch("Just a circle", sketch, 100)

design.save()
