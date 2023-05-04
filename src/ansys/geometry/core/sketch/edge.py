"""Provides the ``SketchEdge`` class."""

from beartype.typing import TYPE_CHECKING
from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math import Point2D

if TYPE_CHECKING:
    from ansys.geometry.core.math import Plane


class SketchEdge:
    """Provides for modeling edges forming sketched shapes."""

    @property
    def start(self) -> Point2D:
        """Point that is the start point of the edge."""
        raise NotImplementedError("Each edge must provide the start point definition.")

    @property
    def end(self) -> Point2D:
        """Point that is the end point of the edge."""
        raise NotImplementedError("Each edge must provide the end point definition.")

    @property
    def length(self) -> Quantity:
        """Length of the edge."""
        raise NotImplementedError("Each edge must provide the length definition.")

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
        raise NotImplementedError("Each edge must provide the polydata definition.")

    def plane_change(self, plane: "Plane") -> None:
        """
        Redefine the plane containing SketchEdge objects.

        Notes
        -----
        This implies that their 3D definition may suffer changes. By default, it does
        nothing. It is required to be implemented in child SketchEdge classes.

        Parameters
        ----------
        plane : Plane
            Desired new plane which will contain the sketched edge.
        """
        pass
