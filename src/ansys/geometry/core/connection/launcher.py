"""Provides for connecting to Geometry service instances."""
import os
import socket
import logging
from distutils.sysconfig import get_python_lib
from pathlib import Path
import errno
import logging
import os
import subprocess

from beartype.typing import TYPE_CHECKING, Dict, Optional, Union

from ansys.geometry.core.connection.backend import BackendType, ProductVersions, ApiVersions
from ansys.geometry.core.connection.defaults import (
    DEFAULT_PIM_CONFIG, 
    DEFAULT_PORT,)
from ansys.geometry.core.connection.environment import (
    WINDOWS_GEOMETRY_SERVICE_FOLDER, 
    DISCOVERY_FOLDER, 
    SPACECLAIM_FOLDER, 
    MANIFEST_FILENAME,
    BACKEND_SUBFOLDER,
    ADDINS_SUBFOLDER,
    GEOMETRY_SERVICE_EXE,
    DISCOVERY_EXE,
    SPACECLAIM_EXE,
    BACKEND_LOG_LEVEL_VARIABLE,
    BACKEND_TRACE_VARIABLE,
    BACKEND_HOST_VARIABLE,
    BACKEND_PORT_VARIABLE,
    BACKEND_API_VERSION_VARIABLE,
    BACKEND_SPACECLAIM_OPTIONS,
    BACKEND_ADDIN_MANIFEST_ARGUMENT,
)
from ansys.geometry.core.connection.local_instance import (
    _HAS_DOCKER,
    GeometryContainers,
    LocalDockerInstance,
)
from ansys.geometry.core.connection.product_instance import ProductInstance

from ansys.geometry.core.logger import LOG as logger
from ansys.geometry.core.misc import check_type
from ansys.tools.path import get_available_ansys_installations

try:
    import ansys.platform.instancemanagement as pypim

    _HAS_PIM = True
except ModuleNotFoundError:  # pragma: no cover
    _HAS_PIM = False

from ansys.geometry.core.connection.client import MAX_MESSAGE_LENGTH

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.modeler import Modeler


def launch_modeler(**kwargs: Optional[Dict]) -> "Modeler":
    """
    Start the ``Modeler`` for PyGeometry.

    Parameters
    ----------
    **kwargs : dict, default: None
        Launching functions keyword arguments. For allowable keyword arguments, see the
        :func:`launch_remote_modeler` and :func:`launch_local_modeler` methods. Some of
        them might be unused.

    Returns
    -------
    ansys.geometry.core.Modeler
        Pythonic interface for geometry modeling.

    Examples
    --------
    Launch the Ansys Geometry service.

    >>> from ansys.geometry.core import launch_modeler
    >>> modeler = launch_modeler()
    """
    # A local Docker container of the Geometry service or PyPIM is required for
    # this to work. Neither is integrated, but we can consider adding them later.

    # Another alternative is to run Docker locally from this method.

    # Start PyGeometry with PyPIM if the environment is configured for it
    # and a directive on how to launch it was not passed.
    if _HAS_PIM and pypim.is_configured():
        logger.info("Starting Geometry service remotely. The startup configuration is ignored.")
        return launch_remote_modeler(**kwargs)

    # Otherwise, we are in the "local Docker Container" scenario
    if _HAS_DOCKER and LocalDockerInstance.is_docker_installed():
        logger.info("Starting Geometry service locally from Docker container.")
        return launch_local_modeler(**kwargs)

    # If we reached this point...
    raise NotImplementedError("Geometry service cannot be initialized.")


def launch_remote_modeler(version: Optional[str] = None, **kwargs: Optional[Dict]) -> "Modeler":
    """
    Start the Geometry service remotely using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where PyPIM is configured. PyPIM is the Pythonic
    interface to communicate with the PIM (Product Instance Management)
    API. You can use the
    :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if PyPIM is configured.

    Parameters
    ----------
    version : str, default: None
        Version of the Geometry service to run in the three-digit format.
        For example, "212". If you do not specify the version, the server
        chooses the version.
    **kwargs : dict, default: None
        Launching functions keyword arguments. For allowable keyword arguments, see the
        :func:`launch_remote_modeler` and :func:`launch_local_modeler` methods. Some of
        them might be unused.

    Returns
    -------
    ansys.geometry.core.modeler.Modeler
        Instance of the Geometry service.
    """
    return _launch_pim_instance(
        is_pim_light=False,
        product_name="geometry",
        product_version=version,
        backend_type=None,
    )


