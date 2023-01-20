"""Module containing the ``LocalDockerInstance`` class."""

from enum import Enum

from beartype import beartype as check_input_types
from beartype.typing import Optional, Tuple, Union
import docker
from docker.errors import APIError
from docker.models.containers import Container

from ansys.geometry.core.connection.defaults import DEFAULT_PORT
from ansys.geometry.core.logger import LOG as logger


class GeometryContainers(Enum):
    """Provides an enum holding the different Geometry services available."""

    WINDOWS_LATEST_STABLE = 0, "windows", "ghcr.io/pyansys/pygeometry:latest"
    LINUX_LATEST_STABLE = 1, "linux", None


class LocalDockerInstance:

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
        except APIError:
            return False

    @check_input_types
    def __init__(
        self,
        port: int = DEFAULT_PORT,
        connect_to_existing_service: bool = False,
        name: Optional[str] = None,
        image: Optional[GeometryContainers] = None,
    ) -> None:

        # Initialize instance variables
        self._container = None
        self._existed_previously = False

        # Check the port availability
        port_available, cont = self._check_port_availability(port)

        # If a service was already deployed... check if it is a Geometry Service
        # in case we want to connect to it
        if cont and connect_to_existing_service and self._is_cont_geom_service(cont):
            self._container = cont.image
            self._existed_previously = True
            return

        # At this stage we can confirm that we have to deploy our own Geometry Service.
        # Let's get started with it!
        #
        # First, let's check if the port is available... otherwise raise error
        if port_available:
            self._deploy_container(port=port, name=name, image=image)
        else:
            raise RuntimeWarning(f"Geometry service cannot be deployed on port {port}")

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
                if tag == geom_services.value[2]:
                    return True

        # If we reached this point, this means that our image is not a Geometry Service
        return False

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
        RuntimeWarning
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
        if image is None or image.value[1] != docker_os:
            raise RuntimeWarning(f"Geometry service cannot be launched on {docker_os}")

        # At this point, we are good to deploy the Geometry Service!
        #
        # WIP!
