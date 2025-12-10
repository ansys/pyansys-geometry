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
"""Module containing the assembly condition service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.assembly_condition import GRPCAssemblyConditionService
from .conversions import build_grpc_id


class GRPCAssemblyConditionServiceV1(GRPCAssemblyConditionService):
    """Assembly condition service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    assembly condition service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.relationships.assemblycondition_pb2_grpc import (
            AssemblyConditionStub,
        )

        self.stub = AssemblyConditionStub(channel)

    @protect_grpc
    def create_align_condition(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.relationships.assemblycondition_pb2 import (
            CreateAlignRequest,
            CreateAlignRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateAlignRequest(
            request_data=[
                CreateAlignRequestData(
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    geometric_a_id=build_grpc_id(kwargs["geometric_a_id"]),
                    geometric_b_id=build_grpc_id(kwargs["geometric_b_id"]),
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreateAlign(request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "id": resp.align_condition.condition.id,
            "is_deleted": resp.align_condition.condition.is_deleted,
            "is_enabled": resp.align_condition.condition.is_enabled,
            "is_satisfied": resp.align_condition.condition.is_satisfied,
            "offset": resp.align_condition.offset,
            "is_reversed": resp.align_condition.is_reversed,
            "is_valid": resp.align_condition.is_valid,
        }

    @protect_grpc
    def create_tangent_condition(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.relationships.assemblycondition_pb2 import (
            CreateTangentRequest,
            CreateTangentRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateTangentRequest(
            request_data=[
                CreateTangentRequestData(
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    geometric_a_id=build_grpc_id(kwargs["geometric_a_id"]),
                    geometric_b_id=build_grpc_id(kwargs["geometric_b_id"]),
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreateTangent(request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "id": resp.tangent_condition.condition.id,
            "is_deleted": resp.tangent_condition.condition.is_deleted,
            "is_enabled": resp.tangent_condition.condition.is_enabled,
            "is_satisfied": resp.tangent_condition.condition.is_satisfied,
            "offset": resp.tangent_condition.offset,
            "is_reversed": resp.tangent_condition.is_reversed,
            "is_valid": resp.tangent_condition.is_valid,
        }

    @protect_grpc
    def create_orient_condition(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.design.relationships.assemblycondition_pb2 import (
            CreateOrientRequest,
            CreateOrientRequestData,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateOrientRequest(
            request_data=[
                CreateOrientRequestData(
                    parent_id=build_grpc_id(kwargs["parent_id"]),
                    geometric_a_id=build_grpc_id(kwargs["geometric_a_id"]),
                    geometric_b_id=build_grpc_id(kwargs["geometric_b_id"]),
                )
            ]
        )

        # Call the gRPC service
        resp = self.stub.CreateOrient(request).response_data[0]

        # Return the response - formatted as a dictionary
        return {
            "id": resp.orient_condition.condition.id,
            "is_deleted": resp.orient_condition.condition.is_deleted,
            "is_enabled": resp.orient_condition.condition.is_enabled,
            "is_satisfied": resp.orient_condition.condition.is_satisfied,
            "offset": resp.orient_condition.offset,
            "is_reversed": resp.orient_condition.is_reversed,
            "is_valid": resp.orient_condition.is_valid,
        }
