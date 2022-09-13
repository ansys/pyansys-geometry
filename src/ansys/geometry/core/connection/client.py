"""Provides a wrapped abstraction of the gRPC proto API definition and stubs."""
import logging
import os
import time

import grpc
from grpc._channel import _InactiveRpcError
from grpc.health.v1 import health_pb2, health_pb2_grpc

from ansys.geometry.core.designer.design import Design

LOG = logging.getLogger(__name__)
LOG.setLevel("CRITICAL")

# Default 256 MB message length
MAX_MESSAGE_LENGTH = int(os.environ.get("PYMAPDL_MAX_MESSAGE_LENGTH", 256 * 1024**2))


def wait_until_healthy(channel: grpc.Channel, timeout: float):
    """
    Wait until a channel is healthy before returning.

    Parameters
    ----------
    channel : grpc.Channel
        Channel to wait until established and healthy.
    timeout : float
        Timeout in seconds. One attempt will be made each 100 milliseconds until
        timeout is exceeded.

    Raises
    ------
    TimeoutError
        Raised when the total elapsed time exceeds ``timeout``.

    """
    t_max = time.time() + timeout
    health_stub = health_pb2_grpc.HealthStub(channel)
    request = health_pb2.HealthCheckRequest(service="")
    while time.time() < t_max:
        try:
            out = health_stub.Check(request, timeout=0.1)
            if out.status is health_pb2.HealthCheckResponse.SERVING:
                break
        except _InactiveRpcError:
            continue
    else:
        raise TimeoutError("Health check timed out.")


class GrpcClient:
    """
    Wraps a geometry gRPC connection.

    Parameters
    ----------
    channel : grpc.Channel
        gRPC channel for server communication.
    """

    def __init__(
        self, host: str = "localhost", port: int = 50051, channel: grpc.Channel = None, timeout=60
    ):
        """Initialize the ``GrpcClient`` object."""
        self._closed = False

        if channel:
            # Used for PyPIM when directly providing a channel
            if not isinstance(grpc_client, grpc.Channel):
                raise TypeError(
                    f"Expected a grpc.Channel for `grpc_client`, got {type(GrpcClient)}"
                )
            self._channel = channel
            self._target = str(channel)
        else:
            self._target = f"{host}:{port}"
            LOG.debug("Opening insecure channel at %s", self._target)
            self._channel = grpc.insecure_channel(
                self._target,
                options=[
                    ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
                ],
            )

        # do not finish initialization until channel is healthy
        wait_until_healthy(self._channel, timeout)

        # self._design_stub = DesignsStub(self._channel)

    @property
    def healthy(self) -> bool:
        """Return if the client channel if healthy."""
        if self._closed:
            return False
        health_stub = health_pb2_grpc.HealthStub(self._channel)
        request = health_pb2.HealthCheckRequest(service="")
        try:
            out = health_stub.Check(request, timeout=0.1)
            return out.status is health_pb2.HealthCheckResponse.SERVING
        except _InactiveRpcError:
            return False

    def __repr__(self) -> str:
        """String representation of the client."""
        lines = []
        lines.append(f"Ansys Geometry Modeler Client ({hex(id(self))})")
        lines.append(f"  Target:     {self._target}")
        if self._closed:
            lines.append(f"  Connection: Closed")
        elif self.healthy:
            lines.append(f"  Connection: Healthy")
        else:
            lines.append(f"  Connection: Unhealthy")
        return "\n".join(lines)

    def close(self):
        """Close the channel."""
        self._closed = True
        self._channel.close()

    def create_design(self) -> Design:
        pass
        # new_design = self._design_stub.New(NewDesignRequest())

        # return Design(new_design.id)
        # return None
