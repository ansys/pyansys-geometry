"""``LineSketch`` class module."""

from ansys.geometry.core.primitives.point import Point3D
from ansys.geometry.core.sketch.curve import SketchCurve


class LineSketch(SketchCurve):
    """
    Provides Line representation within a sketch environment.

    Parameters
    ----------
    point_1: Point3D
        Start of the line segment.
    point_2: Point3D
        End of the line segment.
    """

    def __init__(self, point_1: Point3D, point_2: Point3D):
        """Constructor method for ``LineSketch``."""
        self._point_1 = point_1
        self._point_2 = point_2

    @property
    def point_1(self):
        """Returns the start of the line segment."""
        return self._point_1

    @point_1.setter
    def point_1(self, point_1):
        """Set the start of the line segment."""
        if not isinstance(point_1, Point3D):
            raise ValueError("The parameter 'point_1' should be a Point3D object.")
        self._point_1 = point_1

    @property
    def point_2(self):
        """Returns the end of the line segment."""
        return self._point_2

    @point_2.setter
    def point_2(self, point_2):
        """Set the end of the line segment."""
        if not isinstance(point_2, Point3D):
            raise ValueError("The parameter 'point_2' should be a Point3D object.")
        self._point_1 = point_2
