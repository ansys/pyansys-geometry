"""``Segment`` class module."""

from beartype import beartype as check_input_types
import numpy as np
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import UNIT_LENGTH, check_ndarray_is_all_nan
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

    @check_input_types
    def __init__(
        self,
        start: Point2D,
        end: Point2D,
    ):
        """Constructor method for ``Segment``."""
        super().__init__()

        # Perform sanity checks on Point values given
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

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """
        Returns the vtk polydata representation for PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            The vtk pyvista.Polydata configuration.
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
        """Equals operator for ``Segment``."""
        return self.start == other.start and self.end == other.end

    def __ne__(self, other: "Segment") -> bool:
        """Not equals operator for ``Segment``."""
        return not self == other
