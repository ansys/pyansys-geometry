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
"""Module containing the faces service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.conversions import to_area, to_distance
from ..base.faces import GRPCFacesService
from .conversions import (
    build_grpc_id,
    from_grpc_curve_to_curve,
    from_grpc_point_to_point3d,
    from_grpc_surface_to_surface,
)


class GRPCFacesServiceV0(GRPCFacesService):  # pragma: no cover
    """Faces service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    faces service. It is specifically designed for the v0 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v0.faces_pb2_grpc import FacesStub

        self.stub = FacesStub(channel)

    @protect_grpc
    def get_surface(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetSurface(request=request)

        # Return the response - formatted as a dictionary
        return {
            "surface": from_grpc_surface_to_surface(response, kwargs["surface_type"]),
        }

    @protect_grpc
    def get_box_uv(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetBoxUV(request=request)

        # Return the response - formatted as a dictionary
        return {
            "uv_box": {
                "u": (response.start_u, response.end_u),
                "v": (response.start_v, response.end_v),
            }
        }

    @protect_grpc
    def get_area(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetArea(request=request)

        # Return the response - formatted as a dictionary
        return {"area": to_area(response.area)}

    @protect_grpc
    def get_edges(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetEdges(request=request)

        # Return the response - formatted as a dictionary
        return {
            "edges": [
                {
                    "id": edge.id,
                    "curve_type": edge.curve_type,
                    "is_reversed": edge.is_reversed,
                }
                for edge in response.edges
            ]
        }
    
    @protect_grpc
    def get_vertices(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        from ansys.api.geometry.v0.faces_pb2 import GetVerticesRequest

        request = GetVerticesRequest(face_id=build_grpc_id(kwargs["id"]))

        # Call the gRPC service
        response = self.stub.GetVertices(request=request)

        # Return the response - formatted as a dictionary
        return {
            "vertices": [
                {
                    "id": vertex.id.id,
                    "position": from_grpc_point_to_point3d(vertex.position),
                }
                for vertex in response.vertices
            ]
        }

    @protect_grpc
    def get_loops(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetLoops(request=request)

        # Return the response - formatted as a dictionary
        return {
            "loops": [
                {
                    "type": loop.type,
                    "length": to_distance(loop.length).value,
                    "min_corner": from_grpc_point_to_point3d(loop.bounding_box.min),
                    "max_corner": from_grpc_point_to_point3d(loop.bounding_box.max),
                    "edges": [edge for edge in loop.edges],
                }
                for loop in response.loops
            ]
        }

    @protect_grpc
    def get_color(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(kwargs["id"])

        # Call the gRPC service
        response = self.stub.GetColor(request=request)

        # Return the response - formatted as a dictionary
        return {"color": response.color}

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

    @protect_grpc
    def set_color(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.faces_pb2 import SetColorRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetColorRequest(
            face_id=kwargs["id"],
            color=kwargs["color"],
        )
        # Call the gRPC service
        response = self.stub.SetColor(request=request)

        # Return the response - formatted as a dictionary
        return {"success": response.success}

    @protect_grpc
    def get_normal(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.faces_pb2 import GetNormalRequest
        from ansys.geometry.core.math.vector import UnitVector3D

        # Create the request - assumes all inputs are valid and of the proper type
        request = GetNormalRequest(
            id=kwargs["id"],
            u=kwargs["u"],
            v=kwargs["v"],
        )

        # Call the gRPC service
        response = self.stub.GetNormal(request=request)

        # Return the response - formatted as a dictionary
        return {
            "normal": UnitVector3D(
                [response.direction.x, response.direction.y, response.direction.z]
            ),
        }

    @protect_grpc
    def evaluate(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.faces_pb2 import EvaluateRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = EvaluateRequest(
            id=kwargs["id"],
            u=kwargs["u"],
            v=kwargs["v"],
        )

        # Call the gRPC service
        response = self.stub.Evaluate(request=request)

        # Return the response - formatted as a dictionary
        return {
            "point": from_grpc_point_to_point3d(response.point),
        }

    @protect_grpc
    def create_iso_parametric_curve(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.faces_pb2 import CreateIsoParamCurvesRequest
        from ansys.geometry.core.shapes.parameterization import Interval

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateIsoParamCurvesRequest(
            id=kwargs["id"],
            u_dir_curve=kwargs["use_u_param"],
            proportion=kwargs["parameter"],
        )

        # Call the gRPC service
        response = self.stub.CreateIsoParamCurves(request=request)

        # Return the response - formatted as a dictionary
        return {
            "curves": [
                {
                    "geometry": from_grpc_curve_to_curve(curve.curve),
                    "start": from_grpc_point_to_point3d(curve.start),
                    "end": from_grpc_point_to_point3d(curve.end),
                    "interval": Interval(curve.interval_start, curve.interval_end),
                    "length": to_distance(curve.length).value,
                }
                for curve in response.curves
            ]
        }
