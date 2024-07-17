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
"""Provides for evaluating decimal precision."""

import math

from ansys.geometry.core.typing import Real

LENGTH_ACCURACY: Real = 1e-8
"""Constant for decimal accuracy in length comparisons."""

ANGLE_ACCURACY: Real = 1e-6
"""Constant for decimal accuracy in angle comparisons."""

DOUBLE_ACCURACY: Real = 1e-13
"""Constant for double accuracy."""


class Accuracy:
    """Decimal precision evaluations for math operations."""

    @staticmethod
    def length_accuracy() -> Real:
        """Return the ``LENGTH_ACCURACY`` constant."""
        return LENGTH_ACCURACY

    @staticmethod
    def angle_accuracy() -> Real:
        """Return the ``ANGLE_ACCURACY`` constant."""
        return ANGLE_ACCURACY

    @staticmethod
    def double_accuracy() -> Real:
        """Return the ``DOUBLE_ACCURACY`` constant."""
        return DOUBLE_ACCURACY

    @staticmethod
    def length_is_equal(comparison_length: Real, reference_length: Real) -> bool:
        """Check if the comparison length is equal to the reference length.

        Notes
        -----
        The check is done up to the constant value specified for ``LENGTH_ACCURACY``.

        Returns
        -------
        bool
            ``True`` if the comparison length is equal to the reference length
            within the length accuracy, ``False`` otherwise.
        """
        return Accuracy.is_within_tolerance(
            comparison_length, reference_length, LENGTH_ACCURACY, LENGTH_ACCURACY
        )

    @staticmethod
    def equal_doubles(a: Real, b: Real):
        """Compare two double values."""
        return Accuracy.is_within_tolerance(a, b, DOUBLE_ACCURACY, DOUBLE_ACCURACY)

    @staticmethod
    def compare_with_tolerance(
        a: Real, b: Real, relative_tolerance: Real, absolute_tolerance: Real
    ) -> Real:
        """Compare two doubles given the relative and absolute tolerances."""
        if Accuracy.is_within_tolerance(a, b, relative_tolerance, absolute_tolerance):
            return 0
        elif a < b:
            return -1
        else:
            return 1

    @staticmethod
    def length_is_greater_than_or_equal(comparison_length: Real, reference_length: Real) -> bool:
        """Check if the length is greater than the reference length.

        Notes
        -----
        The check is done up to the constant value specified for ``LENGTH_ACCURACY``.

        Returns
        -------
        bool
            ``True`` if the comparison length is greater than the reference length within
            the length accuracy, ``False`` otherwise.
        """
        return bool(
            comparison_length > reference_length
            or Accuracy.length_is_equal(comparison_length, reference_length)
        )

    @staticmethod
    def length_is_less_than_or_equal(comparison_length: Real, reference_length: Real) -> bool:
        """Check if the length is less than or equal to the reference length.

        Notes
        -----
        The check is done up to the constant value specified for ``LENGTH_ACCURACY``.

        Returns
        -------
        bool
            ``True`` if the comparison length is less than or equal to the reference length
            within the length accuracy, ``False`` otherwise.
        """
        return bool(
            comparison_length < reference_length
            or Accuracy.length_is_equal(comparison_length, reference_length)
        )

    @staticmethod
    def length_is_zero(length: Real) -> bool:
        """Check if the length is within the length accuracy of exact zero.

        Returns
        -------
        bool
            ``True`` if the length is within the length accuracy of exact zero,
            ``False`` otherwise.
        """
        return bool(length <= LENGTH_ACCURACY and length >= -LENGTH_ACCURACY)

    @staticmethod
    def length_is_negative(length: Real) -> bool:
        """Check if the length is below a negative length accuracy.

        Returns
        -------
        bool
            ``True`` if the length is below a negative length accuracy,
             ``False`` otherwise.
        """
        return bool(length < -LENGTH_ACCURACY)

    @staticmethod
    def length_is_positive(length: Real) -> bool:
        """Check if the length is above a positive length accuracy.

        Returns
        -------
        bool
            ``True`` if the length is above a positive length accuracy,
             ``False`` otherwise.
        """
        return bool(length > LENGTH_ACCURACY)

    @staticmethod
    def angle_is_zero(angle: Real) -> bool:
        """Check if the length is within the angle accuracy of exact zero.

        Returns
        -------
        bool
            ``True`` if the length is within the angle accuracy of exact zero,
             ``False`` otherwise.
        """
        return bool(abs(angle) < ANGLE_ACCURACY)

    @staticmethod
    def angle_is_negative(angle: Real) -> bool:
        """Check if the angle is below a negative angle accuracy.

        Returns
        -------
        bool
            ``True`` if the angle is below a negative angle accuracy,
             ``False`` otherwise.
        """
        return bool(angle <= -ANGLE_ACCURACY)

    @staticmethod
    def angle_is_positive(angle: Real) -> bool:
        """Check if the angle is above a positive angle accuracy.

        Returns
        -------
        bool
           ``True`` if the angle is above a positive angle accuracy,
            ``False`` otherwise.
        """
        return bool(angle >= ANGLE_ACCURACY)

    @staticmethod
    def is_within_tolerance(
        a: Real, b: Real, relative_tolerance: Real, absolute_tolerance: Real
    ) -> bool:
        """Check if two values are inside a relative and absolute tolerance.

        Parameters
        ----------
        a : Real
            First value.
        b : Real
            Second value.
        relative_tolerance : Real
            Relative tolerance accepted.
        absolute_tolerance : Real
            Absolute tolerance accepted.

        Returns
        -------
        bool
            ``True`` if the values are inside the accepted tolerances,
            ``False`` otherwise.
        """
        # The code doesn't work for comparing infinity and non-infinite numbers!
        a_is_infinite = math.isinf(a)
        b_is_infinite = math.isinf(b)

        if a_is_infinite or b_is_infinite:
            if (a_is_infinite and a > 0) ^ (b_is_infinite and b > 0):
                return False
            if (a_is_infinite and a < 0) ^ (b_is_infinite and b < 0):
                return False

        difference = abs(a - b)
        return bool(
            difference < absolute_tolerance or difference <= relative_tolerance * 0.5 * abs(a + b)
        )
