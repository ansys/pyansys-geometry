from ansys.geometry.core import launch_modeler
from ansys.geometry.core.math import Point3D, UnitVector3D
from ansys.geometry.core.math.frame import Frame
from ansys.geometry.core.math.plane import Plane
from ansys.geometry.core.misc import UNITS


modeler = launch_modeler()
    

design = modeler.create_design("MyAssembly")
main_component = design.add_component("MainComponent")

xy_plane = Plane(
    origin=Point3D([0, 0, 0], UNITS.m),
    direction_x=UnitVector3D([1, 0, 0]),
    direction_y=UnitVector3D([0, 1, 0]),
)
datum_plane = main_component.create_datum_plane("XY_Reference_Plane", xy_plane)
print(f"Created datum plane: {datum_plane.name}")

ref_frame = Frame(
    origin=Point3D([0, 0, 0], UNITS.m),
    direction_x=UnitVector3D([1, 0, 0]),
    direction_y=UnitVector3D([0, 1, 0]),
)
coord_system = main_component.create_coordinate_system(
    "Reference_Frame", ref_frame
)
print(f"Created coordinate system: {coord_system.name}")

# DEBUG: Check actual types
print(f"\n[DEBUG] Datum plane ID type: {type(datum_plane.id)}")
print(f"[DEBUG] Datum plane ID value: {datum_plane.id}")
print(f"[DEBUG] Coordinate system ID type: {type(coord_system.id)}")
print(f"[DEBUG] Coordinate system ID value: {coord_system.id}")
print(f"[DEBUG] Has .id attribute?: {hasattr(coord_system.id, 'id')}")
if hasattr(coord_system.id, 'id'):
    print(f"[DEBUG] Inner .id value: {coord_system.id.id}")

# Create a named selection that groups these reference entities
ref_entities = design.create_named_selection(
    "ReferenceGeometry",
    datum_planes=[datum_plane],
    coordinate_systems=[coord_system],
)
print(f"Created named selection: {ref_entities.name}")

# Access the named selection members as a final user would
print("\nNamed Selection Contents:")
print(f"  Datum planes: {[dp.name for dp in ref_entities.datum_planes]}")
print(f"  Coordinate systems: {[cs.name for cs in ref_entities.coordinate_systems]}")

print(input("Press Enter to exit..."))








