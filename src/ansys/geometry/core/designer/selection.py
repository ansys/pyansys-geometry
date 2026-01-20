# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
"""Module for creating a named selection."""

from typing import TYPE_CHECKING, Union

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.designer.beam import Beam
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.designer.component import Component
from ansys.geometry.core.designer.designpoint import DesignPoint
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.designer.vertex import Vertex
from ansys.geometry.core.errors import GeometryRuntimeError
from ansys.geometry.core.misc.auxiliary import (
    get_beams_from_ids,
    get_bodies_from_ids,
    get_components_from_ids,
    get_design_points_from_ids,
    get_edges_from_ids,
    get_faces_from_ids,
    get_vertices_from_ids,
)
from ansys.geometry.core.misc.checks import min_backend_version

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.design import Design


class NamedSelection:
    """Represents a single named selection within the design assembly.

    This class synchronizes to a design within a supporting Geometry service instance.

    A named selection organizes one or more design entities together for common actions
    against the entire group.

    Parameters
    ----------
    name : str
        User-defined name for the named selection.
    design : Design
        Design instance to which the named selection belongs.
    grpc_client : GrpcClient
        Active supporting Geometry service instance for design modeling.
    bodies : list[Body], default: None
        All bodies to include in the named selection.
    faces : list[Face], default: None
        All faces to include in the named selection.
    edges : list[Edge], default: None
        All edges to include in the named selection.
    beams : list[Beam], default: None
        All beams to include in the named selection.
    design_points : list[DesignPoints], default: None
        All design points to include in the named selection.
    components: list[Component], default: None
        All components to include in the named selection.
    vertices: list[Vertex], default: None
        All vertices to include in the named selection.
    """

    def __init__(
        self,
        name: str,
        design: "Design",
        grpc_client: GrpcClient,
        bodies: list[Body] | None = None,
        faces: list[Face] | None = None,
        edges: list[Edge] | None = None,
        beams: list[Beam] | None = None,
        design_points: list[DesignPoint] | None = None,
        components: list[Component] | None = None,
        vertices: list[Vertex] | None = None,
        preexisting_id: str | None = None,
    ):
        """Initialize the ``NamedSelection`` class."""
        self._name = name
        self._design = design
        self._grpc_client = grpc_client

        # Convert None to empty lists
        bodies = bodies if bodies is not None else []
        faces = faces if faces is not None else []
        edges = edges if edges is not None else []
        beams = beams if beams is not None else []
        design_points = design_points if design_points is not None else []
        components = components if components is not None else []
        vertices = vertices if vertices is not None else []

        # Instantiate
        self._bodies = bodies
        self._faces = faces
        self._edges = edges
        self._beams = beams
        self._design_points = design_points
        self._components = components
        self._vertices = vertices

        # Store ids for later use... when verifying if the NS changed.
        self._ids_cached = {
            "bodies": [body.id for body in bodies],
            "faces": [face.id for face in faces],
            "edges": [edge.id for edge in edges],
            "beams": [beam.id for beam in beams],
            "design_points": [dp.id for dp in design_points],
            "components": [component.id for component in components],
            "vertices": [vertex.id for vertex in vertices],
        }

        if preexisting_id:
            self._id = preexisting_id
            return

        # All ids should be unique - no duplicated values
        ids = set()

        # Loop over all entities to get their ids
        for value in self._ids_cached.values():
            for entity_id in value:
                ids.add(entity_id)

        response = self._grpc_client.services.named_selection.create_named_selection(
            name=name, members=ids
        )
        self._id = response.get("id")

    @property
    def id(self) -> str:
        """ID of the named selection."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the named selection."""
        return self._name

    @name.setter
    @min_backend_version(26, 1, 0)
    def name(self, value: str) -> None:
        """Set the name of the named selection."""
        self._grpc_client.services.named_selection.rename_named_selection(
            id=self._id, new_name=value
        )
        self._name = value

    @property
    def bodies(self) -> list[Body]:
        """All bodies in the named selection."""
        self.__verify_ns()
        if self._bodies is None:
            # Get all bodies from the named selection
            self._bodies = get_bodies_from_ids(self._design, self._ids_cached["bodies"])

        return self._bodies

    @property
    def faces(self) -> list[Face]:
        """All faces in the named selection."""
        self.__verify_ns()
        if self._faces is None:
            # Get all faces from the named selection
            self._faces = get_faces_from_ids(self._design, self._ids_cached["faces"])

        return self._faces

    @property
    def edges(self) -> list[Edge]:
        """All edges in the named selection."""
        self.__verify_ns()
        if self._edges is None:
            # Get all edges from the named selection
            self._edges = get_edges_from_ids(self._design, self._ids_cached["edges"])

        return self._edges

    @property
    def beams(self) -> list[Beam]:
        """All beams in the named selection."""
        self.__verify_ns()
        if self._beams is None:
            # Get all beams from the named selection
            self._beams = get_beams_from_ids(self._design, self._ids_cached["beams"])

        return self._beams

    @property
    def design_points(self) -> list[DesignPoint]:
        """All design points in the named selection."""
        self.__verify_ns()
        if self._design_points is None:
            # Get all design points from the named selection
            self._design_points = get_design_points_from_ids(
                self._design,
                self._ids_cached["design_points"],
            )

        return self._design_points

    @property
    def components(self) -> list[Component]:
        """All components in the named selection."""
        self.__verify_ns()
        if self._grpc_client.backend_version < (26, 1, 0):
            self._grpc_client.log.warning(
                "Accessing components in named selections is only"
                " consistent starting in version 2026 R1."
            )
            return []
        if self._components is None:
            # Get all components from the named selection
            self._components = get_components_from_ids(self._design, self._ids_cached["components"])

        return self._components

    @property
    def vertices(self) -> list[Vertex]:
        """All vertices in the named selection."""
        self.__verify_ns()
        if self._grpc_client.backend_version < (26, 1, 0):
            self._grpc_client.log.warning(
                "Accessing vertices of named selections is only"
                " consistent starting in version 2026 R1."
            )
            return []
        if self._vertices is None:
            # Get all vertices from the named selection
            self._vertices = get_vertices_from_ids(self._design, self._ids_cached["vertices"])

        return self._vertices

    def add_members(
        self,
        bodies: list[Body] | None = None,
        faces: list[Face] | None = None,
        edges: list[Edge] | None = None,
        beams: list[Beam] | None = None,
        design_points: list[DesignPoint] | None = None,
        components: list[Component] | None = None,
        vertices: list[Vertex] | None = None,
    ) -> "NamedSelection":
        """Add members to the named selection.

        Parameters
        ----------
    bodies : list[Body], default: None
        All bodies to add to the named selection.
    faces : list[Face], default: None
        All faces to add to the named selection.
    edges : list[Edge], default: None
        All edges to add to the named selection.
    beams : list[Beam], default: None
        All beams to add to the named selection.
    design_points : list[DesignPoints], default: None
        All design points to add to the named selection.
    components: list[Component], default: None
        All components to add to the named selection.
    vertices: list[Vertex], default: None
        All vertices to add to the named selection.

        Returns
        -------
        NamedSelection
            The new named selection with the added members.

        Notes
        -----
        Named selections are immutable. This method creates a new named selection with the added
        members.
        """
        # Update cache
        self.__verify_ns()

        # Convert None to empty lists
        bodies = bodies if bodies is not None else []
        faces = faces if faces is not None else []
        edges = edges if edges is not None else []
        beams = beams if beams is not None else []
        design_points = design_points if design_points is not None else []
        components = components if components is not None else []
        vertices = vertices if vertices is not None else []

        new_ns = NamedSelection(
            self._name,
            self._design,
            self._grpc_client,
            bodies=bodies + self._bodies,
            faces=faces + self._faces,
            edges=edges + self._edges,
            beams=beams + self._beams,
            design_points=design_points + self._design_points,
            components=components + self._components,
            vertices=vertices + self._vertices,
        )

        # Delete the old NS server-side
        self._grpc_client.services.named_selection.delete_named_selection(id=self._id)

        return new_ns

    def remove_members(
        self,
        members: list[Union[Body, Face, Edge, Beam, DesignPoint, Component, Vertex]],
    ) -> "NamedSelection":
        """Remove members from the named selection.

        Parameters
        ----------
        members : list of Body, Face, Edge, Beam, DesignPoint, Component, or Vertex
            The members to remove from the named selection.

        Returns
        -------
        NamedSelection
            The new named selection with the members removed.
        """
        # Update cache
        self.__verify_ns()

        # Check to make sure NS will not be empty after removal
        if len(members) >= len(self._bodies) + len(self._faces) + len(self._edges) + len(
            self._beams
        ) + len(self._design_points) + len(self._components) + len(self._vertices):
            raise GeometryRuntimeError("NamedSelection cannot be empty after removal.")

        return NamedSelection(
            self._name,
            self._design,
            self._grpc_client,
            bodies=[body for body in self._bodies if body not in members],
            faces=[face for face in self._faces if face not in members],
            edges=[edge for edge in self._edges if edge not in members],
            beams=[beam for beam in self._beams if beam not in members],
            design_points=[dp for dp in self._design_points if dp not in members],
            components=[component for component in self._components if component not in members],
            vertices=[vertex for vertex in self._vertices if vertex not in members],
        )

    def __verify_ns(self) -> None:
        """Verify that the contents of the named selection are up to date."""
        if self._grpc_client.backend_version < (25, 2, 0):
            self._grpc_client.log.warning(
                "Accessing members of named selections is only"
                " consistent starting in version 2025 R2."
            )
            return

        # Get all entities from the named selection
        response = self._grpc_client.services.named_selection.get_named_selection(id=self._id)

        # Check if the named selection has changed
        ids = {
            "bodies": response.get("bodies"),
            "faces": response.get("faces"),
            "edges": response.get("edges"),
            "beams": response.get("beams"),
            "design_points": response.get("design_points"),
            "components": response.get("components"),
            "vertices": response.get("vertices"),
        }

        for key in ids:
            if ids[key] != self._ids_cached[key]:
                # Clear the cache for that specific entity
                setattr(self, f"_{key}", None)
                # Update the cache
                self._ids_cached[key] = ids[key]

    def __repr__(self) -> str:
        """Represent the ``NamedSelection`` as a string."""
        lines = [f"ansys.geometry.core.designer.selection.NamedSelection {hex(id(self))}"]
        lines.append(f"  Name                 : {self._name}")
        lines.append(f"  Id                   : {self._id}")
        lines.append(f"  N Bodies             : {len(self.bodies)}")
        lines.append(f"  N Faces              : {len(self.faces)}")
        lines.append(f"  N Edges              : {len(self.edges)}")
        lines.append(f"  N Beams              : {len(self.beams)}")
        lines.append(f"  N Design Points      : {len(self.design_points)}")
        lines.append(f"  N Components         : {len(self.components)}")
        lines.append(f"  N Vertices           : {len(self.vertices)}")
        return "\n".join(lines)
