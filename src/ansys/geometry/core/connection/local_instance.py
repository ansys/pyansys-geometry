"""Module containing the ``LocalDockerInstance`` class."""
from enum import Enum
from functools import wraps
import os

from beartype import beartype as check_input_types
from beartype.typing import Optional, Tuple, Union

try:
    import docker
    from docker.errors import APIError, ContainerError, ImageNotFound
    from docker.models.containers import Container

    _HAS_DOCKER = True
except ModuleNotFoundError:  # pragma: no cover
    _HAS_DOCKER = False

from ansys.geometry.core.connection.defaults import DEFAULT_PORT, GEOMETRY_SERVICE_DOCKER_IMAGE
from ansys.geometry.core.logger import LOG as logger


def _docker_python_available(func):
    """
    Check whether docker is installed as Python package or not.

    Works as a decorator.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _HAS_DOCKER:  # pragma: no cover
            raise ModuleNotFoundError(
                "The package 'docker' is required to use the LocalDockerInstance class."
            )
        else:
            return func(*args, **kwargs)

    return wrapper


class GeometryContainers(Enum):
    """Provides an enum holding the different Geometry services available."""

    WINDOWS_LATEST = 0, "windows", "windows-latest"
    LINUX_LATEST = 1, "linux", "linux-latest"
    WINDOWS_LATEST_UNSTABLE = 2, "windows", "windows-latest-unstable"
    LINUX_LATEST_UNSTABLE = 3, "linux", "linux-latest-unstable"


class LocalDockerInstance:
    """
    ``LocalDockerInstance`` class.

    This class is used for instantiating a Geometry service (as a local Docker container).
    By default, if a container with the Geometry service already exists at the given port,
    it will connect to it. Otherwise, it will try to launch its own service.

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
    """

    __DOCKER_CLIENT__: "docker.DockerClient" = None
    """
    Docker client class variable. By default, none is needed. It will be lazy
    initialized.

    Notes
    -----
    ``__DOCKER_CLIENT__`` is a class variable, meaning that it is
    the same variable for all instances of this class.
    """

    @staticmethod
    @_docker_python_available
    def docker_client() -> "docker.DockerClient":
        """Return the initialized ``__DOCKER_CLIENT__`` object.

        Notes
        -----
        LocalDockerInstance performs a lazy loading initialization of the class
        variable ``__DOCKER_CLIENT__``.

        Returns
        -------
        docker.DockerClient
            The initialized Docker client.

        """
        if not LocalDockerInstance.__DOCKER_CLIENT__:
            LocalDockerInstance.__DOCKER_CLIENT__ = docker.from_env()

        return LocalDockerInstance.__DOCKER_CLIENT__

    @staticmethod
    @_docker_python_available
    def is_docker_installed() -> bool:
        """
        Check whether there is a local install of Docker engine available and running.

        Returns
        -------
        bool
            ``True`` if Docker engine is running, ``False`` otherwise.
        """
        # When trying to ping, this throws back an error if the
        # server is not available
        try:
            return LocalDockerInstance.docker_client().ping()
        except APIError:  # pragma: no cover
            return False

    @check_input_types
    @_docker_python_available
    def __init__(
        self,
        port: int = DEFAULT_PORT,
        connect_to_existing_service: bool = True,
        restart_if_existing_service: bool = False,
        name: Optional[str] = None,
        image: Optional[GeometryContainers] = None,
    ) -> None:
        """``LocalDockerInstance`` constructor."""
        # Initialize instance variables
        self._container: Container = None
        self._existed_previously: bool = False

        # Check the port availability
        port_available, cont = self._check_port_availability(port)

        # If a service was already deployed... check if it is a Geometry service
        # in case we want to connect to it
        if cont and connect_to_existing_service and self._is_cont_geom_service(cont):
            # Now, let's check if a restart of the service is required
            if restart_if_existing_service:
                logger.warning(f"Restarting service already running at port {port}...")
                cont.restart()

            # Finally, store the container
            self._container = cont
            self._existed_previously = True
            return

        # At this stage we can confirm that we have to deploy our own Geometry service.
        # Let's get started with it!
        #
        # First, let's check if the port is available... otherwise raise error
        if port_available:
            self._deploy_container(port=port, name=name, image=image)
        else:
            raise RuntimeError(f"Geometry service cannot be deployed on port {port}")

    def _check_port_availability(self, port: int) -> Tuple[bool, Optional["Container"]]:
        """
        Check whether the requested port is available for deployment or not.

        Notes
        -----
        If not available, it also returns the ``Container`` deployed
        at that port.

        Returns
        -------
        tuple[bool, Container]
            Tuple with boolean indicating whether port is available (i.e. ``True``) or not.
            If not available, it also returns the container occupying that port.
        """
        # First, check if there is a container already running at that port
        for cont in self.docker_client().containers.list():
            for _, ports_shared in cont.attrs["NetworkSettings"]["Ports"].items():
                # If no ports are shared, continue looping
                if not ports_shared:
                    continue

                # Check shared ports otherwise
                for port_shared in ports_shared:
                    if int(port_shared["HostPort"]) == port:
                        logger.warning(f"Service already running at port {port}...")
                        return (False, cont)

        # If you reached here, just return default values
        return (True, None)

    def _is_cont_geom_service(self, cont: "Container") -> bool:
        """Check whether a provided ``Container`` object is a Geometry service container or not.

        Parameters
        ----------
        cont : Container
            Container deployed to check.

        Returns
        -------
        bool
            Returns ``True`` if the container provided is a Geometry service.
            Otherwise, ``False``.
        """
        # If one of the tags matches a Geometry service tag --> Return True
        for tag in cont.image.tags:
            for geom_services in GeometryContainers:
                if tag == f"{GEOMETRY_SERVICE_DOCKER_IMAGE}:{geom_services.value[2]}":
                    return True

        # If we reached this point, this means that our image is not a Geometry service
        return False  # pragma: no cover

    def _deploy_container(
        self, port: int, name: Union[str, None], image: Union[GeometryContainers, None]
    ):
        """
        Handle the deployment of a Geometry service according to the arguments.

        Parameters
        ----------
        port : int
            Port under which the service should be deployed.
        name : Union[str, None], optional
            Name given to the deployed container. If ``None``, Docker will provide
            an arbitrary name.
        image : Union[GeometryContainers, None]
            Geometry service Docker container image to be used. If ``None``, the
            latest container version matching

        Raises
        ------
        RuntimeError
            In case the Geometry service cannot be launched.
        """
        # First of all let's get the Docker Engine OS
        docker_os = self.docker_client().info()["OSType"]

        # If no image is provided, we will default to the whatever Docker engine OS
        # your system is running on... Latest images will be used since they are the
        # ones defined first in the GeometryContainers enum class.
        if image is None:
            for geom_service in GeometryContainers:
                if geom_service.value[1] == docker_os:
                    image = geom_service
                    break

        # If image is still None, this means it cannot be deployed on your OS
        #
        # Also, if you requested an image incompatible with the existing OS, it
        # will not be possible either.
        if image is None or image.value[1] != docker_os:  # pragma: no cover
            raise RuntimeError(f"Geometry service cannot be launched on {docker_os}")

        # At this point, we are good to deploy the Geometry service!
        #
        # Check if the license server env variable is available
        license_server = os.getenv("ANSRV_GEO_LICENSE_SERVER", None)
        if not license_server:  # pragma: no cover
            raise RuntimeError(
                f"No license server provided... Store its value under the following env variable: ANSRV_GEO_LICENSE_SERVER."  # noqa: E501
            )

        # Try to deploy it
        try:
            container: Container = self.docker_client().containers.run(
                image=f"{GEOMETRY_SERVICE_DOCKER_IMAGE}:{image.value[2]}",
                detach=True,
                auto_remove=True,
                name=name,
                ports={"50051/tcp": port},
                environment={
                    "LICENSE_SERVER": license_server,
                    "LOG_LEVEL": os.getenv("ANSRV_GEO_LOG_LEVEL", 2),
                    "ENABLE_TRACE": os.getenv("ANSRV_GEO_ENABLE_TRACE", 0),
                    "USE_DEBUG_MODE": os.getenv("ANSRV_GEO_USE_DEBUG_MODE", 0),
                },
            )
        except ImageNotFound as err:  # pragma: no cover
            raise RuntimeError(
                f"Geometry service Docker image {image.value[1]} not found. Please download it first to your machine."  # noqa: E501
            )
        except (ContainerError, APIError) as err:
            raise RuntimeError(
                f"Geometry service Docker image error when initialized. Error: {err.explanation}"
            )

        # If the deployment went fine, this means that we have deployed our service!
        self._container = container
        self._existed_previously = False

    @property
    def container(self) -> "Container":
        """Docker Container object hosting the Geometry service deployed."""
        return self._container

    @property
    def existed_previously(self) -> bool:
        """
        Indicate whether the container previously existed or not.

        Returns ``False`` if the Geometry service was effectively
        deployed by this class or ``True`` if it already existed.
        """
        return self._existed_previously
