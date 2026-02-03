# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
"""Module containing the unsupported service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.unsupported import GRPCUnsupportedService
from .conversions import (
    build_grpc_id,
    from_grpc_point_to_point3d,
    from_point3d_to_grpc_point,
    from_unit_vector_to_grpc_direction,
)


class GRPCUnsupportedServiceV0(GRPCUnsupportedService):
    """Unsupported service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
        from ansys.api.geometry.v0.unsupported_pb2_grpc import UnsupportedStub

        self.stub = UnsupportedStub(channel)
        self.commands_stub = CommandsStub(channel)

    @protect_grpc
    def get_import_id_map(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.unsupported_pb2 import ImportIdRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ImportIdRequest(type=kwargs["id_type"].value)

        # Call the gRPC service
        response = self.stub.GetImportIdMap(request)

        # Return the response - formatted as a dictionary
        return {
            "id_map": {k: v.id for k, v in response.id_map.items()},  # dict[str, str]
            "id_type": kwargs["id_type"],
        }

    @protect_grpc
    def set_export_ids(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.unsupported_pb2 import ExportIdRequest, SetExportIdsRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = SetExportIdsRequest(
            export_data=[
                ExportIdRequest(
                    moniker=build_grpc_id(data.moniker),
                    id=data.value,
                    type=data.id_type.value,
                )
                for data in kwargs["export_data"]
            ]
        )

        # Call the gRPC service
        _ = self.stub.SetExportIds(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def set_single_export_id(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.unsupported_pb2 import ExportIdRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = ExportIdRequest(
            moniker=build_grpc_id(kwargs["export_data"].moniker),
            id=kwargs["export_data"].value,
            type=kwargs["export_data"].id_type.value,
        )

        # Call the gRPC service
        _ = self.stub.SetExportId(request)

        # Return the response - formatted as a dictionary
        return {}