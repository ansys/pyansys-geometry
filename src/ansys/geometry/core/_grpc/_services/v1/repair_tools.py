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
"""Module containing the repair tools service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.repair_tools import GRPCRepairToolsService
from .conversions import (
    build_grpc_id,
    from_angle_to_grpc_quantity,
    from_area_to_grpc_quantity,
    from_length_to_grpc_quantity,
    response_problem_area_for_body,
    response_problem_area_for_edge,
    response_problem_area_for_face,
    serialize_repair_command_response,
)


class GRPCRepairToolsServiceV1(GRPCRepairToolsService):  # noqa: D102
    """Repair tools service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    Repair Tools service. It is specifically designed for the v1 version
    of the Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):
        from ansys.api.discovery.v1.operations.repair_pb2_grpc import RepairStub

        self.stub = RepairStub(channel)

    @protect_grpc
    def find_split_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindSplitEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindSplitEdgesRequest(
            body_or_face_ids=[build_grpc_id(item) for item in kwargs["bodies_or_faces"]],
            angle=from_angle_to_grpc_quantity(kwargs["angle"])
            if kwargs["angle"] is not None
            else None,
            distance=from_length_to_grpc_quantity(kwargs["distance"])
            if kwargs["distance"] is not None
            else None,
        )

        # Call the gRPC service
        response = self.stub.FindSplitEdges(request)

        # Format and return the response as a dictionary
        return response_problem_area_for_edge(response)

    @protect_grpc
    def find_extra_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindExtraEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindExtraEdgesRequest(
            selection_id=[build_grpc_id(item) for item in kwargs["selection"]]
        )

        # Return the response - formatted as a dictionary
        response = self.stub.FindExtraEdges(request)

        # Return the response - formatted as a dictionary
        return response_problem_area_for_edge(response)

    @protect_grpc
    def find_inexact_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindInexactEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindInexactEdgesRequest(
            selection_id=[build_grpc_id(item) for item in kwargs["selection"]]
        )

        # Call the gRPC service
        response = self.stub.FindInexactEdges(request)

        # Return the response - formatted as a dictionary
        return response_problem_area_for_edge(response)

    @protect_grpc
    def find_short_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindShortEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindShortEdgesRequest(
            selection_id=[build_grpc_id(item) for item in kwargs["selection"]],
            max_edge_length=from_length_to_grpc_quantity(kwargs["length"]),
        )

        # Call the gRPC service
        response = self.stub.FindShortEdges(request)

        return response_problem_area_for_edge(response)

    @protect_grpc
    def find_duplicate_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindDuplicateFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindDuplicateFacesRequest(
            face_ids=[build_grpc_id(face) for face in kwargs["faces"]]
        )

        # Call the gRPC service
        response = self.stub.FindDuplicateFaces(request)

        # Return the response - formatted as a dictionary
        return response_problem_area_for_face(response)

    @protect_grpc
    def find_missing_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindMissingFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindMissingFacesRequest(
            face_ids=[build_grpc_id(face) for face in kwargs["faces"]],
            angle=from_angle_to_grpc_quantity(kwargs["angle"])
            if kwargs["angle"] is not None
            else None,
            distance=from_length_to_grpc_quantity(kwargs["distance"])
            if kwargs["distance"] is not None
            else None,
        )

        # Call the gRPC service
        response = self.stub.FindMissingFaces(request)

        # Return the response - formatted as a dictionary
        return response_problem_area_for_face(response)

    @protect_grpc
    def find_small_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindSmallFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindSmallFacesRequest(
            selection_id=[build_grpc_id(item) for item in kwargs["selection"]],
            area=from_area_to_grpc_quantity(kwargs["area"]) if kwargs["area"] is not None else None,
            width=from_length_to_grpc_quantity(kwargs["width"])
            if kwargs["width"] is not None
            else None,
        )

        # Call the gRPC service
        response = self.stub.FindSmallFaces(request)

        # Return the response - formatted as a dictionary
        return response_problem_area_for_edge(response)

    @protect_grpc
    def find_stitch_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindStitchFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindStitchFacesRequest(
            face_ids=[build_grpc_id(face) for face in kwargs["faces"]],
            maximum_distance=from_length_to_grpc_quantity(kwargs["distance"])
            if kwargs["distance"] is not None
            else None,
        )

        # Call the gRPC service
        response = self.stub.FindStitchFaces(request)

        # Return the response - formatted as a dictionary
        return response_problem_area_for_body(response)

    @protect_grpc
    def find_simplify(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindAdjustSimplifyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindAdjustSimplifyRequest(
            selection_id=[build_grpc_id(item) for item in kwargs["selection"]]
        )

        # Call the gRPC service
        response = self.stub.FindAdjustSimplify(request)

        # Return the response - formatted as a dictionary
        return response_problem_area_for_body(response)

    @protect_grpc
    def find_interferences(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindInterferenceRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindInterferenceRequest(
            body_ids=[build_grpc_id(body) for body in kwargs["bodies"]],
            cut_smaller_body=kwargs["cut_smaller_body"],
        )

        # Call the gRPC service
        response = self.stub.FindInterference(request)

        # Return the response - formatted as a dictionary
        return response_problem_area_for_body(response)

    @protect_grpc
    def find_and_fix_short_edges(self, **kwargs):  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindShortEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindShortEdgesRequest(
            selection_id=[build_grpc_id(item) for item in kwargs["selection"]],
            max_edge_length=from_length_to_grpc_quantity(kwargs["length"]),
            comprehensive=kwargs["comprehensive_result"],
        )

        # Call the gRPC service
        response = self.stub.FindAndFixShortEdges(request)

        return serialize_repair_command_response(response.response_data)

    @protect_grpc
    def find_and_fix_extra_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindExtraEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindExtraEdgesRequest(
            selection_id=[build_grpc_id(item) for item in kwargs["selection"]],
            comprehensive=kwargs["comprehensive_result"],
        )

        # Call the gRPC service
        response = self.stub.FindAndFixExtraEdges(request)

        return serialize_repair_command_response(response.response_data)

    @protect_grpc
    def find_and_fix_split_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindSplitEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindSplitEdgesRequest(
            body_or_face_ids=[build_grpc_id(item) for item in kwargs["bodies_or_faces"]],
            distance=from_length_to_grpc_quantity(kwargs["length"]),
            comprehensive=kwargs["comprehensive_result"],
        )

        # Call the gRPC service
        response = self.stub.FindAndFixSplitEdges(request)

        return serialize_repair_command_response(response.response_data)

    @protect_grpc
    def find_and_fix_simplify(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindAdjustSimplifyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindAdjustSimplifyRequest(
            selection_id=[build_grpc_id(item) for item in kwargs["selection"]],
            comprehensive=kwargs["comprehensive_result"],
        )

        # Call the gRPC service
        response = self.stub.FindAndSimplify(request)

        return serialize_repair_command_response(response.response_data)

    @protect_grpc
    def find_and_fix_stitch_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FindStitchFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindStitchFacesRequest(
            face_ids=[build_grpc_id(item) for item in kwargs["body_ids"]],
            maximum_distance=from_length_to_grpc_quantity(kwargs["max_distance"])
            if kwargs["max_distance"] is not None
            else None,
            allow_multiple_bodies=kwargs["allow_multiple_bodies"],
            maintain_components=kwargs["maintain_components"],
            check_for_coincidence=kwargs["check_for_coincidence"],
            comprehensive=kwargs["comprehensive_result"],
        )

        # Call the gRPC service
        response = self.stub.FindAndFixStitchFaces(request)

        return serialize_repair_command_response(response.response_data)

    @protect_grpc
    def inspect_geometry(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import InspectGeometryRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = InspectGeometryRequest(
            body_ids=[build_grpc_id(body) for body in kwargs.get("body_ids", [])]
        )

        # Call the gRPC service
        response = self.stub.InspectGeometry(request)

        # Serialize and return the response
        return self.__serialize_inspect_result_response(response)

    @protect_grpc
    def repair_geometry(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import RepairGeometryRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = RepairGeometryRequest(
            body_ids=[build_grpc_id(body) for body in kwargs.get("bodies")]
        )

        # Call the gRPC service
        response = self.stub.RepairGeometry(request)

        # Return the response - formatted as a dictionary
        return serialize_repair_command_response(response)

    @protect_grpc
    def fix_duplicate_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FixDuplicateFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixDuplicateFacesRequest(
            duplicate_face_problem_area_id=int(kwargs["duplicate_face_problem_area_id"]),
        )

        # Call the gRPC service
        response = self.stub.FixDuplicateFaces(request)

        # Return the response - formatted as a dictionary
        return serialize_repair_command_response(response.result)

    @protect_grpc
    def fix_missing_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FixMissingFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixMissingFacesRequest(
            missing_face_problem_area_id=int(kwargs["missing_face_problem_area_id"]),
        )

        # Call the gRPC service
        response = self.stub.FixMissingFaces(request)

        # Return the response - formatted as a dictionary
        return serialize_repair_command_response(response.result)

    @protect_grpc
    def fix_inexact_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FixInexactEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixInexactEdgesRequest(
            inexact_edge_problem_area_id=int(kwargs["inexact_edge_problem_area_id"]),
        )

        # Call the gRPC service
        response = self.stub.FixInexactEdges(request)

        # Return the response - formatted as a dictionary
        return serialize_repair_command_response(response.result)

    @protect_grpc
    def fix_extra_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FixExtraEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixExtraEdgesRequest(
            extra_edge_problem_area_id=int(kwargs["extra_edge_problem_area_id"]),
        )

        # Call the gRPC service
        response = self.stub.FixExtraEdges(request)

        # Return the response - formatted as a dictionary
        return serialize_repair_command_response(response.result)

    @protect_grpc
    def fix_short_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FixShortEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixShortEdgesRequest(
            short_edge_problem_area_id=int(kwargs["short_edge_problem_area_id"]),
        )

        # Call the gRPC service
        response = self.stub.FixShortEdges(request)

        # Return the response - formatted as a dictionary
        return serialize_repair_command_response(response.result)

    @protect_grpc
    def fix_small_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FixSmallFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixSmallFacesRequest(
            small_face_problem_area_id=int(kwargs["small_face_problem_area_id"]),
        )

        # Call the gRPC service
        response = self.stub.FixSmallFaces(request)

        # Return the response - formatted as a dictionary
        return serialize_repair_command_response(response.result)

    @protect_grpc
    def fix_split_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FixSplitEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixSplitEdgesRequest(
            split_edge_problem_area_id=int(kwargs["split_edge_problem_area_id"]),
        )

        # Call the gRPC service
        response = self.stub.FixSplitEdges(request)

        # Return the response - formatted as a dictionary
        return serialize_repair_command_response(response.result)

    @protect_grpc
    def fix_stitch_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FixStitchFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixStitchFacesRequest(
            stitch_face_problem_area_id=int(kwargs["stitch_face_problem_area_id"]),
        )

        # Call the gRPC service
        response = self.stub.FixStitchFaces(request)

        # Return the response - formatted as a dictionary
        return serialize_repair_command_response(response.result)

    @protect_grpc
    def fix_unsimplified_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FixAdjustSimplifyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixAdjustSimplifyRequest(
            adjust_simplify_problem_area_id=int(kwargs["adjust_simplify_problem_area_id"]),
        )

        # Call the gRPC service
        response = self.stub.FixAdjustSimplify(request)

        # Return the response - formatted as a dictionary
        return serialize_repair_command_response(response)

    @protect_grpc
    def fix_interference(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.repair_pb2 import FixInterferenceRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixInterferenceRequest(
            interference_problem_area_id=int(kwargs["interference_problem_area_id"]),
        )

        # Call the gRPC service
        response = self.stub.FixInterference(request)

        # Return the response - formatted as a dictionary
        return serialize_repair_command_response(response.result)

    def __serialize_inspect_result_response(self, response) -> dict:  # noqa: D102
        def serialize_body(body):
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

        def serialize_face(face):
            return {
                "id": face.id,
                "surface_type": face.surface_type,
                "export_id": face.export_id,
                "is_reversed": getattr(face, "is_reversed", False),
                "parent_id": face.parent_id.id,
            }

        def serialize_edge(edge):
            return {
                "id": edge.id,
                "curve_type": edge.curve_type,
                "export_id": edge.export_id,
                "length": edge.length,
                "owner_id": edge.owner_id,
                "parent": serialize_body(edge.parent) if hasattr(edge, "parent") else None,
            }

        def serialize_issue(issue):
            return {
                "message_type": issue.message_type,
                "message_id": issue.message_id,
                "message": issue.message,
                "faces": [serialize_face(f) for f in issue.faces],
                "edges": [serialize_edge(e) for e in issue.edges],
            }

        return {
            "issues_by_body": [
                {
                    "body": serialize_body(body_issues.body),
                    "issues": [serialize_issue(i) for i in body_issues.issues],
                }
                for body_issues in response.issues_by_body
            ]
        }
