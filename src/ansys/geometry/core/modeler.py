"""``Modeler`` class module."""
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
    Provides a modeler class for interacting with an open session of
    the Geometry service.

    Parameters
    ----------
    host : str,  default: DEFAULT_HOST
        Host where the server is running.
    port : Union[str, int], default: DEFAULT_PORT
        Port number where the server is running.
    channel : ~grpc.Channel, default: None
        gRPC channel for server communication.
    remote_instance : ansys.platform.instancemanagement.Instance
        The corresponding remote instance when the Geometry Service
        is launched through PyPIM. This instance will be deleted when calling
        :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close >`.
    timeout : Real, default: 60
        Timeout in seconds to achieve the connection..
    logging_level : int, default: INFO
        The logging level to be applied to the client.
        By default, ``INFO``.
    logging_file : str or Path, default: None
        The file to output the log, if requested.
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
        """Constructor method for ``Modeler``."""
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
        """The ``Modeler`` instance client."""
        return self._client

    @check_input_types
    def create_design(self, name: str) -> Design:
        """Initializes a new design with the connected client.

        Parameters
        ----------
        name : str
            Name assigned to the design.

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
