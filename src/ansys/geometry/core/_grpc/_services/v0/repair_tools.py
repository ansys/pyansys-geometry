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
"""Module containing the repair tools service implementation for v0."""

from google.protobuf.wrappers_pb2 import Int32Value
import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.conversions import from_measurement_to_server_angle, from_measurement_to_server_length
from ..base.repair_tools import GRPCRepairToolsService
from .conversions import (
    serialize_tracker_command_response,
)


class GRPCRepairToolsServiceV0(GRPCRepairToolsService):  # noqa: D102
    """Repair tools service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    Repair Tools service. It is specifically designed for the v0 version
    of the Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):
        from ansys.api.geometry.v0.repairtools_pb2_grpc import RepairToolsStub

        self.stub = RepairToolsStub(channel)

    @protect_grpc
    def find_split_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindSplitEdgesRequest
        from google.protobuf.wrappers_pb2 import DoubleValue

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindSplitEdgesRequest(
            bodies_or_faces=kwargs["bodies_or_faces"],
            angle=(
                DoubleValue(value=float(from_measurement_to_server_angle(kwargs["angle"])))
                if kwargs["angle"] is not None
                else None
            ),
            distance=(
                DoubleValue(value=float(from_measurement_to_server_length(kwargs["distance"])))
                if kwargs["distance"] is not None
                else None
            ),
        )

        # Call the gRPC service
        response = self.stub.FindSplitEdges(request)

        # Format and return the response as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "edges": res.edge_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_extra_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindExtraEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindExtraEdgesRequest(selection=kwargs["selection"])

        # Return the response - formatted as a dictionary
        response = self.stub.FindExtraEdges(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "edges": res.edge_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_inexact_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindInexactEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindInexactEdgesRequest(selection=kwargs["selection"])

        # Call the gRPC service
        response = self.stub.FindInexactEdges(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "edges": res.edge_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_short_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindShortEdgesRequest
        from google.protobuf.wrappers_pb2 import DoubleValue

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindShortEdgesRequest(
            selection=kwargs["selection"],
            max_edge_length=DoubleValue(value=from_measurement_to_server_length(kwargs["length"])),
        )

        # Call the gRPC service
        response = self.stub.FindShortEdges(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "edges": res.edge_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_duplicate_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindDuplicateFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindDuplicateFacesRequest(faces=kwargs["faces"])

        # Call the gRPC service
        response = self.stub.FindDuplicateFaces(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "faces": res.face_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_missing_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindMissingFacesRequest
        from google.protobuf.wrappers_pb2 import DoubleValue

        from ..base.conversions import (
            from_measurement_to_server_angle,
            from_measurement_to_server_length,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindMissingFacesRequest(
            faces=kwargs["faces"],
            angle=DoubleValue(value=from_measurement_to_server_angle(kwargs["angle"]))
            if kwargs["angle"] is not None
            else None,
            distance=DoubleValue(value=from_measurement_to_server_length(kwargs["distance"]))
            if kwargs["distance"] is not None
            else None,
        )

        # Call the gRPC service
        response = self.stub.FindMissingFaces(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "edges": res.edge_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_small_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindSmallFacesRequest
        from google.protobuf.wrappers_pb2 import DoubleValue

        from ..base.conversions import (
            from_measurement_to_server_area,
            from_measurement_to_server_length,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindSmallFacesRequest(
            selection=kwargs["selection"],
            area=DoubleValue(value=from_measurement_to_server_area(kwargs["area"]))
            if kwargs["area"] is not None
            else None,
            width=DoubleValue(value=from_measurement_to_server_length(kwargs["width"]))
            if kwargs["width"] is not None
            else None,
        )

        # Call the gRPC service
        response = self.stub.FindSmallFaces(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "faces": res.face_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_stitch_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindStitchFacesRequest
        from google.protobuf.wrappers_pb2 import DoubleValue

        from ..base.conversions import from_measurement_to_server_length

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindStitchFacesRequest(
            faces=kwargs["faces"],
            maximum_distance=DoubleValue(
                value=from_measurement_to_server_length(kwargs["distance"])
            )
            if kwargs["distance"] is not None
            else None,
        )

        # Call the gRPC service
        response = self.stub.FindStitchFaces(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "bodies": res.body_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_simplify(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindAdjustSimplifyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindAdjustSimplifyRequest(selection=kwargs["selection"])

        # Call the gRPC service
        response = self.stub.FindAdjustSimplify(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "bodies": res.body_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_interferences(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindInterferenceRequest
        from google.protobuf.wrappers_pb2 import BoolValue

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindInterferenceRequest(
            bodies=kwargs["bodies"],
            cut_smaller_body=BoolValue(value=kwargs["cut_smaller_body"]),
        )

        # Call the gRPC service
        response = self.stub.FindInterference(request)

        # Return the response - formatted as a dictionary
        return {
            "problems": [
                {
                    "id": res.id,
                    "bodies": res.body_monikers,
                }
                for res in response.result
            ]
        }

    @protect_grpc
    def find_and_fix_short_edges(self, **kwargs):  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindShortEdgesRequest
        from google.protobuf.wrappers_pb2 import DoubleValue

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindShortEdgesRequest(
            selection=kwargs["selection"],
            max_edge_length=DoubleValue(value=from_measurement_to_server_length(kwargs["length"])),
            comprehensive=kwargs["comprehensive_result"],
        )

        # Call the gRPC service
        response = self.stub.FindAndFixShortEdges(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "found": response.found,
            "repaired": response.repaired,
            "created_bodies_monikers": [],
            "modified_bodies_monikers": [],
            "tracker_response": serialized_tracker_response,
        }

    @protect_grpc
    def find_and_fix_extra_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindExtraEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindExtraEdgesRequest(
            selection=kwargs["selection"],
            comprehensive=kwargs["comprehensive_result"],
        )

        # Call the gRPC service
        response = self.stub.FindAndFixExtraEdges(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "found": response.found,
            "repaired": response.repaired,
            "created_bodies_monikers": response.created_bodies_monikers,
            "modified_bodies_monikers": response.modified_bodies_monikers,
            "tracker_response": serialized_tracker_response,
        }

    @protect_grpc
    def find_and_fix_split_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindSplitEdgesRequest
        from google.protobuf.wrappers_pb2 import DoubleValue

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindSplitEdgesRequest(
            bodies_or_faces=kwargs["bodies_or_faces"],
            distance=DoubleValue(value=float(from_measurement_to_server_length(kwargs["length"]))),
            comprehensive=kwargs["comprehensive_result"],
        )

        # Call the gRPC service
        response = self.stub.FindAndFixSplitEdges(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "found": response.found,
            "repaired": response.repaired,
            "created_bodies_monikers": [],
            "modified_bodies_monikers": [],
            "tracker_response": serialized_tracker_response,
        }

    @protect_grpc
    def find_and_fix_simplify(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindAdjustSimplifyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindAdjustSimplifyRequest(
            selection=kwargs["selection"],
            comprehensive=kwargs["comprehensive_result"],
        )

        # Call the gRPC service
        response = self.stub.FindAndSimplify(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "found": response.found,
            "repaired": response.repaired,
            "created_bodies_monikers": [],
            "modified_bodies_monikers": [],
            "tracker_response": serialized_tracker_response,
        }

    @protect_grpc
    def find_and_fix_stitch_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FindStitchFacesRequest
        from google.protobuf.wrappers_pb2 import BoolValue, DoubleValue

        from ..base.conversions import from_measurement_to_server_length

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindStitchFacesRequest(
            faces=kwargs["body_ids"],
            maximum_distance=DoubleValue(
                value=from_measurement_to_server_length(kwargs["max_distance"])
            )
            if kwargs["max_distance"] is not None
            else None,
            allow_multiple_bodies=BoolValue(value=kwargs["allow_multiple_bodies"]),
            maintain_components=BoolValue(value=kwargs["maintain_components"]),
            check_for_coincidence=BoolValue(value=kwargs["check_for_coincidence"]),
            comprehensive=kwargs["comprehensive_result"],
        )

        # Call the gRPC service
        response = self.stub.FindAndFixStitchFaces(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "created_bodies_monikers": response.created_bodies_monikers,
            "modified_bodies_monikers": response.modified_bodies_monikers,
            "found": response.found,
            "repaired": response.repaired,
            "tracker_response": serialized_tracker_response,
        }

    @protect_grpc
    def inspect_geometry(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import InspectGeometryRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = InspectGeometryRequest(bodies=kwargs.get("bodies", []))

        # Call the gRPC service
        inspect_result_response = self.stub.InspectGeometry(request)

        # Serialize and return the response
        return self.__serialize_inspect_result_response(inspect_result_response)

    @protect_grpc
    def repair_geometry(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import RepairGeometryRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = RepairGeometryRequest(bodies=kwargs.get("bodies", []))

        # Call the gRPC service
        response = self.stub.RepairGeometry(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.result.success,
        }

    @protect_grpc
    def fix_duplicate_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FixDuplicateFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixDuplicateFacesRequest(
            duplicate_face_problem_area_id=Int32Value(
                value=int(kwargs["duplicate_face_problem_area_id"])
            ),
        )

        # Call the gRPC service
        response = self.stub.FixDuplicateFaces(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.result.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "tracker_response": serialized_tracker_response,
            "success": response.result.success,
            "created_bodies_monikers": response.result.created_bodies_monikers,
            "modified_bodies_monikers": response.result.modified_bodies_monikers,
        }

    @protect_grpc
    def fix_missing_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FixMissingFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixMissingFacesRequest(
            missing_face_problem_area_id=Int32Value(
                value=int(kwargs["missing_face_problem_area_id"])
            ),
        )

        # Call the gRPC service
        response = self.stub.FixMissingFaces(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.result.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "tracker_response": serialized_tracker_response,
            "success": response.result.success,
            "created_bodies_monikers": response.result.created_bodies_monikers,
            "modified_bodies_monikers": response.result.modified_bodies_monikers,
        }

    @protect_grpc
    def fix_inexact_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FixInexactEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixInexactEdgesRequest(
            inexact_edge_problem_area_id=Int32Value(
                value=int(kwargs["inexact_edge_problem_area_id"])
            ),
        )

        # Call the gRPC service
        response = self.stub.FixInexactEdges(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.result.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "tracker_response": serialized_tracker_response,
            "success": response.result.success,
            "created_bodies_monikers": response.result.created_bodies_monikers,
            "modified_bodies_monikers": response.result.modified_bodies_monikers,
        }

    @protect_grpc
    def fix_extra_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FixExtraEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixExtraEdgesRequest(
            extra_edge_problem_area_id=Int32Value(value=int(kwargs["extra_edge_problem_area_id"])),
        )

        # Call the gRPC service
        response = self.stub.FixExtraEdges(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.result.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "tracker_response": serialized_tracker_response,
            "success": response.result.success,
            "created_bodies_monikers": response.result.created_bodies_monikers,
            "modified_bodies_monikers": response.result.modified_bodies_monikers,
        }

    @protect_grpc
    def fix_short_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FixShortEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixShortEdgesRequest(
            short_edge_problem_area_id=Int32Value(value=int(kwargs["short_edge_problem_area_id"])),
        )

        # Call the gRPC service
        response = self.stub.FixShortEdges(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.result.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "tracker_response": serialized_tracker_response,
            "success": response.result.success,
            "created_bodies_monikers": response.result.created_bodies_monikers,
            "modified_bodies_monikers": response.result.modified_bodies_monikers,
        }

    @protect_grpc
    def fix_small_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FixSmallFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixSmallFacesRequest(
            small_face_problem_area_id=Int32Value(value=int(kwargs["small_face_problem_area_id"])),
        )

        # Call the gRPC service
        response = self.stub.FixSmallFaces(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.result.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "tracker_response": serialized_tracker_response,
            "success": response.result.success,
            "created_bodies_monikers": response.result.created_bodies_monikers,
            "modified_bodies_monikers": response.result.modified_bodies_monikers,
        }

    @protect_grpc
    def fix_split_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FixSplitEdgesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixSplitEdgesRequest(
            split_edge_problem_area_id=Int32Value(value=int(kwargs["split_edge_problem_area_id"])),
        )

        # Call the gRPC service
        response = self.stub.FixSplitEdges(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.result.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "tracker_response": serialized_tracker_response,
            "success": response.result.success,
            "created_bodies_monikers": response.result.created_bodies_monikers,
            "modified_bodies_monikers": response.result.modified_bodies_monikers,
        }

    @protect_grpc
    def fix_stitch_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FixStitchFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixStitchFacesRequest(
            stitch_face_problem_area_id=Int32Value(
                value=int(kwargs["stitch_face_problem_area_id"])
            ),
        )

        # Call the gRPC service
        response = self.stub.FixStitchFaces(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.result.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "tracker_response": serialized_tracker_response,
            "success": response.result.success,
            "created_bodies_monikers": response.result.created_bodies_monikers,
            "modified_bodies_monikers": response.result.modified_bodies_monikers,
        }

    @protect_grpc
    def fix_unsimplified_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FixAdjustSimplifyRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixAdjustSimplifyRequest(
            adjust_simplify_problem_area_id=Int32Value(
                value=int(kwargs["adjust_simplify_problem_area_id"])
            ),
        )

        # Call the gRPC service
        response = self.stub.FixAdjustSimplify(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.result.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "tracker_response": serialized_tracker_response,
            "success": response.result.success,
            "created_bodies_monikers": response.result.created_bodies_monikers,
            "modified_bodies_monikers": response.result.modified_bodies_monikers,
        }

    @protect_grpc
    def fix_interference(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.repairtools_pb2 import FixInterferenceRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FixInterferenceRequest(
            interference_problem_area_id=Int32Value(
                value=int(kwargs["interference_problem_area_id"])
            ),
        )

        # Call the gRPC service
        response = self.stub.FixInterference(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.result.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "tracker_response": serialized_tracker_response,
            "success": response.result.success,
            "created_bodies_monikers": response.result.created_bodies_monikers,
            "modified_bodies_monikers": response.result.modified_bodies_monikers,
        }

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
