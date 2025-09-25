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
"""Module containing the components service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.components import GRPCComponentsService


class GRPCComponentsServiceV1(GRPCComponentsService):
    """Components service for gRPC communication with the Geometry server.

    This class provides methods to call components in the
    Geometry server using gRPC. It is specifically designed for the v1
    version of the Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v1.components_pb2_grpc import ComponentsStub

        self.stub = ComponentsStub(channel)

    @protect_grpc
    def create(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def set_name(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def set_placement(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def set_shared_topology(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def delete(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def import_groups(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def make_independent(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError