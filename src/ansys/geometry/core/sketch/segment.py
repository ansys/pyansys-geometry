"""Provides the ``SketchSegment`` class."""

from beartype import beartype as check_input_types
import numpy as np
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math import Plane, Point2D, Point3D, UnitVector3D
from ansys.geometry.core.misc import DEFAULT_UNITS, check_ndarray_is_all_nan
from ansys.geometry.core.primitives import Line
from ansys.geometry.core.sketch.edge import SketchEdge


class SketchSegment(SketchEdge, Line):
    """
    Provides segment representation of a line.

    Parameters
    ----------
    start : Point2D
        Point that is the start of the line segment.
    end : Point2D
        Point that is the end of the line segment.
    plane : Plane, optional
        Plane containing the sketched circle, by default global XY Plane.
    """

    @check_input_types
    def __init__(
        self,
        start: Point2D,
        end: Point2D,
        plane: Plane = Plane(),
    ):
        """Initialize ``SketchSegment`` class."""
        # Call SketchEdge init method
        SketchEdge.__init__(self)

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
            self._start.unit = self._end.unit = DEFAULT_UNITS.LENGTH

        # Call the Line init method
        self._init_primitive_line_from_plane(plane)

    def _init_primitive_line_from_plane(self, plane: Plane) -> None:
        """
        Initialize correctly the underlying primitive ``Line`` class.

        Parameters
        ----------
        plane : Plane
            Plane containing the sketched line.
        """
        # Find the global start and end points
        start_glb = plane.origin + Point3D(
            self.start[0] * plane.direction_x + self.start[1] * plane.direction_y,
            unit=self.start.base_unit,
        )
        end_glb = plane.origin + Point3D(
            self.end[0] * plane.direction_x + self.end[1] * plane.direction_y,
            unit=self.end.base_unit,
        )

        # Define the line direction
        line_direction = UnitVector3D.from_points(start_glb, end_glb)

        # Call the Line init method
        Line.__init__(self, start_glb, line_direction)

    @property
    def start(self) -> Point2D:
        """Point that is the start of the segment."""
        return self._start

    @property
    def end(self) -> Point2D:
        """Point that is the end of the segment."""
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
        import numpy as np

        return pv.Line(
            np.array(
                [
                    self.start.x.m_as(DEFAULT_UNITS.LENGTH),
                    self.start.y.m_as(DEFAULT_UNITS.LENGTH),
                    0,
                ],
                dtype=np.float_,
            ),
            np.array(
                [self.end.x.m_as(DEFAULT_UNITS.LENGTH), self.end.y.m_as(DEFAULT_UNITS.LENGTH), 0],
                dtype=np.float_,
            ),
        )

    @check_input_types
    def __eq__(self, other: "SketchSegment") -> bool:
        """Equals operator for the ``SketchSegment`` class."""
        return self.start == other.start and self.end == other.end

    def __ne__(self, other: "SketchSegment") -> bool:
        """Not equals operator for the ``SketchSegment`` class."""
        return not self == other

    def plane_change(self, plane: "Plane") -> None:
        """
        Redefine the plane containing SketchSegment objects.

        Notes
        -----
        This implies that their 3D definition may suffer changes.

        Parameters
        ----------
        plane : Plane
            Desired new plane which will contain the sketched segment.
        """
        # Reinitialize the Line definition for the given plane
        self._init_primitive_line_from_plane(plane)
