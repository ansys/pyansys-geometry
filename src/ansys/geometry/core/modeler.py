"""Provides the ``Modeler`` class."""
import logging
from pathlib import Path

from beartype import beartype as check_input_types
from beartype.typing import TYPE_CHECKING, Optional, Union
from grpc import Channel

from ansys.geometry.core.connection import DEFAULT_HOST, DEFAULT_PORT, GrpcClient
from ansys.geometry.core.designer import Design
from ansys.geometry.core.typing import Real

if TYPE_CHECKING:  # pragma: no cover
    from ansys.platform.instancemanagement import Instance


class Modeler:
    """
    Provides for interacting with an open session of
    the Geometry service.

    Parameters
    ----------
    host : str, optional
        Host where the server is running.
        The default is ``DEFAULT_HOST``.
    port : Union[str, int], optional
        Port number where the server is running.
        The default is ``DEFAULT_PORT``.
    channel : ~grpc.Channel, optional
        gRPC channel for server communication.
        The default is ``None``.
    timeout : Real, optional
        Timeout in seconds to achieve the connection.
        The default is ``60``.
    remote_instance : ansys.platform.instancemanagement.Instance
        Corresponding remote instance when the Geometry service
        is launched through PyPIM. This instance is deleted when the
        :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close >`
        method is called.
    logging_level : int, optional
        Logging level to apply to the client.
        The default is ``INFO``.
    logging_file : str, Path, optional
        File to output the log to, if requested. The default is ``None``.
    """

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: Union[str, int] = DEFAULT_PORT,
        channel: Optional[Channel] = None,
        remote_instance: Optional["Instance"] = None,
        timeout: Optional[Real] = 60,
        logging_level: Optional[int] = logging.INFO,
        logging_file: Optional[Union[Path, str]] = None,
    ):
        """Constructor method for the ``Modeler`` class."""
        self._client = GrpcClient(
            host=host,
            port=port,
            channel=channel,
            remote_instance=remote_instance,
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

    @check_input_types
    def create_design(self, name: str) -> Design:
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
        design = Design(name, self._client)
        self._designs.append(design)
        return self._designs[-1]

    def __repr__(self):
        """String representation of the modeler."""
        lines = []
        lines.append(f"Ansys Geometry Modeler ({hex(id(self))})")
        lines.append("")
        lines.append(str(self._client))
        return "\n".join(lines)
