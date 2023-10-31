# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.

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
