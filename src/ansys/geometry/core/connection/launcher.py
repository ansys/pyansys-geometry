"""Provides for connecting to Geometry service instances."""
from beartype.typing import TYPE_CHECKING, Dict, Optional

from ansys.geometry.core.connection.defaults import DEFAULT_PORT
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
    """Start the ``Modeler`` for PyGeometry.

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
    from ansys.geometry.core.modeler import Modeler

    check_type(version, (type(None), str))

    if not _HAS_PIM:  # pragma: no cover
        raise ModuleNotFoundError(
            "The package 'ansys-platform-instancemanagement' is required to use this function."
        )

    pim = pypim.connect()
    instance = pim.create_instance(product_name="geometry", product_version=version)
    instance.wait_for_ready()
    channel = instance.build_grpc_channel(
        options=[
            ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
        ]
    )
    return Modeler(channel=channel, remote_instance=instance)


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
