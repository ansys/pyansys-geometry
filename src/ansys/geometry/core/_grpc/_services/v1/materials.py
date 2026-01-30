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
"""Module containing the materials service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.materials import GRPCMaterialsService
from .conversions import from_material_to_grpc_material


class GRPCMaterialsServiceV1(GRPCMaterialsService):
    """Materials service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    materials service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.data.cadmaterial_pb2_grpc import CADMaterialStub

        self.stub = CADMaterialStub(channel)

    @protect_grpc
    def add_material(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.data.cadmaterial_pb2 import CreateRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateRequest(
            request_data=[from_material_to_grpc_material(kwargs["material"])],
        )

        # Call the gRPC service
        _ = self.stub.Create(request=request)

        # Convert the response to a dictionary
        return {}

    @protect_grpc
    def remove_material(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.data.cadmaterial_pb2 import DeleteRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = DeleteRequest(
            request_data=[from_material_to_grpc_material(mat) for mat in kwargs["materials"]]
        )

        # Call the gRPC service
        _ = self.stub.Delete(request=request)

        # Convert the response to a dictionary
        return {}
