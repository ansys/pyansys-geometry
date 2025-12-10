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
"""Module containing the assembly condition service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.assembly_condition import GRPCAssemblyConditionService
from .conversions import build_grpc_id


class GRPCAssemblyConditionServiceV0(GRPCAssemblyConditionService):
    """Assembly condition service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    assembly condition service. It is specifically designed for the v0 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub

        self.stub = CommandsStub(channel)

    @protect_grpc
    def create_align_condition(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import (
            CreateAlignTangentOrientGearConditionRequest,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateAlignTangentOrientGearConditionRequest(
            parent=build_grpc_id(kwargs["parent_id"]),
            geometric_a=build_grpc_id(kwargs["geometric_a_id"]),
            geometric_b=build_grpc_id(kwargs["geometric_b_id"]),
        )

        # Call the gRPC service
        resp = self.stub.CreateAlignCondition(request)

        # Return the response - formatted as a dictionary
        return {
            "id": resp.condition.moniker,
            "is_deleted": resp.condition.is_deleted,
            "is_enabled": resp.condition.is_enabled,
            "is_satisfied": resp.condition.is_satisfied,
            "offset": resp.offset,
            "is_reversed": resp.is_reversed,
            "is_valid": resp.is_valid,
        }

    @protect_grpc
    def create_tangent_condition(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import (
            CreateAlignTangentOrientGearConditionRequest,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateAlignTangentOrientGearConditionRequest(
            parent=build_grpc_id(kwargs["parent_id"]),
            geometric_a=build_grpc_id(kwargs["geometric_a_id"]),
            geometric_b=build_grpc_id(kwargs["geometric_b_id"]),
        )

        # Call the gRPC service
        resp = self.stub.CreateTangentCondition(request)

        # Return the response - formatted as a dictionary
        return {
            "id": resp.condition.moniker,
            "is_deleted": resp.condition.is_deleted,
            "is_enabled": resp.condition.is_enabled,
            "is_satisfied": resp.condition.is_satisfied,
            "offset": resp.offset,
            "is_reversed": resp.is_reversed,
            "is_valid": resp.is_valid,
        }

    @protect_grpc
    def create_orient_condition(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import (
            CreateAlignTangentOrientGearConditionRequest,
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateAlignTangentOrientGearConditionRequest(
            parent=build_grpc_id(kwargs["parent_id"]),
            geometric_a=build_grpc_id(kwargs["geometric_a_id"]),
            geometric_b=build_grpc_id(kwargs["geometric_b_id"]),
        )

        # Call the gRPC service
        resp = self.stub.CreateOrientCondition(request)

        # Return the response - formatted as a dictionary
        return {
            "id": resp.condition.moniker,
            "is_deleted": resp.condition.is_deleted,
            "is_enabled": resp.condition.is_enabled,
            "is_satisfied": resp.condition.is_satisfied,
            "offset": resp.offset,
            "is_reversed": resp.is_reversed,
            "is_valid": resp.is_valid,
        }
