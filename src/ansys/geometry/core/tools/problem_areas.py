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
"""The problem area definition."""
from abc import abstractmethod

from ansys.api.geometry.v0.repairtools_pb2 import (
    FixDuplicateFacesRequest,
    FixInexactEdgesRequest,
    FixMissingFacesRequest,
    FixSmallFacesRequest,
    FixSplitEdgesRequest,
    FixStitchFacesRequest,
)
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from beartype.typing import List
from google.protobuf.wrappers_pb2 import Int32Value

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.tools.repair_tool_message import RepairToolMessage


class ProblemArea:
    """
    Represents problem areas.

    Parameters
    ----------
    id : str
        Server-defined ID for the problem area.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    """

    def __init__(self, id: str, grpc_client: GrpcClient):
        """Initialize a new instance of a problem area class."""
        self._id = id
        self._id_grpc = Int32Value(value=int(id))
        self._repair_stub = RepairToolsStub(grpc_client.channel)

    @property
    def id(self) -> str:
        """The id of the problem area."""
        return self._id

    @abstractmethod
    def fix(self):
        """Fix problem area."""
        raise NotImplementedError("Fix method is not implemented in the base class.")


class DuplicateFaceProblemAreas(ProblemArea):
    """
    Provides duplicate face problem area definition.

    Represents a duplicate face problem area with unique identifier and associated faces.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    faces : List[str]
        List of faces associated with the design.
    """

    def __init__(self, id: str, faces: List[str], grpc_client: GrpcClient):
        """Initialize a new instance of the duplicate face problem area class."""
        super().__init__(id, grpc_client)
        self._faces = faces

    @property
    def faces(self) -> List[str]:
        """
        The list of the problem area ids.

        This method returns the list of problem area ids with duplicate faces.
        """
        return self._faces

    def fix(self) -> RepairToolMessage:
        """
        Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        response = self._repair_stub.FixDuplicateFaces(
            FixDuplicateFacesRequest(duplicate_face_problem_area_id=self._id_grpc)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message


class MissingFaceProblemAreas(ProblemArea):
    """
    Provides missing face problem area definition.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    edges : List[str]
        List of edges associated with the design.
    """

    def __init__(self, id: str, edges: List[str], grpc_client: GrpcClient):
        """Initialize a new instance of the missing face problem area class."""
        super().__init__(id, grpc_client)
        self._edges = edges

    @property
    def edges(self) -> List[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._edges

    def fix(self) -> RepairToolMessage:
        """
        Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        response = self._repair_stub.FixMissingFaces(
            FixMissingFacesRequest(missing_face_problem_area_id=self._id_grpc)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message


class InexactEdgeProblemAreas(ProblemArea):
    """
    Represents an inexact edge problem area with unique identifier and associated edges.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    edges : List[str]
        List of edges associated with the design.
    """

    def __init__(self, id: str, edges: List[str], grpc_client: GrpcClient):
        """Initialize a new instance of the inexact edge problem area class."""
        super().__init__(id, grpc_client)
        self._edges = edges

    @property
    def edges(self) -> List[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._edges

    def fix(self) -> RepairToolMessage:
        """
        Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        response = self._repair_stub.FixInexactEdges(
            FixInexactEdgesRequest(inexact_edge_problem_area_id=self._id_grpc)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message


class ExtraEdgeProblemAreas(ProblemArea):
    """
    Represents a extra edge problem area with unique identifier and associated edges.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    edges : List[str]
        List of edges associated with the design.
    """

    def __init__(self, id: str, edges: List[str], grpc_client: GrpcClient):
        """Initialize a new instance of the extra edge problem area class."""
        super().__init__(id, grpc_client)
        self._edges = edges

    @property
    def edges(self) -> List[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._edges


class SmallFaceProblemAreas(ProblemArea):
    """
    Represents a small face problem area with unique identifier and associated faces.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    faces : List[str]
        List of edges associated with the design.
    """

    def __init__(self, id: str, faces: List[str], grpc_client: GrpcClient):
        """Initialize a new instance of the small face problem area class."""
        super().__init__(id, grpc_client)
        self._faces = faces

    @property
    def faces(self) -> List[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._faces

    def fix(self) -> RepairToolMessage:
        """
        Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        response = self._repair_stub.FixSmallFaces(
            FixSmallFacesRequest(small_face_problem_area_id=self._id_grpc)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message


class SplitEdgeProblemAreas(ProblemArea):
    """
    Represents a split edge problem area with unique identifier and associated edges.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    edges : List[str]
        List of edges associated with the design.
    """

    def __init__(self, id: str, edges: List[str], grpc_client: GrpcClient):
        """Initialize a new instance of the split edge problem area class."""
        super().__init__(id, grpc_client)
        self._edges = edges

    @property
    def edges(self) -> List[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._edges

    def fix(self) -> RepairToolMessage:
        """
        Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        response = self._repair_stub.FixSplitEdges(
            FixSplitEdgesRequest(split_edge_problem_area_id=self._id_grpc)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message


class StitchFaceProblemAreas(ProblemArea):
    """
    Represents a stitch face problem area with unique identifier and associated faces.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    faces : List[str]
        List of faces associated with the design.
    """

    def __init__(self, id: str, faces: List[str], grpc_client: GrpcClient):
        """Initialize a new instance of the stitch face problem area class."""
        super().__init__(id, grpc_client)
        self._faces = faces

    @property
    def faces(self) -> List[str]:
        """The list of the ids of the faces connected to this problem area."""
        return self._faces

    def fix(self) -> RepairToolMessage:
        """
        Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        response = self._repair_stub.FixStitchFaces(
            FixStitchFacesRequest(stitch_face_problem_area_id=self._id_grpc)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message
