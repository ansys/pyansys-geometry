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
"""Module containing the admin service implementation for v0."""

import warnings

import grpc
import semver

from ansys.geometry.core.errors import protect_grpc

from ..base.admin import GRPCAdminService
from .conversions import from_grpc_backend_type_to_backend_type


class GRPCAdminServiceV0(GRPCAdminService):
    """Admin service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    admin service. It is specifically designed for the v0 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.dbu.v0.admin_pb2_grpc import AdminStub

        self.stub = AdminStub(channel)

    @protect_grpc
    def get_backend(self, **kwargs) -> dict:  # noqa: D102
        # TODO: Remove this context and filter once the protobuf UserWarning is downgraded to INFO
        # https://github.com/grpc/grpc/issues/37609
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore", "Protobuf gencode version", UserWarning, "google.protobuf.runtime_version"
            )
            from google.protobuf.empty_pb2 import Empty

        # Create the request - assumes all inputs are valid and of the proper type
        request = Empty()

        # Call the gRPC service
        response = self.stub.GetBackend(request=request)

        # COMPATIBILITY HACK: retrieve the backend version -- for versions after 24R1
        if hasattr(response, "version"):
            ver = response.version
            backend_version = semver.Version(ver.major_release, ver.minor_release, ver.service_pack)
        else:  # pragma: no cover
            # If the version is not available, set a default version
            backend_version = semver.Version(24, 1, 0)

        # Convert the response to a dictionary
        return {
            "backend": from_grpc_backend_type_to_backend_type(response.type),
            "version": backend_version,
        }

    @protect_grpc
    def get_logs(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.admin_pb2 import LogsRequest, LogsTarget, PeriodType

        # Create the request - assumes all inputs are valid and of the proper type
        request = LogsRequest(
            target=LogsTarget.CLIENT,
            period_type=PeriodType.CURRENT if not kwargs["all_logs"] else PeriodType.ALL,
            null_path=None,
            null_period=None,
        )

        # Call the gRPC service
        logs_generator = self.stub.GetLogs(request)
        logs: dict[str, str] = {}

        # Convert the response to a dictionary
        for chunk in logs_generator:
            if chunk.log_name not in logs:
                logs[chunk.log_name] = ""
            logs[chunk.log_name] += chunk.log_chunk.decode()

        return {"logs": logs}
