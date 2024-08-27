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
"""The problem area definition."""

from abc import abstractmethod
from typing import TYPE_CHECKING

from google.protobuf.wrappers_pb2 import Int32Value

from ansys.api.geometry.v0.repairtools_pb2 import (
    FixDuplicateFacesRequest,
    FixExtraEdgesRequest,
    FixInexactEdgesRequest,
    FixMissingFacesRequest,
    FixShortEdgesRequest,
    FixSmallFacesRequest,
    FixSplitEdgesRequest,
    FixStitchFacesRequest,
)
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.misc.auxiliary import (
    get_design_from_body,
    get_design_from_edge,
    get_design_from_face,
)
from ansys.geometry.core.misc.checks import check_type_all_elements_in_iterable
from ansys.geometry.core.tools.repair_tool_message import RepairToolMessage

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.designer.body import Body
    from ansys.geometry.core.designer.edge import Edge
    from ansys.geometry.core.designer.face import Face


class ProblemArea:
    """Represents problem areas.

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
    """Provides duplicate face problem area definition.

    Represents a duplicate face problem area with unique identifier and associated faces.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    faces : list[Face]
        List of faces associated with the design.
    """

    def __init__(self, id: str, grpc_client: GrpcClient, faces: list["Face"]):
        """Initialize a new instance of the duplicate face problem areaclass."""
        super().__init__(id, grpc_client)

        from ansys.geometry.core.designer.face import Face

        # Verify that all elements in the list are of type Face
        check_type_all_elements_in_iterable(faces, Face)

        self._faces = faces

    @property
    def faces(self) -> list["Face"]:
        """The list of the edges connected to this problem area."""
        return self._faces

    def fix(self) -> RepairToolMessage:
        """Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        if not self.faces:
            return RepairToolMessage(False, [], [])

        parent_design = get_design_from_face(self.faces[0])
        response = self._repair_stub.FixDuplicateFaces(
            FixDuplicateFacesRequest(duplicate_face_problem_area_id=self._id_grpc)
        )
        parent_design._update_design_inplace()
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )

        return message


class MissingFaceProblemAreas(ProblemArea):
    """Provides missing face problem area definition.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    edges : list[Edge]
        List of edges associated with the design.
    """

    def __init__(self, id: str, grpc_client: GrpcClient, edges: list["Edge"]):
        """Initialize a new instance of the missing face problem area class."""
        super().__init__(id, grpc_client)

        from ansys.geometry.core.designer.edge import Edge

        # Verify that all elements in the list are of type Edge
        check_type_all_elements_in_iterable(edges, Edge)

        self._edges = edges

    @property
    def edges(self) -> list["Edge"]:
        """The list of the edges connected to this problem area."""
        return self._edges

    def fix(self) -> RepairToolMessage:
        """Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        if not self.edges:
            return RepairToolMessage(False, [], [])

        parent_design = get_design_from_edge(self.edges[0])
        response = self._repair_stub.FixMissingFaces(
            FixMissingFacesRequest(missing_face_problem_area_id=self._id_grpc)
        )
        parent_design._update_design_inplace()
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message


class InexactEdgeProblemAreas(ProblemArea):
    """Represents an inexact edge problem area with unique identifier and associated edges.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    edges : list[Edge]
        List of edges associated with the design.
    """

    def __init__(self, id: str, grpc_client: GrpcClient, edges: list["Edge"]):
        """Initialize a new instance of the inexact edge problem area class."""
        super().__init__(id, grpc_client)

        from ansys.geometry.core.designer.edge import Edge

        # Verify that all elements in the list are of type Edge
        check_type_all_elements_in_iterable(edges, Edge)

        self._edges = edges

    @property
    def edges(self) -> list["Edge"]:
        """The list of the edges connected to this problem area."""
        return self._edges

    def fix(self) -> RepairToolMessage:
        """Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        if not self.edges:
            return RepairToolMessage(False, [], [])

        parent_design = get_design_from_edge(self.edges[0])
        response = self._repair_stub.FixInexactEdges(
            FixInexactEdgesRequest(inexact_edge_problem_area_id=self._id_grpc)
        )
        parent_design._update_design_inplace()
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message


