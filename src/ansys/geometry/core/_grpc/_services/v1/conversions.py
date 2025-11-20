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
"""Module containing v1 related conversions from PyAnsys Geometry objects to gRPC messages."""

from typing import TYPE_CHECKING

from ansys.api.discovery.v1.commonenums_pb2 import BackendType as GRPCBackendType
from ansys.api.discovery.v1.commonmessages_pb2 import EntityIdentifier

if TYPE_CHECKING:
    from ansys.geometry.core.connection.backend import BackendType


def from_grpc_backend_type_to_backend_type(
    grpc_backend_type: GRPCBackendType,
) -> "BackendType":
    """Convert a gRPC backend type to a backend type.

    Parameters
    ----------
    backend_type : GRPCBackendType
        Source backend type.

    Returns
    -------
    BackendType
        Converted backend type.
    """
    from ansys.geometry.core.connection.backend import BackendType

    # Map the gRPC backend type to the corresponding BackendType
    backend_type = None

    if grpc_backend_type == GRPCBackendType.BACKENDTYPE_DISCOVERY:
        backend_type = BackendType.DISCOVERY
    elif grpc_backend_type == GRPCBackendType.BACKENDTYPE_SPACECLAIM:
        backend_type = BackendType.SPACECLAIM
    elif grpc_backend_type == GRPCBackendType.BACKENDTYPE_WINDOWS_DMS:
        backend_type = BackendType.WINDOWS_SERVICE
    elif grpc_backend_type == GRPCBackendType.BACKENDTYPE_LINUX_DMS:
        backend_type = BackendType.LINUX_SERVICE
    elif grpc_backend_type == GRPCBackendType.BACKENDTYPE_CORE_SERVICE_LINUX:
        backend_type = BackendType.CORE_LINUX
    elif grpc_backend_type == GRPCBackendType.BACKENDTYPE_CORE_SERVICE_WINDOWS:
        backend_type = BackendType.CORE_WINDOWS
    elif grpc_backend_type == GRPCBackendType.BACKENDTYPE_DISCOVERY_HEADLESS:
        backend_type = BackendType.DISCOVERY_HEADLESS
    else:
        raise ValueError(f"Invalid backend type: {grpc_backend_type}")

    return backend_type


def build_grpc_id(id: str) -> EntityIdentifier:
    """Build an EntityIdentifier gRPC message.

    Parameters
    ----------
    id : str
        Source ID.

    Returns
    -------
    EntityIdentifier
        Geometry service gRPC entity identifier message.
    """
    return EntityIdentifier(id=id)
