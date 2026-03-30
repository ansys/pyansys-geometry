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
"""Module containing the points service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.points import GRPCPointsService
from .conversions import (
    build_grpc_id,
    from_angle_to_grpc_quantity,
    from_grpc_point_to_point3d,
    from_grpc_quantity_to_distance,
    from_length_to_grpc_quantity,
    from_line_to_grpc_line,
    from_point3d_to_grpc_design_point,
    serialize_tracked_command_response,
)


class GRPCPointsServiceV1(GRPCPointsService):
    """Points service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    points service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.constructs.datumpoint_pb2_grpc import DatumPointStub
        from ansys.api.discovery.v1.operations.edit_pb2_grpc import EditStub

        self.stub = DatumPointStub(channel)
        self.edit_stub = EditStub(channel)

    @protect_grpc
    def create_design_points(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.constructs.datumpoint_pb2 import (
            DatumPointCreationRequest,
            DatumPointCreationRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = DatumPointCreationRequest(
            request_data=[
                DatumPointCreationRequestData(
                    points=[from_point3d_to_grpc_design_point(point) for point in kwargs["points"]],
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.Create(request)

        # Return the response - formatted as a dictionary
        return {"point_ids": [p.id for p in response.ids]}

    @protect_grpc
    def revolve_points(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            RevolveDatumPointRequest,
            RevolveDatumPointRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = RevolveDatumPointRequest(
            request_data=[
                RevolveDatumPointRequestData(
                    selection_ids=[build_grpc_id(id) for id in kwargs["selection_ids"]],
                    axis=from_line_to_grpc_line(kwargs["axis"]),
                    angle=from_angle_to_grpc_quantity(kwargs["angle"]),
                )
            ]
        )

        # Call the gRPC service
        response = self.edit_stub.RevolveDatumPoint(request)
        serialized_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_command_response.command_response.success,
            "created_curves": [
                {
                    "id": curve.id.id,
                    "name": curve.owner_name,
                    "length": from_grpc_quantity_to_distance(curve.length),
                    "start_point": from_grpc_point_to_point3d(curve.points[0]),
                    "end_point": from_grpc_point_to_point3d(curve.points[1])
                    if len(curve.points) > 1
                    else None,
                    "parent_id": curve.parent_id.id,
                }
                for curve in response.response_data[0].created_curves
            ],
            "tracked_response": serialized_response,
        }

    @protect_grpc
    def revolve_points_by_helix(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            RevolveDatumPointByHelixRequest,
            RevolveDatumPointByHelixRequestData,
        )

        # Create the request - one request_data item per point so the server
        # creates one helix curve per point.
        request = RevolveDatumPointByHelixRequest(
            request_data=[
                RevolveDatumPointByHelixRequestData(
                    selection_ids=[build_grpc_id(id)],
                    axis=from_line_to_grpc_line(kwargs["axis"]),
                    height=from_length_to_grpc_quantity(kwargs["height"]),
                    pitch=from_length_to_grpc_quantity(kwargs["pitch"]),
                    taper_angle=from_angle_to_grpc_quantity(kwargs["taper_angle"]),
                    right_handed=kwargs["right_handed"],
                    pull_symmetric=kwargs["pull_symmetric"],
                )
                for id in kwargs["selection_ids"]
            ]
        )

        # Call the gRPC service
        response = self.edit_stub.RevolveDatumPointByHelix(request)
        serialized_response = serialize_tracked_command_response(response.tracked_command_response)

        # Collect created curves from all response_data items (one per point).
        created_curves = [
            {
                "id": curve.id.id,
                "name": curve.owner_name,
                "length": from_grpc_quantity_to_distance(curve.length),
                "start_point": from_grpc_point_to_point3d(curve.points[0]),
                "end_point": from_grpc_point_to_point3d(curve.points[1])
                if len(curve.points) > 1
                else None,
                "parent_id": curve.parent_id.id,
            }
            for rd in response.response_data
            for curve in rd.created_curves
        ]

        return {
            "success": response.tracked_command_response.command_response.success,
            "created_curves": created_curves,
            "tracked_response": serialized_response,
        }

    @protect_grpc
    def sweep_points(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            SweepDatumPointRequest,
            SweepDatumPointRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = SweepDatumPointRequest(
            request_data=[
                SweepDatumPointRequestData(
                    selection_ids=[build_grpc_id(id) for id in kwargs["selection_ids"]],
                    trajectory_ids=[build_grpc_id(id) for id in kwargs["trajectory_ids"]],
                    distance=from_length_to_grpc_quantity(kwargs["distance"]),
                )
            ]
        )

        # Call the gRPC service
        response = self.edit_stub.SweepDatumPoint(request)
        serialized_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_command_response.command_response.success,
            "created_curves": [
                {
                    "id": curve.id.id,
                    "name": curve.owner_name,
                    "length": from_grpc_quantity_to_distance(curve.length),
                    "start_point": from_grpc_point_to_point3d(curve.points[0]),
                    "end_point": from_grpc_point_to_point3d(curve.points[1])
                    if len(curve.points) > 1
                    else None,
                    "parent_id": curve.parent_id.id,
                }
                for curve in response.response_data[0].created_curves
            ],
            "tracked_response": serialized_response,
        }
