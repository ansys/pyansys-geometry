"""``Material`` class module."""

from typing import List, Optional

from pint import Quantity

from ansys.geometry.core.materials.property import MaterialProperty, MaterialPropertyType
from ansys.geometry.core.misc import check_type


class Material:
    """
    Provides data structure for individual material.

    Parameters
    ----------
    display_name: str
        User-defined display name.
    density: ~pint.Quantity
        Material density.
    additional_properties: Optional[List[MaterialProperty]]
        Additional material properties. By default, ``[]``.
    """

    def __init__(
        self,
        display_name: str,
        density: Quantity,
        additional_properties: Optional[List[MaterialProperty]] = [],
    ):
        """Constructor method for ``Material``."""
        self._display_name = display_name
        check_type(density, Quantity)
        self._density = MaterialProperty(MaterialPropertyType.DENSITY, display_name, density)

        # Add the density to the properties list
        additional_properties.append(self._density)
        self._properties = additional_properties

    @property
    def properties(self) -> List[MaterialProperty]:
        """Return the list of properties."""
        return self._properties

    def add_property(
        self, type: MaterialPropertyType, display_name: str, quantity: Quantity
    ) -> None:
        """Add a ``MaterialProperty`` to the ``Material``.

        Parameters
        ----------
        type : MaterialPropertyType
            ``MaterialPropertyType`` value.
        display_name: str
            User-defined display name.
        quantity: ~pint.Quantity
            Value and unit.
        """
        self._properties.append(MaterialProperty(type, display_name, quantity))
