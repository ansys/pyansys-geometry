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
"""Provides for interacting with the Geometry service."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Generator, Optional

from grpc import Channel

from ansys.api.dbu.v0.dbuapplication_pb2 import RunScriptFileRequest
from ansys.api.dbu.v0.dbuapplication_pb2_grpc import DbuApplicationStub
from ansys.api.dbu.v0.designs_pb2 import OpenRequest
from ansys.api.dbu.v0.designs_pb2_grpc import DesignsStub
from ansys.api.geometry.v0.commands_pb2 import UploadFileRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from ansys.geometry.core.connection.backend import ApiVersions, BackendType
from ansys.geometry.core.connection.client import GrpcClient
import ansys.geometry.core.connection.defaults as pygeom_defaults
from ansys.geometry.core.errors import GeometryRuntimeError, protect_grpc
from ansys.geometry.core.misc.checks import check_type, deprecated_method, min_backend_version
from ansys.geometry.core.misc.options import ImportOptions
from ansys.geometry.core.tools.measurement_tools import MeasurementTools
from ansys.geometry.core.tools.prepare_tools import PrepareTools
from ansys.geometry.core.tools.repair_tools import RepairTools
from ansys.geometry.core.tools.unsupported import UnsupportedCommands
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.connection.docker_instance import LocalDockerInstance
    from ansys.geometry.core.connection.product_instance import ProductInstance
    from ansys.geometry.core.designer.design import Design
    from ansys.geometry.core.designer.geometry_commands import GeometryCommands
    from ansys.platform.instancemanagement import Instance


class Modeler:
    """Provides for interacting with an open session of the Geometry service.

    Parameters
    ----------
    host : str,  default: DEFAULT_HOST
        Host where the server is running.
    port : str | int, default: DEFAULT_PORT
        Port number where the server is running.
    channel : ~grpc.Channel, default: None
        gRPC channel for server communication.
    remote_instance : ansys.platform.instancemanagement.Instance, default: None
        Corresponding remote instance when the Geometry service
        is launched using `PyPIM <https://github.com/ansys/pypim>`_. This instance
        is deleted when the :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close>`
        method is called.
    docker_instance : LocalDockerInstance, default: None
        Corresponding local Docker instance when the Geometry service is launched using the
        :func:`launch_docker_modeler<ansys.geometry.core.connection.launcher.launch_docker_modeler>`
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
        host: str = pygeom_defaults.DEFAULT_HOST,
        port: str | int = pygeom_defaults.DEFAULT_PORT,
        channel: Channel | None = None,
        remote_instance: Optional["Instance"] = None,
        docker_instance: Optional["LocalDockerInstance"] = None,
        product_instance: Optional["ProductInstance"] = None,
        timeout: Real = 120,
        logging_level: int = logging.INFO,
        logging_file: Path | str | None = None,
        backend_type: BackendType | None = None,
    ):
        """Initialize the ``Modeler`` class."""
        from ansys.geometry.core.designer.geometry_commands import GeometryCommands

        self._grpc_client = GrpcClient(
            host=host,
            port=port,
            channel=channel,
            remote_instance=remote_instance,
            docker_instance=docker_instance,
            product_instance=product_instance,
            timeout=timeout,
            logging_level=logging_level,
            logging_file=logging_file,
            backend_type=backend_type,
        )

        # Single design for the Modeler
        self._design: Optional["Design"] = None

        # Enabling tools/commands for all: repair and prepare tools, geometry commands
        self._measurement_tools = MeasurementTools(self._grpc_client)
        self._repair_tools = RepairTools(self._grpc_client, self)
        self._prepare_tools = PrepareTools(self._grpc_client)
        self._geometry_commands = GeometryCommands(self._grpc_client)
        self._unsupported = UnsupportedCommands(self._grpc_client, self)

    @property
    def client(self) -> GrpcClient:
        """``Modeler`` instance client."""
        return self._grpc_client

    @property
    def design(self) -> "Design":
        """Retrieve the design within the modeler workspace."""
        return self._design

    @property
    @deprecated_method(alternative="design", version="0.9.0", remove="0.11.0")
    def designs(self) -> dict[str, "Design"]:
        """Retrieve the design within the modeler workspace.

        Notes
        -----
        This method is deprecated. Use the :func:`design` property instead.
        """
        return {self._design.id: self._design}

    def create_design(self, name: str) -> "Design":
        """Initialize a new design with the connected client.

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

        # If a previous design was available... inform the user that it will be deleted
        # when creating a new design.
        if self._design is not None and self._design.is_active:
            self.client.log.warning("Closing previous design before creating a new one.")
            self._design.close()

        # Create the new design
        design = Design(name, self)

        # Update the design stored in the modeler
        self._design = design

        return self._design

    def get_active_design(self, sync_with_backend: bool = True) -> "Design":
        """Get the active design on the modeler object.

        Parameters
        ----------
        sync_with_backend : bool, default: True
            Whether to sync the active design with the remote service. If set to False,
            the active design may be out-of-sync with the remote service. This is useful
            when the active design is known to be up-to-date.

        Returns
        -------
        Design
            Design object already existing on the modeler.
        """
        if self._design is not None and self._design.is_active:
            # Check if sync_with_backend is requested
            if sync_with_backend:
                self._design._update_design_inplace()
            return self._design
        else:
            self.client.log.warning("No active design available.")

        return None

    def read_existing_design(self) -> "Design":
        """Read the existing design on the service with the connected client.

        Returns
        -------
        Design
            Design object already existing on the server.
        """
        from ansys.geometry.core.designer.design import Design

        # Simply deactivate the existing design in case it is active...
        # - If it is the same design, it will be re-read (but we should not close it on the server)
        # - If it is a different design, it was closed previously (via open_file or create_design)
        if self._design is not None and self._design.is_active:
            self._design._is_active = False

        self._design = Design("", self, read_existing_design=True)

        return self._design

    def close(self, close_design: bool = True) -> None:
        """Access the client's close method.

        Parameters
        ----------
        close_design : bool, default: True
            Whether to close the design before closing the client.
        """
        # Close design (if requested)
        if close_design and self._design is not None:
            self._design.close()

        # Close the client
        self.client.close()

    def exit(self, close_design: bool = True) -> None:
        """Access the client's close method.

        Parameters
        ----------
        close_design : bool, default: True
            Whether to close the design before closing the client.

        Notes
        -----
        This method is calling the same method as
        :func:`close() <ansys.geometry.core.modeler.Modeler.close>`.
        """
        self.close(close_design=close_design)

    @protect_grpc
    def _upload_file(
        self,
        file_path: str,
        open_file: bool = False,
        import_options: ImportOptions = ImportOptions(),
    ) -> str:
        """Upload a file from the client to the server.

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

        Notes
        -----
        This method creates a file on the server that has the same name and extension
        as the file on the client.
        """
        from pathlib import Path

        fp_path = Path(file_path).resolve()

        if not fp_path.exists():
            raise ValueError(f"Could not find file: {file_path}")
        if fp_path.is_dir():
            raise ValueError("File path must lead to a file, not a directory.")

        file_name = fp_path.name

        with fp_path.open(mode="rb") as file:
            data = file.read()

        c_stub = CommandsStub(self.client.channel)

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
    def _upload_file_stream(
        self,
        file_path: str,
        open_file: bool = False,
        import_options: ImportOptions = ImportOptions(),
    ) -> str:
        """Upload a file from the client to the server via streaming.

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

        Notes
        -----
        This method creates a file on the server that has the same name and extension
        as the file on the client.
        """
        from pathlib import Path

        fp_path = Path(file_path).resolve()

        if not fp_path.exists():
            raise ValueError(f"Could not find file: {file_path}")
        if fp_path.is_dir():
            raise ValueError("File path must lead to a file, not a directory.")

        c_stub = CommandsStub(self.client.channel)

        response = c_stub.StreamFileUpload(
            self._generate_file_chunks(fp_path, open_file, import_options)
        )
        return response.file_path

    def _generate_file_chunks(
        self, file_path: Path, open_file: bool, import_options: ImportOptions
    ) -> Generator[UploadFileRequest, None, None]:
        """Generate appropriate chunk sizes for uploading files.

        Parameters
        ----------
        file_path : Path
            Path of the file to upload. The extension of the file must be included.
        open_file : bool
            Whether to open the file in the Geometry service.
        import_options : ImportOptions
            Import options that toggle certain features when opening a file.

        Yields
        ------
        UploadFileRequest
            Request object for uploading a file in chunks.
        """
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

    def open_file(
        self,
        file_path: str | Path,
        upload_to_server: bool = True,
        import_options: ImportOptions = ImportOptions(),
    ) -> "Design":
        """Open a file.

        This method imports a design into the service. On Windows, ``.scdocx``
        and HOOPS Exchange formats are supported. On Linux, only the ``.scdocx``
        format is supported.

        If the file is a shattered assembly with external references, the whole containing folder
        will need to be uploaded. Ensure proper folder structure in order to prevent the uploading
        of unnecessary files.

        Parameters
        ----------
        file_path : str, ~pathlib.Path
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
        # Use str format of Path object here
        file_path = str(file_path) if isinstance(file_path, Path) else file_path

        # Close the existing design if it is active
        if self._design is not None and self._design.is_active:
            self._design.close()

        # Format-specific logic - upload the whole containing folder for assemblies
        if upload_to_server:
            fp_path = Path(file_path)
            file_size_kb = fp_path.stat().st_size
            if any(
                ext in str(file_path) for ext in [".CATProduct", ".asm", ".solution", ".sldasm"]
            ):
                dir = fp_path.parent
                for file in dir.iterdir():
                    full_path = file.resolve()
                    if full_path != fp_path:
                        if full_path.stat().st_size < pygeom_defaults.MAX_MESSAGE_LENGTH:
                            self._upload_file(full_path)
                        elif self.client.backend_version >= (25, 2, 0):
                            self._upload_file_stream(full_path)
                        else:  # pragma: no cover
                            raise RuntimeError(
                                "File is too large to upload."
                                " Service versions above 25R2 support streaming."
                            )

            if file_size_kb < pygeom_defaults.MAX_MESSAGE_LENGTH:
                self._upload_file(file_path, True, import_options)
            elif self.client.backend_version >= (25, 2, 0):
                self._upload_file_stream(file_path, True, import_options)
            else:  # pragma: no cover
                raise RuntimeError(
                    "File is too large to upload. Service versions above 25R2 support streaming."
                )
        else:
            DesignsStub(self.client.channel).Open(
                OpenRequest(filepath=file_path, import_options=import_options.to_dict())
            )

        return self.read_existing_design()

    def __repr__(self) -> str:
        """Represent the modeler as a string."""
        lines = []
        lines.append(f"Ansys Geometry Modeler ({hex(id(self))})")
        lines.append("")
        lines.append(str(self.client))
        return "\n".join(lines)

    @protect_grpc
    def run_discovery_script_file(
        self,
        file_path: str | Path,
        script_args: dict[str, str] | None = None,
        import_design: bool = False,
        api_version: int | str | ApiVersions = None,
    ) -> tuple[dict[str, str], Optional["Design"]]:
        """Run a Discovery script file.

        .. note::

            If arguments are passed to the script, they must be in the form of a dictionary.
            On the server side, the script will receive the arguments as a dictionary of strings,
            under the variable name ``argsDict``. For example, if the script is called with the
            arguments ``run_discovery_script_file(..., script_args = {"length": "20"}, ...)``,
            the script will receive the dictionary ``argsDict`` with the key-value pair
            ``{"length": "20"}``.

        .. note::

            If an output is expected from the script, it will be returned as a dictionary of
            strings. The keys and values of the dictionary are the variables and their values
            that the script returns. However, it is necessary that the script creates a
            dictionary called ``result`` with the variables and their values that are expected
            to be returned. For example, if the script is expected to return the number of bodies
            in the design, the script should create a dictionary called ``result`` with the
            key-value pair ``{"numBodies": numBodies}``, where ``numBodies`` is the number of
            bodies in the design.

        The implied API version of the script should match the API version of the running
        Geometry Service. DMS API versions 24.1 and later are supported. DMS is a
        Windows-based modeling service that has been containerized to ease distribution,
        execution, and remotability operations.

        Parameters
        ----------
        file_path : str | ~pathlib.Path
            Path of the file. The extension of the file must be included.
        script_args : dict[str, str], optional.
            Arguments to pass to the script. By default, ``None``.
        import_design : bool, optional.
            Whether to refresh the current design from the service. When the script
            is expected to modify the existing design, set this to ``True`` to retrieve
            up-to-date design data. When this is set to ``False`` (default) and the
            script modifies the current design, the design may be out-of-sync. By default,
            ``False``.
        api_version : int | str | ApiVersions, optional
            The scripting API version to use. For example, version 24.1 can be passed as
            an integer 241, a string "241" or using the
            ``ansys.geometry.core.connection.backend.ApiVersions`` enum class.
            By default, ``None``. When specified, the service will attempt to run the script with
            the specified API version. If the API version is not supported, the service will raise
            an error. If you are using Discovery or SpaceClaim, the product will determine the API
            version to use, so there is no need to specify this parameter.

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

        Notes
        -----
            The Ansys Geometry Service only supports scripts that are of the
            same version as the running service. Any ``api_version`` input will
            be ignored.
        """
        # Use str format of Path object here
        file_path = str(file_path) if isinstance(file_path, Path) else file_path

        # Check if API version is specified... if so, validate it
        if api_version is not None:
            if BackendType.is_headless_service(self.client.backend_type):
                self.client.log.warning(
                    "The Ansys Geometry Service only supports "
                    "scripts that are of its same API version."
                )
                self.client.log.warning("Ignoring specified API version.")
                api_version = None
            else:  # pragma: no cover
                # Testing is only performed on Windows Service...
                # but this method has been tested independently
                api_version = ApiVersions.parse_input(api_version)

        serv_path = self._upload_file(file_path)
        ga_stub = DbuApplicationStub(self.client.channel)
        request = RunScriptFileRequest(
            script_path=serv_path,
            script_args=script_args,
            api_version=api_version.value if api_version is not None else None,
        )

        self.client.log.debug(f"Running Discovery script file at {file_path}...")
        response = ga_stub.RunScriptFile(request)

        if not response.success:
            raise GeometryRuntimeError(response.message)

        self.client.log.debug(f"Script result message: {response.message}")

        if import_design:
            return (dict(response.values), self.read_existing_design())
        else:
            return dict(response.values)

    @property
    def repair_tools(self) -> RepairTools:
        """Access to repair tools."""
        return self._repair_tools

    @property
    def prepare_tools(self) -> PrepareTools:
        """Access to prepare tools."""
        return self._prepare_tools

    @property
    @min_backend_version(24, 2, 0)
    def measurement_tools(self) -> MeasurementTools:
        """Access to measurement tools."""
        return self._measurement_tools

    @property
    def geometry_commands(self) -> "GeometryCommands":
        """Access to geometry commands."""
        return self._geometry_commands

    @property
    def unsupported(self) -> "UnsupportedCommands":
        """Access to unsupported commands."""
        return self._unsupported

    @min_backend_version(25, 1, 0)
    def get_service_logs(
        self,
        all_logs: bool = False,
        dump_to_file: bool = False,
        logs_folder: str | Path | None = None,
    ) -> str | dict[str, str] | Path:
        """Get the service logs.

        Parameters
        ----------
        all_logs : bool, default: False
            Flag indicating whether all logs should be retrieved. By default,
            only the current logs are retrieved.
        dump_to_file : bool, default: False
            Flag indicating whether the logs should be dumped to a file.
            By default, the logs are not dumped to a file.
        logs_folder : str,  Path or None, default: None
            Name of the folder where the logs should be dumped. This parameter
            is only used if the ``dump_to_file`` parameter is set to ``True``.

        Returns
        -------
        str
            Service logs as a string. This is returned if the ``dump_to_file`` parameter
            is set to ``False``.
        dict[str, str]
            Dictionary containing the logs. The keys are the logs names,
            and the values are the logs as strings. This is returned if the ``all_logs``
            parameter is set to ``True`` and the ``dump_to_file`` parameter
            is set to ``False``.
        Path
            Path to the folder containing the logs (if the ``all_logs``
            parameter is set to ``True``) or the path to the log file (if only
            the current logs are retrieved). The ``dump_to_file`` parameter
            must be set to ``True``.
        """
        return self.client._get_service_logs(
            all_logs=all_logs, dump_to_file=dump_to_file, logs_folder=logs_folder
        )
