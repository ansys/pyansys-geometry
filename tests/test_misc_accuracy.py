# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

import math

from ansys.geometry.core.misc.accuracy import Accuracy


def test_length():
    """Determine effective length accuracy comparisons."""
    assert not Accuracy.length_is_zero(5)
    assert not Accuracy.length_is_zero(1e-7)
    assert Accuracy.length_is_zero(0)
    assert Accuracy.length_is_zero(1e-9)

    assert not Accuracy.length_is_negative(5)
    assert not Accuracy.length_is_negative(1e-10)
    assert not Accuracy.length_is_negative(1e-7)
    assert not Accuracy.length_is_negative(0)
    assert not Accuracy.length_is_negative(-1e-9)
    assert not Accuracy.length_is_negative(-1e-8)
    assert Accuracy.length_is_negative(-5)
    assert Accuracy.length_is_negative(-1e-7)

    assert not Accuracy.length_is_positive(-5)
    assert not Accuracy.length_is_positive(-1e-10)
    assert not Accuracy.length_is_positive(-1e-7)
    assert not Accuracy.length_is_positive(0)
    assert not Accuracy.length_is_positive(1e-9)
    assert not Accuracy.length_is_positive(1e-8)
    assert Accuracy.length_is_positive(5)
    assert Accuracy.length_is_positive(1e-7)


def test_angle():
    """Determine effective angle accuracy comparisons."""
    assert not Accuracy.angle_is_zero(5)
    assert not Accuracy.angle_is_zero(1e-6)
    assert Accuracy.angle_is_zero(0)
    assert Accuracy.angle_is_zero(1e-7)

    assert not Accuracy.angle_is_negative(5)
    assert not Accuracy.angle_is_negative(-1e-8)
    assert not Accuracy.angle_is_negative(1e-7)
    assert not Accuracy.angle_is_negative(0)
    assert Accuracy.angle_is_negative(-5)
    assert Accuracy.angle_is_negative(-1e-6)
    assert Accuracy.angle_is_negative(-1e-5)

    assert not Accuracy.angle_is_positive(-5)
    assert not Accuracy.angle_is_positive(1e-8)
    assert not Accuracy.angle_is_positive(1e-7)
    assert not Accuracy.angle_is_positive(0)
    assert Accuracy.angle_is_positive(5)
    assert Accuracy.angle_is_positive(1e-6)
    assert Accuracy.angle_is_positive(1e-5)


def test_within_tolerance():
    """Determine effective tolerance comparison."""
    # due to relative tolerance
    assert Accuracy.is_within_tolerance(5, 7, 0.4, 1.0)
    assert Accuracy.is_within_tolerance(5, 7, 1 / 3, 1.0)
    assert not Accuracy.is_within_tolerance(5, 7, 0.3, 1.0)

    # due to absolute tolerance
    assert not Accuracy.is_within_tolerance(5, 6, 0, 1)
    assert Accuracy.is_within_tolerance(5, 6, 0, 1.1)

    # test for infinity
    assert not Accuracy.is_within_tolerance(math.inf, math.inf, 1, 2)
    assert not Accuracy.is_within_tolerance(-math.inf, -math.inf, 1, 2)
    assert not Accuracy.is_within_tolerance(math.inf, 10, 1, 2)
    assert not Accuracy.is_within_tolerance(10, math.inf, 1, 2)
    assert not Accuracy.is_within_tolerance(-math.inf, 10, 1, 2)
    assert not Accuracy.is_within_tolerance(10, -math.inf, 1, 2)
    assert not Accuracy.is_within_tolerance(math.inf, -math.inf, 1, 2)
    assert not Accuracy.is_within_tolerance(-math.inf, math.inf, 1, 2)


