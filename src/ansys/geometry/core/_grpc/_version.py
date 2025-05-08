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
"""Module containing methods and classes to detect the gRPC version used."""

from enum import Enum, unique

from google.protobuf.empty_pb2 import Empty
import grpc

# ATTEMPT v0 IMPORT
try:
    import ansys.api.dbu.v0.admin_pb2_grpc as dbu_v0_admin_pb2_grpc
except ImportError:
    dbu_v0_admin_pb2_grpc = None

# ATTEMPT v1 IMPORT
try:
    import ansys.api.dbu.v1.admin_pb2_grpc as dbu_v1_admin_pb2_grpc
except ImportError:
    dbu_v1_admin_pb2_grpc = None


@unique
class GeometryApiProtos(Enum):
    """Enumeration of the supported versions of the gRPC API protocol."""

    V0 = 0, dbu_v0_admin_pb2_grpc
    V1 = 1, dbu_v1_admin_pb2_grpc

    @staticmethod
    def get_latest_version() -> "GeometryApiProtos":
        """Get the latest version of the gRPC API protocol."""
        val = max(version.value[0] for version in GeometryApiProtos)
        return GeometryApiProtos.from_int_value(val)

    @staticmethod
    def from_int_value(version_int: int) -> "GeometryApiProtos":
        """Get the enumeration value from an integer."""
        for version in GeometryApiProtos:
            if version.value[0] == version_int:
                return version
        raise ValueError(f"Invalid version integer: {version_int}")

    @staticmethod
    def from_string(version_string: str) -> "GeometryApiProtos":
        """Get the enumeration value from a string."""
        for version in GeometryApiProtos:
            if version.name == version_string.capitalize():
                return version
        raise ValueError(f"Invalid version string: {version_string}")

    def verify_supported(self, channel: grpc.Channel) -> bool:
        """Check if the version is supported.

        Parameters
        ----------
        channel : grpc.Channel
            The gRPC channel to the server.

        Returns
        -------
        bool
            True if the server supports the version, otherwise False.

        Notes
        -----
        This method checks if the server supports the gRPC API protocol version.
        """
        pb2_grpc = self.value[1]
        if pb2_grpc is None:
            return False

        try:
            admin_stub = pb2_grpc.AdminStub(channel)
            admin_stub.Health(Empty())
            return True
        except grpc.RpcError:
            return False


def set_proto_version(
    channel: grpc.Channel, version: GeometryApiProtos | str | None = None
) -> "GeometryApiProtos":
    """Set the version of the gRPC API protocol used by the server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    version : GeometryApiProtos | str | None
        The version of the gRPC API protocol to use. If None, the latest
        version is used.

    Returns
    -------
    GeometryApiProtos
        The version of the gRPC API protocol used by the server.
    """
    # Sanity check the input
    if isinstance(version, str):
        version = GeometryApiProtos.from_string(version)

    # Check the server supports the requested version (if specified)
    if version and not version.verify_supported(channel):
        raise ValueError(f"Server does not support the requested version: {version.name}")

    # If no version specified... Attempt to use all of them, starting
    # with the latest version
    if version is None:
        version = GeometryApiProtos.get_latest_version()
        while not version.verify_supported(channel):
            version = GeometryApiProtos.from_int_value(version.value[0] - 1)

    # Return the version
    return version
