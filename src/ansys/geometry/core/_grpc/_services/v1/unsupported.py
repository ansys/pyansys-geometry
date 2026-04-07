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
"""Module containing the unsupported service implementation for v1."""

from ansys.api.discovery.v1.commands.unsupported_pb2 import SetExportIdData, SetExportIdRequest
import grpc

from ansys.geometry.core.errors import protect_grpc

from ..base.unsupported import GRPCUnsupportedService
from .conversions import build_grpc_id


class GRPCUnsupportedServiceV1(GRPCUnsupportedService):
    """Unsupported service for gRPC communication with the Geometry server.

    Parameters
    ----------
    channel : grpc.Channel
        The gRPC channel to the server.
    """

    def __init__(self, channel: grpc.Channel):  # noqa: D102
        from ansys.api.discovery.v1.commands.file_pb2_grpc import FileStub
        from ansys.api.discovery.v1.commands.unsupported_pb2_grpc import UnsupportedStub

        self.stub = UnsupportedStub(channel)
        self.file_stub = FileStub(channel)

    @protect_grpc
    def load_addin(self, **kwargs) -> dict:  # noqa: D102
        from pathlib import Path
        from typing import Generator

        from ansys.api.discovery.v1.commands.file_pb2 import LoadAddinRequest

        import ansys.geometry.core.connection.defaults as pygeom_defaults

        def request_generator(
            addin_path: Path,
            addin_name: str,
        ) -> Generator[LoadAddinRequest, None, None]:
            """Generate requests for streaming file upload."""
            msg_buffer = 5 * 1024  # 5KB - for additional message data
            if pygeom_defaults.MAX_MESSAGE_LENGTH - msg_buffer < 0:  # pragma: no cover
                raise ValueError("MAX_MESSAGE_LENGTH is too small for file upload.")

            chunk_size = pygeom_defaults.MAX_MESSAGE_LENGTH - msg_buffer
            with Path.open(addin_path, "rb") as file:
                while chunk := file.read(chunk_size):
                    test_req = LoadAddinRequest(
                        addin_path=addin_path.stem,
                        addin_name=addin_name,
                        data=chunk,
                    )
                    yield test_req

        # Call the gRPC service
        response = self.file_stub.LoadAddin(
            request_generator(
                addin_path=kwargs["addin_path"],
                addin_name=kwargs["addin_name"],
            )
        )

        # Return the response - formatted as a dictionary
        return {"command_response": response.command_response}

    @protect_grpc
    def run_addin_method(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commands.file_pb2 import RunAddinMethodRequest

        from .conversions import from_grpc_any, to_grpc_any

        # Create the request - arguments are converted from Python types to Any
        request = RunAddinMethodRequest(
            addin_name=kwargs["addin_name"],
            method_name=kwargs["method_name"],
            arguments=[to_grpc_any(arg) for arg in kwargs.get("arguments", [])],
        )

        # Call the gRPC service
        response = self.file_stub.RunAddinMethod(request)

        # Convert the response from Any back to a Python type
        return_value = from_grpc_any(response.return_value)

        # Return the response - formatted as a dictionary
        return {
            "return_value": return_value,
            "command_response": response.command_response
        }

    @protect_grpc
    def get_import_id_map(self, **kwargs) -> dict:  # noqa: D102
        from ansys.api.discovery.v1.commands.unsupported_pb2 import GetImportIdMapRequest

        # Create the request - assumes all inputs are valid and of the proper type
        request = GetImportIdMapRequest(type=kwargs["id_type"].value)

        # Call the gRPC service
        response = self.stub.GetImportIdMap(request)

        # Return the response - formatted as a dictionary
        return {
            "id_map": {k: v.id for k, v in response.id_map.items()},  # dict[str, str]
            "id_type": kwargs["id_type"],
        }

    @protect_grpc
    def set_export_ids(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = SetExportIdRequest(
            export_data=[
                SetExportIdData(
                    moniker_id=build_grpc_id(data.moniker),
                    id=data.value,
                    type=data.id_type.value,
                )
                for data in kwargs["export_data"]
            ]
        )

        # Call the gRPC service
        _ = self.stub.SetExportId(request)

        # Return the response - formatted as a dictionary
        return {}

    @protect_grpc
    def set_single_export_id(self, **kwargs) -> dict:  # noqa: D102
        # Create the request - assumes all inputs are valid and of the proper type
        request = SetExportIdRequest(
            export_data=[
                SetExportIdData(
                    moniker_id=build_grpc_id(kwargs["export_data"].moniker),
                    id=kwargs["export_data"].value,
                    type=kwargs["export_data"].id_type.value,
                )
            ]
        )

        # Call the gRPC service
        _ = self.stub.SetExportId(request)

        # Return the response - formatted as a dictionary
        return {}
