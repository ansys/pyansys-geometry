"""Data types for plotting."""
from typing import Any, List

import pyvista as pv

from ansys.geometry.core.designer.edge import Edge


class EdgePlot:
    """
    Mapper class to relate pyansys-geometry edges with its PyVista actor.

    Parameters
    ----------
    actor : pv.Actor
        PyVista actor that represents the edge.
    edge_object : Edge
        Pyansys-geometry edge that is represented by the PyVista actor.
    parent : GeomObjectPlot, optional
        Parent pyansys-geometry object of this edge, by default None.
    """

    def __init__(self, actor: pv.Actor, edge_object: Edge, parent: "GeomObjectPlot" = None) -> None:
        """Initialize EdgePlot variables."""
        self._actor = actor
        self._object = edge_object
        self._parent = parent

    @property
    def actor(self) -> pv.Actor:
        """
        Return PyVista actor of the object.

        Returns
        -------
        pv.Actor
            PyVista actor.
        """
        return self._actor

    @property
    def edge_object(self) -> Edge:
        """
        Return the pyansys-geometry edge.

        Returns
        -------
        Edge
            Pyansys-geometry edge.
        """
        return self._object

    @property
    def parent(self) -> Any:
        """
        Parent pyansys-geometry object of this edge.

        Returns
        -------
        Any
            Pyansys-geometry object.
        """
        return self._parent

    @property
    def name(self) -> str:
        """
        Return the name of the edge.

        Returns
        -------
        str
            Name of the edge.
        """
        if self.parent:
            return f"{self.parent.name}-{self.edge_object.id}"
        else:
            return self.edge_object.id

    @parent.setter
    def parent(self, parent: "GeomObjectPlot"):
        """
        Set the parent object of the edge.

        Parameters
        ----------
        parent : GeomObjectPlot
            Parent of the edge.
        """
        self._parent = parent


class GeomObjectPlot:
    """
    Mapper class to relate pyansys-geometry objects with its PyVista actor.

    Parameters
    ----------
    actor : pv.Actor
        PyVista actor that represents the pyansys-geometry object.
    object : Any
        Pyansys-geometry object that is represented.
    edges : List[EdgePlot], optional
        List of edges of the pyansys-geometry object, by default None.
    """

    def __init__(self, actor: pv.Actor, object: Any, edges: List[EdgePlot] = None) -> None:
        """Initialize GeomObjectPlot variables."""
        self._actor = actor
        self._object = object
        self._edges = edges

    @property
    def actor(self) -> pv.Actor:
        """
        Return the PyVista actor of the pyansys-geometry object.

        Returns
        -------
        pv.Actor
            Actor of the pyansys-geometry object.
        """
        return self._actor

    @property
    def object(self) -> Any:
        """
        Return the pyansys-geometry object.

        Returns
        -------
        Any
            Pyansys-geometry object.
        """
        return self._object

    @property
    def edges(self) -> List[EdgePlot]:
        """
        Return the list of edges associated to this pyansys-geometry object.

        Returns
        -------
        List[EdgePlot]
            List of the edges of this object.
        """
        return self._edges

    @edges.setter
    def edges(self, edges: List[EdgePlot]):
        """
        Set the edges of this object.

        Parameters
        ----------
        edges : List[EdgePlot]
            List of the edges of this object.
        """
        self._edges = edges

    @property
    def name(self) -> str:
        """
        Return the name of this object.

        Returns
        -------
        str
            Name of the object.
        """
        return self._object.name