def launch_local_modeler(
    port: int = DEFAULT_PORT,
    connect_to_existing_service: bool = True,
    restart_if_existing_service: bool = False,
    name: Optional[str] = None,
    image: Optional[GeometryContainers] = None,
    **kwargs: Optional[Dict],
) -> "Modeler":
    """
    Start the Geometry service locally using the ``LocalDockerInstance`` class.

    When calling this method, a Geometry service (as a local Docker container)
    is started. By default, if a container with the Geometry service already exists
    at the given port, it will connect to it. Otherwise, it will try to launch its own
    service.

    Parameters
    ----------
    port : int, optional
        Localhost port at which the Geometry service will be deployed or which
        the ``Modeler`` will connect to (if it is already deployed). By default,
        value will be the one at ``DEFAULT_PORT``.
    connect_to_existing_service : bool, optional
        Boolean indicating whether if the Modeler should connect to a Geometry
        Service already deployed at that port, by default ``True``.
    restart_if_existing_service : bool, optional
        Boolean indicating whether the Geometry service (which is already running)
        should be restarted when attempting connection, by default ``False``
    name : Optional[str], optional
        Name of the Docker container to be deployed, by default ``None``, which
        means that Docker will assign it a random name.
    image : Optional[GeometryContainers], optional
        The Geometry service Docker image to be deployed, by default ``None``, which
        means that the ``LocalDockerInstance`` class will identify the OS of your
        Docker engine and deploy the latest version of the Geometry service for that
        OS.
    **kwargs : dict, default: None
        Launching functions keyword arguments. For allowable keyword arguments, see the
        :func:`launch_remote_modeler` and :func:`launch_local_modeler` methods. Some of
        them might be unused.

    Returns
    -------
    Modeler
        Instance of the Geometry service.
    """
    from ansys.geometry.core.modeler import Modeler

    if not _HAS_DOCKER:  # pragma: no cover
        raise ModuleNotFoundError("The package 'docker' is required to use this function.")

    # Call the LocalDockerInstance ctor.
    local_instance = LocalDockerInstance(
        port=port,
        connect_to_existing_service=connect_to_existing_service,
        restart_if_existing_service=restart_if_existing_service,
        name=name,
        image=image,
    )

    # Once the local instance is ready... return the Modeler
    return Modeler(host="localhost", port=port, local_instance=local_instance)


def launch_modeler_with_pimlight_and_discovery(version: Optional[str] = None) -> "Modeler":
    """
    Start Discovery remotely using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where PyPIM is configured. PyPIM is the Pythonic
    interface to communicate with the PIM (Product Instance Management)
    API. You can use the
    :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if PyPIM is configured.

    Parameters
    ----------
    version : str, default: None
        Version of Discovery to run in the three-digit format.
        For example, "212". If you do not specify the version, the server
        chooses the version.

    Returns
    -------
    ansys.geometry.core.Modeler
        Instance of Modeler.
    """
    return _launch_pim_instance(
        is_pim_light=True,
        product_name="discovery",
        product_version=version,
        backend_type=BackendType.DISCOVERY,
    )


def launch_modeler_with_pimlight_and_geometry_service(version: Optional[str] = None) -> "Modeler":
    """
    Start the GeometryService remotely using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where PyPIM is configured. PyPIM is the Pythonic
    interface to communicate with the PIM (Product Instance Management)
    API. You can use the
    :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if PyPIM is configured.

    Parameters
    ----------
    version : str, default: None
        Version of GeometryService to run in the three-digit format.
        For example, "232". If you do not specify the version, the server
        chooses the version.

    Returns
    -------
    ansys.geometry.core.Modeler
        Instance of Modeler.
    """
    return _launch_pim_instance(
        is_pim_light=True,
        product_name="geometryservice",
        product_version=version,
        backend_type=BackendType.WINDOWS_SERVICE,
    )


