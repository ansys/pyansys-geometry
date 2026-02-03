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
    from_length_to_grpc_quantity,
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
        from ansys.api.discovery.v1.operations.rayfire_pb2_grpc import RayFireStub

        self.stub = RayFireStub(channel)

    @protect_grpc
    def rayfire(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.rayfire_pb2 import FireRequest, FireRequestData

        # Create the request - assumes all inputs are valid and of the proper type
        request = FireRequest(
            request_data=[
                FireRequestData(
                    body_id=build_grpc_id(kwargs["body_id"]),
                    faces_ids=[build_grpc_id(face_id) for face_id in kwargs["face_ids"]],
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    points=[from_point3d_to_grpc_point(point) for point in kwargs["points"]],
                    max_distance=from_length_to_grpc_quantity(kwargs["max_distance"]),
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.Fire(request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "impacts": [
                {"body_id": impact.body.id, "point": from_grpc_point_to_point3d(impact.point)}
                for impact in response.single_ray_fire_impacts.impacts
            ]
        }

    @protect_grpc
    def rayfire_ordered(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.rayfire_pb2 import (
            FireOrderedRequest,
            FireOrderedRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = FireOrderedRequest(
            request_data=[
                FireOrderedRequestData(
                    body_id=build_grpc_id(kwargs["body_id"]),
                    faces_ids=[build_grpc_id(face_id) for face_id in kwargs["face_ids"]],
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    ray_radius=from_length_to_grpc_quantity(kwargs["ray_radius"]),
                    points=[from_point3d_to_grpc_point(point) for point in kwargs["points"]],
                    max_distance=from_length_to_grpc_quantity(kwargs["max_distance"]),
                    tight_tolerance=kwargs["tight_tolerance"],
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.FireOrdered(request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "ordered_impacts": [
                {
                    [
                        {
                            "body_id": impact.body.id,
                            "point": from_grpc_point_to_point3d(impact.point),
                        }
                        for impact in ordered_impacts.impacts
                    ]
                }
                for ordered_impacts in response.ordered_fire_impacts
            ]
        }

    @protect_grpc
    def rayfire_faces(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.rayfire_pb2 import (
            FireFacesRequest,
            FireFacesRequestData,
        )

        from .conversions import from_rayfire_options_to_grpc_rayfire_options

        # Create options
        options = (
            from_rayfire_options_to_grpc_rayfire_options(kwargs["options"])
            if kwargs["options"]
            else None
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = FireFacesRequest(
            request_data=[
                FireFacesRequestData(
                    body_id=build_grpc_id(kwargs["body_id"]),
                    faces_ids=[build_grpc_id(face_id) for face_id in kwargs["face_ids"]],
                    points=[from_point3d_to_grpc_point(point) for point in kwargs["points"]],
                    options=options,
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.FireFaces(request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "face_impacts": [
                {
                    [
                        {
                            "face_id": impact.face.id,
                            "point": from_grpc_point_to_point3d(impact.point),
                        }
                        for impact in face_impact.impacts
                    ]
                }
                for face_impact in response.faces_fire_impacts
            ]
        }

    @protect_grpc
    def rayfire_ordered_uv(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.rayfire_pb2 import (
            FireOrderedUVRequest,
            FireOrderedUVRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = FireOrderedUVRequest(
            request_data=[
                FireOrderedUVRequestData(
                    body_id=build_grpc_id(kwargs["body_id"]),
                    faces_ids=[build_grpc_id(face_id) for face_id in kwargs["face_ids"]],
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    ray_radius=from_length_to_grpc_quantity(kwargs["ray_radius"]),
                    points=[from_point3d_to_grpc_point(point) for point in kwargs["points"]],
                    max_distance=from_length_to_grpc_quantity(kwargs["max_distance"]),
                    tight_tolerance=kwargs["tight_tolerance"],
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.FireOrderedUV(request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "ordered_impacts": [
                {
                    [
                        {
                            "body_id": impact.body.id,
                            "point": from_grpc_point_to_point3d(impact.point),
                            "u": impact.u,
                            "v": impact.v,
                        }
                        for impact in ordered_impact.impacts
                    ]
                }
                for ordered_impact in response.ordered_fire_impacts
            ]
        }
