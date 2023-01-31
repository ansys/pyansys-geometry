"""Module containing the ``LocalDockerInstance`` class."""
from enum import Enum
import os

from beartype import beartype as check_input_types
from beartype.typing import Optional, Tuple, Union
import docker
from docker.errors import APIError, ContainerError, ImageNotFound
from docker.models.containers import Container

from ansys.geometry.core.connection.defaults import DEFAULT_PORT, GEOMETRY_SERVICE_DOCKER_IMAGE
from ansys.geometry.core.logger import LOG as logger


class GeometryContainers(Enum):
    """Provides an enum holding the different Geometry services available."""

    WINDOWS_LATEST = 0, "windows", "windows-latest"
    LINUX_LATEST = 1, "linux", "linux-latest"
    WINDOWS_LATEST_UNSTABLE = 0, "windows", "windows-latest-unstable"
    LINUX_LATEST_UNSTABLE = 1, "linux", "linux-latest-unstable"


class LocalDockerInstance:
    """
    ``LocalDockerInstance`` class.

    This class is used for instatiating a Geometry service (as a local Docker container).
    By default, if a container with the Geometry service already exists at the given port,
    it will connect to it. Otherwise, it will try to launch its own service.

    Parameters
    ----------
    port : int, optional
        Localhost port at which the Geometry Service will be deployed or which
        the ``Modeler`` will connect to (if it is already deployed). By default,
        value will be the one at ``DEFAULT_PORT``.
    connect_to_existing_service : bool, optional
        Boolean indicating whether if the Modeler should connect to a Geometry
        Service already deployed at that port, by default ``True``.
    restart_if_existing_service : bool, optional
        Boolean indicating whether the Geometry Service (which is already running)
        should be restarted when attempting connection, by default ``False``
    name : Optional[str], optional
        Name of the Docker container to be deployed, by default ``None``, which
        means that Docker will assign it a random name.
    image : Optional[GeometryContainers], optional
        The Geometry Service Docker image to be deployed, by default ``None``, which
        means that the ``LocalDockerInstance`` class will identify the OS of your
        Docker engine and deploy the latest version of the Geometry Service for that
        OS.
    """

    __DOCKER_CLIENT__: docker.DockerClient = None
    """Docker client class variable. By default, none is needed.
    It will be lazy initialized.

    Notes
    -----
    ``__DOCKER_CLIENT__`` is a class variable, meaning that it is
    the same variable for all instances of this class.
    """

    @staticmethod
    def docker_client() -> docker.DockerClient:
        """Static method for returning the initialized ``__DOCKER_CLIENT__`` object.
        LocalDockerInstance performs a lazy loading initialization of the class
        variable ``__DOCKER_CLIENT__``.

        Returns
        -------
        docker.DockerClient
            The initialized Docker client.

        Notes
        -----
        This method is used as a lazy loader for the ``__DOCKER_CLIENT__`` object.
        """
        if not LocalDockerInstance.__DOCKER_CLIENT__:
            LocalDockerInstance.__DOCKER_CLIENT__ = docker.from_env()

        return LocalDockerInstance.__DOCKER_CLIENT__

    @staticmethod
    def is_docker_installed() -> bool:
        """Checks whether there is a local install of Docker engine available
        and running.

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

        # If a service was already deployed... check if it is a Geometry Service
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

        # At this stage we can confirm that we have to deploy our own Geometry Service.
        # Let's get started with it!
        #
        # First, let's check if the port is available... otherwise raise error
        if port_available:
            self._deploy_container(port=port, name=name, image=image)
        else:
            raise RuntimeError(f"Geometry service cannot be deployed on port {port}")

    def _check_port_availability(self, port: int) -> Tuple[bool, Optional[Container]]:
        """Private method which checks whether the requested port is available for
        deployment or not. If not available, it also returns the ``Container`` deployed
        at that port.

        Returns
        -------
        tuple[bool, Container]
            Tuple with boolean indicating whether port is available (i.e. ``True``) or not.
            If not available, it also returns the container occupying that port.
        """
        # First, check if there is a container already running at that port
        for cont in self.docker_client().containers.list():
            for (_, ports_shared) in cont.attrs["NetworkSettings"]["Ports"].items():
                for port_shared in ports_shared:
                    if int(port_shared["HostPort"]) == port:
                        logger.warning(f"Service already running at port {port}...")
                        return (False, cont)

        # If you reached here, just return default values
        return (True, None)

    def _is_cont_geom_service(self, cont: Container) -> bool:
        """Private method for checking whether a provided ``Container``
        object is a Geometry Service container or not.

        Parameters
        ----------
        cont : Container
            Container deployed to check.

        Returns
        -------
        bool
            Returns ``True`` if the container provided is a Geometry Service.
            Otherwise, ``False``.
        """
        # If one of the tags matches a Geometry service tag --> Return True
        for tag in cont.image.tags:
            for geom_services in GeometryContainers:
                if tag == f"{GEOMETRY_SERVICE_DOCKER_IMAGE}:{geom_services.value[2]}":
                    return True

        # If we reached this point, this means that our image is not a Geometry Service
        return False  # pragma: no cover

    def _deploy_container(
        self, port: int, name: Union[str, None], image: Union[GeometryContainers, None]
    ):
        """Private method for handling the deployment of a Geometry Service container
        according to the provided arguments

        Parameters
        ----------
        port : int
            Port under which the service should be deployed.
        name : Union[str, None], optional
            Name given to the deployed container. If ``None``, Docker will provide
            an arbitrary name.
        image : Union[GeometryContainers, None]
            Geometry Service Docker container image to be used. If ``None``, the
            latest container version matching

        Raises
        ------
        RuntimeError
            In case the Geometry Service cannot be launched.
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

        # At this point, we are good to deploy the Geometry Service!
        #
        # WIP!
        try:
            container: Container = self.docker_client().containers.run(
                image=f"{GEOMETRY_SERVICE_DOCKER_IMAGE}:{image.value[2]}",
                detach=True,
                auto_remove=True,
                name=name,
                ports={"50051/tcp": port},
                environment={
                    "LOG_LEVEL": os.getenv("GEOMSERVICE_LOG_LEVEL", 2),
                    "ENABLE_TRACE": os.getenv("GEOMSERVICE_ENABLE_TRACE", 0),
                    "USE_DEBUG_MODE": os.getenv("GEOMSERVICE_USE_DEBUG_MODE", 0),
                    "LICENSE_SERVER": os.getenv("GEOMSERVICE_LICENSE_SERVER", None),
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
    def container(self) -> Container:
        """Docker Container object hosting the Geometry Service deployed."""
        return self._container

    @property
    def existed_previously(self) -> bool:
        """Indicates whether the container hosting the Geometry Service
        was effectively deployed by this class or if it already existed."""
        return self._existed_previously
