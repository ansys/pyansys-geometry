"""``Accuracy`` class module."""


import math

LENGTH_ACCURACY = 1e-8
"""SpaceClaim constant for decimal accuracy in length comparisons."""

ANGLE_ACCURACY = 1e-6
"""SpaceClaim constant for decimal accuracy in angle comparisons."""


class Accuracy:
    """
    Provides decimal precision evaluations for actions such as equivalency.
    """

    def length_is_zero(length: float) -> bool:
        """Returns ``True`` if length is within length accuracy of exact zero."""
        return length <= LENGTH_ACCURACY and length >= -LENGTH_ACCURACY

    def length_is_negative(length: float) -> bool:
        """Returns ``True`` if length is below a negative length accuracy."""
        return length < -LENGTH_ACCURACY

    def length_is_positive(length: float) -> bool:
        """Returns ``True`` if length is above a positive length accuracy."""
        return length > LENGTH_ACCURACY

    def angle_is_zero(angle: float) -> bool:
        """Returns ``True`` if length is within angle accuracy of exact zero."""
        return abs(angle) < ANGLE_ACCURACY

    def angle_is_negative(angle: float) -> bool:
        """Returns ``True`` if angle is below a negative angle accuracy."""
        return angle <= -ANGLE_ACCURACY

    def angle_is_positive(angle: float) -> bool:
        """Returns ``True`` if angle is above a positive angle accuracy."""
        return angle >= ANGLE_ACCURACY

    def is_within_tolerance(
        a: float, b: float, relative_tolerance: float, absolute_tolerance: float
    ) -> bool:
        # The code doesn't work for comparing infinity and non-infinite numbers!
        a_is_infinite = math.isinf(a)
        b_is_infinite = math.isinf(b)

        if a_is_infinite or b_is_infinite:
            if (a_is_infinite and a > 0) ^ (b_is_infinite and b > 0):
                return False
            if (a_is_infinite and a < 0) ^ (b_is_infinite and b < 0):
                return False

        difference = abs(a - b)
        return difference < absolute_tolerance or difference <= relative_tolerance * 0.5 * abs(
            a + b
        )
