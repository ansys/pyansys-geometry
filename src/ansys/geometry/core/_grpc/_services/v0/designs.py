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
from .conversions import (
    _check_write_body_facets_input,
    build_grpc_id,
    from_design_file_format_to_grpc_part_export_format,
    from_grpc_tess_to_pd,
    from_tess_options_to_grpc_tess_options,
)


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
        from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub

        self.designs_stub = DesignsStub(channel)
        self.commands_stub = CommandsStub(channel)

    @protect_grpc
    def open(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.designs_pb2 import OpenRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = OpenRequest(
            filepath=kwargs["filepath"],
            import_options=kwargs["import_options"].to_dict(),
        )

        # Call the gRPC service
        _ = self.designs_stub.Open(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def new(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.designs_pb2 import NewRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = NewRequest(name=kwargs["name"])

        # Call the gRPC service
        response = self.designs_stub.New(request)

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
        _ = self.designs_stub.Close(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def put_active(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = build_grpc_id(id=kwargs["design_id"])

        # Call the gRPC service
        _ = self.designs_stub.PutActive(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def save_as(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.designs_pb2 import SaveAsRequest

        _check_write_body_facets_input(kwargs["backend_version"], kwargs["write_body_facets"])

        # Create the request - assumes all inputs are valid and of the proper type
        request = SaveAsRequest(
            filepath=kwargs["filepath"], write_body_facets=kwargs["write_body_facets"]
        )

        # Call the gRPC service
        _ = self.designs_stub.SaveAs(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def download_export(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.designs_pb2 import DownloadExportFileRequest

        _check_write_body_facets_input(kwargs["backend_version"], kwargs["write_body_facets"])

        # Create the request - assumes all inputs are valid and of the proper type
        request = DownloadExportFileRequest(
            format=from_design_file_format_to_grpc_part_export_format(kwargs["format"]),
            write_body_facets=kwargs["write_body_facets"],
        )

        # Call the gRPC service
        response = self.designs_stub.DownloadExportFile(request)

        # Return the response - formatted as a dictionary
        data = bytes()
        data += response.data
        return {"data": data}

    @protect_grpc
    def stream_download_export(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.designs_pb2 import DownloadExportFileRequest

        _check_write_body_facets_input(kwargs["backend_version"], kwargs["write_body_facets"])

        # Create the request - assumes all inputs are valid and of the proper type
        request = DownloadExportFileRequest(
            format=from_design_file_format_to_grpc_part_export_format(kwargs["format"]),
            write_body_facets=kwargs["write_body_facets"],
        )

        # Call the gRPC service
        response = self.designs_stub.StreamDownloadExportFile(request)

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
        _ = self.designs_stub.Insert(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def get_active(self, **kwargs) -> dict:  # noqa: D102
        from google.protobuf.empty_pb2 import Empty

        # Call the gRPC service
        response = self.designs_stub.GetActive(request=Empty())

        # Return the response - formatted as a dictionary
        if response:
            return {
                "design_id": response.id,
                "main_part_id": response.main_part.id,
                "name": response.name,
            }

    @protect_grpc
    def upload_file(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.geometry.v0.commands_pb2 import UploadFileRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = UploadFileRequest(
            data=kwargs["data"],
            file_name=kwargs["file_name"],
            open=kwargs["open_file"],
            import_options=kwargs["import_options"].to_dict(),
        )

        # Call the gRPC service
        response = self.commands_stub.UploadFile(request)

        # Return the response - formatted as a dictionary
        return {"file_path": response.file_path}

    @protect_grpc
    def upload_file_stream(self, **kwargs) -> dict:  # noqa: D102
        from pathlib import Path
        from typing import TYPE_CHECKING, Generator

        from ansys.api.geometry.v0.commands_pb2 import UploadFileRequest

        import ansys.geometry.core.connection.defaults as pygeom_defaults

        if TYPE_CHECKING:  # pragma: no cover
            from ansys.geometry.core.misc.options import ImportOptions

        def request_generator(
            file_path: Path, open_file: bool, import_options: "ImportOptions"
        ) -> Generator[UploadFileRequest, None, None]:
            """Generate requests for streaming file upload."""
            msg_buffer = 5 * 1024  # 5KB - for additional message data
            if pygeom_defaults.MAX_MESSAGE_LENGTH - msg_buffer < 0:  # pragma: no cover
                raise ValueError("MAX_MESSAGE_LENGTH is too small for file upload.")

            chunk_size = pygeom_defaults.MAX_MESSAGE_LENGTH - msg_buffer
            with Path.open(file_path, "rb") as file:
                while chunk := file.read(chunk_size):
                    yield UploadFileRequest(
                        data=chunk,
                        file_name=file_path.name,
                        open=open_file,
                        import_options=import_options.to_dict(),
                    )

        # Call the gRPC service
        response = self.commands_stub.StreamFileUpload(
            request_generator(
                file_path=kwargs["file_path"],
                open_file=kwargs["open_file"],
                import_options=kwargs["import_options"],
            )
        )

        # Return the response - formatted as a dictionary
        return {"file_path": response.file_path}

    @protect_grpc
    def stream_design_tessellation(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.dbu.v0.designs_pb2 import DesignTessellationRequest

        # If there are options, convert to gRPC options
        options = (
            from_tess_options_to_grpc_tess_options(kwargs["options"])
            if kwargs["options"] is not None
            else None
        )

        # Create the request - assumes all inputs are valid and of the proper type
        request = DesignTessellationRequest(
            options=options
        )

        # Call the gRPC service
        response = self.designs_stub.StreamDesignTessellation(request)

        # Return the response - formatted as a dictionary
        tess_map = {}
        for elem in response:
            for body_id, body_tess in elem.body_tessellation.items():
                tess = {}
                for face_id, face_tess in body_tess.face_tessellation.items():
                    tess[face_id] = from_grpc_tess_to_pd(face_tess)
                tess_map[body_id] = tess

        return {
            "tessellation": tess_map,
        }