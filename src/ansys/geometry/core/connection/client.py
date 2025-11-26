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

from beartype import beartype as check_input_types
import grpc
from grpc._channel import _InactiveRpcError
from grpc_health.v1 import health_pb2, health_pb2_grpc
import semver

from ansys.geometry.core._grpc._services._service import _GRPCServices
from ansys.geometry.core.connection.backend import BackendType
import ansys.geometry.core.connection.defaults as pygeom_defaults
from ansys.geometry.core.connection.docker_instance import LocalDockerInstance
from ansys.geometry.core.connection.product_instance import ProductInstance
from ansys.geometry.core.logger import LOG, PyGeometryCustomAdapter
from ansys.geometry.core.misc.checks import deprecated_method
from ansys.geometry.core.typing import Real

try:
    from ansys.platform.instancemanagement import Instance
except ModuleNotFoundError:  # pragma: no cover
    pass


def _create_geometry_channel(
    target: str,
    transport_mode: str,
    uds_dir: Path | str | None = None,
    uds_id: str | None = None,
    certs_dir: Path | str | None = None,
) -> grpc.Channel:
    """Create a Geometry service gRPC channel.

    Parameters
    ----------
    target : str
        Target of the channel. This is usually a string in the form of
        ``host:port``.
    transport_mode : str
        Transport mode selected. Options are: "insecure", "uds", "wnua", "mtls"
    uds_dir : Path | str | None
        Directory to use for Unix Domain Sockets (UDS) transport mode.
        By default `None` and thus it will use the "~/.conn" folder.
    uds_id : str | None
        Optional ID to use for the UDS socket filename.
        By default `None` and thus it will use "aposdas_socket.sock".
        Otherwise, the socket filename will be "aposdas_socket-<uds_id>.sock".
    certs_dir : Path | str | None
        Directory to use for TLS certificates.
        By default `None` and thus search for the "ANSYS_GRPC_CERTIFICATES" environment variable.
        If not found, it will use the "certs" folder assuming it is in the current working
        directory.

    Returns
    -------
    ~grpc.Channel
        gRPC channel for the Geometry service.

    Notes
    -----
    Contains specific options for the Geometry service.
    """
    from ansys.tools.common.cyberchannel import create_channel

    # Split target into host and port
    host, port = target.split(":")

    # Add specific gRPC options for the Geometry service
    grpc_options = [
        ("grpc.max_receive_message_length", pygeom_defaults.MAX_MESSAGE_LENGTH),
        ("grpc.max_send_message_length", pygeom_defaults.MAX_MESSAGE_LENGTH),
    ]

    # Create the channel accordingly
    return create_channel(
        transport_mode=transport_mode,
        host=host,
        port=port,
        uds_service="aposdas_socket",
        uds_dir=uds_dir,
        uds_id=uds_id,
        certs_dir=certs_dir,
        grpc_options=grpc_options,
    )


