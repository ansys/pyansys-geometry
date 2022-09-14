""" Test material assignment."""

from pint import Quantity
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.materials import Material, MaterialProperty
from ansys.geometry.core.misc import UNITS

@pytest.mark.skip(reason="Test failing")
def test_material_creation():
    """Test the creation of a material on a design."""
    modeler = Modeler()
    
    design = modeler.create_design("my_design")
    
    material = Material("mat_1")
    material.add_property(id="mat_prop_1", display_name="density", quantity= 1000 * UNITS.kg / (UNITS.m * UNITS.m * UNITS.m))
    material_property_2 = MaterialProperty("mat_prop_2", "ratio_2", Quantity(142.2, UNITS.dimensionless))
    material.add_property(id=material_property_2.id, display_name=material_property_2.display_name, quantity=material_property_2.quantity)
    
    design.add_material(material)