"""Module containing the ``ProductInstance`` class."""
import logging
import os
import signal
import socket
import subprocess

from ansys.tools.path import get_available_ansys_installations
from beartype.typing import TYPE_CHECKING, Dict

from ansys.geometry.core.connection.backend import ApiVersions, BackendType
from ansys.geometry.core.logger import LOG as logger

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.modeler import Modeler

"""Provides constant and environment variables values or names."""

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
"""
Default backend's addin filename.

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

BACKEND_API_VERSION_VARIABLE = "API_VERSION"
"""
The backend's api version environment variable for local start.

To be used only with Ansys Discovery and Ansys SpaceClaim.
"""

BACKEND_SPACECLAIM_OPTIONS = "--spaceclaim-options"
"""
The additional argument for local Ansys Discovery start.

To be used only with Ansys Discovery.
"""

BACKEND_ADDIN_MANIFEST_ARGUMENT = "/ADDINMANIFESTFILE="
"""
The argument to specify the backend's addin manifest file's path.

To be used only with Ansys Discovery and Ansys SpaceClaim.
"""


class ProductInstance:
    """
    ``ProductInstance`` class.

    This class is used as a handle for a local session of Ansys Product's backend: Discovery,
    Windows Geometry Service or SpaceClaim.

    Parameters
    ----------
    pid : int
        The local instance's process identifier. This allows to  keep track of the process
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
            logging.error(str(oserr))
            return False
        return True


def prepare_and_start_backend(
    backend_type: BackendType,
    product_version: int = None,
    host: str = "localhost",
    port: int = None,
    enable_trace: bool = False,
    log_level: int = 2,
    api_version: ApiVersions = ApiVersions.latest,
    timeout: int = 150,
) -> "Modeler":
    """
    Start the Geometry service locally using the ``ProductInstance`` class.

    When calling this method, a standalone Geometry service is started.
    By default, if an endpoint is specified (by defining `host` and `port` parameters)
    but the endpoint isnt't available, the startup will fail. Otherwise, it will try to
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
    log_level : int, optional
        Backend's log level from 0 to 3:
            0: Chatterbox
            1: Debug
            2: Warning
            3: Error
        The default is ``2`` (Warning).
    api_version: ``ApiVersions``, optional
        The backend's API version to be used at runtime. Goes from API v21 to
        the latest. Default is ``ApiVersions.latest``.
    timeout : int, optional
        Timeout for starting the backend startup process. The default is 150.

    Exceptions
    ----------
    ConnectionError:
        if the specified endpoint is already in use, a connection error will be raised.
    SystemError:
        if there isn't an Ansys products 23.2 version or later installed
        or if a specific product's version is requested but not installed locally then
        a SystemError will be raised.

    Returns
    -------
    Modeler
        Instance of the Geometry service.
    """
    from ansys.geometry.core.modeler import Modeler

    port = _check_port_or_get_one(port)
    installations = get_available_ansys_installations()
    keys = list(installations.keys())
    latest_version = max(keys)
    _check_minimal_versions(latest_version)
    if product_version != None:
        _check_version_is_available(product_version, installations)
    else:
        product_version = latest_version

    args = []
    env_copy = _get_common_env(host=host, port=port, enable_trace=enable_trace, log_level=log_level)
    logger.debug(env_copy)
    if backend_type == BackendType.DISCOVERY:
        args.append(os.path.join(installations[product_version], DISCOVERY_FOLDER, DISCOVERY_EXE))
        args.append(BACKEND_SPACECLAIM_OPTIONS)
        args.append(
            BACKEND_ADDIN_MANIFEST_ARGUMENT
            + _manifest_path_provider(product_version, installations)
        )
        env_copy[BACKEND_API_VERSION_VARIABLE] = str(api_version)
    elif backend_type == BackendType.SPACECLAIM:
        args.append(os.path.join(installations[product_version], SPACECLAIM_FOLDER, SPACECLAIM_EXE))
        args.append(
            BACKEND_ADDIN_MANIFEST_ARGUMENT
            + _manifest_path_provider(product_version, installations)
        )
        env_copy[BACKEND_API_VERSION_VARIABLE] = str(api_version)
    else:
        # We're starting the Windows GeometryService (DMS)
        installations = get_available_ansys_installations()
        keys = list(installations.keys())
        latest_version = max(keys)
        args.append(
            os.path.join(
                installations[latest_version], WINDOWS_GEOMETRY_SERVICE_FOLDER, GEOMETRY_SERVICE_EXE
            )
        )
    logger.debug(args)
    instance = ProductInstance(_start_program(args, env_copy).pid)
    return Modeler(
        host=host, port=port, timeout=timeout, product_instance=instance, backend_type=backend_type
    )


def _get_available_port():
    sock = socket.socket()
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def _is_port_available(port: int, host: str = "localhost") -> bool:
    if port != 0:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
                logging.info("Port" + str(port) + " is available.")
                return True
            except:
                logging.error(
                    f"Check port availability failed. Port {port} already in use."
                )
                return False


def _manifest_path_provider(version: int, available_installations: dict):
    return os.path.join(
        available_installations[version], ADDINS_SUBFOLDER, BACKEND_SUBFOLDER, MANIFEST_FILENAME
    )


def _start_program(args, local_env) -> subprocess.Popen:
    logging.info("Starting program: " + str(args))
    session = subprocess.Popen(
        args,
        shell=os.name != "nt",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=local_env,
    )
    return session


def _check_minimal_versions(latest_installed_version: int):
    if latest_installed_version < 232:
        msg = "PyGeometry is compatible with Ansys Products from version 23.2.1."
        msg.join("Please install Ansys products 23.2.1 or later.")
        logging.error(msg)
        raise SystemError(msg)


def _check_version_is_available(version: int, installations: Dict[int, str]):
    if version not in installations:
        msg = f"The requested Ansys product's version: {version} isn't available,"
        msg.join("please specify a different version.")
        logging.error(msg)
        raise SystemError(msg)


def _check_port_or_get_one(port: int) -> int:
    if port != None and _is_port_available(port) == False:
        msg = "Port " + str(port) + " is already in use. Please specify a different one."
        logging.error(msg)
        raise ConnectionError(msg)
    elif port == None:
        port = _get_available_port()
    return port


def _get_common_env(host: str, port: int, enable_trace: bool, log_level: int) -> dict[str, str]:
    env_copy = os.environ.copy()
    env_copy[BACKEND_HOST_VARIABLE] = host
    env_copy[BACKEND_PORT_VARIABLE] = str(port)
    if enable_trace == True:
        env_copy[BACKEND_TRACE_VARIABLE] = str(1)
    else:
        env_copy[BACKEND_TRACE_VARIABLE] = str(0)

    env_copy[BACKEND_LOG_LEVEL_VARIABLE] = str(log_level)
    return env_copy
