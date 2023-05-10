"""Provides the ``MaterialProperty`` class."""

from enum import Enum, unique

from beartype import beartype as check_input_types
from pint import Quantity


@unique
class MaterialPropertyType(Enum):
    """Provides an enum holding the possible values for ``MaterialProperty`` objects."""

    DENSITY = "Density"
    ELASTIC_MODULUS = "ElasticModulus"
    POISSON_RATIO = "PoissonsRatio"
    SHEAR_MODULUS = "ShearModulus"
    SPECIFIC_HEAT = "SpecificHeat"
    TENSILE_STRENGTH = "TensileStrength"
    THERMAL_CONDUCTIVITY = "ThermalConductivity"

    def from_id(id: str) -> "MaterialPropertyType":
        """
        Return the ``MaterialPropertyType`` value from the service representation.

        Parameters
        ----------
        id : str
            Geometry Service string representation of a property type.

        Returns
        -------
        MaterialPropertyType
            Common name for property type.
        """
        relations = {
            "General.Density.Mass": "Density",
            "Linear.Isotropic.Emodulus": "ElasticModulus",
            "Linear.Isotropic.Poisson": "PoissonsRatio",
            "Linear.Isotropic.Gmodulus": "ShearModulus",
            "Heat.Iso.Cp": "SpecificHeat",
            "Nonlinear.vonMises.Ultimate": "TensileStrength",
            "Heat.Iso.Conduction": "ThermalConductivity",
        }
        return MaterialPropertyType(relations.get(id))


class MaterialProperty:
    """
    Provides the data structure for a material property.

    Parameters
    ----------
    type : MaterialPropertyType
        Type of the material property.
    name: str
        Material property name.
    quantity: ~pint.Quantity
        Value and unit.
    """

    @check_input_types
    def __init__(
        self,
        type: MaterialPropertyType,
        name: str,
        quantity: Quantity,
    ):
        """Initialize ``MaterialProperty`` class."""
        self._type = type
        self._name = name
        self._quantity = quantity

    @property
    def type(self) -> MaterialPropertyType:
        """Material property ID."""
        return self._type

    @property
    def name(self) -> str:
        """Material property name."""
        return self._name

    @property
    def quantity(self) -> Quantity:
        """Material property quantity and unit."""
        return self._quantity
