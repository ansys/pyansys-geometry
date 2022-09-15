"""``Material`` class module."""

from typing import List, Optional

from pint import Quantity

from ansys.geometry.core.materials.property import MaterialProperty
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
        self._density = MaterialProperty("density", display_name, density)

        # Add the density to the properties list
        additional_properties.append(self._density)
        self._properties = additional_properties

    @property
    def properties(self) -> List[MaterialProperty]:
        """Return the list of properties."""
        return self._properties

    def add_property(self, id: str, display_name: str, quantity: Quantity) -> None:
        """Add a ``MaterialProperty`` to the ``Material``.

        Parameters
        ----------
        id : str
            User-defined identifier.
        display_name: str
            User-defined display name.
        quantity: ~pint.Quantity
            Value and unit.
        """
        self._properties.append(MaterialProperty(id, display_name, quantity))
