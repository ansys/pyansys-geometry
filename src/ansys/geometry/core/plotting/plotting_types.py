# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Data types for plotting."""
from beartype.typing import Any, List
import pyvista as pv

from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.logger import LOG


class EdgePlot:
    """
    Mapper class to relate PyAnsys Geometry edges with its PyVista actor.

    Parameters
    ----------
    actor : ~pyvista.Actor
        PyVista actor that represents the edge.
    edge_object : Edge
        PyAnsys Geometry edge that is represented by the PyVista actor.
    parent : GeomObjectPlot, optional
        Parent PyAnsys Geometry object of this edge, by default ``None``.
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
        ~pyvista.Actor
            PyVista actor.
        """
        return self._actor

    @property
    def edge_object(self) -> Edge:
        """
        Return the PyAnsys Geometry edge.

        Returns
        -------
        Edge
            PyAnsys Geometry edge.
        """
        return self._object

    @property
    def parent(self) -> Any:
        """
        Parent PyAnsys Geometry object of this edge.

        Returns
        -------
        Any
            PyAnsys Geometry object.
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
    Mapper class to relate PyAnsys Geometry objects with its PyVista actor.

    Parameters
    ----------
    actor : pv.Actor
        PyVista actor that represents the pyansys-geometry object.
    object : Any
        PyAnsys Geometry object that is represented.
    edges : List[EdgePlot], optional
        List of edges of the PyAnsys Geometry object, by default ``None``.
    add_body_edges: bool, optional
        Flag to specify if you want to be able to add edges.
    """

    def __init__(
        self,
        actor: pv.Actor,
        object: Any,
        edges: List[EdgePlot] = None,
        add_body_edges: bool = True,
    ) -> None:
        """Initialize GeomObjectPlot variables."""
        self._actor = actor
        self._object = object
        self._edges = edges
        self._add_body_edges = add_body_edges

    @property
    def actor(self) -> pv.Actor:
        """
        Return the PyVista actor of the PyAnsys Geometry object.

        Returns
        -------
        ~pyvista.Actor
            Actor of the PyAnsys Geometry object.
        """
        return self._actor

    @property
    def object(self) -> Any:
        """
        Return the PyAnsys Geometry object.

        Returns
        -------
        Any
            PyAnsys Geometry object.
        """
        return self._object

    @property
    def edges(self) -> List[EdgePlot]:
        """
        Return the list of edges associated to this PyAnsys Geometry object.

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
        if self._add_body_edges:
            self._edges = edges
        else:
            LOG.warning(
                "To add edges to this body, it should be initialized with add_body_edges flag."
            )

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

    @property
    def add_body_edges(self) -> bool:
        """
        Return whether you want to be able to add edges.

        Returns
        -------
        bool
            Flag to add edges.
        """
        return self._add_body_edges
