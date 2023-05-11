"""Provides the ``Modeler`` class."""
import logging
from pathlib import Path

from ansys.api.geometry.v0.commands_pb2 import UploadFileRequest
from ansys.api.geometry.v0.commands_pb2_grpc import CommandsStub
from beartype.typing import TYPE_CHECKING, Optional, Union
from grpc import Channel

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.connection.defaults import DEFAULT_HOST, DEFAULT_PORT
from ansys.geometry.core.misc import check_type
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.platform.instancemanagement import Instance

    from ansys.geometry.core.connection.local_instance import LocalDockerInstance
    from ansys.geometry.core.designer import Design


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
        is launched through PyPIM. This instance is deleted when the
        :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close >`
        method is called.
    local_instance : LocalDockerInstance, default: None
        Corresponding local instance when the Geometry service is launched through
        the ``launch_local_modeler()`` interface. This instance will be deleted
        when the :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close >`
        method is called.
    timeout : Real, default: 60
        Timeout in seconds to achieve the connection.
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
        timeout: Optional[Real] = 60,
        logging_level: Optional[int] = logging.INFO,
        logging_file: Optional[Union[Path, str]] = None,
    ):
        """Initialize ``Modeler`` class."""
        self._client = GrpcClient(
            host=host,
            port=port,
            channel=channel,
            remote_instance=remote_instance,
            local_instance=local_instance,
            timeout=timeout,
            logging_level=logging_level,
            logging_file=logging_file,
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
        return self._designs[-1]

    def read_existing_design(self) -> "Design":
        """
        Read existing design on the service with the connected client.

        Returns
        -------
        Design
            Design object already living on the server.
        """
        from ansys.geometry.core.designer.design import Design

        design = Design("", self._client, read_existing_design=True)
        self._designs.append(design)
        return self._designs[-1]

    def close(self) -> None:
        """``Modeler`` easy-access method to the client's close method."""
        return self.client.close()

    def _upload_file(self, file_path: str, open_file: bool = False) -> str:
        """
        Upload a file from the client to the server. ``file_path`` must include the extension.

        The new file created on the server will have the same name and extension.

        Parameters
        ----------
        file_path : str
            The path of the file. Must include extension.
        open_file : bool
            Open the file in the Geometry Service.

        Returns
        -------
        file_path : str
            The full path of the uploaded file on the server machine.
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
            UploadFileRequest(data=data, file_name=file_name, open=open_file)
        )
        return response.file_path

    def open_file(self, file_path: str) -> "Design":
        """
        Open a file. ``file_path`` must include the extension.

        This imports a design into the service. On Windows, `.scdocx` and HOOPS Exchange formats
        are supported. On Linux, only `.scdocx` is supported.

        Parameters
        ----------
        file_path : str
            The path of the file. Must include extension.

        Returns
        -------
        Design
            The newly imported design.
        """
        self._upload_file(file_path, True)
        return self.read_existing_design()

    def __repr__(self) -> str:
        """Represent the modeler as a string."""
        lines = []
        lines.append(f"Ansys Geometry Modeler ({hex(id(self))})")
        lines.append("")
        lines.append(str(self._client))
        return "\n".join(lines)
