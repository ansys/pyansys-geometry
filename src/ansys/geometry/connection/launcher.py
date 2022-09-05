"""Module for connecting to geometry service instances."""

import grpc

from ansys.geometry.connection.grpc_client import GrpcClient
from ansys.geometry.core.direct_modeler import DirectModeler


def connect_geometry_direct_modeler(endpoint: str) -> DirectModeler:
    """Start DirectModeler locally.

    Parameters
    ----------
    endpoint : str
        Fully qualified server address for the connection.

    Returns
    -------
    ansys.geometry.core.DirectModeler
        Pythonic interface for geometry modeling.

    Examples
    --------
    Connect to existing direct modeler geometry service.

    >>> from ansys.geometry.connection.launcher import connect_geometry_direct_modeler
    >>> direct_modeler = connect_geometry_direct_modeler("localhost:50051")
    """

    grpc_channel = grpc.insecure_channel(endpoint)

    direct_modeler = DirectModeler(GrpcClient(grpc_channel))

    return direct_modeler
