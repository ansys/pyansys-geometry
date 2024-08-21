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
"""Provides tools for repairing bodies."""

from typing import TYPE_CHECKING

from google.protobuf.wrappers_pb2 import DoubleValue

from ansys.api.geometry.v0.bodies_pb2_grpc import BodiesStub
from ansys.api.geometry.v0.repairtools_pb2 import (
    FindDuplicateFacesRequest,
    FindExtraEdgesRequest,
    FindInexactEdgesRequest,
    FindMissingFacesRequest,
    FindShortEdgesRequest,
    FindSmallFacesRequest,
    FindSplitEdgesRequest,
    FindStitchFacesRequest,
)
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.misc.auxiliary import (
    get_bodies_from_ids,
    get_design_from_body,
    get_edges_from_ids,
    get_faces_from_ids,
)
from ansys.geometry.core.tools.problem_areas import (
    DuplicateFaceProblemAreas,
    ExtraEdgeProblemAreas,
    InexactEdgeProblemAreas,
    MissingFaceProblemAreas,
    ShortEdgeProblemAreas,
    SmallFaceProblemAreas,
    SplitEdgeProblemAreas,
    StitchFaceProblemAreas,
)
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body


class RepairTools:
    """Repair tools for PyAnsys Geometry."""

    def __init__(self, grpc_client: GrpcClient):
        """Initialize a new instance of the ``RepairTools`` class."""
        self._grpc_client = grpc_client
        self._repair_stub = RepairToolsStub(self._grpc_client.channel)
        self._bodies_stub = BodiesStub(self._grpc_client.channel)

    def find_split_edges(
        self, bodies: list["Body"], angle: Real = 0.0, length: Real = 0.0
    ) -> list[SplitEdgeProblemAreas]:
        """Find split edges in the given list of bodies.

        This method finds the split edge problem areas and returns a list of split edge
        problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that split edges are investigated on.
        angle : Real
            The maximum angle between edges.
        length : Real
            The maximum length of the edges.

        Returns
        -------
        list[SplitEdgeProblemAreas]
            List of objects representing split edge problem areas.
        """
        if not bodies:
            return []

        angle_value = DoubleValue(value=float(angle))
        length_value = DoubleValue(value=float(length))
        body_ids = [body.id for body in bodies]

        problem_areas_response = self._repair_stub.FindSplitEdges(
            FindSplitEdgesRequest(
                bodies_or_faces=body_ids, angle=angle_value, distance=length_value
            )
        )
        parent_design = get_design_from_body(bodies[0])
        return [
            SplitEdgeProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.edge_monikers),
            )
            for res in problem_areas_response.result
        ]

    def find_extra_edges(self, bodies: list["Body"]) -> list[ExtraEdgeProblemAreas]:
        """Find the extra edges in the given list of bodies.

        This method find the extra edge problem areas and returns a list of extra edge
        problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that extra edges are investigated on.

        Returns
        -------
        list[ExtraEdgeProblemArea]
            List of objects representing extra edge problem areas.
        """
        if not bodies:
            return []

        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindExtraEdges(
            FindExtraEdgesRequest(selection=body_ids)
        )
        parent_design = get_design_from_body(bodies[0])

        return [
            ExtraEdgeProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.edge_monikers),
            )
            for res in problem_areas_response.result
        ]

    def find_inexact_edges(self, bodies: list["Body"]) -> list[InexactEdgeProblemAreas]:
        """Find inexact edges in the given list of bodies.

        This method find the inexact edge problem areas and returns a list of inexact
        edge problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that inexact edges are investigated on.

        Returns
        -------
        list[InExactEdgeProblemArea]
            List of objects representing inexact edge problem areas.
        """
        if not bodies:
            return []

        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindInexactEdges(
            FindInexactEdgesRequest(selection=body_ids)
        )

        parent_design = get_design_from_body(bodies[0])

        return [
            InexactEdgeProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.edge_monikers),
            )
            for res in problem_areas_response.result
        ]

    def find_short_edges(
        self, bodies: list["Body"], length: Real = 0.0
    ) -> list[ShortEdgeProblemAreas]:
        """Find the short edge problem areas.

        This method finds the short edge problem areas and returns a list of
        these objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that short edges are investigated on.

        Returns
        -------
        list[ShortEdgeProblemAreas]
            List of objects representing short edge problem areas.
        """
        if not bodies:
            return []

        problem_areas_response = self._repair_stub.FindShortEdges(
            FindShortEdgesRequest(
                selection=[body.id for body in bodies],
                max_edge_length=DoubleValue(value=length),
            )
        )

        parent_design = get_design_from_body(bodies[0])
        return [
            ShortEdgeProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.edge_monikers),
            )
            for res in problem_areas_response.result
        ]

    def find_duplicate_faces(self, bodies: list["Body"]) -> list[DuplicateFaceProblemAreas]:
        """Find the duplicate face problem areas.

        This method finds the duplicate face problem areas and returns a list of
        duplicate face problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that duplicate faces are investigated on.

        Returns
        -------
        list[DuplicateFaceProblemAreas]
            List of objects representing duplicate face problem areas.
        """
        if not bodies:
            return []

        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindDuplicateFaces(
            FindDuplicateFacesRequest(faces=body_ids)
        )

        parent_design = get_design_from_body(bodies[0])
        return [
            DuplicateFaceProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_faces_from_ids(parent_design, res.face_monikers),
            )
            for res in problem_areas_response.result
        ]

    def find_missing_faces(self, bodies: list["Body"]) -> list[MissingFaceProblemAreas]:
        """Find the missing faces.

        This method find the missing face problem areas and returns a list of missing
        face problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that missing faces are investigated on.

        Returns
        -------
        list[MissingFaceProblemAreas]
            List of objects representing missing face problem areas.
        """
        if not bodies:
            return []
        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindMissingFaces(
            FindMissingFacesRequest(faces=body_ids)
        )
        parent_design = get_design_from_body(bodies[0])

        return [
            MissingFaceProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_edges_from_ids(parent_design, res.edge_monikers),
            )
            for res in problem_areas_response.result
        ]

    def find_small_faces(self, bodies: list["Body"]) -> list[SmallFaceProblemAreas]:
        """Find the small face problem areas.

        This method finds and returns a list of ids of small face problem areas
        objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that small faces are investigated on.

        Returns
        -------
        list[SmallFaceProblemAreas]
            List of objects representing small face problem areas.
        """
        if not bodies:
            return []

        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindSmallFaces(
            FindSmallFacesRequest(selection=body_ids)
        )
        parent_design = get_design_from_body(bodies[0])

        return [
            SmallFaceProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_faces_from_ids(parent_design, res.face_monikers),
            )
            for res in problem_areas_response.result
        ]

    def find_stitch_faces(self, bodies: list["Body"]) -> list[StitchFaceProblemAreas]:
        """Return the list of stitch face problem areas.

        This method find the stitch face problem areas and returns a list of ids of stitch face
        problem areas objects.

        Parameters
        ----------
        bodies : list[Body]
            List of bodies that stitchable faces are investigated on.

        Returns
        -------
        list[StitchFaceProblemAreas]
            List of objects representing stitch face problem areas.
        """
        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindStitchFaces(
            FindStitchFacesRequest(faces=body_ids)
        )
        parent_design = get_design_from_body(bodies[0])
        return [
            StitchFaceProblemAreas(
                f"{res.id}",
                self._grpc_client,
                get_bodies_from_ids(parent_design, res.body_monikers),
            )
            for res in problem_areas_response.result
        ]
