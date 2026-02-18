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
"""Module containing the planes service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.planes import GRPCPlanesService
from .conversions import build_grpc_id, from_grpc_plane_to_plane, from_plane_to_grpc_plane


class GRPCPlanesServiceV1(GRPCPlanesService):
    """Planes service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    planes service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.constructs.datumplane_pb2_grpc import DatumPlaneStub

        self.stub = DatumPlaneStub(channel)

    @protect_grpc
    def create(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.constructs.datumplane_pb2 import (
            DatumPlaneCreationRequest,
            DatumPlaneCreationRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = DatumPlaneCreationRequest(
            request_data=[
                DatumPlaneCreationRequestData(
                    plane=from_plane_to_grpc_plane(kwargs["plane"]),
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    name=kwargs["name"],
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.Create(request).planes[0]

        # Return the response - formatted as a dictionary
        return {
            "id": response.id.id,
        }

    @protect_grpc
    def get_all(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import ParentEntityRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ParentEntityRequest(parent_id=build_grpc_id(kwargs["parent_id"]))

        # Call the gRPC service
        response = self.stub.GetAll(request)

        # Return the response - formatted as a dictionary
        return {
            "planes": [
                {
                    "id": plane.id.id,
                    "name": plane.name,
                    "plane": (
                        from_grpc_plane_to_plane(plane.plane) if plane.HasField("plane") else None
                    ),
                    "parent_id": plane.parent_id.id,
                }
                for plane in response.planes
            ]
        }

    @protect_grpc
    def delete(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(
            ids=[build_grpc_id(id=kwargs["plane_id"])],
        )

        # Call the gRPC service
        response = self.stub.Delete(request)

        # Return the response - formatted as a dictionary
        return {
            "deleted_ids": [plane.id for plane in response.deleted_object_ids],
            "failed_ids": [plane.id for plane in response.failed_deletion_ids],
        }
