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
"""Module containing the Named Selection service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.named_selection import GRPCNamedSelectionService
from .conversions import build_grpc_id


class GRPCNamedSelectionServiceV1(GRPCNamedSelectionService):  # pragma: no cover
    """Named Selection service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    Named Selection service. It is specifically designed for the v1 version
    of the Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.selections.namedselection_pb2_grpc import (
            NamedSelectionStub,
        )

        self.stub = NamedSelectionStub(channel)

    @protect_grpc
    def get_named_selection(self, **kwargs):  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import EntityRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = EntityRequest(id=build_grpc_id(kwargs["id"]))

        # Call the gRPC service
        response = self.stub.Get(request).named_selection

        # Return the response - formatted as a dictionary
        return {
            "id": response.id.id,
            "name": response.name,
            "bodies": [body.id.id for body in response.bodies],
            "faces": [face.id.id for face in response.faces],
            "edges": [edge.id.id for edge in response.edges],
            "beams": [beam.id.id for beam in response.beams],
            "design_points": [dp.id.id for dp in response.design_points],
            "components": [comp.id.id for comp in response.components],
            "vertices": [vertex.id.id for vertex in response.vertices],
        }

    @protect_grpc
    def create_named_selection(self, **kwargs):  # noqa: D102
        from ansys.api.discovery.v1.design.selections.namedselection_pb2 import (
            CreateRequest,
            CreateRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateRequest(
            request_data=[
                CreateRequestData(
                    name=kwargs["name"],
                    members_ids=[build_grpc_id(id) for id in kwargs["members"]],
                )
            ]
        )

        # Call the gRPC service
        response = self.stub.Create(request).named_selections[0]

        # Return the response - formatted as a dictionary
        return {
            "id": response.id.id,
            "name": response.name,
            "bodies": [body.id.id for body in response.bodies],
            "faces": [face.id.id for face in response.faces],
            "edges": [edge.id.id for edge in response.edges],
            "beams": [beam.id.id for beam in response.beams],
            "design_points": [dp.id.id for dp in response.design_points],
            "components": [comp.id.id for comp in response.components],
            "vertices": [vertex.id.id for vertex in response.vertices],
        }

    @protect_grpc
    def delete_named_selection(self, **kwargs):  # noqa: D102
        from ansys.api.discovery.v1.commonmessages_pb2 import MultipleEntitiesRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = MultipleEntitiesRequest(ids=[build_grpc_id(kwargs["id"])])

        # Call the gRPC service
        self.stub.Delete(request)

        # Return the response - empty dictionary
        return {}

    @protect_grpc
    def rename_named_selection(self, **kwargs):  # noqa: D102
        from ansys.api.discovery.v1.design.designmessages_pb2 import (
            SetDesignEntityNameRequest,
            SetDesignEntityNameRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetDesignEntityNameRequest(
            request_data=[
                SetDesignEntityNameRequestData(
                    id=build_grpc_id(kwargs["id"]),
                    name=kwargs["new_name"],
                )
            ]
        )

        # Call the gRPC service
        self.stub.SetName(request)

        # Return the response - empty dictionary
        return {}
