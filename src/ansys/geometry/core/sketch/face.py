"""``SketchFace`` class module."""

from typing import List, Optional

from pint import Quantity

from ansys.geometry.core.math import Plane, Point2D
from ansys.geometry.core.sketch.edge import SketchEdge


class SketchFace:
    """Provides base class for modeling closed 2D sketches.

    Parameters
    ----------
    edges : List[SketchEdge]
        All of the connected edges forming the face.
    """

    def __init__(self, edges: List[SketchEdge] = []):
        """Initializes the ``SketchFace``."""

        self._edges = edges

    def points(self, plane: Plane, num_points: Optional[int] = 100) -> List[Point2D]:
        """Returns a list containing all the points belonging to the shape.

        Parameters
        ----------
        num_points : int
            Desired number of points belonging to the shape.

        Returns
        -------
        List[Point2D]
            A list of points representing the shape.
        """
        try:
            local_points = self.local_points(num_points)
        except TypeError:
            local_points = self.local_points()

        return [
            (plane.origin + Point2D(plane.local_to_global @ point, point.base_unit))
            for point in local_points
        ]

    def local_points(self) -> List[Point2D]:
        """Generates a sampled list of points along the edges forming the face.

        Returns
        -------
        List[Point2D]
            A list of points along the edges forming the face.
        """
        raise NotImplementedError("Each face must provide this definition.")

    @property
    def edges(self) -> List[SketchEdge]:
        """Returns a list containing all edges forming the face.

        Returns
        -------
        List[SketchEdge]
            A list of component edges forming the face.
        """
        raise NotImplementedError("Each face must provide this definition.")

    @property
    def perimeter(self) -> Quantity:
        """Return the perimeter of the face.

        Returns
        -------
        Quantity
            The perimeter of the face.
        """
        perimeter = 0
        for edge in self._edges:
            perimeter += edge.length
        return perimeter
