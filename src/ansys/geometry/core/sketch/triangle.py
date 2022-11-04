"""Provides the ``Triangle`` class."""

from beartype import beartype as check_input_types
import pyvista as pv

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import UNIT_LENGTH
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.segment import Segment


class Triangle(SketchFace):
    """Provides for modeling 2D triangles.

    Parameters
    ----------
    point1: Point2D
        Point that represents a triangle vertex.
    point2: Point2D
        Point that represents a triangle vertex.
    point3: Point2D
        Point that represents a triangle vertex.
    """

    @check_input_types
    def __init__(self, point1: Point2D, point2: Point2D, point3: Point2D):
        """Initialize the triangle."""
        super().__init__()

        self._point1 = point1
        self._point2 = point2
        self._point3 = point3

        self._edges.append(Segment(self._point1, self._point2))
        self._edges.append(Segment(self._point2, self._point3))
        self._edges.append(Segment(self._point3, self._point1))

    @property
    def point1(self) -> Point2D:
        """Triangle vertex 1."""
        return self._point1

    @property
    def point2(self) -> Point2D:
        """Triangle vertex 2."""
        return self._point2

    @property
    def point3(self) -> Point2D:
        """Triangle vertex 3."""
        return self._point3

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
        return pv.Triangle(
            [
                [self.point1.x.m_as(UNIT_LENGTH), self.point1.y.m_as(UNIT_LENGTH), 0],
                [self.point2.x.m_as(UNIT_LENGTH), self.point2.y.m_as(UNIT_LENGTH), 0],
                [self.point3.x.m_as(UNIT_LENGTH), self.point3.y.m_as(UNIT_LENGTH), 0],
            ]
        )
