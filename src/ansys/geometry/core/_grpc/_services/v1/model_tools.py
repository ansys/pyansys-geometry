# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
"""Module containing the model tools service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.model_tools import GRPCModelToolsService
from .conversions import (
    build_grpc_id,
    from_length_to_grpc_quantity,
    serialize_tracked_command_response,
)


class GRPCModelToolsServiceV1(GRPCModelToolsService):
    """Model tools service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    model tools service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2_grpc import EditStub
        from ansys.api.discovery.v1.operations.sketch_pb2_grpc import SketchStub

        self.stub = EditStub(channel)
        self.sketch_stub = SketchStub(channel)

    @protect_grpc
    def chamfer(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import ChamferRequest, ChamferRequestData

        # Create the request - assumes all inputs are valid and of the proper type
        request = ChamferRequest(
            request_data=[
                ChamferRequestData(
                    ids=[build_grpc_id(id) for id in kwargs["selection_ids"]],
                    distance=from_length_to_grpc_quantity(kwargs["distance"]),
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.Chamfer(request).response_data[0]

        # Return the response as a dictionary
        return {
            "success": response.success,
        }

    @protect_grpc
    def fillet(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import FilletRequest, FilletRequestData

        # Create the request - assumes all inputs are valid and of the proper type
        request = FilletRequest(
            request_data=[
                FilletRequestData(
                    ids=[build_grpc_id(id) for id in kwargs["selection_ids"]],
                    radius=from_length_to_grpc_quantity(kwargs["radius"]),
                )
            ]
        )

        # Call the gRPC service and serialize the response
        response = self.stub.Fillet(request)
        tracked_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response as a dictionary
        return {
            "success": tracked_response.get("success"),
        }

    @protect_grpc
    def full_fillet(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import FullFilletRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = FullFilletRequest(
            face_ids=[build_grpc_id(id) for id in kwargs["selection_ids"]],
        )

        # Call the gRPC service and serialize the response
        response = self.stub.FullFillet(request)
        tracked_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response as a dictionary
        return {
            "success": tracked_response.get("success"),
        }

    @protect_grpc
    def move_rotate(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            MoveRotateRequest,
            MoveRotateRequestData,
        )

        from .conversions import from_angle_to_grpc_quantity, from_line_to_grpc_line

        # Create the request - assumes all inputs are valid and of the proper type
        request = MoveRotateRequest(
            request_data=[
                MoveRotateRequestData(
                    selection_ids=[build_grpc_id(kwargs["selection_id"])],
                    axis=from_line_to_grpc_line(kwargs["axis"]),
                    angle=from_angle_to_grpc_quantity(kwargs["angle"]),
                )
            ]
        )

        # Call the gRPC service and serialize the response
        response = self.stub.MoveRotate(request)
        tracked_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response as a dictionary
        return {
            "success": tracked_response.get("success"),
            "modified_bodies": [body.get("id") for body in tracked_response.get("modified_bodies")],
            "modified_faces": [face.get("id") for face in tracked_response.get("modified_faces")],
            "modified_edges": [edge.get("id") for edge in tracked_response.get("modified_edges")],
        }

    @protect_grpc
    def move_translate(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            MoveTranslateRequest,
            MoveTranslateRequestData,
        )

        from .conversions import from_unit_vector_to_grpc_direction

        # Create the request - assumes all inputs are valid and of the proper type
        request = MoveTranslateRequest(
            request_data=[
                MoveTranslateRequestData(
                    selection_ids=[build_grpc_id(kwargs["selection_id"])],
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    distance=from_length_to_grpc_quantity(kwargs["distance"]),
                )
            ]
        )
        # Call the gRPC service and serialize the response
        response = self.stub.MoveTranslate(request)
        tracked_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response as a dictionary
        return {
            "success": tracked_response.get("success"),
        }

    @protect_grpc
    def create_sketch_line(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.sketch_pb2 import (
            CreateSketchLineRequest,
            CreateSketchLineRequestData,
        )

        from .conversions import from_point3d_to_grpc_point

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateSketchLineRequest(
            request_data=[
                CreateSketchLineRequestData(
                    point1=from_point3d_to_grpc_point(kwargs["start"]),
                    point2=from_point3d_to_grpc_point(kwargs["end"]),
                )
            ]
        )

        # Call the gRPC service
        _ = self.sketch_stub.CreateSketchLine(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def detach_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            DetachFacesRequest,
            DetachFacesRequestData,
        )

        selections = kwargs["selections"]
        items_to_detach = sum(len(selection) for selection in selections)

        # Create the request - assumes all inputs are valid and of the proper type
        request = DetachFacesRequest(
            request_data=[
                DetachFacesRequestData(ids=[build_grpc_id(id) for id in selection])
                for selection in selections
            ]
        )

        # Call the gRPC service
        result = self.stub.DetachFaces(request)
        tracked_response = serialize_tracked_command_response(result.tracked_command_response)

        # Return the result - formatted as a dictionary
        return {
            "success": len(result.successfully_set_ids) == items_to_detach,
            "created_bodies": [body.get("id") for body in tracked_response.get("created_bodies")],
            "modified_bodies": [body.get("id") for body in tracked_response.get("modified_bodies")],
            "modified_faces": [face.get("id") for face in tracked_response.get("modified_faces")],
            "tracked_response": tracked_response,
        }
