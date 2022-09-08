"""``Units`` module for PyGeometry."""

from pint import Quantity, Unit, UnitRegistry

from ansys.geometry.core.misc.checks import (
    check_is_float_int,
    check_is_pint_unit,
    check_pint_unit_compatibility,
)
from ansys.geometry.core.typing import Real

UNITS = UnitRegistry()
"""Unit manager."""

UNIT_LENGTH = UNITS.meter
"""Default length unit for PyGeometry."""

UNIT_ANGLE = UNITS.radian
"""Default angle unit for PyGeometry."""


class PhysicalQuantity:
    """Base class to handle units homogeneously throughout PyGeometry.

    Parameters
    ----------
    unit : Unit
        The units to be considered for our class
    """

    def __init__(self, unit: Unit):
        """Constructor for ``PhysicalQuantity``."""
        check_is_pint_unit(unit, "unit")
        self._unit = unit
        _, self._base_unit = UNITS.get_base_units(unit)

    @property
    def unit(self) -> Unit:
        """Returns the unit of the object."""
        return self._unit

    @unit.setter
    def unit(self, unit: Unit) -> None:
        """Sets the unit of the object."""
        check_is_pint_unit(unit, "unit")
        check_pint_unit_compatibility(unit, self._base_unit)
        self._unit = unit

    @property
    def base_unit(self) -> Unit:
        """Returns the base unit of the object."""
        return self._base_unit

    def __get_quantity(self, input: Real) -> Quantity:
        """Returns input value as a ~:class:`pint.Quantity`.

        Parameters
        ----------
        input : Real
            The number to be expressed as a quantity

        Returns
        -------
        Quantity
            The physical quantity the number represents.
        """
        return (input * self.base_unit).ito(self.unit)