def launch_modeler_with_pimlight_and_spaceclaim(version: Optional[str] = None) -> "Modeler":
    """
    Start SpaceClaim remotely using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where PyPIM is configured. PyPIM is the Pythonic
    interface to communicate with the PIM (Product Instance Management)
    API. You can use the
    :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if PyPIM is configured.

    Parameters
    ----------
    version : str, default: None
        Version of SpaceClaim to run in the three-digit format.
        For example, "212". If you do not specify the version, the server
        chooses the version.

    Returns
    -------
    ansys.geometry.core.Modeler
        Instance of Modeler.
    """
    return _launch_pim_instance(
        is_pim_light=True,
        product_name="scdm",
        product_version=version,
        backend_type=BackendType.SPACECLAIM,
    )


def _launch_pim_instance(
    is_pim_light: bool,
    product_name: str,
    product_version: Optional[str] = None,
    backend_type: Optional[BackendType] = None,
):
    """
    Start the service using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where PyPIM is configured. PyPIM is the Pythonic
    interface to communicate with the PIM (Product Instance Management)
    API. You can use the
    :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if PyPIM is configured.

    Parameters
    ----------
    is_pim_light : bool
        Whether PIM Light is being used (i.e. for running PIM on a local machine).
    product_name : str
        Name of the service to run.
    product_version : str, optional
        Version of the service to run. By default, ``None``.
    backend_type : BackendType, optional
        Service backend type deployed. By default, ``None``.

    Returns
    -------
    ansys.geometry.core.modeler.Modeler
        Instance of the Geometry service.
    """
    from ansys.geometry.core.modeler import Modeler

    check_type(product_version, (type(None), str))

    if not _HAS_PIM:  # pragma: no cover
        raise ModuleNotFoundError(
            "The package 'ansys-platform-instancemanagement' is required to use this function."
        )

    # If PIM Light is being used and PyPIM configuration is not defined... use defaults.
    if is_pim_light and not os.environ.get("ANSYS_PLATFORM_INSTANCEMANAGEMENT_CONFIG", None):
        os.environ["ANSYS_PLATFORM_INSTANCEMANAGEMENT_CONFIG"] = DEFAULT_PIM_CONFIG
        pop_out = True
    else:
        pop_out = False

    # Perform PyPIM connection
    pim = pypim.connect()
    instance = pim.create_instance(product_name=product_name, product_version=product_version)
    instance.wait_for_ready()
    channel = instance.build_grpc_channel(
        options=[
            ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
        ]
    )

    # If the default PyPIM configuration was used... remove
    if pop_out:
        os.environ.pop("ANSYS_PLATFORM_INSTANCEMANAGEMENT_CONFIG")

    return Modeler(channel=channel, remote_instance=instance, backend_type=backend_type)

def launch_modeler_with_geometry_service( 
    host : str = "localhost", 
    port: int = None, 
    enable_trace: bool = False, 
    log_level: int = 2, 
    timeout = 150) -> "Modeler":
    """"""
    return _prepare_and_start_backend(
        BackendType.WINDOWS_SERVICE,
        product_version= ProductVersions.latest,
        host= host,
        port= port,
        enable_trace= enable_trace,
        log_level= log_level,
        api_version= ApiVersions.latest,
        timeout= timeout)

            
def launch_modeler_with_discovery(
    product_version: Union[ProductVersions, int] = ProductVersions.latest.value, 
    host: str = "localhost", 
    port: int = None, 
    enable_trace: bool = False, 
    log_level: int = 2, 
    api_version: ApiVersions = ApiVersions.latest, 
    timeout = 150):
    """"""

    return _prepare_and_start_backend(
        BackendType.DISCOVERY,
        product_version= product_version,
        host= host,
        port= port,
        enable_trace= enable_trace,
        log_level= log_level,
        api_version= api_version,
        timeout= timeout)

        
def launch_modeler_with_spaceclaim(   
    product_version: Union[ProductVersions, int] = ProductVersions.latest.value, 
    host: str = "localhost", 
    port: int = None, 
    enable_trace: bool = False, 
    log_level: int = 2, 
    api_version: ApiVersions = ApiVersions.latest,
    timeout = 150):
    """"""
    return _prepare_and_start_backend(
        BackendType.SPACECLAIM,
        product_version= product_version,
        host= host,
        port= port,
        enable_trace= enable_trace,
        log_level= log_level,
        api_version= api_version,
        timeout= timeout)        

