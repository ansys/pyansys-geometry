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
"""Module containing the Commands Script service implementation for v1."""

import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.commands_script import GRPCCommandsScriptService


class GRPCCommandsScriptServiceV1(GRPCCommandsScriptService):
    """Commands Script service for gRPC communication with the Geometry server.

    This class provides methods to interact with the Geometry server's
    Commands Script service. It is specifically designed for the v1 version
    of the Geometry API.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    @protect_grpc
    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.commands.script_pb2_grpc import ScriptStub

        self.stub = ScriptStub(channel)

    @protect_grpc
    def run_script_file(self, **kwargs) -> dict:  # noqa: D102
        from pathlib import Path
        from typing import Generator

        from ansys.api.discovery.v1.commands.script_pb2 import RunScriptFileRequest

        import ansys.geometry.core.connection.defaults as pygeom_defaults

        def request_generator(
            script_path: Path,
            file_path: str,
            script_args: dict,
            api_version: int | None,
        ) -> Generator[RunScriptFileRequest, None, None]:
            """Generate requests for streaming file upload."""
            msg_buffer = 5 * 1024  # 5KB - for additional message data
            if pygeom_defaults.MAX_MESSAGE_LENGTH - msg_buffer < 0:  # pragma: no cover
                raise ValueError("MAX_MESSAGE_LENGTH is too small for file upload.")

            chunk_size = pygeom_defaults.MAX_MESSAGE_LENGTH - msg_buffer
            with Path.open(script_path, "rb") as file:
                while chunk := file.read(chunk_size):
                    test_req = RunScriptFileRequest(
                        script_path=str(file_path),
                        script_args=script_args,
                        api_version=api_version,
                        data=chunk,
                    )
                    yield test_req

        # Call the gRPC service
        response = self.stub.RunScriptFile(
            request_generator(
                script_path=kwargs["script_path"],
                file_path=kwargs["original_path"],
                script_args=kwargs["script_args"],
                api_version=kwargs["api_version"],
            )
        )

        # Return the response - formatted as a dictionary
        return {
            "success": response.command_response.success,
            "message": response.command_response.message,
            "values": None if not response.values else dict(response.values),
        }
