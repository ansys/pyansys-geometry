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
"""Module containing the ``ProductInstance`` class."""

import logging
import os
from pathlib import Path
import signal
import socket

# Subprocess is needed to start the backend. But
# the input is controlled by the library. Excluding bandit check.
import subprocess  # nosec B404
from typing import TYPE_CHECKING

from ansys.geometry.core.connection.backend import ApiVersions, BackendType
from ansys.geometry.core.logger import LOG
from ansys.tools.path import get_available_ansys_installations, get_latest_ansys_installation

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.modeler import Modeler


WINDOWS_GEOMETRY_SERVICE_FOLDER = "GeometryService"
"""Default Geometry Service's folder name into the unified installer."""

DISCOVERY_FOLDER = "Discovery"
"""Default Discovery's folder name into the unified installer."""

SPACECLAIM_FOLDER = "scdm"
"""Default SpaceClaim's folder name into the unified installer."""

ADDINS_SUBFOLDER = "Addins"
"""Default global Addins's folder name into the unified installer."""

BACKEND_SUBFOLDER = "ApiServer"
"""Default backend's folder name into the ``ADDINS_SUBFOLDER`` folder."""

MANIFEST_FILENAME = "Presentation.ApiServerAddIn.Manifest.xml"
"""Default backend's add-in filename.

To be used only for local start of Ansys Discovery or Ansys SpaceClaim.
"""

GEOMETRY_SERVICE_EXE = "Presentation.ApiServerDMS.exe"
"""The Windows Geometry Service's filename."""

DISCOVERY_EXE = "Discovery.exe"
"""The Ansys Discovery's filename."""

SPACECLAIM_EXE = "SpaceClaim.exe"
"""The Ansys SpaceClaim's filename."""

BACKEND_LOG_LEVEL_VARIABLE = "LOG_LEVEL"
"""The backend's log level environment variable for local start."""

BACKEND_TRACE_VARIABLE = "ENABLE_TRACE"
"""The backend's enable trace environment variable for local start."""

BACKEND_HOST_VARIABLE = "API_ADDRESS"
"""The backend's ip address environment variable for local start."""

BACKEND_PORT_VARIABLE = "API_PORT"
"""The backend's port number environment variable for local start."""

BACKEND_LOGS_FOLDER_VARIABLE = "ANS_DSCO_REMOTE_LOGS_FOLDER"
"""The backend's logs folder path to be used.

Only applicable to the Ansys Geometry Service.
"""

BACKEND_API_VERSION_VARIABLE = "API_VERSION"
"""The backend's api version environment variable for local start.

To be used only with Ansys Discovery and Ansys SpaceClaim.
"""

BACKEND_SPACECLAIM_OPTIONS = "--spaceclaim-options"
"""The additional argument for local Ansys Discovery start.

To be used only with Ansys Discovery.
"""

BACKEND_ADDIN_MANIFEST_ARGUMENT = "/ADDINMANIFESTFILE="
"""The argument to specify the backend's add-in manifest file's path.

To be used only with Ansys Discovery and Ansys SpaceClaim.
"""

BACKEND_SPACECLAIM_HIDDEN = "/Headless=True"
"""The argument to hide SpaceClaim's UI on the backend.

To be used only with Ansys SpaceClaim.
"""

BACKEND_SPACECLAIM_HIDDEN_ENVVAR_KEY = "SPACECLAIM_MODE"
"""SpaceClaim hidden backend's environment variable key.

To be used only with Ansys SpaceClaim.
"""

BACKEND_SPACECLAIM_HIDDEN_ENVVAR_VALUE = "2"
"""SpaceClaim hidden backend's environment variable value.

To be used only with Ansys SpaceClaim.
"""

BACKEND_DISCOVERY_HIDDEN = "--hidden"
"""The argument to hide Discovery's UI on the backend.

To be used only with Ansys Discovery.
"""

BACKEND_SPLASH_OFF = "/Splash=False"
"""The argument to specify the backend's add-in manifest file's path.

To be used only with Ansys Discovery and Ansys SpaceClaim.
"""


