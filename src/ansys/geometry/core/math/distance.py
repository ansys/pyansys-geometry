"""``Distance`` class module."""

from typing import Optional, Union

from pint import Quantity, Unit

from ansys.geometry.core.misc.checks import check_is_float_int
from ansys.geometry.core.misc.units import UNIT_LENGTH, PhysicalQuantity
from ansys.geometry.core.typing import Real


class Distance(PhysicalQuantity):
    """PhysicalQuantity subclass for holding a distance.

    Parameters
    ----------
    value : Union[Real, Quantity]
        The value of the distance to be considered.
    unit : Optional[Unit], optional
        The units to be considered for the given value, by default UNIT_LENGTH.
    """

    def __init__(self, value: Union[Real, Quantity], unit: Optional[Unit] = UNIT_LENGTH):
        """Constructor for ``Distance``."""
        # Check the input
        if isinstance(value, Quantity):
            # TODO: inform that if Quantity is given, we will ignore provided unit value
            unit = value.units
        else:
            check_is_float_int(value, "value")
            value = Quantity(value, unit)

        # Call the PhysicalQuantity ctor.
        super().__init__(unit, expected_dimensions=UNIT_LENGTH)

        # Store the value
        self._value = self._base_units_magnitude(value)

    @property
    def value(self) -> Quantity:
        """Get the value of the distance."""
        return self._get_quantity(self._value)

    @value.setter
    def value(self, value: Quantity) -> None:
        """Set the distance value."""
        self._value = self._base_units_magnitude(value)
