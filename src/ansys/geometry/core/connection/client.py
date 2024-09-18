# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module providing a wrapped abstraction of the gRPC stubs."""

import atexit
import logging
from pathlib import Path
import time
from typing import Optional

from beartype import beartype as check_input_types
from google.protobuf.empty_pb2 import Empty
import grpc
from grpc._channel import _InactiveRpcError
from grpc_health.v1 import health_pb2, health_pb2_grpc
import semver

from ansys.api.dbu.v0.admin_pb2 import BackendType as GRPCBackendType
from ansys.api.dbu.v0.admin_pb2_grpc import AdminStub
from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.connection.defaults import DEFAULT_HOST, DEFAULT_PORT, MAX_MESSAGE_LENGTH
from ansys.geometry.core.connection.docker_instance import LocalDockerInstance
from ansys.geometry.core.connection.product_instance import ProductInstance
from ansys.geometry.core.logger import LOG, PyGeometryCustomAdapter
from ansys.geometry.core.typing import Real

try:
    from ansys.platform.instancemanagement import Instance
except ModuleNotFoundError:  # pragma: no cover
    pass


def wait_until_healthy(channel: grpc.Channel, timeout: float):
    """Wait until a channel is healthy before returning.

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
    """Wraps the gRPC connection for the Geometry service.

    Parameters
    ----------
    host : str, default: DEFAULT_HOST
        Host where the server is running.
    port : str or int, default: DEFAULT_PORT
        Port number where the server is running.
    channel : ~grpc.Channel, default: None
        gRPC channel for server communication.
    remote_instance : ansys.platform.instancemanagement.Instance, default: None
        Corresponding remote instance when the Geometry service
        is launched through `PyPIM <https://github.com/ansys/pypim>`_.
        This instance is deleted when calling the
        :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close >`
        method.
    docker_instance : LocalDockerInstance, default: None
        Corresponding local Docker instance when the Geometry service is launched using
        the ``launch_docker_modeler()`` method. This local Docker instance is deleted
        when the :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close >`
        method is called.
    product_instance : ProductInstance, default: None
        Corresponding local product instance when the product (Discovery or SpaceClaim)
        is launched through the ``launch_modeler_with_geometry_service()``,
        ``launch_modeler_with_discovery()`` or the ``launch_modeler_with_spaceclaim()``
        interface. This instance will be deleted
        when the :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close >`
        method is called.
    timeout : real, default: 120
        Maximum time to spend trying to make the connection.
    logging_level : int, default: INFO
        Logging level to apply to the client.
    logging_file : str or Path, default: None
        File to output the log to, if requested.
    backend_type: BackendType, default: None
        Type of the backend that PyAnsys Geometry is communicating with. By default, this
        value is unknown, which results in ``None`` being the default value.
    """

    @check_input_types
    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: str | int = DEFAULT_PORT,
        channel: grpc.Channel | None = None,
        remote_instance: Optional["Instance"] = None,
        docker_instance: LocalDockerInstance | None = None,
        product_instance: ProductInstance | None = None,
        timeout: Real = 120,
        logging_level: int = logging.INFO,
        logging_file: Path | str | None = None,
        backend_type: BackendType | None = None,
    ):
        """Initialize the ``GrpcClient`` object."""
        self._closed = False
        self._remote_instance = remote_instance
        self._docker_instance = docker_instance
        self._product_instance = product_instance
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
        self._log = LOG.add_instance_logger(
            name=self._target, client_instance=self, level=logging_level
        )
        if logging_file:
            if isinstance(logging_file, Path):
                logging_file = str(logging_file)
            self._log.log_to_file(filename=logging_file, level=logging_level)

        self._admin_stub = AdminStub(self._channel)

        # retrieve the backend information
        grpc_backend_response = self._admin_stub.GetBackend(Empty())

        # if no backend type has been specified, ask the backend which type it is
        if backend_type is None:
            grpc_backend_type = grpc_backend_response.type
            if grpc_backend_type == GRPCBackendType.DISCOVERY:
                backend_type = BackendType.DISCOVERY
            elif grpc_backend_type == GRPCBackendType.SPACECLAIM:
                backend_type = BackendType.SPACECLAIM
            elif grpc_backend_type == GRPCBackendType.WINDOWS_DMS:
                backend_type = BackendType.WINDOWS_SERVICE
            elif grpc_backend_type == GRPCBackendType.LINUX_DMS:
                backend_type = BackendType.LINUX_SERVICE

        # Store the backend type
        self._backend_type = backend_type
        self._multiple_designs_allowed = (
            False if backend_type in (BackendType.DISCOVERY, BackendType.LINUX_SERVICE) else True
        )

        # retrieve the backend version
        if hasattr(grpc_backend_response, "version"):
            ver = grpc_backend_response.version
            self._backend_version = semver.Version(
                ver.major_release, ver.minor_release, ver.service_pack
            )
        else:
            LOG.warning("The backend version is only available after 24.1 version.")
            self._backend_version = semver.Version(24, 1, 0)

        # Register the close method to be called at exit - irrespectively of
        # the user calling it or not...
        atexit.register(self.close)

    @property
    def backend_type(self) -> BackendType:
        """Backend type.

        Options are ``Windows Service``, ``Linux Service``, ``Discovery``,
        and ``SpaceClaim``.

        Notes
        -----
        This method might return ``None`` because determining the backend type is
        not straightforward.
        """
        return self._backend_type

    @property
    def backend_version(self) -> semver.version.Version:
        """Get the current backend version.

        Returns
        -------
        ~semver.version.Version
            Backend version.
        """
        return self._backend_version

    @property
    def multiple_designs_allowed(self) -> bool:
        """Flag indicating whether multiple designs are allowed.

        Notes
        -----
        This method will return ``False`` if the backend type is ``Discovery`` or
        ``Linux Service``. Otherwise, it will return ``True``.
        """
        return self._multiple_designs_allowed

    @property
    def channel(self) -> grpc.Channel:
        """Client gRPC channel."""
        return self._channel

    @property
    def log(self) -> PyGeometryCustomAdapter:
        """Specific instance logger."""
        return self._log

    @property
    def is_closed(self) -> bool:
        """Flag indicating whether the client connection is closed."""
        return self._closed

    @property
    def healthy(self) -> bool:
        """Flag indicating whether the client channel is healthy."""
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
        """Represent the client as a string."""
        lines = []
        lines.append(f"Ansys Geometry Modeler Client ({hex(id(self))})")
        lines.append(f"  Target:     {self._target}")
        if self._closed:
            lines.append("  Connection: Closed")
        elif self.healthy:
            lines.append("  Connection: Healthy")
        else:
            lines.append("  Connection: Unhealthy")  # pragma: no cover
        return "\n".join(lines)

    def close(self):
        """Close the channel.

        Notes
        -----
        If an instance of the Geometry service was started using
        `PyPIM <https://github.com/ansys/pypim>`_, this instance is
        deleted. Furthermore, if a local Docker instance
        of the Geometry service was started, it is stopped.
        """
        if self._closed is True:  # pragma: no cover
            self.log.debug("Connection is already closed. Ignoring request.")
            return

        if self._remote_instance:
            self._remote_instance.delete()  # pragma: no cover
        elif self._docker_instance:
            if not self._docker_instance.existed_previously:
                self._docker_instance.container.stop()
            else:
                self.log.warning(
                    "Geometry service was not shut down because it was already running..."
                )
        elif self._product_instance:
            self._product_instance.close()

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
