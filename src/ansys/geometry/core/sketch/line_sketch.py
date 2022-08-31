"""``LineSketch`` class module."""

from ansys.geometry.core.primitives.point3D import Point3D
from ansys.geometry.core.sketch.sketch_curve import SketchCurve


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
