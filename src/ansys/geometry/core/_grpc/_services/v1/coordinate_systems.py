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
"""Module containing the coordinate systems service implementation for v1."""

import grpc

from ansys.geometry.core._grpc._services.v1.conversions import build_grpc_id
from ansys.geometry.core.errors import protect_grpc

from ..base.coordinate_systems import GRPCCoordinateSystemService
from .conversions import from_frame_to_grpc_frame, from_grpc_frame_to_frame


class GRPCCoordinateSystemServiceV1(GRPCCoordinateSystemService):  # pragma: no cover
    """Coordinate systems service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    coordinate systems service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.constructs.coordinatesystem_pb2_grpc import (
            CoordinateSystemStub,
        )

        self.stub = CoordinateSystemStub(channel)

    @protect_grpc
    def create(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.constructs.coordinatesystem_pb2 import (
            CreateRequest,
            CreateRequestData,
        )

        # Create the request data - assumes all inputs are valid and of the proper type
        request = CreateRequest(
            request_data=[
                CreateRequestData(
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    name=kwargs["name"],
                    frame=from_frame_to_grpc_frame(kwargs["frame"]),
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.Create(request=request)

        # Return the response - formatted as a dictionary
        # Note: response.coordinate_systems is a repeated field, we return the first one
        coord_system = response.coordinate_systems[0]
        return {
            "id": coord_system.id,
            "name": coord_system.name,
            "frame": from_grpc_frame_to_frame(coord_system.frame),
        }
