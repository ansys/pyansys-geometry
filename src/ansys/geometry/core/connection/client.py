"""Provides a wrapped abstraction of the gRPC proto API definition and stubs."""

import logging
from pathlib import Path
import time

from beartype import beartype as check_input_types
from beartype.typing import Optional, Union
import grpc
from grpc._channel import _InactiveRpcError
from grpc_health.v1 import health_pb2, health_pb2_grpc

from ansys.geometry.core import LOG as logger
from ansys.geometry.core.connection.defaults import DEFAULT_HOST, DEFAULT_PORT, MAX_MESSAGE_LENGTH
from ansys.geometry.core.logger import PyGeometryCustomAdapter
from ansys.geometry.core.typing import Real

try:
    from ansys.platform.instancemanagement import Instance
except ModuleNotFoundError:  # pragma: no cover
    pass


def wait_until_healthy(channel: grpc.Channel, timeout: float):
    """
    Wait until a channel is healthy before returning.

    Parameters
    ----------
    channel : ~grpc.Channel
        Channel that must be established and healthy.
    timeout : float
        Timeout in seconds. An attempt is made every 100 milliseconds
        until the timeout is exceeded.

    Raises
    ------
    TimeoutError
        Raised when the total elapsed time exceeds the value for the ``timeout`` parameter.

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
        target_str = channel._channel.target().decode()
        raise TimeoutError(
            f"Channel health check to target '{target_str}' timed out after {timeout} seconds."
        )


class GrpcClient:
    """
    Wraps the gRPC connection for the Geometry service.

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
    remote_instance : ansys.platform.instancemanagement.Instance
        Corresponding remote instance when the Geometry service
        is launched through PyPIM. This instance is deleted when calling the
        :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close >`
        method.
    timeout : real, optional
        Timeout in seconds to achieve the connection.
        The default is 60 seconds.
    logging_level : int, optional
        Logging level to apply to the client.
        The default is ``INFO``.
    logging_file : optional [str, Path]
        File to output the log to, if requested. The default is ``None``.
    """

    @check_input_types
    def __init__(
        self,
        host: Optional[str] = DEFAULT_HOST,
        port: Union[str, int] = DEFAULT_PORT,
        channel: Optional[grpc.Channel] = None,
        remote_instance: Optional["Instance"] = None,
        timeout: Optional[Real] = 60,
        logging_level: Optional[int] = logging.INFO,
        logging_file: Optional[Union[Path, str]] = None,
    ):
        """Initialize the ``GrpcClient`` object."""
        self._closed = False
        self._remote_instance = remote_instance
        if channel:
            # Used for PyPIM when directly providing a channel
            self._channel = channel
            self._target = str(channel)
        else:
            self._target = f"{host}:{port}"
            self._channel = grpc.insecure_channel(
                self._target,
                options=[
                    ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
                ],
            )

        # do not finish initialization until channel is healthy
        wait_until_healthy(self._channel, timeout)

        # once connection with the client is established, create a logger
        self._log = logger.add_instance_logger(
            name=self._target, client_instance=self, level=logging_level
        )
        if logging_file:
            if isinstance(logging_file, Path):
                logging_file = str(logging_file)
            self._log.log_to_file(filename=logging_file, level=logging_level)

    @property
    def channel(self) -> grpc.Channel:
        """gRPC channel of the client."""
        return self._channel

    @property
    def log(self) -> PyGeometryCustomAdapter:
        """Specific instance logger."""
        return self._log

    @property
    def healthy(self) -> bool:
        """Check if the client channel if healthy."""
        if self._closed:
            return False
        health_stub = health_pb2_grpc.HealthStub(self._channel)
        request = health_pb2.HealthCheckRequest(service="")
        try:
            out = health_stub.Check(request, timeout=0.1)
            return out.status is health_pb2.HealthCheckResponse.SERVING
        except _InactiveRpcError:  # pragma: no cover
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
            lines.append(f"  Connection: Unhealthy")  # pragma: no cover
        return "\n".join(lines)

    def close(self):
        """Close the channel.

        Notes
        -----
        If an instance of the Geometry service was started using
        PyPIM, this instance is deleted.
        """
        if self._remote_instance:
            self._remote_instance.delete()  # pragma: no cover
        self._closed = True
        self._channel.close()

    def target(self) -> str:
        """Get the target of the channel."""
        if self._closed:
            return ""
        return self._channel._channel.target().decode()

    def get_name(self) -> str:
        """Get the target name of the connection."""
        return self._target
