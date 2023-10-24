# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
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

from ansys.api.geometry.v0.repairtools_pb2 import (
    FindDuplicateFacesRequest,
    FindExtraEdgesRequest,
    FindInexactEdgesRequest,
    FindMissingFacesRequest,
    FindSmallFacesRequest,
    FindSplitEdgesRequest,
    FindStitchFacesRequest,
)
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from beartype.typing import List
from google.protobuf.wrappers_pb2 import DoubleValue

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.tools.problem_areas import (
    DuplicateFaceProblemAreas,
    ExtraEdgeProblemAreas,
    InexactEdgeProblemAreas,
    MissingFaceProblemAreas,
    SmallFaceProblemAreas,
    SplitEdgeProblemAreas,
    StitchFaceProblemAreas,
)
from ansys.geometry.core.typing import Real


class RepairTools:
    """Repair tools for PyAnsys Geometry."""

    def __init__(self, grpc_client: GrpcClient):
        """Initialize Repair Tools class."""
        self._grpc_client = grpc_client
        self._repair_stub = RepairToolsStub(self._grpc_client.channel)

    def find_split_edges(
        self, ids: List[str], angle: Real = 0.0, length: Real = 0.0
    ) -> List[SplitEdgeProblemAreas]:
        """
        Find split edges in the given list of bodies.

        This method finds the split edge problem areas and returns a list of split edge
        problem areas objects.

        Parameters
        ----------
        ids : List[str]
            Server-defined ID for the bodies.
        angle : Real
            The maximum angle between edges.
        length : Real
            The maximum length of the edges.

        Returns
        ----------
        List[SplitEdgeProblemAreas]
            List of objects representing split edge problem areas.
        """
        angle_value = DoubleValue(value=float(angle))
        length_value = DoubleValue(value=float(length))
        problem_areas_response = self._repair_stub.FindSplitEdges(
            FindSplitEdgesRequest(bodies_or_faces=ids, angle=angle_value, distance=length_value)
        )

        problem_areas = []
        for res in problem_areas_response.result:
            connected_edges = []
            for edge_moniker in res.edge_monikers:
                connected_edges.append(edge_moniker)
            problem_area = SplitEdgeProblemAreas(res.id, connected_edges, self._grpc_client)
            problem_areas.append(problem_area)

        return problem_areas

    def find_extra_edges(self, ids: List[str]) -> List[ExtraEdgeProblemAreas]:
        """
        Find the extra edges in the given list of bodies.

        This method find the extra edge problem areas and returns a list of extra edge
        problem areas objects.

        Parameters
        ----------
        ids : List[str]
            Server-defined ID for the bodies.

        Returns
        ----------
        List[ExtraEdgeProblemArea]
            List of objects representing extra edge problem areas.
        """
        problem_areas_response = self._repair_stub.FindExtraEdges(
            FindExtraEdgesRequest(selection=ids)
        )
        problem_areas = []
        for res in problem_areas_response.result:
            connected_edges = []
            for edge_moniker in res.edge_monikers:
                connected_edges.append(edge_moniker)
            problem_area = ExtraEdgeProblemAreas(res.id, connected_edges, self._grpc_client)
            problem_areas.append(problem_area)

        return problem_areas

    def find_inexact_edges(self, ids) -> List[InexactEdgeProblemAreas]:
        """
        Find inexact edges in the given list of bodies.

        This method find the inexact edge problem areas and returns a list of inexact
        edge problem areas objects.

        Parameters
        ----------
        ids : List[str]
            Server-defined ID for the bodies.

        Returns
        -------
        List[InExactEdgeProblemArea]
            List of objects representing inexact edge problem areas.
        """
        problem_areas_response = self._repair_stub.FindInexactEdges(
            FindInexactEdgesRequest(selection=ids)
        )
        problem_areas = []
        for res in problem_areas_response.result:
            connected_edges = []
            for edge_moniker in res.edge_monikers:
                connected_edges.append(edge_moniker)
            problem_area = InexactEdgeProblemAreas(res.id, connected_edges, self._grpc_client)
            problem_areas.append(problem_area)

        return problem_areas

    def find_duplicate_faces(self, ids) -> List[DuplicateFaceProblemAreas]:
        """
        Find the duplicate face problem areas.

        This method finds the duplicate face problem areas and returns a list of
        duplicate face problem areas objects.

        Parameters
        ----------
        ids : List[str]
            Server-defined ID for the bodies.

        Returns
        -------
        List[DuplicateFaceProblemAreas]
            List of objects representing duplicate face problem areas.
        """
        problem_areas_response = self._repair_stub.FindDuplicateFaces(
            FindDuplicateFacesRequest(faces=ids)
        )
        problem_areas = []
        for res in problem_areas_response.result:
            connected_edges = []
            for face_moniker in res.face_monikers:
                connected_edges.append(face_moniker)
            problem_area = DuplicateFaceProblemAreas(res.id, connected_edges, self._grpc_client)
            problem_areas.append(problem_area)

        return problem_areas

    def find_missing_faces(self, ids) -> List[MissingFaceProblemAreas]:
        """
        Find the missing faces.

        This method find the missing face problem areas and returns a list of missing
        face problem areas objects.

        Parameters
        ----------
        ids : List[str]
            Server-defined ID for the bodies.

        Returns
        -------
        List[MissingFaceProblemAreas]
            List of objects representing missing face problem areas.
        """
        problem_areas_response = self._repair_stub.FindMissingFaces(
            FindMissingFacesRequest(faces=ids)
        )
        problem_areas = []
        for res in problem_areas_response.result:
            connected_edges = []
            for edge_moniker in res.edge_monikers:
                connected_edges.append(edge_moniker)
            problem_area = MissingFaceProblemAreas(res.id, connected_edges, self._grpc_client)
            problem_areas.append(problem_area)

        return problem_areas

    def find_small_faces(self, ids) -> List[SmallFaceProblemAreas]:
        """
        Find the small face problem areas.

        This method finds and returns a list of ids of small face problem areas
        objects.

        Parameters
        ----------
        ids : List[str]
            Server-defined ID for the bodies.

        Returns
        -------
        List[SmallFaceProblemAreas]
            List of objects representing small face problem areas.
        """
        problem_areas_response = self._repair_stub.FindSmallFaces(
            FindSmallFacesRequest(selection=ids)
        )
        problem_areas = []
        for res in problem_areas_response.result:
            connected_edges = []
            for face_moniker in res.face_monikers:
                connected_edges.append(face_moniker)
            problem_area = SmallFaceProblemAreas(res.id, connected_edges, self._grpc_client)
            problem_areas.append(problem_area)

        return problem_areas

    def find_stitch_faces(self, ids) -> List[StitchFaceProblemAreas]:
        """
        Return the list of stitch face problem areas.

        This method find the stitch face problem areas and returns a list of ids of stitch face
        problem areas objects.

        Parameters
        ----------
        ids : List[str]
            Server-defined ID for the bodies.

        Returns
        -------
        List[StitchFaceProblemAreas]
            List of objects representing stitch face problem areas.
        """
        problem_areas_response = self._repair_stub.FindStitchFaces(
            FindStitchFacesRequest(faces=ids)
        )
        problem_areas = []
        for res in problem_areas_response.result:
            connected_edges = []
            for face_moniker in res.body_monikers:
                connected_edges.append(face_moniker)
            problem_area = StitchFaceProblemAreas(res.id, connected_edges, self._grpc_client)
            problem_areas.append(problem_area)

        return problem_areas
