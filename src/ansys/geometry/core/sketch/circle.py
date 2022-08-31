"""``CircleSketch`` class module."""

from ansys.geometry.core.primitives.direction import Direction
from ansys.geometry.core.primitives.point3D import Point3D
from ansys.geometry.core.sketch.curve import SketchCurve


class CircleSketch(SketchCurve):
    """
    Provides circle representation within a sketch environment.

    Parameters
    ----------
    origin : Point3D
        Centered origin of the circle.
    dir_x: Direction
        X-plane direction.
    dir_y: Direction
        Y-plane direction.
    radius: float
        Circle radius.
    """

    def __init__(self, origin: Point3D, dir_x: Direction, dir_y: Direction, radius: float):
        """Constructor method for ``CircleSketch``."""
        self._origin = origin
        self._dir_x = dir_x
        self._dir_y = dir_y
        self._radius = radius
