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

from ansys.geometry.core.errors import protect_grpc

from ..base.prepare_tools import GRPCPrepareToolsService


class GRPCPrepareToolsServiceV1(GRPCPrepareToolsService):
    """Prepare tools service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    Prepare Tools service. It is specifically designed for the v1 version
    of the Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v1.preparetools_pb2_grpc import PrepareToolsStub

        self.stub = PrepareToolsStub(channel)

    def extract_volume_from_faces(self, **kwargs) -> dict:  # noqa: D102
        """Extract a volume from input faces."""
        raise NotImplementedError

    def extract_volume_from_edge_loops(self, **kwargs) -> dict:  # noqa: D102
        """Extract a volume from input edge loop."""
        raise NotImplementedError

    def remove_rounds(self, **kwargs) -> dict:  # noqa: D102
        """Remove rounds from geometry."""
        raise NotImplementedError

    def share_topology(self, **kwargs) -> dict:  # noqa: D102
        """Share topology between the given bodies."""
        raise NotImplementedError

    def enhanced_share_topology(self, **kwargs) -> dict:  # noqa: D102
        """Share topology between the given bodies."""
        raise NotImplementedError

    def find_logos(self, **kwargs) -> dict:  # noqa: D102
        """Detect logos in geometry."""
        raise NotImplementedError

    def find_and_remove_logos(self, **kwargs) -> dict:  # noqa: D102
        """Detect and remove logos in geometry."""
        raise NotImplementedError