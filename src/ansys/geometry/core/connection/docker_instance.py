# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
"""Module for connecting to a local Geometry Service Docker container."""

from enum import Enum
from functools import wraps
import os
from typing import Optional

from beartype import beartype as check_input_types

try:
    from docker.client import DockerClient
    from docker.errors import APIError, ContainerError, ImageNotFound
    from docker.models.containers import Container

    _HAS_DOCKER = True
except ModuleNotFoundError:  # pragma: no cover
    _HAS_DOCKER = False

from ansys.geometry.core.connection.defaults import DEFAULT_PORT, GEOMETRY_SERVICE_DOCKER_IMAGE
from ansys.geometry.core.logger import LOG


def _docker_python_available(func):
    """Check whether Docker is installed as a Python package.

    This function works as a decorator.
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
    """Provides an enum holding the available Geometry services."""

    WINDOWS_LATEST = 0, "windows", "windows-latest"
    LINUX_LATEST = 1, "linux", "linux-latest"
    WINDOWS_LATEST_UNSTABLE = 2, "windows", "windows-latest-unstable"
    LINUX_LATEST_UNSTABLE = 3, "linux", "linux-latest-unstable"
    WINDOWS_24_1 = 4, "windows", "windows-24.1"
    LINUX_24_1 = 5, "linux", "linux-24.1"
    WINDOWS_24_2 = 6, "windows", "windows-24.2"
    LINUX_24_2 = 7, "linux", "linux-24.2"


class LocalDockerInstance:
    """Instantiates a Geometry service as a local Docker container.

    By default, if a container with the Geometry service already exists at the given port,
    PyAnsys Geometry connects to it. Otherwise, PyAnsys Geometry tries to launch its own service.

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
    name : str or None, default: None
        Name of the Docker container to deploy. The default is ``None``,
        in which case Docker assigns it a random name.
    image : GeometryContainers or None, default: None
        The Geometry service Docker image to deploy. The default is ``None``,
        in which case the ``LocalDockerInstance`` class identifies the OS of your
        Docker engine and deploys the latest version of the Geometry service for that
        OS.
    """

    __DOCKER_CLIENT__: "DockerClient" = None
    """Docker client class variable.

    Notes
    -----
    The default is ``None``, in which case lazy initialization is used.
    ``__DOCKER_CLIENT__`` is a class variable, meaning that it is
    the same variable for all instances of this class.
    """

    @staticmethod
    @_docker_python_available
    def docker_client() -> "DockerClient":
        """Get the initialized ``__DOCKER_CLIENT__`` object.

        Notes
        -----
        The ``LocalDockerInstance`` class performs a lazy initialization of the
        ``__DOCKER_CLIENT__`` class variable.

        Returns
        -------
        ~docker.client.DockerClient
            Initialized Docker client.
        """
        if not LocalDockerInstance.__DOCKER_CLIENT__:
            LocalDockerInstance.__DOCKER_CLIENT__ = DockerClient.from_env()

        return LocalDockerInstance.__DOCKER_CLIENT__

    @staticmethod
    @_docker_python_available
    def is_docker_installed() -> bool:
        """Check a local installation of Docker engine is available and running.

        Returns
        -------
        bool
            ``True`` if Docker engine is available and running, ``False`` otherwise.
        """
        # When trying to ping, this throws an error if the
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
        name: str | None = None,
        image: GeometryContainers | None = None,
    ) -> None:
        """``LocalDockerInstance`` constructor."""
        # Initialize instance variables
        self._container: Container = None
        self._existed_previously: bool = False

        # Check the port availability
        port_available, cont = self._check_port_availability(port)

        # If a service was already deployed... check if it is a Geometry service
        # in case you want to connect to it
        if cont and connect_to_existing_service and self._is_cont_geom_service(cont):
            # Now, check if a restart of the service is required
            if restart_if_existing_service:
                LOG.warning(f"Restarting service already running at port {port}...")
                cont.restart()

            # Finally, store the container
            self._container = cont
            self._existed_previously = True
            return

        # At this stage, confirm that you have to deploy our own Geometry service.
        #
        # First, check if the port is available... otherwise raise error
        if port_available:
            self._deploy_container(port=port, name=name, image=image)
        else:
            raise RuntimeError(f"Geometry service cannot be deployed on port {port}")

    def _check_port_availability(self, port: int) -> tuple[bool, Optional["Container"]]:
        """Check whether the requested port is available for deployment.

        Returns
        -------
        tuple[bool, Container]
            Tuple with a Boolean indicating whether the port is available.
            If the port is not available, the container deployed at that port is also returned.
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
                        LOG.warning(f"Service is already running at port {port}...")
                        return (False, cont)

        # If you reached here, just return default values
        return (True, None)

    def _is_cont_geom_service(self, cont: "Container") -> bool:
        """Check a provided ``Container`` object is a Geometry service container.

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

        # If you have reached this point, the image is not a Geometry service
        return False  # pragma: no cover

    def _deploy_container(self, port: int, name: str | None, image: GeometryContainers | None):
        """Handle the deployment of a Geometry service.

        Parameters
        ----------
        port : int
            Port under which the service should be deployed.
        name : str or None, optional
            Name given to the deployed container. If ``None``, Docker will provide
            an arbitrary name.
        image : GeometryContainers or None
            Geometry service Docker container image to be used. If ``None``, the
            latest container version matching

        Raises
        ------
        RuntimeError
            In case the Geometry service cannot be launched.
        """
        # First get the Docker Engine OS
        docker_os = self.docker_client().info()["OSType"]

        # If no image is provided, default to the whatever Docker engine OS
        # your system is running on... Latest images are used because they are the
        # ones defined first in the GeometryContainers enum class.
        if image is None:
            for geom_service in GeometryContainers:
                if geom_service.value[1] == docker_os:
                    image = geom_service
                    break

        # If image is still None, this means it cannot be deployed on your OS
        #
        # Also, if you requested an image incompatible with the existing OS, it
        # is not possible either.
        if image is None or image.value[1] != docker_os:  # pragma: no cover
            raise RuntimeError(f"Geometry service cannot be launched on {docker_os}")

        # At this point, you are can deploy the Geometry service.
        #
        # Check if the license server env variable is available
        license_server = os.getenv("ANSRV_GEO_LICENSE_SERVER", None)
        if not license_server:  # pragma: no cover
            raise RuntimeError(
                "No license server provided... Store its value under the following env variable: ANSRV_GEO_LICENSE_SERVER."  # noqa: E501
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
        except ImageNotFound:  # pragma: no cover
            raise RuntimeError(
                f"Geometry service Docker image {image.value[1]} not found. Download it first to your machine."  # noqa: E501
            )
        except (ContainerError, APIError) as err:
            raise RuntimeError(
                f"Geometry service Docker image error when initialized. Error: {err.explanation}"
            )

        # If the deployment went fine, this means that you have deployed the service.
        self._container = container
        self._existed_previously = False

    @property
    def container(self) -> "Container":
        """Docker container object that hosts the deployed Geometry service."""
        return self._container

    @property
    def existed_previously(self) -> bool:
        """Flag indicating whether the container previously existed.

        Returns ``False`` if the Geometry service was effectively
        deployed by this class or ``True`` if it already existed.
        """
        return self._existed_previously


def get_geometry_container_type(instance: LocalDockerInstance) -> GeometryContainers | None:
    """Provide back the ``GeometryContainers`` value.

    Notes
    -----
    This method returns the first hit on the available tags.

    Parameters
    ----------
    instance : LocalDockerInstance
        The LocalDockerInstance object.

    Returns
    -------
    GeometryContainers or None
        The GeometryContainer value corresponding to the previous image or None
        if not match.
    """
    for tag in instance.container.image.tags:
        for geom_services in GeometryContainers:
            if tag == f"{GEOMETRY_SERVICE_DOCKER_IMAGE}:{geom_services.value[2]}":
                return geom_services

    return None
