"""``Modeler`` class module."""
import logging
from pathlib import Path
from typing import Optional, Union

from grpc import Channel

from ansys.geometry.core.connection import DEFAULT_HOST, DEFAULT_PORT, GrpcClient
from ansys.geometry.core.designer import Design
from ansys.geometry.core.misc import check_type


class Modeler:
    """
    Provides a modeler class for interacting with an open session of
    the Geometry service.

    Parameters
    ----------
    host : str, optional
        Host where the server is running.
        By default, ``DEFAULT_HOST``.
    port : Union[str, int], optional
        Port number where the server is running.
        By default, ``DEFAULT_PORT``.
    channel : ~grpc.Channel, optional
        gRPC channel for server communication.
        By default, ``None``.
    timeout : Real, optional
        Timeout in seconds to achieve the connection.
        By default, 60 seconds.
    logging_level : int, optional
        The logging level to be applied to the client.
        By default, ``INFO``.
    logging_file : Optional[str, Path]
        The file to output the log, if requested. By default, ``None``.
    """

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: Union[str, int] = DEFAULT_PORT,
        channel: Channel = None,
        timeout=60,
        logging_level: Optional[int] = logging.INFO,
        logging_file: Optional[Union[Path, str]] = None,
    ):
        """Constructor method for ``Modeler``."""
        self._client = GrpcClient(
            host=host,
            port=port,
            channel=channel,
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
        check_type(name, str)
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
