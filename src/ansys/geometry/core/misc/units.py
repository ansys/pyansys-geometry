# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Provides for handling units homogeneously throughout PyAnsys Geometry."""

from beartype import beartype as check_input_types
from pint import Quantity, Unit, UnitRegistry, set_application_registry

from ansys.geometry.core.misc.checks import check_pint_unit_compatibility
from ansys.geometry.core.typing import Real

UNITS = UnitRegistry()
"""Units manager."""

# This forces pint to set the previous UnitRegistry as the one to use
set_application_registry(UNITS)


class PhysicalQuantity:
    """Provides the base class for handling units throughout PyAnsys Geometry.

    Parameters
    ----------
    unit : ~pint.Unit
        Units for the class.
    expected_dimensions : ~pint.Unit, default: None
        Units for the dimensionality of the physical quantity.
    """

    @check_input_types
    def __init__(self, unit: Unit, expected_dimensions: Unit | None = None):
        """Initialize the ``PhysicalQuantity`` class."""
        if expected_dimensions:
            check_pint_unit_compatibility(unit, expected_dimensions)

        self._unit = unit
        _, self._base_unit = UNITS.get_base_units(unit)

    @property
    def unit(self) -> Unit:
        """Unit of the object."""
        return self._unit

    @unit.setter
    @check_input_types
    def unit(self, unit: Unit) -> None:
        """Set the unit of the object."""
        check_pint_unit_compatibility(unit, self._base_unit)
        self._unit = unit

    @property
    def base_unit(self) -> Unit:
        """Base unit of the object."""
        return self._base_unit

    def _get_quantity(self, input: Real) -> Quantity:
        """Return the input value as a ~:class:`pint.Quantity` class.

        Parameters
        ----------
        input : Real
            Number to express as a quantity.

        Returns
        -------
        ~pint.Quantity
            Physical quantity that the number represents.
        """
        return Quantity(input, units=self.base_unit).to(self.unit)

    @check_input_types
    def _base_units_magnitude(self, input: Quantity) -> Real:
        """Get the input's :class:`pint.Quantity` magnitude in base units.

        Parameters
        ----------
        input : ~pint.Quantity
            :class:`pint.Quantity` class to process.

        Returns
        -------
        Real
            Input's magnitude in base units.
        """
        check_pint_unit_compatibility(input.units, self._base_unit)
        return input.to_base_units().m
