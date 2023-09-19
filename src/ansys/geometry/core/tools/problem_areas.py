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


from ansys.api.geometry.v0.repairtools_pb2 import FixDuplicateFacesRequest
from ansys.api.geometry.v0.repairtools_pb2 import FixInexactEdgesRequest
from ansys.api.geometry.v0.repairtools_pb2 import FixExtraEdgesRequest
from ansys.api.geometry.v0.repairtools_pb2 import FixMissingFacesRequest
from ansys.api.geometry.v0.repairtools_pb2 import FixSmallFacesRequest
from ansys.api.geometry.v0.repairtools_pb2 import FixStitchFacesRequest
from ansys.api.geometry.v0.repairtools_pb2 import FixShortEdgesRequest
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from google.protobuf.wrappers_pb2 import Int32Value

from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.tools.repair_tool_message import RepairToolMessage

"""The duplicate face problem area definition."""
class DuplicateFaceProblemAreas:
    """
    Represents a duplicate face problem area.

    Resas with unique identifier and associated
    faces.

    Attributes:
        _id (str): A unique identifier for the problem area.
        _faces (list[str]): A list of faces associated with the design.
    """

    def __init__(self, id: str, faces: list[str]):
        """
        Initialize a new instance of the duplicate face problem area class.

        :param id: A unique identifier for the design.
        :type id: str
        :param design_edges: A list of faces associated with the design.
        :type design_edges: list[str]
        """
        self._id = id
        self._faces = faces

    @property
    def id(self) -> str:
        """The id of the problem area."""
        return self._id

    @property
    def faces(self) -> list[str]:
        """
        The list of the problem area ids.

        This method returns the list of problem area ids with duplicate faces.
        """
        return self._faces

    def fix(self):
        """Fix the problem area."""
        client = GrpcClient()
        id_value = Int32Value(value=int(self._id))
        response = RepairToolsStub(client.channel).FixDuplicateFaces(
            FixDuplicateFacesRequest(duplicate_face_problem_area_id=id_value)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message


class MissingFaceProblemAreas:
    """
    Provides missing face problem area definition.

    Represents a duplicate face problem area with unique identifier and associated faces.

    Attributes:
        _id (str): A unique identifier for the problem area.
        _edges (list[str]): A list of faces associated with the design.
    """

    def __init__(self, id: str, edges: list[str]):
        """
        Initialize a new instance of the missing face problem area class.

        :param id: A unique identifier for the design.
        :type id: str
        :param edges: A list of edges associated with the design.
        :type edges: list[str]
        """
        self._id = id
        self._edges = edges

    @property
    def id(self) -> str:
        """The id of the problem area."""
        return self._id

    @property
    def edges(self) -> list[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._edges

    def fix(self):
        """Fix the problem area."""
        client = GrpcClient()
        id_value = Int32Value(value=int(self._id))
        response = RepairToolsStub(client.channel).FixMissingFaces(
            FixMissingFacesRequest(missing_face_problem_area_id=id_value)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message

class InexactEdgeProblemAreas:
    """
    Represents an inexact edge problem area with unique identifier and associated edges.

    Attributes:
        _id (str): A unique identifier for the problem area.
        _edges (list[str]): A list of edges associated with the design.
    """

    def __init__(self, id: str, edges: list[str]):
        """
        Initialize a new instance of the inexact edge problem area class.

        :param id: A unique identifier for the design.
        :type id: str
        :param edges: A list of edges associated with the design.
        :type edges: list[str]
        """
        self._id = id
        self._edges = edges

    @property
    def id(self):
        """The id of the problem area."""
        return self._id

    @property
    def edges(self) -> list[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._edges

    def fix(self):
        """Fix the problem area."""
        client = GrpcClient()
        id_value = Int32Value(value=int(self._id))
        response = RepairToolsStub(client.channel).FixInexactEdges(
            FixInexactEdgesRequest(inexact_edge_problem_area_id=id_value)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message

class ExtraEdgeProblemAreas:
    """
    Represents a extra edge problem area with unique identifier and associated edges.

    Attributes:
        _id (str): A unique identifier for the problem area.
        _edges (list[str]): A list of edges associated with the design.
    """

    def __init__(self, id: str, edges: list[str]):
        """
        Initialize a new instance of the extra edge problem area class.

        :param id: A unique identifier for the design.
        :type id: str
        :param edges: A list of edges associated with the design.
        :type edges: list[str]
        """
        self._id = id
        self._edges = edges

    @property
    def id(self) -> str:
        """The id of the problem area."""
        return self._id

    @property
    def edges(self) -> list[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._edges

    def fix(self):
        """Fix the problem area."""
        client = GrpcClient()
        id_value = Int32Value(value=int(self._id))
        response = RepairToolsStub(client.channel).FixExtraEdges(
            FixExtraEdgesRequest(extra_edge_problem_area_id=id_value)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message

class ShortEdgeProblemAreas:
    """
    Represents a short edge problem area with unique identifier and associated edges.

    Attributes:
        _id (str): A unique identifier for the problem area.
        _edges (list[str]): A list of edges associated with the design.
    """

    def __init__(self, id: str, edges: list[str]):
        """
        Initialize a new instance of the short edge problem area class.

        :param id: A unique identifier for the design.
        :type id: str
        :param edges: A list of edges associated with the design.
        :type edges: list[str]
        """
        self._id = id
        self._edges = edges

    @property
    def id(self) -> str:
        """The id of the problem area."""
        return self._id

    @property
    def design_edges(self) -> list[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._design_edges

    def fix(self):
        """Fix the problem area."""
        client = GrpcClient()
        id_value = Int32Value(value=int(self._id))
        response = RepairToolsStub(client.channel).FixShortEdges(
            FixShortEdgesRequest(short_edge_problem_area_id=id_value)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message
    
class SmallFaceProblemAreas:
    """
    Represents a small face problem area with unique identifier and associated faces.

    Attributes:
        _id (str): A unique identifier for the problem area.
        _faces (list[str]): A list of faces associated with the design.
    """

    def __init__(self, id: str, faces: list[str]):
        """
        Initialize a new instance of the small face problem area class.

        :param id: A unique identifier for the design.
        :type id: str
        :param design_edges: A list of faces associated with the design.
        :type design_edges: list[str]
        """
        self._id = id
        self._faces = faces

    @property
    def id(self) -> str:
        """The id of the problem area."""
        return self._id

    @property
    def faces(self) -> list[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._faces

    def fix(self):
        """Fix the problem area."""
        client = GrpcClient()
        id_value = Int32Value(value=int(self._id))
        response = RepairToolsStub(client.channel).FixSmallFaces(
            FixSmallFacesRequest(small_face_problem_area_id=id_value)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message

class SplitEdgeProblemAreas:
    """
    Represents a split edge problem area with unique identifier and associated edges.

    Attributes:
        _id (str): A unique identifier for the problem area.
        _edges (list[str]): A list of edges associated with the design.
    """

    def __init__(self, id: str, edges: list[str]):
        """
        Initialize a new instance of the split edge problem area class.

        :param id: A unique identifier for the design.
        :type id: str
        :param design_edges: A list of faces associated with the design.
        :type design_edges: list[str]
        """
        self._id = id
        self._edges = edges

    @property
    def id(self) -> str:
        """The id of the problem area."""
        return self._id

    @property
    def edges(self) -> list[str]:
        """The list of the ids of the edges connected to this problem area."""
        return self._edges

    def fix(self):
        """Fix the problem area."""
        client = GrpcClient()
        id_value = Int32Value(value=int(self._id))
        response = RepairToolsStub(client.channel).FixSplitEdges(
            FixSplitEdgesRequest(split_edge_problem_area_id=id_value)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message

class StitchFaceProblemAreas:
    """
    Represents a stitch face problem area with unique identifier and associated faces.

    Attributes:
        _id (str): A unique identifier for the problem area.
        _faces (list[str]): A list of faces associated with the design.
    """

    def __init__(self, id: str, faces: list[str]):
        """
        Initialize a new instance of the stitch face problem area class.

        :param id: A unique identifier for the design.
        :type id: str
        :param faces: A list of faces associated with the design.
        :type faces: list[str]
        """
        self._id = id
        self._faces = faces

    @property
    def id(self) -> str:
        """The id of the problem area."""
        return self._id

    @property
    def faces(self) -> list[str]:
        """The list of the ids of the faces connected to this problem area."""
        return self._faces

    def fix(self):
        """Fix the problem area."""
        client = GrpcClient()
        id_value = Int32Value(value=int(self._id))
        response = RepairToolsStub(client.channel).FixStitchFaces(
            FixStitchFacesRequest(stitch_face_problem_area_id=id_value)
        )
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message