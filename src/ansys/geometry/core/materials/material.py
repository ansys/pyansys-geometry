"""Provides the ``Material`` class."""

from beartype import beartype as check_input_types
from beartype.typing import Dict, Optional, Sequence
from pint import Quantity

from ansys.geometry.core.materials.property import MaterialProperty, MaterialPropertyType


class Material:
    """
    Provides the data structure for a material.

    Parameters
    ----------
    name: str
        Material name.
    density: ~pint.Quantity
        Material density.
    additional_properties: Sequence[MaterialProperty], default: None
        Additional material properties.
    """

    @check_input_types
    def __init__(
        self,
        name: str,
        density: Quantity,
        additional_properties: Optional[Sequence[MaterialProperty]] = None,
    ):
        """Initialize ``Material`` class."""
        self._name = name
        self._density = MaterialProperty(MaterialPropertyType.DENSITY, "Density", density)
        if not additional_properties:
            additional_properties = []

        # Add the density to the properties list
        additional_properties.append(self._density)
        self._properties = {}
        for property in additional_properties:
            self._properties[property.type] = property

    @property
    def properties(self) -> Dict[MaterialPropertyType, MaterialProperty]:
        """List of material properties."""
        return self._properties

    @property
    def name(self) -> str:
        """Material name."""
        return self._name

    @check_input_types
    def add_property(self, type: MaterialPropertyType, name: str, quantity: Quantity) -> None:
        """Add a material property to the ``Material`` class.

        Parameters
        ----------
        type : MaterialPropertyType
            Type of the material property.
        name: str
            Material name.
        quantity: ~pint.Quantity
            Value and unit.
        """
        property = MaterialProperty(type, name, quantity)
        self._properties[property.type] = property
