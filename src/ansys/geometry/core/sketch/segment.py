"""``Segment`` class module."""

import numpy as np
from pint import Quantity

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import UNIT_LENGTH, check_ndarray_is_all_nan, check_type
from ansys.geometry.core.misc.checks import check_type_equivalence
from ansys.geometry.core.sketch.edge import SketchEdge


class Segment(SketchEdge):
    """
    Provides Segment representation of a Line.

    Parameters
    ----------
    start : Point2D
        Start of the line segment.
    end : Point2D
        End of the line segment.
    """

    def __init__(
        self,
        start: Point2D,
        end: Point2D,
    ):
        """Constructor method for ``Segment``."""
        super().__init__()

        # Perform sanity checks on Point values given
        check_type(start, Point2D)
        check_ndarray_is_all_nan(start, "start")
        check_type(end, Point2D)
        check_ndarray_is_all_nan(end, "end")

        # Assign values to start and end
        self._start = start
        self._end = end

        # Check segment points values and units
        if self._start == self._end:
            raise ValueError(
                "Parameters 'start' and 'end' have the same values. No segment can be created."
            )

        if not self._start.unit == self._end.unit:
            self._start.unit = self._end.unit = UNIT_LENGTH

    @property
    def start(self) -> Point2D:
        """Returns the start of the ``Segment``.

        Returns
        -------
        Point2D
            The start point of the ``Segment``.
        """
        return self._start

    @property
    def end(self) -> Point2D:
        """Returns the end of the ``Segment``.

        Returns
        -------
        Point2D
            The end point of the ``Segment``.
        """
        return self._end

    @property
    def length(self) -> Quantity:
        """Return the length of the ``Segment``.

        Returns
        -------
        Quantity
            The length of the ``Segment``.
        """
        return np.sqrt(
            np.square(self._end.x - self._start.x) + np.square(self._end.y - self._start.y)
        )

    def __eq__(self, other: "Segment") -> bool:
        """Equals operator for ``Segment``."""
        check_type_equivalence(other, self)
        return self.start == other.start and self.end == other.end

    def __ne__(self, other: "Segment") -> bool:
        """Not equals operator for ``Segment``."""
        return not self == other
