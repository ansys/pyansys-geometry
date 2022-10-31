"""Provides the ``Segment`` class."""

from beartype import beartype as check_input_types
import numpy as np
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import UNIT_LENGTH, check_ndarray_is_all_nan
from ansys.geometry.core.sketch.edge import SketchEdge


class Segment(SketchEdge):
    """
    Provides segment representation of a line.

    Parameters
    ----------
    start : Point2D
        2D point that is the start of the line segment.
    end : Point2D
        2D point that is the end of the line segment.
    """

    @check_input_types
    def __init__(
        self,
        start: Point2D,
        end: Point2D,
    ):
        """Constructor method for the ``Segment`` class."""
        super().__init__()

        # Perform sanity checks on point values given
        check_ndarray_is_all_nan(start, "start")
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
        """2D point that is the start of the segment."""
        return self._start

    @property
    def end(self) -> Point2D:
        """2D point that is the end of the segment."""
        return self._end

    @property
    def length(self) -> Quantity:
        """Length of the segment."""
        return np.sqrt(
            np.square(self._end.x - self._start.x) + np.square(self._end.y - self._start.y)
        )

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """
        VTK polydata representation for PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global Cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            VTK pyvista.Polydata configuration.
        """
        return pv.Line(
            [
                self.start.x.m_as(UNIT_LENGTH),
                self.start.y.m_as(UNIT_LENGTH),
                0,
            ],
            [self.end.x.m_as(UNIT_LENGTH), self.end.y.m_as(UNIT_LENGTH), 0],
        )

    @check_input_types
    def __eq__(self, other: "Segment") -> bool:
        """Equals operator for the ``Segment`` class."""
        return self.start == other.start and self.end == other.end

    def __ne__(self, other: "Segment") -> bool:
        """Not equals operator for the ``Segment`` class."""
        return not self == other
