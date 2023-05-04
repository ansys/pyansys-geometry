"""Provides the ``Accuracy`` class."""


import math

from ansys.geometry.core.typing import Real

LENGTH_ACCURACY = 1e-8
"""Constant for decimal accuracy in length comparisons."""

ANGLE_ACCURACY = 1e-6
"""Constant for decimal accuracy in angle comparisons."""


class Accuracy:
    """Provides decimal precision evaluations for actions such as equivalency."""

    def length_is_equal(comparison_length: Real, reference_length: Real) -> bool:
        """
        Check if the comparison length is equal to the reference length.

        Notes
        -----
        Check is done up to the length accuracy: ``LENGTH_ACCURACY``.

        Returns
        -------
        bool
            ``True`` if the comparison length is equal to the reference length
            within the length accuracy.
        """
        return Accuracy.is_within_tolerance(
            comparison_length, reference_length, LENGTH_ACCURACY, LENGTH_ACCURACY
        )

    def length_is_greater_than_or_equal(comparison_length: Real, reference_length: Real) -> bool:
        """
        Check if the comparison length is greater than the reference length.

        Notes
        -----
        Check is done up to the length accuracy: ``LENGTH_ACCURACY``.

        Returns
        -------
        bool
            ``True`` if the comparison length is greater than the reference length within
            the length accuracy.
        """
        return bool(
            comparison_length > reference_length
            or Accuracy.length_is_equal(comparison_length, reference_length)
        )

    def length_is_less_than_or_equal(comparison_length: Real, reference_length: Real) -> bool:
        """
        Check if the comparison length is less than or equal to the reference length.

        Notes
        -----
        Check is done up to the length accuracy: ``LENGTH_ACCURACY``.

        Returns
        -------
        bool
            ``True`` if the comparison length is less than or equal to the reference length
            within the length accuracy.
        """
        return bool(
            comparison_length < reference_length
            or Accuracy.length_is_equal(comparison_length, reference_length)
        )

    def length_is_zero(length: Real) -> bool:
        """
        Check if the length is within the length accuracy of exact zero.

        Returns
        -------
        bool
            ``True`` if the length is within the length accuracy of exact zero.
        """
        return bool(length <= LENGTH_ACCURACY and length >= -LENGTH_ACCURACY)

    def length_is_negative(length: Real) -> bool:
        """
        Check if the length is below a negative length accuracy.

        Returns
        -------
        bool
            ``True`` if the length is below a negative length accuracy.
        """
        return bool(length < -LENGTH_ACCURACY)

    def length_is_positive(length: Real) -> bool:
        """
        Check if the length is above a positive length accuracy.

        Returns
        -------
        bool
            ``True`` if the length is above a positive length accuracy.
        """
        return bool(length > LENGTH_ACCURACY)

    def angle_is_zero(angle: Real) -> bool:
        """
        Check if the length is within the angle accuracy of exact zero.

        Returns
        -------
        bool
            ``True`` if the length is within the angle accuracy of exact zero.
        """
        return bool(abs(angle) < ANGLE_ACCURACY)

    def angle_is_negative(angle: Real) -> bool:
        """
        Check if the angle is below a negative angle accuracy.

        Returns
        -------
        bool
            ``True`` if the angle is below a negative angle accuracy.
        """
        return bool(angle <= -ANGLE_ACCURACY)

    def angle_is_positive(angle: Real) -> bool:
        """
        Check if the angle is above a positive angle accuracy.

        Returns
        -------
        bool
           ``True`` if the angle is above a positive angle accuracy.
        """
        return bool(angle >= ANGLE_ACCURACY)

    def is_within_tolerance(
        a: Real, b: Real, relative_tolerance: Real, absolute_tolerance: Real
    ) -> bool:
        """
        Check if the a and b values are inside a relative and absolute tolerance.

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
            ``True`` if the values are inside the accepted tolerances.
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
