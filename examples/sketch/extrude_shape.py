from pint import Quantity

from ansys.geometry.core import Modeler
from ansys.geometry.core.materials import Material
from ansys.geometry.core.materials.property import MaterialProperty, MaterialPropertyType
from ansys.geometry.core.math import Point
from ansys.geometry.core.misc.measurements import Distance
from ansys.geometry.core.misc.units import UNITS
from ansys.geometry.core.sketch import Sketch

sketch = Sketch()

sketch.draw_circle(Point([10, 10, 0], UNITS.mm), Distance(10, UNITS.mm))

modeler = Modeler(host="localhost", port=50051)

design = modeler.create_design("ExtrudeProfile")

material = Material(
    "steel",
    Quantity(125, 1000 * UNITS.kg / (UNITS.m * UNITS.m * UNITS.m)),
    [
        MaterialProperty(
            MaterialPropertyType.POISSON_RATIO, "myPoisson", Quantity(0.33, UNITS.dimensionless)
        )
    ],
)

material.add_property(MaterialPropertyType.TENSILE_STRENGTH, "myTensile", Quantity(45))

design.add_material(material)

body = design.extrude_sketch("JustACircle", sketch, Quantity(10, UNITS.mm))

body.assign_material(material)

design.save("C:/ExtrudeProfile.scdocx")
