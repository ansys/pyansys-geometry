"""Provides a wrapped abstraction of the gRPC proto API definition and stubs."""

from ansys.api.geometry.v0.board_pb2 import CreateExtrudedDesignBodyRequest
from ansys.api.geometry.v0.board_pb2_grpc import BoardStub
import grpc
from pint import Quantity

from ansys.geometry.core.designer.component import Component
from ansys.geometry.core.sketch import Sketch

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

        self._board_stub = BoardStub(self._channel)

    @property
    def channel(self):
        return self._channel

    def extrude(self, name: str, component: Component, sketch: Sketch, distance: Quantity):

        extrusion_request = CreateExtrudedDesignBodyRequest(
            distance=distance.m,
            parent=component.id,
            plane=sketch._plane,
            geometries=sketch,
            name=name,
        )

        extrusion_response = self._board_stub.CreateExtrudedDesignBody(extrusion_request)
