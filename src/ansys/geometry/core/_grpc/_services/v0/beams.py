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
"""Module containing the beams service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.beams import GRPCBeamsService


class GRPCBeamsServiceV0(GRPCBeamsService):
    """Beams service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    beams service. It is specifically designed for the v0 version of the
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
    def create_beam_segments(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import CreateBeamSegmentsRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateBeamSegmentsRequest(
            profile=kwargs["profile_id"],
            parent=kwargs["parent_id"],
            lines=kwargs["lines"],
        )

        # Call the gRPC service
        resp = self.stub.CreateBeamSegments(request)

        # Return the response as a dictionary
        return {
            "beam_ids": resp.ids,
        }

    @protect_grpc
    def create_descriptive_beam_segments(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import CreateBeamSegmentsRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = CreateBeamSegmentsRequest(
            profile=kwargs["profile_id"],
            parent=kwargs["parent_id"],
            lines=kwargs["lines"],
        )

        # Call the gRPC service
        resp = self.stub.CreateDescriptiveBeamSegments(request)

        # Return the response as a dictionary
        return {
            "created_beams": resp.created_beams,
        }

    @protect_grpc
    def delete_beam(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.dbumodels_pb2 import EntityIdentifier

        # Create the request - assumes all inputs are valid and of the proper type
        request = EntityIdentifier(id=kwargs["beam_id"])

        # Call the gRPC service
        _ = self.stub.DeleteBeam(request)