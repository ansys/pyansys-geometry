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
"""Module containing the Prepare Tools service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.conversions import from_measurement_to_server_length
from ..base.prepare_tools import GRPCPrepareToolsService
from .conversions import build_grpc_id, serialize_tracker_command_response


class GRPCPrepareToolsServiceV0(GRPCPrepareToolsService):
    """Prepare tools service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    Prepare Tools service. It is specifically designed for the v0 version
    of the Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v0.preparetools_pb2_grpc import PrepareToolsStub

        self.stub = PrepareToolsStub(channel)

    @protect_grpc
    def extract_volume_from_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.preparetools_pb2 import ExtractVolumeFromFacesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ExtractVolumeFromFacesRequest(
            sealing_faces=[build_grpc_id(face) for face in kwargs["sealing_faces"]],
            inside_faces=[build_grpc_id(face) for face in kwargs["inside_faces"]],
        )

        # Call the gRPC service
        response = self.stub.ExtractVolumeFromFaces(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "created_bodies": [body.id for body in response.created_bodies],
            "tracker_response": response.changes,
        }

    @protect_grpc
    def extract_volume_from_edge_loops(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.preparetools_pb2 import ExtractVolumeFromEdgeLoopsRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ExtractVolumeFromEdgeLoopsRequest(
            sealing_edges=[build_grpc_id(edge) for edge in kwargs["sealing_edges"]],
            inside_faces=[build_grpc_id(face) for face in kwargs["inside_faces"]],
        )

        # Call the gRPC service
        response = self.stub.ExtractVolumeFromEdgeLoops(request)

        serialized_tracker_response = serialize_tracker_command_response(
            response=response.complete_command_response
        )

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "created_bodies": [body.id for body in response.created_bodies],
            "complete_command_response": serialized_tracker_response,

        }

    @protect_grpc
    def remove_rounds(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.models_pb2 import Face
        from ansys.api.geometry.v0.preparetools_pb2 import RemoveRoundsRequest
        from google.protobuf.wrappers_pb2 import BoolValue

        # Create the request - assumes all inputs are valid and of the proper type
        request = RemoveRoundsRequest(
            selection=[Face(id=round) for round in kwargs["rounds"]],
            auto_shrink=BoolValue(value=kwargs["auto_shrink"]),
        )

        # Call the gRPC service
        response = self.stub.RemoveRounds(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.result,
        }

    @protect_grpc
    def share_topology(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.models_pb2 import Body
        from ansys.api.geometry.v0.preparetools_pb2 import ShareTopologyRequest
        from google.protobuf.wrappers_pb2 import BoolValue, DoubleValue

        # Create the request - assumes all inputs are valid and of the proper type
        request = ShareTopologyRequest(
            selection=[Body(id=body) for body in kwargs["bodies"]],
            tolerance=DoubleValue(value=from_measurement_to_server_length(kwargs["tolerance"])),
            preserve_instances=BoolValue(value=kwargs["preserve_instances"]),
        )

        # Call the gRPC service
        response = self.stub.ShareTopology(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.result,
        }

    @protect_grpc
    def enhanced_share_topology(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.models_pb2 import Body
        from ansys.api.geometry.v0.preparetools_pb2 import ShareTopologyRequest
        from google.protobuf.wrappers_pb2 import BoolValue, DoubleValue

        # Create the request - assumes all inputs are valid and of the proper type
        request = ShareTopologyRequest(
            selection=[Body(id=body) for body in kwargs["bodies"]],
            tolerance=DoubleValue(value=from_measurement_to_server_length(kwargs["tolerance"])),
            preserve_instances=BoolValue(value=kwargs["preserve_instances"]),
        )

        # Call the gRPC service
        response = self.stub.EnhancedShareTopology(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.success,
            "found": response.found,
            "repaired": response.repaired,
            "created_bodies_monikers": response.created_bodies_monikers,
            "modified_bodies_monikers": response.modified_bodies_monikers,
            "deleted_bodies_monikers": response.deleted_bodies_monikers,
        }

    @protect_grpc
    def find_logos(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.models_pb2 import FindLogoOptions
        from ansys.api.geometry.v0.preparetools_pb2 import FindLogosRequest

        # Check height objects
        min_height = (
            from_measurement_to_server_length(kwargs["min_height"])
            if kwargs["min_height"] is not None
            else None
        )
        max_height = (
            from_measurement_to_server_length(kwargs["max_height"])
            if kwargs["max_height"] is not None
            else None
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindLogosRequest(
            bodies=[build_grpc_id(body) for body in kwargs["bodies"]],
            options=FindLogoOptions(
                min_height=min_height,
                max_height=max_height,
            ),
        )

        # Call the gRPC service
        response = self.stub.FindLogos(request)

        # Return the response - formatted as a dictionary
        return {
            "id": response.id,
            "face_ids": [face.id for face in response.logo_faces],
        }

    @protect_grpc
    def find_and_remove_logos(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.models_pb2 import FindLogoOptions
        from ansys.api.geometry.v0.preparetools_pb2 import FindLogosRequest

        # Check height objects
        min_height = (
            from_measurement_to_server_length(kwargs["min_height"])
            if kwargs["min_height"] is not None
            else None
        )
        max_height = (
            from_measurement_to_server_length(kwargs["max_height"])
            if kwargs["max_height"] is not None
            else None
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = FindLogosRequest(
            bodies=[build_grpc_id(body) for body in kwargs["bodies"]],
            options=FindLogoOptions(
                min_height=min_height,
                max_height=max_height,
            ),
        )

        # Call the gRPC service
        response = self.stub.FindAndRemoveLogos(request)

        # Return the response - formatted as a dictionary
        return {"success": response.success}

    @protect_grpc
    def remove_logo(self, **kwargs):  # noqa: D102
        from ansys.api.geometry.v0.preparetools_pb2 import RemoveLogoRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = RemoveLogoRequest(
            face_ids=[build_grpc_id(id) for id in kwargs["face_ids"]],
        )

        # Call the gRPC service
        response = self.stub.RemoveLogo(request)

        # Return the response - formatted as a dictionary
        return {"success": response.success}

    @protect_grpc
    def detect_helixes(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.models_pb2 import DetectHelixesOptions
        from ansys.api.geometry.v0.preparetools_pb2 import DetectHelixesRequest

        from ansys.geometry.core.shapes.parameterization import Interval

        from ..base.conversions import (
            from_measurement_to_server_length,
            to_distance,
        )
        from .conversions import (
            from_grpc_curve_to_curve,
            from_grpc_point_to_point3d,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = DetectHelixesRequest(
            body_ids=[build_grpc_id(body) for body in kwargs["bodies"]],
            options=DetectHelixesOptions(
                min_radius=from_measurement_to_server_length(kwargs["min_radius"]),
                max_radius=from_measurement_to_server_length(kwargs["max_radius"]),
                fit_radius_error=from_measurement_to_server_length(kwargs["fit_radius_error"]),
            ),
        )

        # Call the gRPC service
        response = self.stub.DetectHelixes(request)

        # If no helixes, return empty dictionary
        if len(response.helixes) == 0:
            return {"helixes": []}

        # Return the response - formatted as a dictionary
        return {
            "helixes": [
                {
                    "trimmed_curve": {
                        "geometry": from_grpc_curve_to_curve(helix.trimmed_curve.curve),
                        "start": from_grpc_point_to_point3d(helix.trimmed_curve.start),
                        "end": from_grpc_point_to_point3d(helix.trimmed_curve.end),
                        "interval": Interval(
                            helix.trimmed_curve.interval_start, helix.trimmed_curve.interval_end
                        ),
                        "length": to_distance(helix.trimmed_curve.length).value,
                    },
                    "edges": [
                        {
                            "id": edge.id,
                            "parent_id": edge.parent.id,
                            "curve_type": edge.curve_type,
                            "is_reversed": edge.is_reversed,
                        }
                        for edge in helix.edges
                    ],
                }
                for helix in response.helixes
            ]
        }
