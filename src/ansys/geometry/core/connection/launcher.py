"""Provides for connecting to instances of the Geometry service."""
import os

from beartype.typing import TYPE_CHECKING, Dict, Optional

from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.connection.defaults import DEFAULT_PIM_CONFIG, DEFAULT_PORT
from ansys.geometry.core.connection.local_instance import (
    _HAS_DOCKER,
    GeometryContainers,
    LocalDockerInstance,
)
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
    Start the ``Modeler`` interface for PyGeometry.

    Parameters
    ----------
    **kwargs : dict, default: None
        Keyword arguments for the launching methods. For allowable keyword arguments, see the
        :func:`launch_remote_modeler` and :func:`launch_local_modeler` methods. Some of
        them might be unused.

    Returns
    -------
    ansys.geometry.core.Modeler
        Pythonic interface for geometry modeling.

    Examples
    --------
    Launch the Geometry service.

    >>> from ansys.geometry.core import launch_modeler
    >>> modeler = launch_modeler()
    """
    # A local Docker container of the Geometry service or `PyPIM <https://github.com/ansys/pypim>`_
    # is required for this to work. Neither is integrated, but they could possibly be added later.

    # Another alternative is to use this method to run Docker locally.

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
    environment where `PyPIM <https://github.com/ansys/pypim>`_ is
    configured. You can use the
    :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if it is configured.

    Parameters
    ----------
    version : str, default: None
        Version of the Geometry service to run in the three-digit format.
        For example, "232". If you do not specify the version, the server
        chooses the version.
    **kwargs : dict, default: None
        Keyword arguments for the launching methods. For allowable keyword arguments, see the
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
    at the given port, it connects to it. Otherwise, it tries to launch its own
    service.

    Parameters
    ----------
    port : int, optional
        Localhost port to deploy the Geometry service on or the
        the ``Modeler`` interface to connect to (if it is already deployed). By default,
        the value is the one for the ``DEFAULT_PORT`` connection parameter.
    connect_to_existing_service : bool, default: True
        Whether the ``Modeler`` interface should connect to a Geometry
        service already deployed at the specified port.
    restart_if_existing_service : bool, default: False
        Whether the Geometry service (which is already running)
        should be restarted when attempting connection.
    name : Optional[str], default: None
        Name of the Docker container to deploy. The default is ``None``,
        in which case Docker assigns it a random name.
    image : Optional[GeometryContainers], default: None
        The Geometry service Docker image to deploy. The default is ``None``,
        in which case the ``LocalDockerInstance`` class identifies the OS of your
        Docker engine and deploys the latest version of the Geometry service for
        that OS.
    **kwargs : dict, default: None
        Keyword arguments for the launching methods. For allowable keyword arguments, see the
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
    Start Ansys Discovery remotely using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where `PyPIM <https://github.com/ansys/pypim>`_ is configured.
    You can use the :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if it is configured.

    Parameters
    ----------
    version : str, default: None
        Version of Discovery to run in the three-digit format.
        For example, "232". If you do not specify the version, the server
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
    Start the Geometry service remotely using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where `PyPIM <https://github.com/ansys/pypim>`_ is configured.
    You can use the :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if it is configured.

    Parameters
    ----------
    version : str, default: None
        Version of the Geometry service to run in the three-digit format.
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
    Start Ansys SpaceClaim remotely using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where `PyPIM <https://github.com/ansys/pypim>`_ is configured.
    You can use the :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if it is configured.

    Parameters
    ----------
    version : str, default: None
        Version of SpaceClaim to run in the three-digit format.
        For example, "232". If you do not specify the version, the server
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
    Start `PyPIM <https://github.com/ansys/pypim>`_ using the PIM API.

    When calling this method, you must ensure that you are in an
    environment where PyPIM is configured. You can use the
    :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
    method to check if it is configured.

    Parameters
    ----------
    is_pim_light : bool
        Whether PIM Light is being used. For example, whether PIM is
        running on a local machine.
    product_name : str
        Name of the service to run.
    product_version : str, default: None
        Version of the service to run.
    backend_type : BackendType, default: None
        Type of backend that PyGeometry is communicating with. By default, this
        value is unknown, which results in ``None`` being the default value.

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
