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
"""Module containing the model tools service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.model_tools import GRPCModelToolsService


class GRPCModelToolsServiceV1(GRPCModelToolsService):
    """Model tools service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    model tools service. It is specifically designed for the v0 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v1.model_tools_pb2_grpc import ModelToolsStub

        self._stub = ModelToolsStub(channel)

    @protect_grpc
    def chamfer(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def fillet(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def full_fillet(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def move_rotate(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def move_translate(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError
