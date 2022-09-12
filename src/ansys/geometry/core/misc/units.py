"""``Units`` module for PyGeometry."""

from typing import Optional, Union

from pint import Quantity, Unit, UnitRegistry

from ansys.geometry.core.misc.checks import check_pint_unit_compatibility, check_type
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
    unit : ~pint.Unit
        The units to be considered for our class.
    expected_dimensions : ~pint.Unit
        The units containing the dimensionality of the ``PhysicalQuantity``.
        By default, None.
    """

    def __init__(self, unit: Unit, expected_dimensions: Optional[Union[Unit, None]] = None):
        """Constructor for ``PhysicalQuantity``."""
        check_type(unit, Unit)
        if expected_dimensions:
            check_type(expected_dimensions, Unit)
            check_pint_unit_compatibility(unit, expected_dimensions)

        self._unit = unit
        _, self._base_unit = UNITS.get_base_units(unit)

    @property
    def unit(self) -> Unit:
        """Returns the unit of the object."""
        return self._unit

    @unit.setter
    def unit(self, unit: Unit) -> None:
        """Sets the unit of the object."""
        check_type(unit, Unit)
        check_pint_unit_compatibility(unit, self._base_unit)
        self._unit = unit

    @property
    def base_unit(self) -> Unit:
        """Returns the base unit of the object."""
        return self._base_unit

    def _get_quantity(self, input: Real) -> Quantity:
        """Returns input value as a ~:class:`pint.Quantity`.

        Parameters
        ----------
        input : Real
            The number to be expressed as a quantity.

        Returns
        -------
        ~pint.Quantity
            The physical quantity the number represents.
        """
        return (input * self.base_unit).to(self.unit)

    def _base_units_magnitude(self, input: Quantity) -> Real:
        """Returns input's :class:`pint.Quantity` magnitude
        in base units.

        Parameters
        ----------
        input : ~pint.Quantity
            The :class:`pint.Quantity` to be processed.

        Returns
        -------
        Real
            The input's magnitude in base units.
        """
        check_type(input, Quantity)
        check_pint_unit_compatibility(input.units, self._base_unit)
        return input.m_as(self._base_unit)
