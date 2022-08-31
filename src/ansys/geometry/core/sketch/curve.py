"""``SketchCurve`` class module."""

from ansys.geometry.core.primitives.point import Point2D


class SketchCurve:
    """Provides base sketch object class all sketch objects."""

    def __init__(self, points: list[Point2D], origin):
        """Initializes the sketch curve from its points.

        Parameters
        ----------
        points : list[Point2D]
            A list of points defining the sketch curve.

        """
        self._points = points
        self._origin = origin

    @property
    def points(self):
        """Return a list of ``Point2D`` instances defining the sketch.

        Returns
        -------
        points : list[Point2D]
            A list of points defining the sketch curve.

        """
        return self._points

    @property
    def origin(self):
        return self._origin

    @property
    def x_coords(self):
        return [point.x for point in self.points]

    @property
    def y_coords(self):
        return [point.y for point in self.points]
