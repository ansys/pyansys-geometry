"""``MaterialProperty`` class module."""

from enum import Enum, unique

from beartype import beartype as check_input_types
from pint import Quantity


@unique
class MaterialPropertyType(Enum):
    """Enum holding the possible values for ``MaterialProperty`` objects."""

    DENSITY = "Density"
    ELASTIC_MODULUS = "ElasticModulus"
    POISSON_RATIO = "PoissonsRatio"
    SHEAR_MODULUS = "ShearModulus"
    SPECIFIC_HEAT = "SpecificHeat"
    TENSILE_STRENGTH = "TensileStrength"
    THERMAL_CONDUCTIVITY = "ThermalConductivity"


class MaterialProperty:
    """
    Provides data structure for individual material properties.

    Parameters
    ----------
    type : MaterialPropertyType
        ``MaterialPropertyType`` value.
    name: str
        User-defined display name.
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
        """Constructor method for ``Material Property``."""
        self._type = type
        self._name = name
        self._quantity = quantity

    @property
    def type(self) -> MaterialPropertyType:
        """Id of the ``MaterialProperty``."""
        return self._type

    @property
    def name(self) -> str:
        """Display name of the ``MaterialProperty``."""
        return self._name

    @property
    def quantity(self) -> Quantity:
        """Quantity of the ``MaterialProperty``."""
        return self._quantity