def wait_until_healthy(
    channel: grpc.Channel | str,
    timeout: float,
    transport_mode: str | None = None,
    uds_dir: Path | str | None = None,
    uds_id: str | None = None,
    certs_dir: Path | str | None = None,
) -> grpc.Channel:
    """Wait until a channel is healthy before returning.

    Parameters
    ----------
    channel : ~grpc.Channel | str
        Channel that must be established and healthy. The target can also be
        passed in. In that case, a channel is created using the default insecure channel.
    timeout : float
        Timeout in seconds. Attempts are made with the following backoff strategy:

        * Starts with 0.1 seconds.
        * If the attempt fails, double the timeout.
        * This is repeated until the next timeoff exceeds the
          value for the remaining time. In that case, a final attempt
          is made with the remaining time.
        * If the total elapsed time exceeds the value for the ``timeout`` parameter,
          a ``TimeoutError`` is raised.
    transport_mode : str | None
        Transport mode selected. Needed if channel is a string.
        Options are: "insecure", "uds", "wnua", "mtls".
    uds_dir : Path | str | None
        Directory to use for Unix Domain Sockets (UDS) transport mode.
        By default `None` and thus it will use the "~/.conn" folder.
    uds_id : str | None
        Optional ID to use for the UDS socket filename.
        By default `None` and thus it will use "aposdas_socket.sock".
        Otherwise, the socket filename will be "aposdas_socket-<uds_id>.sock".
    certs_dir : Path | str | None
        Directory to use for TLS certificates.
        By default `None` and thus search for the "ANSYS_GRPC_CERTIFICATES" environment variable.
        If not found, it will use the "certs" folder assuming it is in the current working
        directory.

    Returns
    -------
    grpc.Channel
        The channel that was passed in. This channel is guaranteed to be healthy.
        If a string was passed in, a channel is created using the default insecure channel.

    Raises
    ------
    TimeoutError
        Raised when the total elapsed time exceeds the value for the ``timeout`` parameter.
    """
    t_max = time.time() + timeout
    t_out = 0.1

    # If the channel is a string, create a channel using the specified transport mode
    channel_creation_required = True if isinstance(channel, str) else False
    tmp_channel = None

    # If transport mode is not specified and a channel creation is required, raise an error
    if channel_creation_required:
        if transport_mode is None:
            raise ValueError(
                "Transport mode must be specified."
                " Use 'transport_mode' parameter with one of the possible options."
                " Options are: 'insecure', 'uds', 'wnua', 'mtls'."
            )
        else:
            from ansys.tools.common.cyberchannel import verify_transport_mode

            verify_transport_mode(transport_mode)

    while time.time() < t_max:
        try:
            tmp_channel = (
                _create_geometry_channel(
                    channel,
                    transport_mode=transport_mode,
                    uds_dir=uds_dir,
                    uds_id=uds_id,
                    certs_dir=certs_dir,
                )
                if channel_creation_required
                else channel
            )
            health_stub = health_pb2_grpc.HealthStub(tmp_channel)
            request = health_pb2.HealthCheckRequest(service="")

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
        target_str = tmp_channel._channel.target().decode()
        raise TimeoutError(
            f"Channel health check to target '{target_str}' timed out after {timeout} seconds."
        )

    return tmp_channel


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
    proto_version : str | None, default: None
        Protocol version to use for communication with the server. If None, v0 is used.
        Available versions are "v0", "v1", etc.
    transport_mode : str | None
        Transport mode selected. Needed if ``channel`` is not provided.
        Options are: "insecure", "uds", "wnua", "mtls".
    uds_dir : Path | str | None
        Directory to use for Unix Domain Sockets (UDS) transport mode.
        By default `None` and thus it will use the "~/.conn" folder.
    uds_id : str | None
        Optional ID to use for the UDS socket filename.
        By default `None` and thus it will use "aposdas_socket.sock".
        Otherwise, the socket filename will be "aposdas_socket-<uds_id>.sock".
    certs_dir : Path | str | None
        Directory to use for TLS certificates.
        By default `None` and thus search for the "ANSYS_GRPC_CERTIFICATES" environment variable.
        If not found, it will use the "certs" folder assuming it is in the current working
        directory.
    """

    @check_input_types
    def __init__(
        self,
        host: str = pygeom_defaults.DEFAULT_HOST,
        port: str | int = pygeom_defaults.DEFAULT_PORT,
        channel: grpc.Channel | None = None,
        remote_instance: Optional["Instance"] = None,
        docker_instance: LocalDockerInstance | None = None,
        product_instance: ProductInstance | None = None,
        timeout: Real = 120,
        logging_level: int = logging.INFO,
        logging_file: Path | str | None = None,
        proto_version: str | None = None,
        transport_mode: str | None = None,
        uds_dir: Path | str | None = None,
        uds_id: str | None = None,
        certs_dir: Path | str | None = None,
    ):
        """Initialize the ``GrpcClient`` object."""
        self._closed = False
        self._remote_instance = remote_instance
        self._docker_instance = docker_instance
        self._product_instance = product_instance
        self._grpc_health_timeout = timeout

        if channel:
            # Used for PyPIM when directly providing a channel
            self._target = str(channel)
            self._channel = wait_until_healthy(channel, self._grpc_health_timeout)
        else:
            self._target = f"{host}:{port}"
            self._channel = wait_until_healthy(
                self._target,
                self._grpc_health_timeout,
                transport_mode=transport_mode,
                uds_dir=uds_dir,
                uds_id=uds_id,
                certs_dir=certs_dir,
            )

            # HACK: If we are using UDS, the target needs to be updated to reflect
            # the actual socket file being used.
            if transport_mode == "uds":
                self._target = self._channel._channel.target().decode()

        # Initialize the gRPC services
        self._services = _GRPCServices(self._channel, version=proto_version)

        # Once connection with the client is established, create a logger
        self._log = LOG.add_instance_logger(
            name=self._target, client_instance=self, level=logging_level
        )
        if logging_file:
            if isinstance(logging_file, Path):
                logging_file = str(logging_file)
            self._log.log_to_file(filename=logging_file, level=logging_level)

        # Retrieve the backend information
        response = self._services.admin.get_backend()

        # Store the backend type and version
        self._backend_type = response.get("backend")
        self._backend_version = response.get("version")
        self._backend_api_server_build_info = response.get("api_server_build_info")
        self._backend_product_build_info = response.get("product_build_info")
        self._backend_additional_info = response.get("additional_info", {})

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
    def services(self) -> _GRPCServices:
        """GRPC services."""
        return self._services

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
            return self.services.admin.get_service_status().get("healthy")
        except Exception:  # pragma: no cover
            return False

    def backend_info(self, indent=0) -> str:
        """Get a string with the backend information.

        Returns
        -------
        str
            String with the backend information.
        """
        base_info = (
            f"{' ' * indent}Version:            {self.backend_version}\n"
            f"{' ' * indent}Backend type:       {self.backend_type.name}\n"
            f"{' ' * indent}Backend number:     {self._backend_product_build_info}\n"
            f"{' ' * indent}API server number:  {self._backend_api_server_build_info}"
        )
        if self._backend_additional_info:
            # Calculate padding to align values consistently
            # (19 chars total for label + colon + spaces)
            additional_info_lines = [
                f"{' ' * indent}{key + ':':<19}{value}"
                for key, value in self._backend_additional_info.items()
            ]
            additional_info_str = "\n".join(additional_info_lines)
            return f"{base_info}\n{additional_info_str}"
        else:  # pragma: no cover
            return base_info

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
        lines.append("  Backend info:")
        lines.append(self.backend_info(indent=4))
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
        logs: dict[str, str] = self._services.admin.get_logs(all_logs=all_logs).get("logs")

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
