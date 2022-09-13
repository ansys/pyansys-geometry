"""``Modeler`` class module."""
import grpc

from ansys.geometry.core.connection.client import GrpcClient
from ansys.geometry.core.designer.design import Design


class Modeler:
    """
    Provides a modeler class for building CAD.

    Should have methods like:
    AddDesign(...) - Adds a new design that is synchronized to the server

    """

    def __init__(
        self, host: str = "localhost", port: int = 50051, channel: grpc.Channel = None, timeout=60
    ):
        """Constructor method for ``DirectModeler``."""
        self._client = GrpcClient(host, port, channel, timeout=timeout)

        # Design[] maintaining references to all designs within the modeler workspace
        self._designs = []

    def create_design(self) -> Design:
        """Initializes a new design with the connected client."""

        design = self._grpc_client.create_design()
        self._designs.append(design)

    def __repr__(self):
        """String representation of the modeler."""
        lines = []
        lines.append(f"Ansys Geometry Modeler ({hex(id(self))})")
        lines.append("")
        lines.append(str(self._client))
        return "\n".join(lines)
