"""``Triangle`` class module."""

from ansys.geometry.core.math import Point2D
from ansys.geometry.core.misc import check_type
from ansys.geometry.core.sketch.face import SketchFace
from ansys.geometry.core.sketch.segment import SketchSegment


class Triangle(SketchFace):
    """A class for modeling 2D triangle shape.

    Parameters
    ----------
    point1: Point2D
        A :class:`Point2D` representing the a triangle vertex.
    point2: Point2D
        A :class:`Point2D` representing the a triangle vertex.
    point3: Point2D
        A :class:`Point2D` representing the a triangle vertex.
    """

    def __init__(self, point1: Point2D, point2: Point2D, point3: Point2D):
        """Initializes the triangle shape."""
        super().__init__()

        check_type(point1, Point2D)
        check_type(point2, Point2D)
        check_type(point3, Point2D)
        self._point1 = point1
        self._point2 = point2
        self._point3 = point3

        self._edges.append(SketchSegment(self._point1, self._point2))
        self._edges.append(SketchSegment(self._point2, self._point3))
        self._edges.append(SketchSegment(self._point3, self._point1))

    @property
    def point1(self) -> Point2D:
        """Triangle vertex 1.

        Returns
        -------
        Point2D
            Triangle vertex 1.
        """
        return self._point1

    @property
    def point2(self) -> Point2D:
        """Triangle vertex 2.

        Returns
        -------
        Point2D
            Triangle vertex 2.
        """
        return self._point2

    @property
    def point3(self) -> Point2D:
        """Triangle vertex 3.

        Returns
        -------
        Point2D
            Triangle vertex 3.
        """
        return self._point3
