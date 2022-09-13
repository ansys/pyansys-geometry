"""``MaterialProperty`` class module."""

from pint import Quantity


class MaterialProperty:
    """
    Provides data structure for individual material properties.

    Parameters
    ----------
    id : str
        User-defined identifier.
    display_name: str
        User-defined display name.
    quantity: ~pint.Quantity
        Value and unit.
    """

    def __init__(
        self,
        id: str,
        display_name: str,
        quantity: Quantity,
    ):
        """Constructor method for ``Material Property``."""
        self._id = id
        self._display_name = display_name
        self._quantity = quantity

    @property
    def id(self) -> str:
        """Id of the ``MaterialProperty``."""
        return self._id

    @property
    def display_name(self) -> str:
        """Display name of the ``MaterialProperty``."""
        return self._display_name

    @property
    def quantity(self) -> Quantity:
        """Quantity of the ``MaterialProperty``."""
        return self._quantity