class ProductInstance:
    """``ProductInstance`` class.

    This class is used as a handle for a local session of Ansys Product's backend: Discovery,
    Windows Geometry Service or SpaceClaim.

    Parameters
    ----------
    pid : int
        The local instance's process identifier. This allows to keep track of the process
        and close it if need be.
    """

    def __init__(self, pid: int):
        """Initialize ``ProductInstance`` class."""
        self._pid = pid

    def close(self) -> bool:
        """Close the process associated to the pid."""
        try:
            os.kill(self._pid, signal.SIGTERM)
        except OSError as oserr:
            LOG.error(str(oserr))
            return False

        return True


def prepare_and_start_backend(
    backend_type: BackendType,
    product_version: int = None,
    host: str = "localhost",
    port: int = None,
    enable_trace: bool = False,
    api_version: ApiVersions = ApiVersions.LATEST,
    timeout: int = 150,
    manifest_path: str = None,
    hidden: bool = False,
    server_log_level: int = 2,
    client_log_level: int = logging.INFO,
    server_logs_folder: str = None,
    client_log_file: str = None,
    log_level: int = None,  # DEPRECATED
    logs_folder: str = None,  # DEPRECATED
) -> "Modeler":
    """Start the requested service locally using the ``ProductInstance`` class.

    When calling this method, a standalone service or product session is started.
    By default, if an endpoint is specified (by defining `host` and `port` parameters)
    but the endpoint is not available, the startup will fail. Otherwise, it will try to
    launch its own service.

    Parameters
    ----------
    product_version: ``int``, optional
        The product version to be started. Goes from v23.2.1 to
        the latest. Default is ``None``.
        If a specific product version is requested but not installed locally,
        a SystemError will be raised.
    host: str, optional
        IP address at which the Geometry service will be deployed. By default,
        its value will be ``localhost``.
    port : int, optional
        Port at which the Geometry service will be deployed. By default, its
        value will be ``None``.
    enable_trace : bool, optional
        Boolean enabling the logs trace on the Geometry service console window.
        By default its value is ``False``.
    api_version: ``ApiVersions``, optional
        The backend's API version to be used at runtime. Goes from API v21 to
        the latest. Default is ``ApiVersions.LATEST``.
    timeout : int, optional
        Timeout for starting the backend startup process. The default is 150.
    manifest_path : str, optional
        Used to specify a manifest file path for the ApiServerAddin. This way,
        it is possible to run an ApiServerAddin from a version an older product
        version. Only applicable for Ansys Discovery and Ansys SpaceClaim.
    hidden : starts the product hiding its UI. Default is ``False``.
    server_log_level : int, optional
        Backend's log level from 0 to 3:
            0: Chatterbox
            1: Debug
            2: Warning
            3: Error

        The default is ``2`` (Warning).
    client_log_level : int, optional
        Logging level to apply to the client. By default, INFO level is used.
        Use the logging module's levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    server_logs_folder : str, optional
        Sets the backend's logs folder path. If nothing is defined,
        the backend will use its default path.
    client_log_file : str, optional
        Sets the client's log file path. If nothing is defined,
        the client will log to the console.
    log_level : int, optional
        DEPRECATED. Use ``server_log_level`` instead.
    logs_folder : str, optional
        DEPRECATED. Use ``server_logs_folder`` instead.

    Raises
    ------
    ConnectionError
        If the specified endpoint is already in use, a connection error will be raised.
    SystemError
        If there is not an Ansys product 23.2 version or later installed
        or if a specific product's version is requested but not installed locally then
        a SystemError will be raised.

    Returns
    -------
    Modeler
        Instance of the Geometry service.
    """
    from ansys.geometry.core.modeler import Modeler

    if os.name != "nt":  # pragma: no cover
        raise RuntimeError("Method 'prepare_and_start_backend' is only available on Windows.")

    # Deprecation behavior... To be removed in release 0.7
    if log_level is not None:  # pragma: no cover
        LOG.warning("Overriding 'server_log_level' with 'log_level' value for now...")
        server_log_level = log_level

    if logs_folder is not None:  # pragma: no cover
        LOG.warning("Overriding 'server_logs_folder' with 'logs_folder' value for now...")
        server_logs_folder = logs_folder

    port = _check_port_or_get_one(port)
    installations = get_available_ansys_installations()
    if product_version is not None:
        _check_version_is_available(product_version, installations)
    else:
        product_version = get_latest_ansys_installation()[0]
        _check_minimal_versions(product_version)

    if server_logs_folder is not None:
        # Verify that the user has write permissions to the folder and that it exists.
        try:
            # Make sure the folder exists...
            Path(server_logs_folder).mkdir(parents=True, exist_ok=True)
            # Create a file to test write permissions...
            Path(server_logs_folder, ".verify").touch(exist_ok=True)
        except PermissionError:
            raise RuntimeError(
                "User does not have write permissions to the logs folder "
                f"{Path(server_logs_folder).resolve()}"
            )

    args = []
    env_copy = _get_common_env(
        host=host,
        port=port,
        enable_trace=enable_trace,
        server_log_level=server_log_level,
        server_logs_folder=server_logs_folder,
    )

    if backend_type == BackendType.DISCOVERY:
        args.append(Path(installations[product_version], DISCOVERY_FOLDER, DISCOVERY_EXE))
        if hidden is True:
            args.append(BACKEND_DISCOVERY_HIDDEN)

        # Here begins the spaceclaim arguments.
        args.append(BACKEND_SPACECLAIM_OPTIONS)
        args.append(
            BACKEND_ADDIN_MANIFEST_ARGUMENT
            + _manifest_path_provider(product_version, installations, manifest_path)
        )
        env_copy[BACKEND_API_VERSION_VARIABLE] = str(api_version)

    elif backend_type == BackendType.SPACECLAIM:
        args.append(Path(installations[product_version], SPACECLAIM_FOLDER, SPACECLAIM_EXE))
        if hidden is True:
            args.append(BACKEND_SPACECLAIM_HIDDEN)
            args.append(BACKEND_SPLASH_OFF)
        args.append(
            BACKEND_ADDIN_MANIFEST_ARGUMENT
            + _manifest_path_provider(product_version, installations, manifest_path)
        )
        env_copy[BACKEND_API_VERSION_VARIABLE] = str(api_version)
        if BACKEND_SPACECLAIM_HIDDEN_ENVVAR_KEY not in env_copy:
            env_copy[BACKEND_SPACECLAIM_HIDDEN_ENVVAR_KEY] = BACKEND_SPACECLAIM_HIDDEN_ENVVAR_VALUE
        else:
            LOG.warning(
                f"Environment variable '{BACKEND_SPACECLAIM_HIDDEN_ENVVAR_KEY}' already exists. "
                f"Using value '{env_copy[BACKEND_SPACECLAIM_HIDDEN_ENVVAR_KEY]}'."
            )

    elif backend_type == BackendType.WINDOWS_SERVICE:
        latest_version = get_latest_ansys_installation()[0]
        args.append(
            Path(
                installations[latest_version], WINDOWS_GEOMETRY_SERVICE_FOLDER, GEOMETRY_SERVICE_EXE
            )
        )
    else:
        raise RuntimeError(
            f"Cannot connect to backend {backend_type.name} using ``prepare_and_start_backend()``"
        )

    LOG.info(f"Launching ProductInstance for {backend_type.name}")
    LOG.debug(f"Args: {args}")
    LOG.debug(f"Environment variables: {env_copy}")

    instance = ProductInstance(__start_program(args, env_copy).pid)

    # Verify that the backend is ready to accept connections
    # before returning the Modeler instance.
    LOG.info("Waiting for backend to be ready...")
    _wait_for_backend(host, port, timeout)

    return Modeler(
        host=host,
        port=port,
        timeout=timeout,
        product_instance=instance,
        backend_type=backend_type,
        logging_level=client_log_level,
        logging_file=client_log_file,
    )


