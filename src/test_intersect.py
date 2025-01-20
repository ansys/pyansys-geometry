a = 1
from ansys.geometry.core import Modeler
#from ansys.geometry.core import launch_modeler_with_discovery
#modeler = launch_modeler_with_discovery()
modeler = Modeler(host="localhost", port= 50051)
design = modeler.open_file(r"D:\ANSYSDEV\pyansys-geometry\tests\integration\files\Combine.Merge.scdocx")
#problem_areas = modeler.repair_tools.find_split_edges(design.bodies, 1.0, 3.6)
b = 1
b1 = design.bodies[0]
b2 = design.bodies[1]
#b1.intersect(b2,True)
b1.unite(b2, True)
d = 2
b1.copy