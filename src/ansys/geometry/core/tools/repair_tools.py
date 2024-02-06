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
from beartype.typing import TYPE_CHECKING, List

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.design import Design

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
        self, bodies: List["Body"], angle: Real = 0.0, length: Real = 0.0
    ) -> List[SplitEdgeProblemAreas]:
        """
        Find split edges in the given list of bodies.

        This method finds the split edge problem areas and returns a list of split edge
        problem areas objects.

        Parameters
        ----------
        bodies : List[Body]
            List of bodies that split edges are investigated on.
        angle : Real
            The maximum angle between edges.
        length : Real
            The maximum length of the edges.

        Returns
        -------
        List[SplitEdgeProblemAreas]
            List of objects representing split edge problem areas.
        """
        angle_value = DoubleValue(value=float(angle))
        length_value = DoubleValue(value=float(length))
        body_ids = [body.id for body in bodies]

        problem_areas_response = self._repair_stub.FindSplitEdges(
            FindSplitEdgesRequest(
                bodies_or_faces=body_ids, angle=angle_value, distance=length_value
            )
        )

        problem_areas = [
            SplitEdgeProblemAreas(res.id, list(res.edge_monikers), self._grpc_client)
            for res in problem_areas_response.result
        ]
        return problem_areas

    def find_extra_edges(self, bodies: List["Body"]) -> List[ExtraEdgeProblemAreas]:
        """
        Find the extra edges in the given list of bodies.

        This method find the extra edge problem areas and returns a list of extra edge
        problem areas objects.

        Parameters
        ----------
        bodies : List[Body]
            List of bodies that extra edges are investigated on.

        Returns
        -------
        List[ExtraEdgeProblemArea]
            List of objects representing extra edge problem areas.
        """
        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindExtraEdges(
            FindExtraEdgesRequest(selection=body_ids)
        )
        parent_design = self.get_root_component(bodies[0])

        return [
            ExtraEdgeProblemAreas(
                res.id, self.get_edges_from_ids(parent_design, res.edge_monikers), self._grpc_client
            )
            for res in problem_areas_response.result
        ]

    def find_inexact_edges(self, bodies: List["Body"]) -> List[InexactEdgeProblemAreas]:
        """
        Find inexact edges in the given list of bodies.

        This method find the inexact edge problem areas and returns a list of inexact
        edge problem areas objects.

        Parameters
        ----------
        bodies : List[Body]
            List of bodies that inexact edges are investigated on.

        Returns
        -------
        List[InExactEdgeProblemArea]
            List of objects representing inexact edge problem areas.
        """
        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindInexactEdges(
            FindInexactEdgesRequest(selection=body_ids)
        )

        parent_design = self.get_root_component(bodies[0])

        return [
            InexactEdgeProblemAreas(
                res.id, self.get_edges_from_ids(parent_design, res.edge_monikers), self._grpc_client
            )
            for res in problem_areas_response.result
        ]

    def find_duplicate_faces(self, bodies: List["Body"]) -> List[DuplicateFaceProblemAreas]:
        """
        Find the duplicate face problem areas.

        This method finds the duplicate face problem areas and returns a list of
        duplicate face problem areas objects.

        Parameters
        ----------
        bodies : List[Body]
            List of bodies that duplicate faces are investigated on.

        Returns
        -------
        List[DuplicateFaceProblemAreas]
            List of objects representing duplicate face problem areas.
        """
        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindDuplicateFaces(
            FindDuplicateFacesRequest(faces=body_ids)
        )

        parent_design = self.get_root_component(bodies[0])
        return [
            DuplicateFaceProblemAreas(
                res.id, self.get_faces_from_ids(parent_design, res.face_monikers), self._grpc_client
            )
            for res in problem_areas_response.result
        ]

    def find_missing_faces(self, bodies: List["Body"]) -> List[MissingFaceProblemAreas]:
        """
        Find the missing faces.

        This method find the missing face problem areas and returns a list of missing
        face problem areas objects.

        Parameters
        ----------
        bodies : List[Body]
            List of bodies that missing faces are investigated on.

        Returns
        -------
        List[MissingFaceProblemAreas]
            List of objects representing missing face problem areas.
        """
        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindMissingFaces(
            FindMissingFacesRequest(faces=body_ids)
        )
        parent_design = self.get_root_component(bodies[0])

        return [
            MissingFaceProblemAreas(
                res.id, self.get_edges_from_ids(parent_design, res.edge_monikers), self._grpc_client
            )
            for res in problem_areas_response.result
        ]

    def find_small_faces(self, bodies: List["Body"]) -> List[SmallFaceProblemAreas]:
        """
        Find the small face problem areas.

        This method finds and returns a list of ids of small face problem areas
        objects.

        Parameters
        ----------
        bodies : List[Body]
            List of bodies that small faces are investigated on.

        Returns
        -------
        List[SmallFaceProblemAreas]
            List of objects representing small face problem areas.
        """
        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindSmallFaces(
            FindSmallFacesRequest(selection=body_ids)
        )
        parent_design = self.get_root_component(bodies[0])

        return [
            SmallFaceProblemAreas(
                res.id, self.get_faces_from_ids(parent_design, res.face_monikers), self._grpc_client
            )
            for res in problem_areas_response.result
        ]

    def find_stitch_faces(self, bodies: List["Body"]) -> List[StitchFaceProblemAreas]:
        """
        Return the list of stitch face problem areas.

        This method find the stitch face problem areas and returns a list of ids of stitch face
        problem areas objects.

        Parameters
        ----------
        bodies : List[Body]
            List of bodies that stitchable faces are investigated on.

        Returns
        -------
        List[StitchFaceProblemAreas]
            List of objects representing stitch face problem areas.
        """
        body_ids = [body.id for body in bodies]
        problem_areas_response = self._repair_stub.FindStitchFaces(
            FindStitchFacesRequest(faces=body_ids)
        )
        parent_design = self.get_root_component(bodies[0])
        return [
            StitchFaceProblemAreas(
                res.id,
                self.get_faces_from_idslist(parent_design, res.body_monikers),
                self._grpc_client,
            )
            for res in problem_areas_response.result
        ]

    def get_faces_from_ids(self, design: "Design", face_ids: List[str]):
        """
        Find the face object from its id.

        This method takes a design and face ids and gets their corresponding face object.

        Parameters
        ----------
        design : Design
            Parent design for the faces.

        face_ids : List[str]
            List of face ids corresponding to the problem area.

        Returns
        -------
        List[Face]
            List of face objects representing duplicate face problem areas.
        """
        return [
            face
            for body in design.bodies
            for face in body.faces
            if str(face.id) in set(map(str, face_ids))
        ]

    def get_edges_from_ids(self, design: "Design", edge_ids: List[str]):
        """
        Find the face object from its id.

        This method takes a design and face ids and gets their corresponding face object.

        Parameters
        ----------
        design : Design
            Parent design for the faces.

        edge_ids : List[str]
            List of face ids corresponding to the problem area.

        Returns
        -------
        List[Edge]
            List of edge objects representing duplicate face problem areas.
        """
        return [
            edge
            for body in design.bodies
            for face in body.faces
            for edge in face.edges
            if str(edge.id) in set(map(str, edge_ids))
        ]

    @staticmethod
    def get_root_component(self, body: "Body"):
        """
        Get the root component (design) of the given body object.

        Parameters
        ----------
        body : Body
            The body object for which to find the root component.

        Returns
        -------
        Component
            The root component of the provided body object.
        """
        component = body.parent_component
        while component.parent_component is not None:
            component = component.parent_component
        return component
