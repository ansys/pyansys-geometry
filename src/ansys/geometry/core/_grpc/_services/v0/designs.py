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
"""Module containing the designs service implementation for v0."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.designs import GRPCDesignsService
from .conversions import build_grpc_id, from_design_file_format_to_grpc_part_export_format


class GRPCDesignsServiceV0(GRPCDesignsService):  # pragma: no cover
    """Designs service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    designs service. It is specifically designed for the v0 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.dbu.v0.designs_pb2_grpc import DesignsStub

        self.stub = DesignsStub(channel)

    @protect_grpc
    def open(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.designs_pb2 import OpenRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = OpenRequest(
            filepath=kwargs["filepath"],
            import_options=kwargs["import_options"].to_dict(),
        )

        # Call the gRPC service
        _ = self.stub.Open(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def new(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.designs_pb2 import NewRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = NewRequest(name=kwargs["name"])

        # Call the gRPC service
        response = self.stub.New(request)

        # Return the response - formatted as a dictionary
        return {
            "design_id": response.id,
            "main_part_id": response.main_part.id,
        }

    @protect_grpc
    def close(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(id=kwargs["design_id"])

        # Call the gRPC service
        _ = self.stub.Close(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def put_active(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(id=kwargs["design_id"])

        # Call the gRPC service
        _ = self.stub.PutActive(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def save_as(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.designs_pb2 import SaveAsRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = SaveAsRequest(filepath=kwargs["filepath"])

        # Call the gRPC service
        _ = self.stub.SaveAs(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def download_export(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.designs_pb2 import DownloadExportFileRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = DownloadExportFileRequest(
            format=from_design_file_format_to_grpc_part_export_format(kwargs["format"])
        )

        # Call the gRPC service
        response = self.stub.DownloadExportFile(request)

        # Return the response - formatted as a dictionary
        data = bytes()
        data += response.data
        return {"data": data}

    @protect_grpc
    def stream_download_export(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.designs_pb2 import DownloadExportFileRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = DownloadExportFileRequest(
            format=from_design_file_format_to_grpc_part_export_format(kwargs["format"])
        )

        # Call the gRPC service
        response = self.stub.StreamDownloadExportFile(request)

        # Return the response - formatted as a dictionary
        data = bytes()
        for elem in response:
            data += elem.data

        return {"data": data}

    @protect_grpc
    def insert(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.designs_pb2 import InsertRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = InsertRequest(
            filepath=kwargs["filepath"], import_named_selections=kwargs["import_named_selections"]
        )

        # Call the gRPC service
        _ = self.stub.Insert(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def get_active(self, **kwargs) -> dict:  # noqa: D102
        from google.protobuf.empty_pb2 import Empty

        # Call the gRPC service
        response = self.stub.GetActive(request=Empty())

        # Return the response - formatted as a dictionary
        if response:
            return {
                "design_id": response.id,
                "main_part_id": response.main_part.id,
                "name": response.name,
            }
