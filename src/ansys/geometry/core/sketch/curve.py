"""``SketchCurve`` class module."""

from typing import Sequence

from ansys.geometry.core.primitives.point import Point2D
from ansys.geometry.core.typing import RealSequence


class SketchCurve:
    """Provides base sketch object class all sketch objects."""

    def __init__(self, points: Sequence[Point2D], origin: Point2D):
        """Initializes the sketch curve from its points.

        Parameters
        ----------
        points : Sequence[Point2D]
            A list of points defining the sketch curve.
        origin : Point2D
            A ``Point2D`` representing the origin of the ellipse.

        """
        self._points = points
        self._origin = origin

    @property
    def points(self) -> Sequence[Point2D]:
        """Return a list of ``Point2D`` instances defining the sketch.

        Returns
        -------
        Sequence[Point2D]
            A list of points defining the sketch curve.

        """
        return self._points

    @property
    def origin(self) -> Point2D:
        """Return the origin of the sketch.

        Returns
        -------
        Point2D
            A ``Point2D`` instance representing the center of the sketch curve

        """
        return self._origin

    @property
    def x_coords(self) -> RealSequence:
        """Returns the x-coordinates of the sketch curve.

        Returns
        -------
        RealSequence

        """
        return [point.x for point in self.points]

    @property
    def y_coords(self) -> RealSequence:
        """Returns the y-coordinates of the sketch curve.

        Returns
        -------
        RealSequence

        """
        return [point.y for point in self.points]
