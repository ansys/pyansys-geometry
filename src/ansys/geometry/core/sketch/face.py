"""``SketchFace`` class module."""

from typing import List

from pint import Quantity

from ansys.geometry.core.sketch.edge import SketchEdge


class SketchFace:
    """Provides base class for modeling closed 2D sketches."""

    def __init__(self):
        """Initializes the ``SketchFace``."""

        self._edges = []

    @property
    def edges(self) -> List[SketchEdge]:
        """Returns a list containing all edges forming the face.

        Returns
        -------
        List[SketchEdge]
            A list of component edges forming the face.
        """
        return self._edges

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
