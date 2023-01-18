"""Module containing the ``LocalDockerInstance`` class."""

from enum import Enum

from beartype import beartype as check_input_types
from beartype.typing import Optional
import docker
from docker.errors import APIError

""" Docker client unique instance. By default, none is needed. It will be lazy initialized."""
DOCKER_CLIENT: docker.DockerClient = None


class GeometryContainers(Enum):
    WINDOWS_LATEST_STABLE = 0, "ghcr.io/pyansys/pygeometry:23.2.0-alpha10"


class LocalDockerInstance:
    @staticmethod
    def is_docker_installed() -> bool:
        """Checks whether there is a local install of Docker engine available
        and running.

        Returns
        -------
        bool
            ``True`` if Docker engine is running, ``False`` otherwise.
        """
        # Lazy initialize the DOCKER_CLIENT object
        LocalDockerInstance.__is_client_available()

        # When trying to ping, this throws back an error if the
        # server is not available
        try:
            return DOCKER_CLIENT.ping()
        except APIError:
            return False

    @staticmethod
    def __is_client_available() -> None:
        """Private method for checking if the ``DOCKER_CLIENT`` object is
        defined or not.

        Notes
        -----
        This method is used as a lazy loader for the ``DOCKER_CLIENT`` object.
        """
        if not DOCKER_CLIENT:
            DOCKER_CLIENT = docker.from_env()

    @check_input_types
    def __init__(self, port: int, name: Optional[str] = None) -> None:

        # Lazy initialize the DOCKER_CLIENT object
        LocalDockerInstance.__is_client_available()

        pass
