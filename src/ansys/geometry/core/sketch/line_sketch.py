from ansys.geometry.core.primitives.point3D import Point3D
from ansys.geometry.core.sketch.sketch_curve import SketchCurve


class LineSketch(SketchCurve):
    """
    Provides Line representation within a sketch environment.

    Parameters
    ----------
    point1: Point3D
        Start of the line segment.
    point2: Point3D
        End of the line segment.
    """

    def __init__(
        self,
        point1: Point3D,
        point2: Point3D,
    ):
        self._point1 = point1
        self._point2 = point2