def _prepare_and_start_backend(
    backend_type: BackendType,
    product_version: Union[ProductVersions, int] = ProductVersions.latest.value, 
    host: str = "localhost", 
    port: int = None, 
    enable_trace: bool = False, 
    log_level: int = 2, 
    api_version: ApiVersions = ApiVersions.latest, 
    timeout = 150) -> "Modeler":

    from ansys.geometry.core.modeler import Modeler

    port = _check_port_or_get_one(port)
    installations = get_available_ansys_installations()    
    _check_minimal_versions()
    _check_version_is_available(product_version, installations)

    args = []
    env_copy = _get_common_env( host= host, port= port, enable_trace=enable_trace, log_level= log_level)

    if(backend_type == BackendType.DISCOVERY):
        args.append(os.path.join(installations[product_version], DISCOVERY_FOLDER, DISCOVERY_EXE))
        args.append(BACKEND_SPACECLAIM_OPTIONS)
        args.append(BACKEND_ADDIN_MANIFEST_ARGUMENT + _manifest_path_provider(product_version, installations))
        env_copy[BACKEND_API_VERSION_VARIABLE] = str(api_version)
    elif( backend_type == BackendType.SPACECLAIM):
        args.append(os.path.join(installations[product_version], SPACECLAIM_FOLDER, SPACECLAIM_EXE))
        args.append(BACKEND_ADDIN_MANIFEST_ARGUMENT + _manifest_path_provider(product_version, installations))
        env_copy[BACKEND_API_VERSION_VARIABLE] = str(api_version)
    else:
        # We're starting the Windows GeometryService (DMS)
        installations = get_available_ansys_installations()
        keys = list(installations.keys())
        latest_version = max(keys)
        args.append(os.path.join(installations[latest_version], WINDOWS_GEOMETRY_SERVICE_FOLDER, GEOMETRY_SERVICE_EXE)) 
    print(args)
    instance = ProductInstance(_start_program(args, env_copy).pid)
    return Modeler(host= host, port = port, timeout = timeout, product_instance=instance, backend_type=backend_type)

def _get_available_port():
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port
    
def _is_port_available(port: int , host: str = "localhost" ) -> bool:
    if port != 0:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
                logging.info("Port" + str(port) + " is available.")
                return True
            except:
                logging.error("Check port availability failed. Port " + str(port) +" already in use.")
                return False

def _manifest_path_provider(version: int , available_installations: dict):
    return os.path.join(
        available_installations[version], 
        ADDINS_SUBFOLDER, 
        BACKEND_SUBFOLDER, 
        MANIFEST_FILENAME
        )        

def _start_program(args, local_env) -> subprocess.Popen:
    logging.info("Starting program: " + str(args))
    session = subprocess.Popen(
        args,
        shell=os.name != "nt",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=local_env
        )
    return session

def _check_minimal_versions():
    installations = get_available_ansys_installations()
    keys = list(installations.keys())
    latest_version = max(keys)
    if latest_version < ProductVersions.V_232.value:
        msg = "PyGeometry is compatible with Ansys Products from version 23.2.1. Please install Ansys products 23.2.1 or later."
        logging.error(msg)
        raise ConnectionError(msg)

def _check_version_is_available(version: int, installations: Dict[int,str]):
    if version not in installations:
        msg = "The requested Ansys product's version isn't available, please specify a different version."
        logging.error(msg)
        raise ConnectionError(msg)

def _check_port_or_get_one(port:int) -> int:

    if port != None and _is_port_available(port) == False:
        msg = "Port " + str(port) + " is already in use. Please specify a different one."
        logging.error(msg)
        raise ConnectionError(msg)
    elif port == None:
        port = _get_available_port()
    return port

def _get_common_env(
    host: str, port: int, 
    enable_trace: bool, 
    log_level: int) -> dict[str,str]:

    env_copy = os.environ.copy()
    env_copy[BACKEND_HOST_VARIABLE] = host
    env_copy[BACKEND_PORT_VARIABLE] = str(port)
    if enable_trace == True:        
        env_copy[BACKEND_TRACE_VARIABLE] = str(1)
    else: 
        env_copy[BACKEND_TRACE_VARIABLE] = str(0)

    env_copy[BACKEND_LOG_LEVEL_VARIABLE] = str(log_level)
    return env_copy