def test_length_reference_equality():
    """Determine effective length accuracy comparisons."""
    assert not Accuracy.length_is_equal(5, 10)
    assert not Accuracy.length_is_equal(5 + 1e-7, 5)
    assert not Accuracy.length_is_equal(5 - 1e-7, 5)
    assert Accuracy.length_is_equal(5, 5)
    assert Accuracy.length_is_equal(5 + 1e-9, 5)
    assert Accuracy.length_is_equal(5 - 1e-9, 5)
    assert Accuracy.length_is_equal(5 + 1e-8, 5)
    assert Accuracy.length_is_equal(5 - 1e-8, 5)

    assert not Accuracy.length_is_less_than_or_equal(10, 5)
    assert not Accuracy.length_is_less_than_or_equal(5 + 1e-7, 5)
    assert Accuracy.length_is_less_than_or_equal(5 + 1e-8, 5)
    assert Accuracy.length_is_less_than_or_equal(5, 5)
    assert Accuracy.length_is_less_than_or_equal(5, 10)
    assert Accuracy.length_is_less_than_or_equal(0, 5)
    assert Accuracy.length_is_less_than_or_equal(5 - 1e-7, 5)
    assert Accuracy.length_is_less_than_or_equal(5 + 1e-10, 5)
    assert Accuracy.length_is_less_than_or_equal(5 + 1e-9, 5)
    assert Accuracy.length_is_less_than_or_equal(5 - 1e-9, 5)

    assert not Accuracy.length_is_greater_than_or_equal(-10, -5)
    assert not Accuracy.length_is_greater_than_or_equal(-5 - 1e-7, -5)
    assert Accuracy.length_is_greater_than_or_equal(-5 - 1e-8, -5)
    assert Accuracy.length_is_greater_than_or_equal(-5, -10)
    assert Accuracy.length_is_greater_than_or_equal(-5, -5)
    assert Accuracy.length_is_greater_than_or_equal(-5 + 1e-7, -5)
    assert Accuracy.length_is_greater_than_or_equal(-5 - 1e-10, -5)
    assert Accuracy.length_is_greater_than_or_equal(-5 - 1e-9, -5)
    assert Accuracy.length_is_greater_than_or_equal(-5 + 1e-9, -5)


def test_properties_accuracy_class():
    """Test properties of the accuracy class."""
    import ansys.geometry.core.misc.accuracy as accuracy_module

    # Initialize the accuracy class
    accuracy_class = Accuracy()

    # Check the properties
    assert accuracy_class.length_accuracy() == accuracy_module.LENGTH_ACCURACY
    assert accuracy_class.angle_accuracy() == accuracy_module.ANGLE_ACCURACY
    assert accuracy_class.double_accuracy() == accuracy_module.DOUBLE_ACCURACY


def test_double_comps():
    """Test double comparisons."""
    # Test equal doubles
    assert Accuracy.equal_doubles(5, 5)
    assert Accuracy.equal_doubles(5 + 1e-13, 5)
    assert Accuracy.equal_doubles(5 - 1e-13, 5)
    assert not Accuracy.equal_doubles(5, 10)
    assert not Accuracy.equal_doubles(5 + 1e-12, 5)
    assert not Accuracy.equal_doubles(5 - 1e-12, 5)

    # Test compare with tolerance
    assert Accuracy.compare_with_tolerance(5, 5, 1e-13, 1e-13) == 0
    assert Accuracy.compare_with_tolerance(5 + 1e-13, 5, 1e-13, 1e-13) == 0
    assert Accuracy.compare_with_tolerance(5 - 1e-13, 5, 1e-13, 1e-13) == 0
    assert Accuracy.compare_with_tolerance(5, 10, 1e-13, 1e-13) == -1
    assert Accuracy.compare_with_tolerance(5 + 1e-12, 5, 1e-13, 1e-13) == 1
    assert Accuracy.compare_with_tolerance(5 - 1e-12, 5, 1e-13, 1e-13) == -1
    assert Accuracy.compare_with_tolerance(5, 5, 1e-12, 1e-12) == 0
    assert Accuracy.compare_with_tolerance(5 + 1e-12, 5, 1e-12, 1e-12) == 0
    assert Accuracy.compare_with_tolerance(5 - 1e-12, 5, 1e-12, 1e-12) == 0
    assert Accuracy.compare_with_tolerance(5, 10, 1e-12, 1e-12) == -1
    assert Accuracy.compare_with_tolerance(5 + 1e-11, 5, 1e-12, 1e-12) == 1
    assert Accuracy.compare_with_tolerance(5 - 1e-11, 5, 1e-12, 1e-12) == -1
    assert Accuracy.compare_with_tolerance(5, 5, 1e-11, 1e-11) == 0