def get_available_port() -> int:
    """Return an available port to be used.

    Returns
    -------
    int
        The available port.
    """
    sock = socket.socket()
    sock.bind((socket.gethostname(), 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def _wait_for_backend(host: str, port: int, timeout: int):
    """Check if the backend is ready to accept connections.

    Parameters
    ----------
    host : str
        The backend's ip address.
    port : int
        The backend's port number.
    timeout : int
        The timeout in seconds.
    """
    import time

    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex((host, port)) == 0:
                LOG.debug("Backend is ready to accept connections.")
                return
            else:
                LOG.debug("Still waiting for backend to be ready... Retrying in 5 seconds.")
                time.sleep(5)

    raise ConnectionError("Timeout while waiting for backend to be ready.")


def _is_port_available(port: int, host: str = "localhost") -> bool:
    """Check whether the argument port is available.

    The optional argument is the ip address where to check port availability.
    Its default is ``localhost``.
    """
    if port != 0:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
                return True
            except socket.error:
                return False


def _manifest_path_provider(
    version: int, available_installations: dict[str, str], manifest_path: str = None
) -> str:
    """Return the ApiServer's add-in manifest file path."""
    if manifest_path:
        if Path(manifest_path).exists():
            return manifest_path
        else:
            LOG.warning(
                "Specified manifest file's path does not exist. Taking install default path."
            )

    # Default manifest path
    def_manifest_path = Path(
        available_installations[version], ADDINS_SUBFOLDER, BACKEND_SUBFOLDER, MANIFEST_FILENAME
    )

    if def_manifest_path.exists():
        return def_manifest_path.as_posix()
    else:
        msg = (
            "Default manifest file's path does not exist."
            " Please specify a valid manifest."
            f" The ApiServer Add-In seems to be missing in {def_manifest_path.parent}"
        )
        LOG.error(msg)
        raise RuntimeError(msg)


def __start_program(args: list[str], local_env: dict[str, str]) -> subprocess.Popen:
    """Start the program.

    Notes
    -----
    The path is the first item of the ``args`` array argument.

    Parameters
    ----------
    args : list[str]
        List of arguments to be passed to the program. The first list's item shall
        be the program path.
    local_env : dict[str,str]
        Environment variables to be passed to the program.

    Returns
    -------
    subprocess.Popen
        The subprocess object.
    """
    # private method and controlled input by library - excluding bandit check.
    return subprocess.Popen(  # nosec B603
        args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=local_env,
    )


def _check_minimal_versions(latest_installed_version: int) -> None:
    """Check client is compatible with Ansys Products.

    Check that at least V232 is installed.
    """
    if abs(latest_installed_version) < 232:
        msg = (
            "PyAnsys Geometry is compatible with Ansys Products from version 23.2.1. "
            + "Please install Ansys products 23.2.1 or later."
        )
        raise SystemError(msg)


def _check_version_is_available(version: int, installations: dict[int, str]) -> None:
    """Check that the requested version for launcher is installed."""
    if version not in installations:
        msg = (
            f"The requested Ansys product's version {version} is not available, "
            + "please specify a different version."
        )
        raise SystemError(msg)


def _check_port_or_get_one(port: int) -> int:
    """If a ``port`` argument is specified, check that it's free.

    If not, raise an error.

    If ``port`` is None, return an available port by calling ``get_available_port``.
    """
    if port:
        if _is_port_available(port):
            return port
        else:
            msg = f"Port {port} is already in use. Please specify a different one."
            raise ConnectionError(msg)
    else:
        return get_available_port()


def _get_common_env(
    host: str,
    port: int,
    enable_trace: bool,
    server_log_level: int,
    server_logs_folder: str = None,
) -> dict[str, str]:
    """Make a copy of the actual system's environment.

    Then update or create some environment variables with the provided
    arguments.
    """
    env_copy = os.environ.copy()

    env_copy[BACKEND_HOST_VARIABLE] = host
    env_copy[BACKEND_PORT_VARIABLE] = f"{port}"
    env_copy[BACKEND_TRACE_VARIABLE] = f"{enable_trace:d}"
    env_copy[BACKEND_LOG_LEVEL_VARIABLE] = f"{server_log_level}"
    if server_logs_folder is not None:
        env_copy[BACKEND_LOGS_FOLDER_VARIABLE] = f"{server_logs_folder}"

    return env_copy
