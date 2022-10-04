"""``Modeler`` class module."""
from typing import Union

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
    remote_instance : ansys.platform.instancemanagement.Instance
        The corresponding remote instance when geometry is launched through
        PyPIM. This instance will be deleted when calling
        :func:`GrpcClient.close <ansys.mapdl.core.Mapdl.exit>`.
    """

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: Union[str, int] = DEFAULT_PORT,
        channel: Channel = None,
        timeout=60,
        remote_instance=None,
    ):
        """Constructor method for ``Modeler``."""
        self._client = GrpcClient(host, port, channel, remote_instance, timeout=timeout)

        # Design[] maintaining references to all designs within the modeler workspace
        self._designs = []

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