class ExtraEdgeProblemAreas(ProblemArea):
    """Represents a extra edge problem area with unique identifier and associated edges.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    edges : list[Edge]
        List of edges associated with the design.
    """

    def __init__(self, id: str, grpc_client: GrpcClient, edges: list["Edge"]):
        """Initialize a new instance of the extra edge problem area class."""
        super().__init__(id, grpc_client)

        from ansys.geometry.core.designer.edge import Edge

        # Verify that all elements in the list are of type Edge
        check_type_all_elements_in_iterable(edges, Edge)

        self._edges = edges

    @property
    def edges(self) -> list["Edge"]:
        """The list of the ids of the edges connected to this problem area."""
        return self._edges

    def fix(self) -> RepairToolMessage:
        """Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        if not self.edges:
            return RepairToolMessage(False, [], [])

        parent_design = get_design_from_edge(self.edges[0])
        request = FixExtraEdgesRequest(extra_edge_problem_area_id=self._id_grpc)
        response = self._repair_stub.FixExtraEdges(request)
        parent_design._update_design_inplace()
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )

        return message


class ShortEdgeProblemAreas(ProblemArea):
    """Represents a short edge problem area with a unique identifier and associated edges.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    edges : list[Edge]
        List of edges associated with the design.
    """

    def __init__(self, id: str, grpc_client: GrpcClient, edges: list["Edge"]):
        """Initialize a new instance of the ``ShortEdgeProblemAreas`` class."""
        super().__init__(id, grpc_client)

        from ansys.geometry.core.designer.edge import Edge

        # Verify that all elements in the list are edges
        check_type_all_elements_in_iterable(edges, Edge)

        self._edges = edges

    @property
    def edges(self) -> list["Edge"]:
        """The list of the ids of the edges connected to this problem area."""
        return self._edges

    def fix(self) -> RepairToolMessage:
        """Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        if not self.edges:
            return RepairToolMessage(False, [], [])

        parent_design = get_design_from_edge(self.edges[0])
        response = self._repair_stub.FixShortEdges(
            FixShortEdgesRequest(short_edge_problem_area_id=self._id_grpc)
        )
        parent_design._update_design_inplace()
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )

        return message


class SmallFaceProblemAreas(ProblemArea):
    """Represents a small face problem area with a unique identifier and associated faces.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    faces : list[Face]
        List of edges associated with the design.
    """

    def __init__(self, id: str, grpc_client: GrpcClient, faces: list["Face"]):
        """Initialize a new instance of the small face problem area class."""
        super().__init__(id, grpc_client)

        from ansys.geometry.core.designer.face import Face

        # Verify that all elements in the list are of type Face
        check_type_all_elements_in_iterable(faces, Face)

        self._faces = faces

    @property
    def faces(self) -> list["Face"]:
        """The list of the ids of the edges connected to this problem area."""
        return self._faces

    def fix(self) -> RepairToolMessage:
        """Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        if not self.faces:
            return RepairToolMessage(False, [], [])

        parent_design = get_design_from_face(self.faces[0])
        response = self._repair_stub.FixSmallFaces(
            FixSmallFacesRequest(small_face_problem_area_id=self._id_grpc)
        )
        parent_design._update_design_inplace()
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message


class SplitEdgeProblemAreas(ProblemArea):
    """Represents a split edge problem area with unique identifier and associated edges.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    edges : list[Edge]
        List of edges associated with the design.
    """

    def __init__(self, id: str, grpc_client: GrpcClient, edges: list["Edge"]):
        """Initialize a new instance of the split edge problem area class."""
        super().__init__(id, grpc_client)

        from ansys.geometry.core.designer.edge import Edge

        # Verify that all elements in the list are of type Edge
        check_type_all_elements_in_iterable(edges, Edge)

        self._edges = edges

    @property
    def edges(self) -> list["Edge"]:
        """The list of edges connected to this problem area."""
        return self._edges

    def fix(self) -> RepairToolMessage:
        """Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        if not self.edges:
            return RepairToolMessage(False, [], [])

        parent_design = get_design_from_edge(self.edges[0])
        response = self._repair_stub.FixSplitEdges(
            FixSplitEdgesRequest(split_edge_problem_area_id=self._id_grpc)
        )
        parent_design._update_design_inplace()
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message


class StitchFaceProblemAreas(ProblemArea):
    """Represents a stitch face problem area with unique identifier and associated faces.

    Parameters
    ----------
    id : str
        Server-defined ID for the body.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    bodies : list[Body]
        List of bodies associated with the design.
    """

    def __init__(self, id: str, grpc_client: GrpcClient, bodies: list["Body"]):
        """Initialize a new instance of the stitch face problem area class."""
        super().__init__(id, grpc_client)

        from ansys.geometry.core.designer.body import Body

        # Verify that all elements in the list are of type Body
        check_type_all_elements_in_iterable(bodies, Body)

        self._bodies = bodies

    @property
    def bodies(self) -> list["Body"]:
        """The list of the bodies connected to this problem area."""
        return self._bodies

    def fix(self) -> RepairToolMessage:
        """Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.
        """
        if not self.bodies:
            return RepairToolMessage(False, [], [])

        parent_design = get_design_from_body(self.bodies[0])
        response = self._repair_stub.FixStitchFaces(
            FixStitchFacesRequest(stitch_face_problem_area_id=self._id_grpc)
        )
        parent_design._update_design_inplace()
        message = RepairToolMessage(
            response.result.success,
            response.result.created_bodies_monikers,
            response.result.modified_bodies_monikers,
        )
        return message
