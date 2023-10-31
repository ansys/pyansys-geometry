# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.

"""
This testing module automatically connects to the Geometry service running at
localhost:50051.

If you want to override these defaults, set the following environment variables.

- export ANSRV_GEO_HOST=127.0.0.1
- export ANSRV_GEO_PORT=50051
"""
import logging
import os
from pathlib import Path

import pytest
import pyvista as pv

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.connection.defaults import GEOMETRY_SERVICE_DOCKER_IMAGE
from ansys.geometry.core.connection.local_instance import GeometryContainers, LocalDockerInstance

pv.OFF_SCREEN = True


@pytest.fixture(scope="session")
def docker_instance(use_existing_service):
    # This will only have a value in case that:
    #
    # 0) The "--use-existing-service=yes" option is not used
    # 1) Docker is installed
    # 2) At least one of the Geometry service images for your OS is downloaded
    #    on the machine
    #
    local_instance = None

    # Check 0)
    # If it is requested the connection to an existing service
    # just return the local instance as None
    if use_existing_service:
        return local_instance

    # Check 1)
    if LocalDockerInstance.is_docker_installed():
        # First of all let's get the Docker Engine OS
        docker_os = LocalDockerInstance.docker_client().info()["OSType"]
        is_image_available = False
        is_image_available_cont = None

        # Now, let's get the OS-related images
        list_images = []
        list_containers = []
        for geom_service in GeometryContainers:
            if geom_service.value[1] == docker_os:
                list_images.append(f"{GEOMETRY_SERVICE_DOCKER_IMAGE}:{geom_service.value[2]}")
                list_containers.append(geom_service)

        # Now, check 2)
        #
        available_images = LocalDockerInstance.docker_client().images.list(
            name=GEOMETRY_SERVICE_DOCKER_IMAGE
        )
        for image in available_images:
            for geom_image, geom_cont in zip(list_images, list_containers):
                if geom_image in image.tags:
                    is_image_available = True
                    is_image_available_cont = geom_cont
                    break

            if is_image_available:
                break

        # Declare a LocalDockerInstance object if all checks went through
        if is_image_available:
            local_instance = LocalDockerInstance(
                connect_to_existing_service=True,
                restart_if_existing_service=True,
                image=is_image_available_cont,
            )

    return local_instance


@pytest.fixture(scope="session")
def modeler(docker_instance):
    # Log to file - accepts str or Path objects, Path is passed for testing/coverage purposes.
    log_file_path = Path(__file__).absolute().parent / "logs" / "integration_tests_logs.txt"

    try:
        os.remove(log_file_path)
    except OSError:
        pass

    modeler = Modeler(
        local_instance=docker_instance, logging_level=logging.DEBUG, logging_file=log_file_path
    )

    yield modeler

    # Cleanup on exit
    modeler.close()
    assert modeler.client.is_closed


@pytest.fixture(scope="session", autouse=True)
def clean_plot_result_images():
    """
    Method cleaning up the image results path.

    Runs before each session once.
    """
    # Create the directory if it does not exist
    results_dir = Path(Path(__file__).parent, "image_cache", "results")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Clean up the directory
    files = os.listdir(results_dir)
    for file in files:
        os.remove(Path(results_dir, file))


@pytest.fixture(scope="session")
def skip_not_on_linux_service(modeler: Modeler):
    if modeler.client.backend_type == BackendType.LINUX_SERVICE:
        return pytest.skip("Implementation not available on Linux service.")  # skip!
