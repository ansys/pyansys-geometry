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

from ansys.tools.common.path import get_available_ansys_installations, get_latest_ansys_installation
from ansys.tools.common.cyberchannel import verify_transport_mode, verify_uds_socket

from ansys.geometry.core.connection.backend import ApiVersions, BackendType
from ansys.geometry.core.logger import LOG

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.modeler import Modeler


WINDOWS_GEOMETRY_SERVICE_FOLDER = "GeometryService"
"""Default Geometry Service's folder name into the unified installer (DMS)."""

CORE_GEOMETRY_SERVICE_FOLDER = "GeometryService"
"""Default Geometry Service's folder name into the unified installer (Core Service)."""

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
"""The Windows Geometry Service's filename (DMS)."""

CORE_GEOMETRY_SERVICE_EXE = "Presentation.ApiServerCoreService.exe"
"""The Windows Geometry Service's filename (Core Service)."""

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

ANSYS_GEOMETRY_SERVICE_ROOT = "ANSYS_GEOMETRY_SERVICE_ROOT"
"""Local Geometry Service install location. This is for GeometryService and CoreGeometryService."""


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
    version: str | int = None,
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
    transport_mode: str | None = None,
    uds_dir: Path | str | None = None,
    uds_id: str | None = None,
    certs_dir: Path | str | None = None,
    specific_minimum_version: int = None,
    server_working_dir: str | Path | None = None,
    product_version: int | None = None,  # Deprecated, use `version` instead.
) -> "Modeler":
    """Start the requested service locally using the ``ProductInstance`` class.

    When calling this method, a standalone service or product session is started.
    By default, if an endpoint is specified (by defining `host` and `port` parameters)
    but the endpoint is not available, the startup will fail. Otherwise, it will try to
    launch its own service.

    Parameters
    ----------
    version : str | int, optional
        The product version to be started. Goes from v24.1 to
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
    specific_minimum_version : int, optional
        Sets a specific minimum version to be checked. If this is not defined,
        the minimum version will be set to 24.1.0.
    server_working_dir : str | Path, optional
        Sets the working directory for the product instance. If nothing is defined,
        the working directory will be inherited from the parent process.
    transport_mode : str | None
        Transport mode selected, by default `None` and thus it will be selected
        for you based on the connection criteria. Options are: "insecure", "uds", "wnua", "mtls"
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
    product_version: ``int``, optional
        The product version to be started. Deprecated, use `version` instead.

    Returns
    -------
    Modeler
        Instance of the Geometry service.

    Raises
    ------
    ConnectionError
        If the specified endpoint is already in use, a connection error will be raised.
    SystemError
        If there is not an Ansys product 24.1 version or later installed
        or if a specific product's version is requested but not installed locally then
        a SystemError will be raised.
    """
    from ansys.geometry.core.modeler import Modeler

    # Handle deprecated product_version argument
    if product_version is not None and version is not None:
        raise ValueError(
            "Both 'product_version' and 'version' arguments are provided. "
            "Please use only 'version'."
        )
    if product_version is not None:
        LOG.warning("The 'product_version' argument is deprecated. Please use 'version' instead.")
        version = product_version

    if os.name != "nt" and not BackendType.is_linux_service(backend_type):  # pragma: no cover
        raise RuntimeError(
            "Method 'prepare_and_start_backend' is only available on Windows."
            "A Linux version is only available for the Core Geometry Service."
        )

    port = _check_port_or_get_one(port)
    installations = get_available_ansys_installations()
    if os.getenv(ANSYS_GEOMETRY_SERVICE_ROOT) is not None and backend_type in (
        BackendType.WINDOWS_SERVICE,
        BackendType.LINUX_SERVICE,
        BackendType.CORE_WINDOWS,
        BackendType.CORE_LINUX,
    ):
        # If the user has set the ANSYS_GEOMETRY_SERVICE_ROOT environment variable,
        # we will use it as the root folder for the Geometry Service.
        pass
    else:
        if version is not None:
            # Sanitize the version input to ensure it's an integer.
            try:
                version = int(version)
            except ValueError:
                raise ValueError(
                    "The 'version' argument must be an integer representing the product version."
                )

            try:
                _check_version_is_available(version, installations)
            except SystemError as serr:
                # The user requested a version as a Student version...
                # Let's negate it and try again... if this works, we override the
                # version variable.
                try:
                    _check_version_is_available(-version, installations)
                except SystemError:
                    # The student version is not installed either... raise the original error.
                    raise serr

                version = -version
        else:
            version = get_latest_ansys_installation()[0]

        # Verify that the minimum version is installed.
        _check_minimal_versions(version, specific_minimum_version)

    # If Windows Service is requested, BUT version is not 2025R1 or earlier, we will have
    # to change the backend type to CORE_WINDOWS and throw a warning.
    if backend_type == BackendType.WINDOWS_SERVICE and version > 251:
        LOG.warning(
            "DMS Windows Service is not available for Ansys versions 2025R2 and later. "
            "Switching to Core Windows Service."
        )
        backend_type = BackendType.CORE_WINDOWS

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
        args.append(Path(installations[version], DISCOVERY_FOLDER, DISCOVERY_EXE))
        if hidden is True:
            args.append(BACKEND_DISCOVERY_HIDDEN)

        # Here begins the spaceclaim arguments.
        args.append(BACKEND_SPACECLAIM_OPTIONS)
        args.append(
            BACKEND_ADDIN_MANIFEST_ARGUMENT
            + _manifest_path_provider(version, installations, manifest_path)
        )
        env_copy[BACKEND_API_VERSION_VARIABLE] = str(api_version)

    elif backend_type == BackendType.SPACECLAIM:
        args.append(Path(installations[version], SPACECLAIM_FOLDER, SPACECLAIM_EXE))
        if hidden is True:
            args.append(BACKEND_SPACECLAIM_HIDDEN)
            args.append(BACKEND_SPLASH_OFF)
        args.append(
            BACKEND_ADDIN_MANIFEST_ARGUMENT
            + _manifest_path_provider(version, installations, manifest_path)
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
        root_service_folder = os.getenv(ANSYS_GEOMETRY_SERVICE_ROOT)
        if root_service_folder is None:
            root_service_folder = Path(installations[version], WINDOWS_GEOMETRY_SERVICE_FOLDER)
        else:
            root_service_folder = Path(root_service_folder)
        args.append(
            Path(
                root_service_folder,
                GEOMETRY_SERVICE_EXE,
            )
        )
    # This should be modified to Windows Core Service in the future
    elif BackendType.is_core_service(backend_type):
        # Define several Ansys Geometry Core Service folders needed
        root_service_folder = os.getenv(ANSYS_GEOMETRY_SERVICE_ROOT)
        if root_service_folder is None:
            root_service_folder = Path(installations[version], CORE_GEOMETRY_SERVICE_FOLDER)
        else:
            root_service_folder = Path(root_service_folder)
        native_folder = root_service_folder / "Native"
        cad_integration_folder = root_service_folder / "CADIntegration"
        cad_integration_folder_bin = cad_integration_folder / "bin"
        schema_folder = root_service_folder / "Schema"

        # Adapt the native folder to the OS
        # The native folder is different for Windows and Linux.
        if os.name == "nt":
            native_folder = native_folder / "Windows"
        else:
            native_folder = native_folder / "Linux"

        # Set the environment variables for the Ansys Geometry Core Service launch
        # ANS_DSCO_REMOTE_IP should be variable "host" directly, but not working...
        env_copy["ANS_DSCO_REMOTE_IP"] = "127.0.0.1" if host == "localhost" else host
        env_copy["ANS_DSCO_REMOTE_PORT"] = str(port)
        env_copy["P_SCHEMA"] = schema_folder.as_posix()
        env_copy["ANSYS_CI_INSTALL"] = cad_integration_folder.as_posix()
        if version:
            env_copy[f"ANSYSCL{version}_DIR"] = (root_service_folder / "licensingclient").as_posix()
        else:
            # Env var is passed... but no product version is defined. We define all of them.
            # Starting on 251... We can use the values in the enum ApiVersions.
            for api_version in ApiVersions:
                if api_version.value < 251:
                    continue
                env_copy[f"ANSYSCL{api_version.value}_DIR"] = (
                    root_service_folder / "licensingclient"
                ).as_posix()

        # License server - for Core Geometry Service. If not defined, it will use the default one.
        if "LICENSE_SERVER" in os.environ:
            pass  # Do nothing... the user has defined the license server.
        elif "ANSRV_GEO_LICENSE_SERVER" in os.environ:
            env_copy["LICENSE_SERVER"] = os.getenv("ANSRV_GEO_LICENSE_SERVER")
        else:
            env_copy["LICENSE_SERVER"] = os.getenv("ANSYSLMD_LICENSE_FILE", "1055@localhost")

        # Adapt the path environment variable to the OS and
        # modify the PATH/LD_LIBRARY_PATH variable to include the path
        # to the Ansys Geometry Core Service
        path_env_var = "PATH" if os.name == "nt" else "LD_LIBRARY_PATH"
        env_copy[path_env_var] = os.pathsep.join(
            [
                root_service_folder.as_posix(),
                native_folder.as_posix(),
                cad_integration_folder_bin.as_posix(),
                env_copy.get(path_env_var, ""),
            ]
        )

        if os.name == "nt":
            # For Windows, we need to use the exe file to launch the Core Geometry Service
            args.append(
                Path(
                    root_service_folder,
                    CORE_GEOMETRY_SERVICE_EXE,
                )
            )
        else:
            # Verify dotnet is installed
            import shutil

            if not any(
                CORE_GEOMETRY_SERVICE_EXE.replace(".exe", "") == file.name
                for file in Path(root_service_folder).iterdir()
            ):
                if not shutil.which("dotnet"):
                    raise RuntimeError(
                        "Cannot find 'dotnet' command. "
                        "Please install 'dotnet' to use the Ansys Geometry Core Service. "
                        "At least dotnet 8.0 is required."
                    )
                # At least dotnet 8.0 is required
                # private method and controlled input by library - excluding bandit check.
                if (
                    subprocess.check_output(["dotnet", "--version"]).decode("utf-8").split(".")[0]  # nosec B607, B603
                    < "8"
                ):
                    raise RuntimeError(
                        "Ansys Geometry Core Service requires at least dotnet 8.0. "
                        "Please install a compatible version."
                    )
                # For Linux, we need to use the dotnet command to launch the Core Geometry Service
                args.append("dotnet")
                args.append(
                    Path(
                        root_service_folder,
                        CORE_GEOMETRY_SERVICE_EXE.replace(".exe", ".dll"),
                    )
                )
            else:
                # For Linux, we need to use the exe file to launch the Core Geometry Service
                args.append(
                    Path(
                        root_service_folder,
                        CORE_GEOMETRY_SERVICE_EXE.replace(".exe", ""),
                    )
                )
    else:
        raise RuntimeError(
            f"Cannot connect to backend {backend_type.name} using ``prepare_and_start_backend()``"
        )

    # Handling transport mode conditions
    exe_args, transport_values = _handle_transport_mode(
        host=host,
        transport_mode=transport_mode,
        uds_dir=uds_dir,
        uds_id=uds_id,
        certs_dir=certs_dir,
    )
    # HACK: This is a temporary hack to pass in the certs dir consistently.
    # Versions 252 and before were not handling the --certs-dir argument properly,
    # so we need to set it explicitly here as an environment variable.
    # This can be removed in future versions.
    #
    # Assign environment variables as needed
    if transport_values["certs_dir"]:
        env_copy["ANSYS_GRPC_CERTIFICATES"] = certs_dir
    
    # On SpaceClaim and Discovery, we need to change the "--" to "/"
    if backend_type in (BackendType.DISCOVERY, BackendType.SPACECLAIM):
        exe_args = [arg.replace("--", "/") for arg in exe_args]


    LOG.info(f"Launching ProductInstance for {backend_type.name}")
    LOG.debug(f"Args: {args}")
    LOG.debug(f"Exe args: {exe_args}")
    LOG.debug(f"Transport mode values: {transport_values}")
    LOG.debug(f"Environment variables: {env_copy}")

    instance = ProductInstance(
        __start_program(args, exe_args, env_copy, server_working_dir=server_working_dir).pid
    )

    # Verify that the backend is ready to accept connections
    # before returning the Modeler instance.
    LOG.info("Waiting for backend to be ready...")
    _wait_for_backend(host, port, timeout, transport_values)

    return Modeler(
        host=host,
        port=port,
        timeout=timeout,
        product_instance=instance,
        logging_level=client_log_level,
        logging_file=client_log_file,
        transport_mode=transport_values["transport_mode"],
        uds_id=transport_values["uds_id"],
        uds_dir=transport_values["uds_dir"],
        certs_dir=transport_values["certs_dir"],
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


def _wait_for_backend(host: str, port: int, timeout: int, transport_values: dict[str, str]) -> None:
    """Check if the backend is ready to accept connections.

    Parameters
    ----------
    host : str
        The backend's ip address.
    port : int
        The backend's port number.
    timeout : int
        The timeout in seconds.
    transport_values : dict[str, str]
        The transport mode values dictionary.
    """
    import time

    start_time = time.time()
    while time.time() - start_time < timeout:
        if transport_values["transport_mode"] == "uds":
            # For UDS, we just check if the socket file exists.
            if verify_uds_socket(
                "aposdas_socket", transport_values["uds_dir"], transport_values["uds_id"]
            ):
                LOG.debug("Backend is ready to accept connections.")
                return
            else:
                LOG.debug("Still waiting for backend to be ready... Retrying in 5 seconds.")
                time.sleep(5)
                continue
        # For other transport modes, we check if the port is open.
        else:
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
    if port == 0:
        return False  # Port 0 is reserved and cannot be used directly.
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


def __start_program(
    args: list[str],
    exe_args: list[str],
    local_env: dict[str, str],
    server_working_dir: str | os.PathLike | None = None,
) -> subprocess.Popen:
    """Start the program.

    Parameters
    ----------
    args : list[str]
        List of arguments to be passed to the program. The first list's item shall
        be the program path.
    exe_args : list[str]
        Additional command line arguments to be passed to the program.
    local_env : dict[str,str]
        Environment variables to be passed to the program.
    server_working_dir : str | Path, optional
        Working directory for the launched process. If None, the working directory
        of the parent process is used.

    Returns
    -------
    subprocess.Popen
        The subprocess object.

    Notes
    -----
    The path is the first item of the ``args`` array argument.
    """
    # private method and controlled input by library - excluding bandit check.
    return subprocess.Popen(  # nosec B603
        args + exe_args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=local_env,
        cwd=server_working_dir,
    )


def _check_minimal_versions(
    latest_installed_version: int, specific_minimum_version: int | None
) -> None:
    """Check client is compatible with Ansys Products.

    Check that at least V241 is installed. Or, if a specific version is requested,
    check that it is installed.
    """
    min_ver = specific_minimum_version or 241
    if abs(latest_installed_version) < min_ver:
        # Split the version into its components.
        major, minor = divmod(min_ver, 10)
        msg = (
            f"PyAnsys Geometry is compatible with Ansys Products from version {major}.{minor}.0. "
            + f"Please install Ansys products {major}.{minor}.0 or later."
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
    env_copy[BACKEND_LOG_LEVEL_VARIABLE] = f"{server_log_level}"

    if server_logs_folder is not None:
        env_copy[BACKEND_LOGS_FOLDER_VARIABLE] = f"{server_logs_folder}"

    if enable_trace:
        env_copy[BACKEND_TRACE_VARIABLE] = "1"  # for backward compatibility
        if server_log_level > 0:
            LOG.warning("Enabling trace mode will override the log level to 0 (Chatterbox).")
            env_copy[BACKEND_LOG_LEVEL_VARIABLE] = "0"

    return env_copy



def _handle_transport_mode(
    host: str,
    transport_mode: str | None = None,
    uds_dir: Path | str | None = None,
    uds_id: str | None = None,
    certs_dir: Path | str | None = None,
) -> tuple[list[str], dict[str, str], str]:
    """Handle transport mode conditions.

    Parameters
    ----------
    host : str
        The backend's ip address.
    transport_mode : str | None
        Transport mode selected, by default `None` and thus it will be selected
        for you based on the connection criteria. Options are: "insecure", "uds", "wnua", "mtls"
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
    tuple[str, dict[str, str]]

    """
    # Localhost addresses
    loopback_localhosts = ("localhost", "127.0.0.1")

    # Command line arguments to be passed to the backend
    exe_args = []

    # If the transport mode is selected, simply use it... with caution.
    if transport_mode is not None:
        verify_transport_mode(transport_mode)
    else:
        # Select the transport mode based on the connection criteria.
        # 1. if host is localhost.. either wnua or uds depending on the OS
        if host in loopback_localhosts:
            transport_mode = "wnua" if os.name == "nt" else "uds"
        else:
            # 2. if host is not localhost.. always default to mtls
            transport_mode = "mtls"

        LOG.info(
            f"Transport mode not specified. Selected '{transport_mode}'"
            " based on connection criteria."
        )

    # If mtls is selected -- verify certs_dir
    if transport_mode == "mtls":
        # Share the certificates directory if needed
        if certs_dir is None:
            certs_dir_env = os.getenv("ANSYS_GRPC_CERTIFICATES", None)
            if certs_dir_env is not None:
                certs_dir = certs_dir_env
            else:
                certs_dir = Path.cwd() / "certs"

        if not Path(certs_dir).is_dir():  # pragma: no cover
            raise RuntimeError(
                "Transport mode 'mtls' was selected, but the expected"
                f" certificates directory does not exist: {certs_dir}"
            )
        LOG.info(f"Using certificates directory: {Path(certs_dir).resolve()}")

        # Determine args to be passed to the backend
        exe_args.append(f"--transport-mode={transport_mode}")
        exe_args.append(f"--certs-dir={Path(certs_dir).resolve()}")

    elif transport_mode == "uds":
        # UDS is only available for localhost connections
        if host not in loopback_localhosts:
            raise RuntimeError("Transport mode 'uds' is only available for localhost connections.")
        # Share the uds_dir if needed
        if uds_dir is None:
            uds_dir = Path.home() / ".conn"

        # If the folder does not exist, create it
        uds_dir.mkdir(parents=True, exist_ok=True)

        # Verify that the UDS file doesn't already exist
        if verify_uds_socket("aposdas_socket", uds_dir, uds_id) is True:
            raise RuntimeError("UDS socket file already exists.")

        # Determine args to be passed to the backend
        exe_args.append(f"--transport-mode={transport_mode}")
        exe_args.append(f"--uds-dir={Path(uds_dir).resolve()}")
        if uds_id is not None:
            exe_args.append(f"--uds-id={uds_id}")

    elif transport_mode == "wnua":
        # WNUA is only available on Windows for localhost connections
        if os.name != "nt":  # pragma: no cover
            raise RuntimeError("Transport mode 'wnua' is only available on Windows.")
        if host not in loopback_localhosts:
            raise RuntimeError("Transport mode 'wnua' is only available for localhost connections.")

        # Determine args to be passed to the backend
        exe_args.append(f"--transport-mode={transport_mode}")

    elif transport_mode == "insecure":
        # Determine args to be passed to the backend
        exe_args.append(f"--transport-mode={transport_mode}")

    else:  # pragma: no cover
        raise RuntimeError(f"Transport mode '{transport_mode}' is not recognized.")

    # Store the final transport values
    transport_values = {
        "transport_mode": transport_mode,
        "uds_dir": uds_dir,
        "uds_id": uds_id,
        "certs_dir": certs_dir,
    }

    # Return the args to be passed to the backend, and the transport values
    return exe_args, transport_values