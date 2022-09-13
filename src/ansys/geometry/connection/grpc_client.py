"""Provides a wrapped abstraction of the gRPC proto API definition and stubs."""

# from ansys.api.geometry.v0.designs_pb2 import NewDesignRequest
# from ansys.api.geometry.v0.designs_pb2_grpc import DesignsStub

import grpc

from ansys.geometry.core.designer.design import Design

# Maximum size for gRPC message
MAX_MESSAGE_LENGTH = 100 * 1024 * 1024


class GrpcClient:
    """
    Wraps a geometry gRPC connection.

    Parameters
    ----------
    channel : grpc.Channel
        gRPC channel for server communication.
    """

    def __init__(self, channel: grpc.Channel):
        """Initialize the ``GrpcClient`` object."""

        if isinstance(channel, grpc.Channel):
            self._channel = channel
        else:
            raise BaseException(
                "Error: no endpoint or channel has been defined for the connection."
            )

        # self._design_stub = DesignsStub(self._channel)

    def create_design(self) -> Design:
        # new_design = self._design_stub.New(NewDesignRequest())

        # return Design(new_design.id)
        return None
