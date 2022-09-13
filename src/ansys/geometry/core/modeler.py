"""``DirectModeler`` class module."""

from ansys.geometry.core.connection.client import GrpcClient

from ansys.geometry.core.designer.design import Design


class DirectModeler:
    """
    Provides DirectModeler class for building CAD designs.

    Should have methods like:
    AddDesign(...) - Adds a new design that is synchronized to the server

    """

    def __init__(self, grpc_client: GrpcClient):
        """Constructor method for ``DirectModeler``."""

        if not isinstance(grpc_client, GrpcClient):
            raise TypeError(f"{GrpcClient} expected to maintain geometry service synchronization.")

        self._grpc_client = grpc_client

        # Design[] maintaining references to all designs within the modeler workspace
        self._designs = []

    def create_design(self) -> Design:
        """Initializes a new design with the connected client."""

        design = self._grpc_client.create_design()
        self._designs.append(design)
