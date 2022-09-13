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

    def add_property(self, property: MaterialProperty) -> None:
        check_type(property, MaterialProperty)
        self._properties.append(property)

    def add_property(self, id: str, display_name: str, quantity: Quantity) -> None:
        self._properties.append(MaterialProperty(id, display_name, quantity))
