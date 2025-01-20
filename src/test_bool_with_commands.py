a = 1
from ansys.geometry.core import Modeler
modeler = Modeler(host="localhost", port= 50051)
design = modeler.open_file(r"D:\ANSYSDEV\pyansys-geometry\tests\integration\files\Combine.Merge.scdocx")

d1 = design.bodies[0]
d2 = design.bodies[1]
    # 1.c.i.x

#d1.unite(d2)
d1.intersect(d2)
#d1.subtract(d2)

assert d2.is_alive
b = 1