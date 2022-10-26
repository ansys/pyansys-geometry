"""``Material`` class module."""

from beartype import beartype
from beartype.typing import Dict, Optional, Sequence
from pint import Quantity

from ansys.geometry.core.materials.property import MaterialProperty, MaterialPropertyType


class Material:
    """
    Provides data structure for individual material.

    Parameters
    ----------
    name: str
        User-defined display name.
    density: ~pint.Quantity
        Material density.
    additional_properties: Optional[Sequence[MaterialProperty]]
        Additional material properties. By default, ``[]``.
    """

    @beartype
    def __init__(
        self,
        name: str,
        density: Quantity,
        additional_properties: Optional[Sequence[MaterialProperty]] = None,
    ):
        """Constructor method for ``Material``."""
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
        """Return the list of properties."""
        return self._properties

    @property
    def name(self) -> str:
        """Name assigned to the ``Material``."""
        return self._name

    @beartype
    def add_property(self, type: MaterialPropertyType, name: str, quantity: Quantity) -> None:
        """Add a ``MaterialProperty`` to the ``Material``.

        Parameters
        ----------
        type : MaterialPropertyType
            ``MaterialPropertyType`` value.
        name: str
            User-defined display name.
        quantity: ~pint.Quantity
            Value and unit.
        """
        property = MaterialProperty(type, name, quantity)
        self._properties[property.type] = property
