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
"""Module containing the Named Selection service implementation for v0."""

import grpc

from ansys.geometry.core.designer.selection import NamedSelection
from ansys.geometry.core.errors import protect_grpc

from ..base.named_selection import GRPCNamedSelectionService


class GRPCNamedSelectionServiceV0(GRPCNamedSelectionService):
    """Named Selection service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    Named Selection service. It is specifically designed for the v0 version
    of the Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v0.namedselections_pb2_grpc import NamedSelectionsStub

        self.stub = NamedSelectionsStub(channel)

    @protect_grpc
    def get_named_selection(self, **kwargs):  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = kwargs["id"]

        # Call the gRPC service
        response = self.stub.Get(request)

        # Return the response - formatted as a dictionary
        return {
            "bodies": response.bodies,
            "faces": response.faces,
            "edges": response.edges,
            "beams": response.beams,
            "design_points": response.design_points,
        }
    
    @protect_grpc
    def create_named_selection(self, **kwargs):  # noqa: D102
        from ansys.api.geometry.v0.namedselections_pb2 import CreateRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateRequest(
            name=kwargs["name"],
            members=kwargs["members"],
        )

        # Call the gRPC service
        response = self.stub.Create(request)

        # Return the response - formatted as a dictionary
        return {
            "id": response.id,
            "name": response.name,
            "bodies": response.bodies,
            "faces": response.faces,
            "edges": response.edges,
            "beams": response.beams,
            "design_points": response.design_points,
        }
    
    @protect_grpc
    def get_all_named_selections(self, **kwargs):  # noqa: D102
        # Call the gRPC service
        response = self.stub.GetAll()

        # Return the response - formatted as a dictionary
        return {
            "named_selections": [
                {
                    "bodies": ns.bodies,
                    "faces": ns.faces,
                    "edges": ns.edges,
                    "beams": ns.beams,
                    "design_points": ns.design_points,
                }
                for ns in response.named_selections
            ]
        }
    
    @protect_grpc
    def delete_named_selection(self, **kwargs):  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = kwargs["id"]

        # Call the gRPC service
        self.stub.Delete(request)

        # Return the response - empty dictionary
        return {}
    
    @protect_grpc
    def delete_named_selection_by_name(self, **kwargs):  # noqa: D102
        from ansys.api.geometry.v0.namedselections_pb2 import DeleteByNameRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = DeleteByNameRequest(
            name=kwargs["name"],
        )

        # Call the gRPC service
        self.stub.DeleteByName(request)

        # Return the response - empty dictionary
        return {}