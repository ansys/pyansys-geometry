# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Module containing the curves service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.curves import GRPCCurvesService
from .conversions import (
    build_grpc_id,
    from_angle_to_grpc_quantity,
    from_curve_to_grpc_curve,
    from_grpc_curve_to_curve,
    from_grpc_point_to_point3d,
    from_grpc_quantity_to_distance,
    from_line_to_grpc_line,
    from_surface_to_grpc_surface,
    from_trimmed_curve_to_grpc_trimmed_curve,
    serialize_tracked_command_response,
)


class GRPCCurvesServiceV1(GRPCCurvesService):
    """Curves service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    curves service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.curve_pb2_grpc import CurveStub
        from ansys.api.discovery.v1.operations.edit_pb2_grpc import EditStub

        self.stub = CurveStub(channel)
        self.edit_stub = EditStub(channel)

    @protect_grpc
    def revolve_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            RevolveCurvesRequest,
            RevolveCurvesRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = RevolveCurvesRequest(
            request_data=[
                RevolveCurvesRequestData(
                    curves=[
                        from_trimmed_curve_to_grpc_trimmed_curve(curve)
                        for curve in kwargs["curves"]
                    ],
                    axis=from_line_to_grpc_line(kwargs["axis"]),
                    angle=from_angle_to_grpc_quantity(kwargs["angle"]),
                    symmetric=kwargs["symmetric"],
                )
            ]
        )

        # Call the gRPC service
        response = self.edit_stub.RevolveCurves(request)
        tracked_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the result - formatted as a dictionary
        return {
            "tracked_response": tracked_response,
        }

    @protect_grpc
    def intersect_curves(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            IntersectCurvesRequest,
            IntersectCurvesRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = IntersectCurvesRequest(
            request_data=[
                IntersectCurvesRequestData(
                    first=from_trimmed_curve_to_grpc_trimmed_curve(kwargs["first"]),
                    second=from_trimmed_curve_to_grpc_trimmed_curve(kwargs["second"]),
                )
            ]
        )

        # Call the gRPC service
        response = self.edit_stub.IntersectCurves(request).response_data[0]

        # Return the result - formatted as a dictionary
        return {
            "intersect": response.intersect,
            "points": [from_grpc_point_to_point3d(point) for point in response.points],
        }

    @protect_grpc
    def intersect_curve_and_surface(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            IntersectCurveAndSurfaceRequest,
            IntersectCurveAndSurfaceRequestData,
        )

        surface, surface_type = from_surface_to_grpc_surface(kwargs["surface"])

        # Create the request - assumes all inputs are valid and of the proper type
        request = IntersectCurveAndSurfaceRequest(
            request_data=[
                IntersectCurveAndSurfaceRequestData(
                    curve=from_curve_to_grpc_curve(kwargs["curve"]),
                    surface=surface,
                    surface_type=surface_type,
                )
            ]
        )

        # Call the gRPC service
        response = self.edit_stub.IntersectCurveAndSurface(request).response_data[0]

        # Return the result - formatted as a dictionary
        return {
            "intersect": response.intersect,
            "points": [from_grpc_point_to_point3d(point) for point in response.points],
        }

    @protect_grpc
    def get(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import EntityRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = EntityRequest(id=build_grpc_id(kwargs["id"]))

        # Call the gRPC service
        response = self.stub.Get(request).curve

        # Return the result - formatted as a dictionary
        return {
            "id": response.id.id,
            "name": response.owner_name,
            "length": from_grpc_quantity_to_distance(response.length),
            "start_point": from_grpc_point_to_point3d(response.points[0]),
            "end_point": from_grpc_point_to_point3d(response.points[1])
            if len(response.points) > 1
            else None,
            "parent_id": response.parent_id.id,
            "geometry": from_grpc_curve_to_curve(response.geometry),
        }

    @protect_grpc
    def get_interval(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetInterval(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "start": response.start,
            "end": response.end,
        }

    @protect_grpc
    def delete(self, **kwargs) -> None:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["curve_id"])])

        # Call the gRPC service
        self.stub.Delete(request=request)
