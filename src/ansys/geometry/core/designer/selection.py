# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

from typing import TYPE_CHECKING

from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier
from ansys.api.geometry.v0.namedselections_pb2 import CreateRequest
from ansys.api.geometry.v0.namedselections_pb2_grpc import NamedSelectionsStub
from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.conversions import grpc_point_to_point3d
from ansys.geometry.core.designer.beam import Beam
from ansys.geometry.core.designer.body import Body
from ansys.geometry.core.designer.designpoint import DesignPoint
from ansys.geometry.core.designer.edge import Edge
from ansys.geometry.core.designer.face import Face
from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.misc.auxiliary import (
    get_beams_from_ids,
    get_bodies_from_ids,
    get_edges_from_ids,
    get_faces_from_ids,
)

if TYPE_CHECKING:
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
    """

    @protect_grpc
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
        preexisting_id: str | None = None,
    ):
        """Initialize the ``NamedSelection`` class."""
        self._name = name
        self._design = design
        self._grpc_client = grpc_client
        self._named_selections_stub = NamedSelectionsStub(self._grpc_client.channel)

        # Create empty arrays if there are none of a type
        if bodies is None:
            bodies = []
        if faces is None:
            faces = []
        if edges is None:
            edges = []
        if beams is None:
            beams = []
        if design_points is None:
            design_points = []

        # Instantiate
        self._bodies = bodies
        self._faces = faces
        self._edges = edges
        self._beams = beams
        self._design_points = design_points

        # Store ids for later use... when verifying if the NS changed.
        self._ids_cached = {
            "bodies": [body.id for body in bodies],
            "faces": [face.id for face in faces],
            "edges": [edge.id for edge in edges],
            "beams": [beam.id for beam in beams],
            "design_points": [dp.id for dp in design_points],
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

        named_selection_request = CreateRequest(name=name, members=ids)
        self._grpc_client.log.debug("Requesting creation of named selection.")
        new_named_selection = self._named_selections_stub.Create(named_selection_request)
        self._id = new_named_selection.id

    @property
    def id(self) -> str:
        """ID of the named selection."""
        return self._id

    @property
    def name(self) -> str:
        """Name of the named selection."""
        return self._name

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
            self._design_points = [
                DesignPoint(dp_id, f"dp: {dp_id}", grpc_point_to_point3d(dp_point))
                for dp_id, dp_point in self._ids_cached["design_points"]
            ]

        return self._design_points

    def __verify_ns(self) -> None:
        """Verify that the contents of the named selection are up to date."""
        if self._grpc_client.backend_version < (25, 2, 0):
            self._grpc_client.log.warning(
                "Accessing members of named selections is only"
                " consistent starting in version 2025 R2."
            )
            return

        # Get all entities from the named selection
        resp = self._named_selections_stub.Get(EntityIdentifier(id=self._id))

        # Check if the named selection has changed
        ids = {
            "bodies": [body.id for body in resp.bodies],
            "faces": [face.id for face in resp.faces],
            "edges": [edge.id for edge in resp.edges],
            "beams": [beam.id.id for beam in resp.beams],
            "design_points": [(dp.id, dp.points[0]) for dp in resp.design_points],
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
        return "\n".join(lines)
