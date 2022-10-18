"""``SketchEdge`` class module."""

from pint import Quantity
import pyvista as pv

from ansys.geometry.core.math import Point2D


class SketchEdge:
    """Provides base class for modeling edges forming sketched shapes."""

    @property
    def start(self) -> Point2D:
        """Returns the start point of the edge.

        Returns
        -------
        Point2D
            The start point of the edge.
        """
        raise NotImplementedError("Each edge must provide start point definition.")

    @property
    def end(self) -> Point2D:
        """Returns the end point of the edge.

        Returns
        -------
        Point2D
            The end point of the edge.
        """
        raise NotImplementedError("Each edge must provide end point definition.")

    @property
    def length(self) -> Quantity:
        """Returns the length of the edge.

        Returns
        -------
        Quantity
            The length of the edge.
        """
        raise NotImplementedError("Each edge must provide length definition.")

    @property
    def visualization_polydata(self) -> pv.PolyData:
        """
        Returns the vtk polydata representation for PyVista visualization.

        The representation lies in the X/Y plane within
        the standard global cartesian coordinate system.

        Returns
        -------
        pyvista.PolyData
            The vtk pyvista.Polydata configuration.
        """
        raise NotImplementedError("Each edge must provide PolyData definition.")
