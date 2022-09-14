"""``Material`` class module."""

from typing import List, Optional

from pint import Quantity

from ansys.geometry.core.materials.property import MaterialProperty


class Material:
    """
    Provides data structure for individual material.

    Parameters
    ----------
    display_name: str
        User-defined display name.
    properties: Optional[List[MaterialProperty]]
        Material properties.
    """

    def __init__(
        self,
        display_name: str,
        properties: Optional[List[MaterialProperty]] = [],
    ):
        """Constructor method for ``Material``."""
        self._display_name = display_name
        self._properties = properties

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
