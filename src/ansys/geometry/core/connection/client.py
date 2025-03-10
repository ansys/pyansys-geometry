# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
import warnings

from ansys.geometry.core.errors import protect_grpc
from ansys.geometry.core.misc.checks import deprecated_method

# TODO: Remove this context and filter once the protobuf UserWarning issue is downgraded to INFO
# https://github.com/grpc/grpc/issues/37609
with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore", "Protobuf gencode version", UserWarning, "google.protobuf.runtime_version"
    )

    from google.protobuf.empty_pb2 import Empty
    import grpc
    from grpc._channel import _InactiveRpcError
    from grpc_health.v1 import health_pb2, health_pb2_grpc

from beartype import beartype as check_input_types
import semver

from ansys.api.dbu.v0.admin_pb2 import (
    BackendType as GRPCBackendType,
    LogsRequest,
    LogsTarget,
    PeriodType,
)
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
        Timeout in seconds. Attempts are made with the following backoff strategy:

        * Starts with 0.1 seconds.
        * If the attempt fails, double the timeout.
        * This is repeated until the next timeoff exceeds the
          value for the remaining time. In that case, a final attempt
          is made with the remaining time.
        * If the total elapsed time exceeds the value for the ``timeout`` parameter,
          a ``TimeoutError`` is raised.

    Raises
    ------
    TimeoutError
        Raised when the total elapsed time exceeds the value for the ``timeout`` parameter.
    """
    t_max = time.time() + timeout
    health_stub = health_pb2_grpc.HealthStub(channel)
    request = health_pb2.HealthCheckRequest(service="")

    t_out = 0.1
    while time.time() < t_max:
        try:
            out = health_stub.Check(request, timeout=t_out)
            if out.status is health_pb2.HealthCheckResponse.SERVING:
                break
        except _InactiveRpcError:
            # Duplicate timeout and try again
            t_now = time.time()
            t_out *= 2
            # If we have time to try again, continue.. but if we don't,
            # just try for the remaining time
            if t_now + t_out > t_max:
                t_out = t_max - t_now
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
                    ("grpc.max_send_message_length", MAX_MESSAGE_LENGTH),
                ],
            )

        # do not finish initialization until channel is healthy
        self._grpc_health_timeout = timeout
        wait_until_healthy(self._channel, self._grpc_health_timeout)

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
            elif grpc_backend_type == GRPCBackendType.CORE_SERVICE_LINUX:
                backend_type = BackendType.CORE_LINUX
            elif grpc_backend_type == GRPCBackendType.CORE_SERVICE_WINDOWS:
                backend_type = BackendType.CORE_WINDOWS
            elif grpc_backend_type == GRPCBackendType.DISCOVERY_HEADLESS:
                backend_type = BackendType.DISCOVERY_HEADLESS

        # Store the backend type
        self._backend_type = backend_type

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
    @deprecated_method(
        info="Multiple designs for the same service are no longer supported.",
        version="0.9.0",
        remove="0.11.0",
    )
    def multiple_designs_allowed(self) -> bool:
        """Flag indicating whether multiple designs are allowed.

        Notes
        -----
        Currently, only one design is allowed per service. This method will always
        return ``False``.
        """
        return False

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
        try:
            wait_until_healthy(self._channel, self._grpc_health_timeout)
            return True
        except TimeoutError:  # pragma: no cover
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

    @check_input_types
    @protect_grpc
    def _get_service_logs(
        self,
        all_logs: bool = False,
        dump_to_file: bool = False,
        logs_folder: str | Path | None = None,
    ) -> str | dict[str, str] | Path:
        """Get the service logs.

        Parameters
        ----------
        all_logs : bool, default: False
            Flag indicating whether all logs should be retrieved. By default,
            only the current logs are retrieved.
        dump_to_file : bool, default: False
            Flag indicating whether the logs should be dumped to a file.
            By default, the logs are not dumped to a file.
        logs_folder : str,  Path or None, default: None
            Name of the folder where the logs should be dumped. This parameter
            is only used if the ``dump_to_file`` parameter is set to ``True``.

        Returns
        -------
        str
            Service logs as a string. This is returned if the ``dump_to_file`` parameter
            is set to ``False``.
        dict[str, str]
            Dictionary containing the logs. The keys are the logs names,
            and the values are the logs as strings. This is returned if the ``all_logs``
            parameter is set to ``True`` and the ``dump_to_file`` parameter
            is set to ``False``.
        Path
            Path to the folder containing the logs (if the ``all_logs``
            parameter is set to ``True``) or the path to the log file (if only
            the current logs are retrieved). The ``dump_to_file`` parameter
            must be set to ``True``.
        """
        request = LogsRequest(
            target=LogsTarget.CLIENT,
            period_type=PeriodType.CURRENT if not all_logs else PeriodType.ALL,
            null_path=None,
            null_period=None,
        )
        logs_generator = self._admin_stub.GetLogs(request)
        logs: dict[str, str] = {}

        for chunk in logs_generator:
            if chunk.log_name not in logs:
                logs[chunk.log_name] = ""
            logs[chunk.log_name] += chunk.log_chunk.decode()

        # Let's handle the various scenarios...
        if not dump_to_file:
            return logs if all_logs else next(iter(logs.values()))
        else:
            if logs_folder is None:
                logs_folder = Path.cwd()
            elif isinstance(logs_folder, str):
                logs_folder = Path(logs_folder)

            logs_folder.mkdir(parents=True, exist_ok=True)
            for log_name, log_content in logs.items():
                with (logs_folder / log_name).open("w") as f:
                    f.write(log_content)

            return (logs_folder / log_name) if len(logs) == 1 else logs_folder
