# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.
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
"""Provides for interacting with the Geometry service."""
import logging
import os
from pathlib import Path

from ansys.api.geometry.v0.commands_pb2 import UploadFileRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from ansys.api.geometry.v0.designs_pb2 import OpenRequest
from ansys.api.geometry.v0.designs_pb2_grpc import DesignsStub
from ansys.api.geometry.v0.geometryapplication_pb2 import RunScriptFileRequest
from ansys.api.geometry.v0.geometryapplication_pb2_grpc import GeometryApplicationStub
from beartype.typing import TYPE_CHECKING, Dict, Optional, Tuple, Union
from grpc import Channel

from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.defaults import DEFAULT_HOST, DEFAULT_PORT
from ansys.geometry.core.errors import GeometryRuntimeError, protect_grpc
from ansys.geometry.core.logger import LOG as logger
from ansys.geometry.core.misc.checks import check_type
from ansys.geometry.core.misc.options import ImportOptions
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.platform.instancemanagement import Instance

    from ansys.geometry.core.connection.local_instance import LocalDockerInstance
    from ansys.geometry.core.connection.product_instance import ProductInstance
    from ansys.geometry.core.designer.design import Design


class Modeler:
    """
    Provides for interacting with an open session of the Geometry service.

    Parameters
    ----------
    host : str,  default: DEFAULT_HOST
        Host where the server is running.
    port : Union[str, int], default: DEFAULT_PORT
        Port number where the server is running.
    channel : ~grpc.Channel, default: None
        gRPC channel for server communication.
    remote_instance : ansys.platform.instancemanagement.Instance, default: None
        Corresponding remote instance when the Geometry service
        is launched using `PyPIM <https://github.com/ansys/pypim>`_. This instance
        is deleted when the :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close>`
        method is called.
    local_instance : LocalDockerInstance, default: None
        Corresponding local instance when the Geometry service is launched using the
        :func:`launch_local_modeler<ansys.geometry.core.connection.launcher.launch_local_modeler>`
        method. This instance is deleted when the
        :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close>`
        method is called.
    product_instance : ProductInstance, default: None
        Corresponding local product instance when the product (Discovery or SpaceClaim)
        is launched through the ``launch_modeler_with_geometry_service()``,
        ``launch_modeler_with_discovery()`` or the ``launch_modeler_with_spaceclaim()``
        interface. This instance will be deleted
        when the :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close >`
        method is called.
    timeout : Real, default: 120
        Time in seconds for trying to achieve the connection.
    logging_level : int, default: INFO
        Logging level to apply to the client.
    logging_file : str, Path, default: None
        File to output the log to, if requested.
    """

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: Union[str, int] = DEFAULT_PORT,
        channel: Optional[Channel] = None,
        remote_instance: Optional["Instance"] = None,
        local_instance: Optional["LocalDockerInstance"] = None,
        product_instance: Optional["ProductInstance"] = None,
        timeout: Optional[Real] = 120,
        logging_level: Optional[int] = logging.INFO,
        logging_file: Optional[Union[Path, str]] = None,
        backend_type: Optional[BackendType] = None,
    ):
        """Initialize the ``Modeler`` class."""
        self._client = GrpcClient(
            host=host,
            port=port,
            channel=channel,
            remote_instance=remote_instance,
            local_instance=local_instance,
            product_instance=product_instance,
            timeout=timeout,
            logging_level=logging_level,
            logging_file=logging_file,
            backend_type=backend_type,
        )

        # Design[] maintaining references to all designs within the modeler workspace
        self._designs = []

    @property
    def client(self) -> GrpcClient:
        """``Modeler`` instance client."""
        return self._client

    def create_design(self, name: str) -> "Design":
        """
        Initialize a new design with the connected client.

        Parameters
        ----------
        name : str
            Name for the new design.

        Returns
        -------
        Design
            Design object created on the server.
        """
        from ansys.geometry.core.designer.design import Design

        check_type(name, str)
        design = Design(name, self._client)
        self._designs.append(design)
        if len(self._designs) > 1:
            logger.warning(
                "Most backends only support one design. "
                + "Previous designs may be deleted (on the service) when creating a new one."
            )
        return self._designs[-1]

    def read_existing_design(self) -> "Design":
        """
        Read the existing design on the service with the connected client.

        Returns
        -------
        Design
            Design object already existing on the server.
        """
        from ansys.geometry.core.designer.design import Design

        design = Design("", self._client, read_existing_design=True)
        self._designs.append(design)
        if len(self._designs) > 1:
            logger.warning(
                "Most backends only support one design. "
                + "Previous designs may be deleted (on the service) when reading a new one."
            )
        return self._designs[-1]

    def close(self) -> None:
        """``Modeler`` method for easily accessing the client's close method."""
        return self.client.close()

    def _upload_file(
        self,
        file_path: str,
        open_file: bool = False,
        import_options: ImportOptions = ImportOptions(),
    ) -> str:
        """
        Upload a file from the client to the server.

        Notes
        -----
        This method creates a file on the server that has the same name and extension
        as the file on the client.

        Parameters
        ----------
        file_path : str
            Path of the file to upload. The extension of the file must be included.
        open_file : bool, default: False
            Whether to open the file in the Geometry service.
        import_options : ImportOptions
            Import options that toggle certain features when opening a file.

        Returns
        -------
        file_path : str
            Full path of the file uploaded to the server.
        """
        import os

        if not os.path.exists(file_path):
            raise ValueError(f"Could not find file: {file_path}")
        if os.path.isdir(file_path):
            raise ValueError("File path must lead to a file, not a directory.")

        file_name = os.path.split(file_path)[1]

        with open(file_path, "rb") as file:
            data = file.read()

        c_stub = CommandsStub(self._client.channel)

        response = c_stub.UploadFile(
            UploadFileRequest(
                data=data,
                file_name=file_name,
                open=open_file,
                import_options=import_options.to_dict(),
            )
        )
        return response.file_path

    @protect_grpc
    def open_file(
        self,
        file_path: str,
        upload_to_server: bool = True,
        import_options: ImportOptions = ImportOptions(),
    ) -> "Design":
        """
        Open a file.

        This method imports a design into the service. On Windows, ``.scdocx``
        and HOOPS Exchange formats are supported. On Linux, only the ``.scdocx``
        format is supported.

        If the file is a shattered assembly with external references, the whole containing folder
        will need to be uploaded. Ensure proper folder structure in order to prevent the uploading
        of unnecessary files.

        Parameters
        ----------
        file_path : str
            Path of the file to open. The extension of the file must be included.
        upload_to_server : bool
            True if the service is running on a remote machine. If service is running on the local
            machine, set to False, as there is no reason to upload the file.
        import_options : ImportOptions
            Import options that toggle certain features when opening a file.

        Returns
        -------
        Design
            Newly imported design.
        """
        # Format-specific logic - upload the whole containing folder for assemblies
        if upload_to_server:
            if any(
                ext in str(file_path) for ext in [".CATProduct", ".asm", ".solution", ".sldasm"]
            ):
                dir = os.path.dirname(file_path)
                files = os.listdir(dir)
                for file in files:
                    full_path = os.path.join(dir, file)
                    if full_path != file_path:
                        self._upload_file(full_path)
            self._upload_file(file_path, True, import_options)
        else:
            DesignsStub(self._client.channel).Open(
                OpenRequest(filepath=file_path, import_options=import_options.to_dict())
            )

        return self.read_existing_design()

    def __repr__(self) -> str:
        """Represent the modeler as a string."""
        lines = []
        lines.append(f"Ansys Geometry Modeler ({hex(id(self))})")
        lines.append("")
        lines.append(str(self._client))
        return "\n".join(lines)

    @protect_grpc
    def run_discovery_script_file(
        self, file_path: str, script_args: Dict[str, str], import_design=False
    ) -> Tuple[Dict[str, str], Optional["Design"]]:
        """
        Run a Discovery script file.

        The implied API version of the script should match the API version of the running
        Geometry Service. DMS API versions 23.2.1 and later are supported. DMS is a
        Windows-based modeling service that has been containerized to ease distribution,
        execution, and remotability operations.

        Parameters
        ----------
        file_path : str
            Path of the file. The extension of the file must be included.
        script_args : dict[str, str]
            Arguments to pass to the script.
        import_design : bool, default: False
            Whether to refresh the current design from the service. When the script
            is expected to modify the existing design, set this to ``True`` to retrieve
            up-to-date design data. When this is set to ``False`` (default) and the
            script modifies the current design, the design may be out-of-sync.

        Returns
        -------
        dict[str, str]
            Values returned from the script.
        Design, optional
            Up-to-date current design. This is only returned if ``import_design=True``.

        Raises
        ------
        GeometryRuntimeError
            If the Discovery script fails to run. Otherwise, assume that the script
            ran successfully.
        """
        serv_path = self._upload_file(file_path)
        ga_stub = GeometryApplicationStub(self._client.channel)
        request = RunScriptFileRequest(
            script_path=serv_path,
            script_args=script_args,
        )

        self.client.log.debug(f"Running Discovery script file at {file_path}...")
        response = ga_stub.RunScriptFile(request)

        if not response.success:
            raise GeometryRuntimeError(response.message)

        self.client.log.debug(f"Script result message: {response.message}")

        if import_design:
            return (response.values, self.read_existing_design())
        else:
            return response.values
