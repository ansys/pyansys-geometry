# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from pint import Quantity
import pytest

from ansys.geometry.core.misc import DEFAULT_UNITS, UNITS, Angle, Distance, measurements


def test_repr_():
    # Testing the __repr__ method of the Measurement class
    mea = measurements.Measurement(5.0, DEFAULT_UNITS.LENGTH, DEFAULT_UNITS.LENGTH)
    assert measurements.Measurement.__repr__(mea) == "5.0 meter"


def test_distance():
    """Simple test function to check the correct functioning of
    ``Distance``.
    """
    # Create a Distance object and test it
    d_value = 10 * UNITS.cm
    d = Distance(d_value.m, unit=d_value.u)

    assert d.base_unit == UNITS.get_base_units(d_value.u)[1]
    assert d.unit == d_value.u
    assert d.value == d_value

    # Let's change the units
    d.unit = new_units = UNITS.mm

    assert d.base_unit == UNITS.get_base_units(d_value.u)[1]
    assert d.unit == new_units
    assert d.value == d_value
    assert d.value.magnitude == d_value.to(new_units).magnitude

    # Let's change the value
    d.value = new_value = 545 * UNITS.km

    assert d.base_unit == UNITS.get_base_units(new_value)[1]
    assert d.unit == new_units
    assert d.value == new_value
    assert d.value.magnitude == new_value.to(new_units).magnitude

    # Now let's test the creation of a Distance object from a Quantity
    d_value_2 = 1345 * UNITS.mm
    d_2 = Distance(d_value_2)

    assert d_2.base_unit == UNITS.get_base_units(d_value_2.u)[1]
    assert d_2.unit == d_value_2.u
    assert d_2.value == d_value_2

    # Now, let's test the creation of a Distance object with a single
    # float value and assuming default units
    d_3_magnitude = 5346
    d_3 = Distance(d_3_magnitude)

    assert d_3.base_unit == UNITS.get_base_units(DEFAULT_UNITS.LENGTH)[1]
    assert d_3.unit == DEFAULT_UNITS.LENGTH
    assert d_3.value == d_3_magnitude * DEFAULT_UNITS.LENGTH

    # Finally check that if you provide a Quantity and some other units,
    # the units provided will be ignored. The units assigned to the
    # input Quantity will be kept.
    d_4_value = 6348 * UNITS.km
    d_4_assigned_units = UNITS.mm
    d_4 = Distance(d_4_value, unit=d_4_assigned_units)

    assert d_4.base_unit == UNITS.get_base_units(d_4_value.u)[1]
    assert d_4.unit == d_4_value.units
    assert not d_4.unit == d_4_assigned_units
    assert d_4.value == d_4_value

    # Let's try out some errors
    with pytest.raises(
        TypeError, match=r"The pint.Unit provided as an input should be a \[length\] quantity."
    ):
        Distance(Quantity(123, UNITS.fahrenheit))

    with pytest.raises(
        TypeError, match=r"The pint.Unit provided as an input should be a \[length\] quantity."
    ):
        Distance(123, unit=UNITS.radian)

    with pytest.raises(
        TypeError, match="The parameter 'value' should have a float or integer value."
    ):
        Distance("avsdbv")


def test_change_units_length():
    """Testing units change for Distance object."""
    # Let's store the original units first
    original_units = DEFAULT_UNITS.LENGTH

    # Check that the distance object is properly built
    a = Distance(10)
    assert a.value == 10 * original_units
    assert DEFAULT_UNITS.LENGTH == original_units

    # Now, let's change the DEFAULT_UNITS
    DEFAULT_UNITS.LENGTH = UNITS.mm
    assert DEFAULT_UNITS.LENGTH == UNITS.mm

    # Check that the distance object is properly built
    # with the new default units
    b = Distance(10)
    assert a.value != b.value
    assert b.value == 10 * UNITS.mm

    # Finally, let's change them back
    DEFAULT_UNITS.LENGTH = original_units
    assert DEFAULT_UNITS.LENGTH == original_units


def test_change_units_angle():
    """Testing units change for Angle object."""
    # Let's store the original units first
    original_units = DEFAULT_UNITS.ANGLE

    # Check that the angle object is properly built
    a = Angle(10)
    assert a.value == 10 * original_units
    assert DEFAULT_UNITS.ANGLE == original_units

    # Now, let's change the DEFAULT_UNITS
    DEFAULT_UNITS.ANGLE = UNITS.degrees
    assert DEFAULT_UNITS.ANGLE == UNITS.degrees

    # Check that the angle object is properly built
    # with the new default units
    b = Angle(10)
    assert a.value != b.value
    assert b.value == 10 * UNITS.degrees

    # Finally, let's change them back
    DEFAULT_UNITS.ANGLE = original_units
    assert DEFAULT_UNITS.ANGLE == original_units
