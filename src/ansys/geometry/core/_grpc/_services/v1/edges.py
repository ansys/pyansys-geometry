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
"""Module containing the edges service implementation for v1."""

from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest
import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.conversions import to_distance
from ..base.edges import GRPCEdgesService
from .conversions import (
    build_grpc_id,
    from_grpc_curve_to_curve,
    from_grpc_point_to_point3d,
    from_length_to_grpc_quantity,
    from_point3d_to_grpc_point,
    from_unit_vector_to_grpc_direction,
    serialize_tracked_command_response,
)


class GRPCEdgesServiceV1(GRPCEdgesService):  # pragma: no cover
    """Edges service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    edges service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.geometry.edge_pb2_grpc import EdgeStub
        from ansys.api.discovery.v1.operations.edit_pb2_grpc import EditStub

        self.stub = EdgeStub(channel)
        self.edit_stub = EditStub(channel)

    @protect_grpc
    def get_edge(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import EntityRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = EntityRequest(id=build_grpc_id(kwargs["id"]))

        # Call the gRPC service
        response = self.stub.Get(request=request)

        # Return the response - formatted as a dictionary
        return {
            "id": response.edge.id,
            "curve_type": response.edge.curve_type,
            "is_reversed": response.edge.is_reversed,
        }

    @protect_grpc
    def get_curve(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetCurve(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "curve": from_grpc_curve_to_curve(response.curve),
        }

    @protect_grpc
    def get_start_and_end_points(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetStartAndEndPoints(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "start": from_grpc_point_to_point3d(response.start),
            "end": from_grpc_point_to_point3d(response.end),
        }

    @protect_grpc
    def get_length(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetLength(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "length": to_distance(response.length.value_in_geometry_units),
        }

    @protect_grpc
    def get_interval(self, **kwargs) -> dict:  # noqa: D102
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
    def get_faces(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetFaces(request=request).response_data[0]

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
    def get_vertices(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetVertices(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "vertices": [
                {
                    "id": vertex.id.id,
                    "position": from_grpc_point_to_point3d(vertex.position),
                }
                for vertex in response.vertices
            ],
        }

    @protect_grpc
    def get_bounding_box(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        response = self.stub.GetBoundingBox(request=request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "min_corner": from_grpc_point_to_point3d(response.box.min),
            "max_corner": from_grpc_point_to_point3d(response.box.max),
            "center": from_grpc_point_to_point3d(response.box.center),
        }

    @protect_grpc
    def extrude_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            ExtrudeEdgesRequest,
            ExtrudeEdgesRequestData,
        )

        # Parse some optional arguments
        point = from_point3d_to_grpc_point(kwargs["point"]) if kwargs["point"] else None
        direction = (
            from_unit_vector_to_grpc_direction(kwargs["direction"]) if kwargs["direction"] else None
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = ExtrudeEdgesRequest(
            request_data=[
                ExtrudeEdgesRequestData(
                    edge_ids=[build_grpc_id(edge_id) for edge_id in kwargs["edge_ids"]],
                    face_id=build_grpc_id(kwargs["face"]),
                    point=point,
                    direction=direction,
                    distance=from_length_to_grpc_quantity(kwargs["distance"]),
                    extrude_type=kwargs["extrude_type"].value,
                    pull_symmetric=kwargs["pull_symmetric"],
                    copy=kwargs["copy"],
                    natural_extension=kwargs["natural_extension"],
                )
            ]
        )

        # Call the gRPC service and serialize the response
        response = self.edit_stub.ExtrudeEdges(request)
        tracked_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response - formatted as a dictionary
        return {
            "success": tracked_response.get("success"),
            "created_bodies": [
                body.get("id").id for body in tracked_response.get("created_bodies")
            ],
        }

    @protect_grpc
    def extrude_edges_up_to(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            ExtrudeEdgesUpToRequest,
            ExtrudeEdgesUpToRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = ExtrudeEdgesUpToRequest(
            request_data=[
                ExtrudeEdgesUpToRequestData(
                    edge_ids=[build_grpc_id(id) for id in kwargs["face_ids"]],
                    up_to_selection_id=build_grpc_id(kwargs["up_to_selection_id"]),
                    seed_point=from_point3d_to_grpc_point(kwargs["seed_point"]),
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    extrude_type=kwargs["extrude_type"].value,
                )
            ]
        )

        # Call the gRPC service and serialize the response
        response = self.edit_stub.ExtrudeFacesUpTo(request=request)
        tracked_response = serialize_tracked_command_response(response.tracked_command_response)

        # Return the response - formatted as a dictionary
        return {
            "success": tracked_response.get("success"),
            "created_bodies": [
                body.get("id").id for body in tracked_response.get("created_bodies")
            ],
        }

    @protect_grpc
    def move_imprint_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            MoveImprintEdgesRequest,
            MoveImprintEdgesRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = MoveImprintEdgesRequest(
            request_data=[
                MoveImprintEdgesRequestData(
                    edge_ids=[build_grpc_id(edge_id) for edge_id in kwargs["edge_ids"]],
                    direction=from_unit_vector_to_grpc_direction(kwargs["direction"]),
                    distance=from_length_to_grpc_quantity(kwargs["distance"]),
                )
            ]
        )

        # Call the gRPC service
        response = self.edit_stub.MoveImprintEdges(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_command_response.command_response.success,
        }

    @protect_grpc
    def offset_edges(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.operations.edit_pb2 import (
            OffsetEdgesRequest,
            OffsetEdgesRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = OffsetEdgesRequest(
            request_data=[
                OffsetEdgesRequestData(
                    edge_ids=[build_grpc_id(edge_id) for edge_id in kwargs["edge_ids"]],
                    value=from_length_to_grpc_quantity(kwargs["offset"]),
                )
            ]
        )

        # Call the gRPC service
        response = self.edit_stub.OffsetEdges(request)

        # Return the response - formatted as a dictionary
        return {
            "success": response.tracked_command_response.command_response.success,
        }
