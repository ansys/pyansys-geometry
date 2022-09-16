""" Test material assignment."""

from pint import Quantity

from ansys.geometry.core import Modeler
from ansys.geometry.core.materials import Material, MaterialProperty, MaterialPropertyType
from ansys.geometry.core.misc import UNITS


def test_material_creation():
    """Test the creation of a material on a design."""
    modeler = Modeler()

    design = modeler.create_design("my_design")

    material = Material("mat_1", 1000 * UNITS.kg / (UNITS.m * UNITS.m * UNITS.m))
    material_property_2 = MaterialProperty(
        MaterialPropertyType.POISSON_RATIO, "ratio_2", Quantity(142.2, UNITS.dimensionless)
    )
    material.add_property(
        type=material_property_2.type,
        display_name=material_property_2.display_name,
        quantity=material_property_2.quantity,
    )

    design.add_material(material)
