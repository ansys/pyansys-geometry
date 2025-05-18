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
"""Module containing the edges service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.conversions import to_distance
from ..base.edges import GRPCEdgesService
from .conversions import build_grpc_id, from_grpc_point_to_point3d


class GRPCEdgesServiceV0(GRPCEdgesService):
    """Edges service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    edges service. It is specifically designed for the v0 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v0.edges_pb2_grpc import EdgesStub

        self.stub = EdgesStub(channel)

    @protect_grpc
    def get_edge(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.Get(request=request)

        # Return the response - formatted as a dictionary
        return {
            "edge_id": response.id,
            "edge_curve_type": response.curve_type,
            "edge_is_reversed": response.is_reversed,
        }

    @protect_grpc
    def get_curve(self, **kwargs) -> dict:  # noqa: D102
        from .conversions import from_grpc_curve_to_curve

        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetCurve(request=request)

        # Return the response - formatted as a dictionary
        return {
            "curve": from_grpc_curve_to_curve(response.curve),
        }

    @protect_grpc
    def get_start_and_end_points(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetStartAndEndPoints(request=request)

        # Return the response - formatted as a dictionary
        return {
            "start": from_grpc_point_to_point3d(response.start),
            "end": from_grpc_point_to_point3d(response.end),
        }

    @protect_grpc
    def get_length(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetLength(request=request)

        # Return the response - formatted as a dictionary
        return {
            "length": to_distance(response.length),
        }

    @protect_grpc
    def get_interval(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetInterval(request=request)

        # Return the response - formatted as a dictionary
        return {
            "start": response.start,
            "end": response.end,
        }

    @protect_grpc
    def get_faces(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetFaces(request=request)

        # Return the response - formatted as a dictionary
        return {
            "faces": [
                {
                    "id": face.id,
                    "surface_type": face.surface_type,
                    "is_reversed": face.is_reversed,
                }
                for face in response.faces
            ],
        }

    @protect_grpc
    def get_bounding_box(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetBoundingBox(request=request)

        # Return the response - formatted as a dictionary
        return {
            "min_corner": from_grpc_point_to_point3d(response.min),
            "max_corner": from_grpc_point_to_point3d(response.max),
            "center": from_grpc_point_to_point3d(response.center),
        }
