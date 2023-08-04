"""Provides for connecting to Geometry service instances."""
import os

from beartype.typing import TYPE_CHECKING, Dict, Optional

from ansys.geometry.core.connection.backend import ApiVersions, BackendType
from ansys.geometry.core.connection.defaults import DEFAULT_PIM_CONFIG, DEFAULT_PORT
from ansys.geometry.core.connection.local_instance import (
    _HAS_DOCKER,
    GeometryContainers,
    LocalDockerInstance,
)
from ansys.geometry.core.connection.product_instance import prepare_and_start_backend
from ansys.geometry.core.logger import LOG as logger
from ansys.geometry.core.misc import check_type

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


def launch_modeler_with_geometry_service(
    host: str = "localhost",
    port: int = None,
    enable_trace: bool = False,
    log_level: int = 2,
    timeout: int = 60,
) -> "Modeler":
    """
    Start the Geometry service locally using the ``ProductInstance`` class.

    When calling this method, a standalone Geometry service is started.
    By default, if an endpoint is specified (by defining `host` and `port` parameters)
    but the endpoint is not available, the startup will fail. Otherwise, it will try to
    launch its own service.

    Parameters
    ----------
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
    timeout : int, optional
        Timeout for starting the backend startup process. The default is 60.

    Exceptions
    ----------
    ConnectionError
        If the specified endpoint is already in use, a connection
        error will be raised.
    SystemError
        If there is not an Ansys product 23.2 version or later installed
        a SystemError will be raised.

    Returns
    -------
    Modeler
        Instance of the Geometry service.
    """
    return prepare_and_start_backend(
        BackendType.WINDOWS_SERVICE,
        host=host,
        port=port,
        enable_trace=enable_trace,
        log_level=log_level,
        api_version=ApiVersions.LATEST,
        timeout=timeout,
    )


def launch_modeler_with_discovery(
    product_version: int = None,
    host: str = "localhost",
    port: int = None,
    log_level: int = 2,
    api_version: ApiVersions = ApiVersions.LATEST,
    timeout: int = 150,
):
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
    ConnectionError
        If the specified endpoint is already in use, a connection error will be raised.
    SystemError:
        If there is not an Ansys product 23.2 version or later installed
        or if a specific product's version is requested but not installed locally then
        a SystemError will be raised.

    Returns
    -------
    Modeler
        Instance of the Geometry service.
    """
    return prepare_and_start_backend(
        BackendType.DISCOVERY,
        product_version=product_version,
        host=host,
        port=port,
        enable_trace=False,
        log_level=log_level,
        api_version=api_version,
        timeout=timeout,
    )


def launch_modeler_with_spaceclaim(
    product_version: int = None,
    host: str = "localhost",
    port: int = None,
    log_level: int = 2,
    api_version: ApiVersions = ApiVersions.LATEST,
    timeout: int = 150,
):
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
    return prepare_and_start_backend(
        BackendType.SPACECLAIM,
        product_version=product_version,
        host=host,
        port=port,
        enable_trace=False,
        log_level=log_level,
        api_version=api_version,
        timeout=timeout,
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
