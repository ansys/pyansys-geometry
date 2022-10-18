"""``SketchFace`` class module."""

from typing import List

from pint import Quantity
import pyvista as pv

from ansys.geometry.core.sketch.edge import SketchEdge


class SketchFace:
    """Provides base class for modeling closed 2D sketches."""

    def __init__(self):
        """Initializes the ``SketchFace``."""
        # TODO: What about the circular faces? Circle, Ellipse are not making use of this...
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
        """Returns the perimeter of the face.

        Returns
        -------
        Quantity
            The perimeter of the face.
        """
        perimeter = 0
        for edge in self._edges:
            perimeter += edge.length
        return perimeter

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """
        Return the vtk polydata representation for PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            The vtk pyvista.Polydata configuration.
        """
        meshes = [edge.visualization_polydata for edge in self.edges]
        return pv.merge(meshes)
