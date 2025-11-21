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
"""Module containing the designs service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.designs import GRPCDesignsService


class GRPCDesignsServiceV1(GRPCDesignsService):  # pragma: no cover
    """Designs service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    designs service. It is specifically designed for the v1 version of the
    Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.design.designdoc_pb2_grpc import DesignDocStub
        from ansys.api.discovery.v1.commands.file_pb2_grpc import FileStub

        self.stub = DesignDocStub(channel)
        self.file_stub = FileStub(channel)

    @protect_grpc
    def open(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def new(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def get_assembly(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def close(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def put_active(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def save_as(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def download_export(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def stream_download_export(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def insert(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def get_active(self, **kwargs) -> dict:  # noqa: D102
        from google.protobuf.empty_pb2 import Empty

        # Call the gRPC service
        response = self.stub.Get(request=Empty())

        # Return the response - formatted as a dictionary
        if response:
            return {
                "design_id": response.design.id,
                "main_part_id": response.design.main_part.id,
                "name": response.design.name,
            }

    @protect_grpc
    def upload_file(self, **kwargs) -> dict:  # noqa: D102
        from pathlib import Path
        from typing import TYPE_CHECKING, Generator

        from ansys.api.discovery.v1.commands.file_pb2 import OpenRequest, OpenMode
        from ansys.api.discovery.v1.commonenums_pb2 import FileFormat
        import ansys.geometry.core.connection.defaults as pygeom_defaults

        if TYPE_CHECKING:  # pragma: no cover
            from ansys.geometry.core.misc.options import ImportOptions

        # ---- 1) Extract and log kwargs ----
        raw_file_path = kwargs.get("file_path")
        open_file = kwargs.get("open_file", False)
        import_options = kwargs.get("import_options")  # may be None

        print("[upload_file] raw_file_path =", raw_file_path)
        print("[upload_file] open_file    =", open_file)
        print("[upload_file] import_opts  =", type(import_options))

        if raw_file_path is None:
            raise ValueError("[upload_file] 'file_path' kwarg is required")

        file_path = Path(raw_file_path)

        # ---- 2) Validate file existence & readability ----
        if not file_path.exists():
            raise FileNotFoundError(f"[upload_file] File does not exist: {file_path!r}")
        if not file_path.is_file():
            raise ValueError(f"[upload_file] Path is not a file: {file_path!r}")

        try:
            size = file_path.stat().st_size
        except Exception as e:
            print("[upload_file] Error stating file:", e)
            raise

        print(f"[upload_file] File exists, size = {size} bytes")

        # ---- 3) Safe helper for import_options.to_dict() ----
        def import_options_to_dict(import_opts: "ImportOptions | None"):
            if import_opts is None:
                print("[upload_file] import_options is None → using empty dict")
                return {}
            try:
                d = import_opts.to_dict()
                print("[upload_file] import_options.to_dict() succeeded")
                return d
            except Exception as e:
                print("[upload_file] ERROR in import_options.to_dict():", repr(e))
                import traceback
                traceback.print_exc()
                # Re-raise so we see the real cause instead of UNKNOWN / iterating requests
                raise

        # Precompute once so we don't repeat this in each chunk
        import_options_dict = import_options_to_dict(import_options)

        # ---- 4) Request generator with strong logging & exception surfacing ----
        def request_generator(
            file_path: Path, open_file: bool, import_options_dict: dict
        ) -> Generator[OpenRequest, None, None]:
            """Generate requests for streaming file upload."""
            import traceback

            msg_buffer = 5 * 1024  # 5KB - for additional message data
            if pygeom_defaults.MAX_MESSAGE_LENGTH - msg_buffer < 0:  # pragma: no cover
                raise ValueError(
                    "[upload_file] MAX_MESSAGE_LENGTH is too small for file upload"
                )

            chunk_size = pygeom_defaults.MAX_MESSAGE_LENGTH - msg_buffer
            print(f"[upload_file] Using chunk_size = {chunk_size} bytes")

            try:
                with file_path.open("rb") as file:
                    chunk_index = 0
                    while True:
                        chunk = file.read(chunk_size)
                        if not chunk:
                            print("[upload_file] No more data to read, stopping generator")
                            break

                        print(
                            f"[upload_file] Yielding chunk {chunk_index}, "
                            f"len={len(chunk)}"
                        )

                        yield OpenRequest(
                            data=chunk,
                            open_mode=OpenMode.OPENMODE_NEW,
                            file_format= FileFormat.FILEFORMAT_DISCO,
                            import_options=import_options_dict,
                        )
                        chunk_index += 1
            except Exception as e:
                print("[upload_file] EXCEPTION inside request_generator:")
                traceback.print_exc()
                # Re-raise so gRPC wraps it, but you still see the root traceback
                raise

        # ---- 5) Call the gRPC service, with extra logging ----
        gen = request_generator(
            file_path=file_path,
            open_file=open_file,
            import_options_dict=import_options_dict,
        )

        from grpc import RpcError

        try:
            print("[upload_file] Calling file_stub.Open(...)")
            response = self.file_stub.Open(gen)
            print("[upload_file] file_stub.Open(...) returned successfully")
        except RpcError as rpc_exc:
            # This is what you currently see as UNKNOWN / Exception iterating requests
            print("[upload_file] RpcError caught in upload_file:")
            print("  code   :", rpc_exc.code())
            print("  details:", rpc_exc.details())
            import traceback

            traceback.print_exc()
            # Re-raise so the higher-level wrapper (protect_grpc) can do its thing
            raise

        # ---- 6) Return the response - formatted as a dictionary ----
        return {"file_path": response.design.path}


    @protect_grpc
    def upload_file_stream(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commands.file_pb2 import UploadFileRequest

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
    def stream_design_tessellation(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError

    @protect_grpc
    def download_file(self, **kwargs) -> dict:  # noqa: D102
        raise NotImplementedError
