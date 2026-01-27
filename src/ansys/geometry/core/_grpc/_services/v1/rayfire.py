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
"""Module containing the rayfire service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.rayfire import GRPCRayfireService
from .conversions import (
    build_grpc_id,
    from_grpc_point_to_point3d,
    from_point3d_to_grpc_point,
    from_unit_vector_to_grpc_direction,
)


class GRPCRayfireServiceV1(GRPCRayfireService):
    """Rayfire service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    rayfire service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.operations.rayfire_pb2_grpc import RayfireStub

        self.stub = RayfireStub(channel)

    @protect_grpc
    def rayfire(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.rayfire_pb2 import RayFireRequest, RayFireRequestData

        # Create the request - assumes all inputs are valid and of the proper type
        request = RayFireRequest(
            request_data=[
                RayFireRequestData(
                    body=build_grpc_id(kwargs["body_id"]),
                    faces=[build_grpc_id(face_id) for face_id in kwargs["face_ids"]],
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    points=[from_point3d_to_grpc_point(point) for point in kwargs["points"]],
                    max_distance=kwargs["max_distance"],
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.RayFire(request)

        # Return the response - formatted as a dictionary
        return {
            "response_data": [
                {
                    "impacts": [
                        {
                            "body_id": impact.body,
                            "point": from_grpc_point_to_point3d(impact.point)
                        }
                        for impact in data.single_ray_fire_impacts.impacts
                    ]
                }
                for data in response.response_data
            ]
        }

    @protect_grpc
    def rayfire_ordered(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.rayfire_pb2 import (
            RayFireOrderedRequest,
            RayFireOrderedRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = RayFireOrderedRequest(
            request_data=[
                RayFireOrderedRequestData(
                    body=build_grpc_id(kwargs["body_id"]),
                    faces=[build_grpc_id(face_id) for face_id in kwargs["face_ids"]],
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    ray_radius=kwargs["ray_radius"],
                    points=[from_point3d_to_grpc_point(point) for point in kwargs["points"]],
                    max_distance=kwargs["max_distance"],
                    tight_tolerance=kwargs["tight_tolerance"],
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.RayFireOrdered(request)

        # Return the response - formatted as a dictionary
        return {
            "response_data": [
                {
                    "ordered_impacts": [
                        {
                            [
                                {
                                    "body_id": impact.body,
                                    "point": from_grpc_point_to_point3d(impact.point)
                                }
                                for impact in ordered_impacts.impacts
                            ]
                        }
                        for ordered_impacts in data.ordered_ray_fire_impacts
                    ]
                }
                for data in response.response_data
            ]
        }

    @protect_grpc
    def rayfire_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.rayfire_pb2 import (
            RayFireFacesRequest,
            RayFireFacesRequestData,
        )

        from .conversions import from_rayfire_options_to_grpc_rayfire_options

        # Create the request - assumes all inputs are valid and of the proper type
        request = RayFireFacesRequest(
            request_data=[
                RayFireFacesRequestData(
                    body=build_grpc_id(kwargs["body_id"]),
                    faces=[build_grpc_id(face_id) for face_id in kwargs["face_ids"]],
                    points=[from_point3d_to_grpc_point(point) for point in kwargs["points"]],
                    options=from_rayfire_options_to_grpc_rayfire_options(kwargs["options"]),
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.RayFireFaces(request)

        # Return the response - formatted as a dictionary
        return {
            "response_data": [
                {
                    "face_impacts": [
                        {
                            [
                                {
                                    "face_id": impact.face,
                                    "point": from_grpc_point_to_point3d(impact.point)
                                }
                                for impact in face_impact.impacts
                            ]
                        }
                        for face_impact in data.faces_ray_fire_impacts
                    ]
                }
                for data in response.response_data
            ]
        }

    @protect_grpc
    def rayfire_ordered_uv(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.rayfire_pb2 import (
            RayFireOrderedUVRequest,
            RayFireOrderedUVRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = RayFireOrderedUVRequest(
            request_data=[
                RayFireOrderedUVRequestData(
                    body=build_grpc_id(kwargs["body_id"]),
                    faces=[build_grpc_id(face_id) for face_id in kwargs["face_ids"]],
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    ray_radius=kwargs["ray_radius"],
                    points=[from_point3d_to_grpc_point(point) for point in kwargs["points"]],
                    max_distance=kwargs["max_distance"],
                    tight_tolerance=kwargs["tight_tolerance"],
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.RayFireOrderedUV(request)

        # Return the response - formatted as a dictionary
        return {
            "response_data": [
                {
                    "ordered_impacts": [
                        {
                            [
                                {
                                    "body_id": impact.body,
                                    "point": from_grpc_point_to_point3d(impact.point),
                                    "u": impact.u,
                                    "v": impact.v
                                }
                                for impact in ordered_impact.impacts
                            ]
                        }
                        for ordered_impact in data.ordered_ray_fire_impacts
                    ]
                }
                for data in response.response_data
            ]
        }