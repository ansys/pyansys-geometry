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

import grpc

from .._version import GeometryApiProtos, set_proto_version
from .base.bodies import GRPCBodyService


class _GRPCServices:
    """
    Placeholder for the gRPC services (i.e. stubs).

    Notes
    -----
    This class provides a unified interface to access the different
    gRPC services available in the Geometry API. It allows for easy
    switching between different versions of the API by using the
    `version` parameter in the constructor. The services are lazy-loaded
    to avoid unnecessary imports and to improve performance.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    version : GeometryApiProtos | str | None
        The version of the gRPC API protocol to use. If None, the latest
        version is used.
    """

    def __init__(self, channel: grpc.Channel, version: GeometryApiProtos | str | None = None):
        """
        Initialize the GRPCServices class.

        Parameters
        ----------
        channel : grpc.Channel
            The gRPC channel to the server.
        version : GeometryApiProtos | str | None
            The version of the gRPC API protocol to use. If None, the latest
            version is used.
        """
        # Set the proto version to be used
        self.version = set_proto_version(channel, version)
        self.channel = channel

        # Lazy load all the services
        self._body_service = None

    @property
    def body_service(self) -> GRPCBodyService:
        """
        Get the body service for the specified version.

        Returns
        -------
        BodyServiceBase
            The body service for the specified version.
        """
        if not self._body_service:
            # Import the appropriate body service based on the version
            from .v0.bodies import GRPCBodyServiceV0
            from .v1.bodies import GRPCBodyServiceV1

            if self.version == GeometryApiProtos.V0:
                self._body_service = GRPCBodyServiceV0(self.channel)
            elif self.version == GeometryApiProtos.V1:
                self._body_service = GRPCBodyServiceV1(self.channel)
            else:
                raise ValueError(f"Unsupported version: {self.version}")

        return self._body_service
