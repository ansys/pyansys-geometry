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
"""The problem area definition."""

from abc import abstractmethod
from typing import TYPE_CHECKING

from google.protobuf.wrappers_pb2 import Int32Value

from ansys.api.geometry.v0.repairtools_pb2 import (
    FixAdjustSimplifyRequest,
    FixDuplicateFacesRequest,
    FixExtraEdgesRequest,
    FixInexactEdgesRequest,
    FixInterferenceRequest,
    FixMissingFacesRequest,
    FixShortEdgesRequest,
    FixSmallFacesRequest,
    FixSplitEdgesRequest,
    FixStitchFacesRequest,
)
from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub
from ansys.geometry.core.connection import GrpcClient
from ansys.geometry.core.errors import protect_grpc
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
        self._grpc_id = Int32Value(value=int(id))
        self._repair_stub = RepairToolsStub(grpc_client.channel)
        self._grpc_client = grpc_client

    @property
    def id(self) -> str:
        """The id of the problem area."""
        return self._id

    @abstractmethod
    def fix(self):
        """Fix problem area."""
        raise NotImplementedError("Fix method is not implemented in the base class.")

    @staticmethod
    def serialize_tracker_command_response(response) -> dict:
        """Serialize a TrackerCommandResponse object into a dictionary.

        Parameters
        ----------
        response : TrackerCommandResponse
            The gRPC TrackerCommandResponse object to serialize.

        Returns
        -------
        dict
            A dictionary representation of the TrackerCommandResponse object.
        """

        def serialize_body(body):
            """Serialize a Body object into a dictionary."""
            return {
                "id": body.id,
                "name": body.name,
                "can_suppress": body.can_suppress,
                "transform_to_master": {
                    "m00": body.transform_to_master.m00,
                    "m11": body.transform_to_master.m11,
                    "m22": body.transform_to_master.m22,
                    "m33": body.transform_to_master.m33,
                },
                "master_id": body.master_id,
                "parent_id": body.parent_id,
            }

        def serialize_entity_identifier(entity):
            """Serialize an EntityIdentifier object into a dictionary."""
            return {
                "id": entity.id,
                # "type": entity.type,
            }

        # Safely serialize each field, defaulting to an empty list if the field is missing
        return {
            "success": response.success,
            "created_bodies": [
                serialize_body(body) for body in getattr(response, "created_bodies", [])
            ],
            "modified_bodies": [
                serialize_body(body) for body in getattr(response, "modified_bodies", [])
            ],
            "deleted_bodies": [
                serialize_entity_identifier(entity)
                for entity in getattr(response, "deleted_bodies", [])
            ],
        }


class DuplicateFaceProblemAreas(ProblemArea):
    """Provides duplicate face problem area definition.

    Represents a duplicate face problem area with unique identifier and associated faces.

    Parameters
    ----------
    id : str
        Server-defined ID for the problem area.
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
        """The list of faces connected to this problem area."""
        return self._faces

    @protect_grpc
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
            FixDuplicateFacesRequest(duplicate_face_problem_area_id=self._grpc_id)
        )
        from ansys.geometry.core import USE_TRACKER_TO_UPDATE_DESIGNS

        if not USE_TRACKER_TO_UPDATE_DESIGNS:
            parent_design._update_design_inplace()
        else:
            tracker_response = response.result.complete_command_response
            serialized_response = self.serialize_tracker_command_response(tracker_response)
            parent_design._update_from_tracker(serialized_response)

        message = RepairToolMessage(
            success=response.result.success,
            created_bodies=response.result.created_bodies_monikers,
            modified_bodies=response.result.modified_bodies_monikers,
        )

        return message


class MissingFaceProblemAreas(ProblemArea):
    """Provides missing face problem area definition.

    Parameters
    ----------
    id : str
        Server-defined ID for the problem area.
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
        """The list of edges connected to this problem area."""
        return self._edges

    @protect_grpc
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
            FixMissingFacesRequest(missing_face_problem_area_id=self._grpc_id)
        )

        serialized_response = self.serialize_tracker_command_response(
            response.result.complete_command_response
        )

        from ansys.geometry.core import USE_TRACKER_TO_UPDATE_DESIGNS

        if not USE_TRACKER_TO_UPDATE_DESIGNS:
            parent_design._update_design_inplace()
        else:
            parent_design._update_from_tracker(serialized_response)

        message = RepairToolMessage(
            success=response.result.success,
            created_bodies=response.result.created_bodies_monikers,
            modified_bodies=response.result.modified_bodies_monikers,
        )
        return message


class InexactEdgeProblemAreas(ProblemArea):
    """Represents an inexact edge problem area with unique identifier and associated edges.

    Parameters
    ----------
    id : str
        Server-defined ID for the problem area.
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
        """The list of edges connected to this problem area."""
        return self._edges

    @protect_grpc
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
            FixInexactEdgesRequest(inexact_edge_problem_area_id=self._grpc_id)
        )

        from ansys.geometry.core import USE_TRACKER_TO_UPDATE_DESIGNS

        if not USE_TRACKER_TO_UPDATE_DESIGNS:
            parent_design._update_design_inplace()
        else:
            tracker_response = response.result.complete_command_response
            serialized_response = self.serialize_tracker_command_response(tracker_response)
            parent_design._update_from_tracker(serialized_response)

        message = RepairToolMessage(
            success=response.result.success,
            created_bodies=response.result.created_bodies_monikers,
            modified_bodies=response.result.modified_bodies_monikers,
        )

        return message


class ExtraEdgeProblemAreas(ProblemArea):
    """Represents a extra edge problem area with unique identifier and associated edges.

    Parameters
    ----------
    id : str
        Server-defined ID for the problem area.
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
        """The list of edges connected to this problem area."""
        return self._edges

    @protect_grpc
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
        request = FixExtraEdgesRequest(extra_edge_problem_area_id=self._grpc_id)
        response = self._repair_stub.FixExtraEdges(request)
        from ansys.geometry.core import USE_TRACKER_TO_UPDATE_DESIGNS

        if not USE_TRACKER_TO_UPDATE_DESIGNS:
            parent_design._update_design_inplace()
        else:
            tracker_response = response.result.complete_command_response
            serialized_response = self.serialize_tracker_command_response(tracker_response)
            parent_design._update_from_tracker(serialized_response)

        message = RepairToolMessage(
            success=response.result.success,
            created_bodies=response.result.created_bodies_monikers,
            modified_bodies=response.result.modified_bodies_monikers,
        )

        return message


class ShortEdgeProblemAreas(ProblemArea):
    """Represents a short edge problem area with a unique identifier and associated edges.

    Parameters
    ----------
    id : str
        Server-defined ID for the problem area.
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
        """The list of edges connected to this problem area."""
        return self._edges

    @protect_grpc
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
            FixShortEdgesRequest(short_edge_problem_area_id=self._grpc_id)
        )
        from ansys.geometry.core import USE_TRACKER_TO_UPDATE_DESIGNS

        if not USE_TRACKER_TO_UPDATE_DESIGNS:
            parent_design._update_design_inplace()
        else:
            tracker_response = response.result.complete_command_response
            serialized_response = self.serialize_tracker_command_response(tracker_response)
            parent_design._update_from_tracker(serialized_response)

        message = RepairToolMessage(
            success=response.result.success,
            created_bodies=response.result.created_bodies_monikers,
            modified_bodies=response.result.modified_bodies_monikers,
        )

        return message


class SmallFaceProblemAreas(ProblemArea):
    """Represents a small face problem area with a unique identifier and associated faces.

    Parameters
    ----------
    id : str
        Server-defined ID for the problem area.
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
        """The list of faces connected to this problem area."""
        return self._faces

    @protect_grpc
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
            FixSmallFacesRequest(small_face_problem_area_id=self._grpc_id)
        )

        from ansys.geometry.core import USE_TRACKER_TO_UPDATE_DESIGNS

        if not USE_TRACKER_TO_UPDATE_DESIGNS:
            parent_design._update_design_inplace()
        else:
            # If USE_TRACKER_TO_UPDATE_DESIGNS is True, we serialize the response
            # and update the parent design with the serialized response.
            tracker_response = response.result.complete_command_response
            serialized_response = self.serialize_tracker_command_response(tracker_response)
            parent_design._update_from_tracker(serialized_response)

        message = RepairToolMessage(
            success=response.result.success,
            created_bodies=response.result.created_bodies_monikers,
            modified_bodies=response.result.modified_bodies_monikers,
        )
        return message


class SplitEdgeProblemAreas(ProblemArea):
    """Represents a split edge problem area with unique identifier and associated edges.

    Parameters
    ----------
    id : str
        Server-defined ID for the problem area.
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

    @protect_grpc
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
            FixSplitEdgesRequest(split_edge_problem_area_id=self._grpc_id)
        )
        from ansys.geometry.core import USE_TRACKER_TO_UPDATE_DESIGNS

        if not USE_TRACKER_TO_UPDATE_DESIGNS:
            parent_design._update_design_inplace()
        else:
            tracker_respone = response.result.complete_command_response
            serialized_response = self.serialize_tracker_command_response(tracker_respone)
            parent_design._update_from_tracker(serialized_response)

        message = RepairToolMessage(
            success=response.result.success,
            created_bodies=response.result.created_bodies_monikers,
            modified_bodies=response.result.modified_bodies_monikers,
        )

        return message


class StitchFaceProblemAreas(ProblemArea):
    """Represents a stitch face problem area with unique identifier and associated faces.

    Parameters
    ----------
    id : str
        Server-defined ID for the problem area.
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
        """The list of bodies connected to this problem area."""
        return self._bodies

    @protect_grpc
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
            FixStitchFacesRequest(stitch_face_problem_area_id=self._grpc_id)
        )
        from ansys.geometry.core import USE_TRACKER_TO_UPDATE_DESIGNS

        if not USE_TRACKER_TO_UPDATE_DESIGNS:
            parent_design._update_design_inplace()
        else:
            tracker_respone = response.result.complete_command_response
            serialized_response = self.serialize_tracker_command_response(tracker_respone)
            parent_design._update_from_tracker(serialized_response)

        message = RepairToolMessage(
            success=response.result.success,
            created_bodies=response.result.created_bodies_monikers,
            modified_bodies=response.result.modified_bodies_monikers,
        )
        return message


class UnsimplifiedFaceProblemAreas(ProblemArea):
    """Represents a unsimplified face problem area with unique identifier and associated faces.

    Parameters
    ----------
    id : str
        Server-defined ID for the problem area.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    faces : list[Face]
        List of faces associated with the design.
    """

    def __init__(self, id: str, grpc_client: GrpcClient, faces: list["Face"]):
        """Initialize a new instance of the unsimplified face problem area class."""
        super().__init__(id, grpc_client)

        self._faces = faces

    @property
    def faces(self) -> list["Face"]:
        """The list of faces connected to this problem area."""
        return self._faces

    @protect_grpc
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
        response = self._repair_stub.FixAdjustSimplify(
            FixAdjustSimplifyRequest(adjust_simplify_problem_area_id=self._grpc_id)
        )
        from ansys.geometry.core import USE_TRACKER_TO_UPDATE_DESIGNS

        if not USE_TRACKER_TO_UPDATE_DESIGNS:
            parent_design._update_design_inplace()
        else:
            tracker_respone = response.result.complete_command_response
            serialized_response = self.serialize_tracker_command_response(tracker_respone)
            parent_design._update_from_tracker(serialized_response)

        message = RepairToolMessage(
            success=response.result.success,
            created_bodies=response.result.created_bodies_monikers,
            modified_bodies=response.result.modified_bodies_monikers,
        )
        return message


class InterferenceProblemAreas(ProblemArea):
    """Represents an interference problem area with a unique identifier and associated bodies.

    Parameters
    ----------
    id : str
        Server-defined ID for the problem area.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    bodies : list[Body]
        List of bodies in the problem area.
    """

    def __init__(self, id: str, grpc_client: GrpcClient, bodies: list["Body"]):
        """Initialize a new instance of the interference problem area class."""
        super().__init__(id, grpc_client)

        self._bodies = bodies

    @property
    def bodies(self) -> list["Body"]:
        """The list of the bodies connected to this problem area."""
        return self._bodies

    @protect_grpc
    def fix(self) -> RepairToolMessage:
        """Fix the problem area.

        Returns
        -------
        message: RepairToolMessage
            Message containing created and/or modified bodies.

        Notes
        -----
        The current implementation does not properly track changes.
        The list of created and modified bodies are empty.
        """
        if not self.bodies:
            return RepairToolMessage(False, [], [])

        parent_design = get_design_from_body(self.bodies[0])
        response = self._repair_stub.FixInterference(
            FixInterferenceRequest(interference_problem_area_id=self._grpc_id)
        )
        parent_design._update_design_inplace()
        ## The tool does not return the created or modified objects.
        ## https://github.com/ansys/pyansys-geometry/issues/1319
        message = RepairToolMessage(response.result.success, [], [])

        return message


class LogoProblemArea(ProblemArea):
    """Represents a logo problem area defined by a list of faces.

    Parameters
    ----------
    id : str
        Server-defined ID for the problem area.
    grpc_client : GrpcClient
        Active supporting geometry service instance for design modeling.
    faces : list[str]
        List of faces defining the logo problem area.
    """

    def __init__(self, id: str, grpc_client: GrpcClient, face_ids: list[str]):
        """Initialize a new instance of the logo problem area class."""
        super().__init__(id, grpc_client)

        self._face_ids = face_ids

    @property
    def face_ids(self) -> list[str]:
        """The ids of the faces defining the logos."""
        return self._face_ids

    def fix(self) -> bool:
        """Fix the problem area by deleting the logos.

        Returns
        -------
        message: bool
            Message that return whether the operation was successful.
        """
        if len(self._face_ids) == 0:
            return False

        response = self._grpc_client._services.prepare_tools.remove_logo(face_ids=self._face_ids)

        return response.get("success")
