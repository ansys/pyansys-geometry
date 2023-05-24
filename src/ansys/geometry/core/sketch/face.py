"""Provides the ``SketchFace`` class."""

from beartype.typing import TYPE_CHECKING, List
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.sketch.edge import SketchEdge

if TYPE_CHECKING:
    from ansys.geometry.core.math import Plane


class SketchFace:
    """Provides modeling closed 2D sketches."""

    def __init__(self):
        """Initialize the sketch face."""
        # TODO: What about the circular faces? Circle, Ellipse are not making use of this...
        self._edges = []

    @property
    def edges(self) -> List[SketchEdge]:
        """List of all component edges forming the face."""
        return self._edges

    @property
    def perimeter(self) -> Quantity:
        """Perimeter of the face."""
        perimeter = 0
        for edge in self._edges:
            perimeter += edge.length
        return perimeter

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """
        VTK polydata representation for PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global Cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            VTK pyvista.Polydata configuration.
        """
        meshes = [edge.visualization_polydata for edge in self.edges]
        return pv.merge(meshes)

    def plane_change(self, plane: "Plane") -> None:
        """
        Redefine the plane containing SketchFace objects.

        Notes
        -----
        This implies that their 3D definition may suffer changes. By default, it does
        nothing. It is required to be implemented in child SketchFace classes.

        Parameters
        ----------
        plane : Plane
            Desired new plane which will contain the sketched face.
        """
        pass
