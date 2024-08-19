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
"""This testing module automatically connects to the Geometry service running
at localhost:50051.

If you want to override these defaults, set the following environment variables.

- export ANSRV_GEO_HOST=127.0.0.1
- export ANSRV_GEO_PORT=50051
"""

import logging
from pathlib import Path

import pytest
import pyvista as pv

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection.backend import BackendType
from ansys.geometry.core.connection.defaults import GEOMETRY_SERVICE_DOCKER_IMAGE
from ansys.geometry.core.connection.docker_instance import GeometryContainers, LocalDockerInstance
import ansys.tools.visualization_interface as viz_interface

pv.OFF_SCREEN = True
viz_interface.TESTING_MODE = True
pv.global_theme.window_size = [600, 600]

IMPORT_FILES_DIR = Path(Path(__file__).parent, "files", "import")
DSCOSCRIPTS_FILES_DIR = Path(Path(__file__).parent, "files", "disco_scripts")
FILES_DIR = Path(Path(__file__).parent, "files")


def skip_if_linux(modeler: Modeler, test_name: str, element_not_available: str):
    """Skip test if running on Linux."""
    if modeler.client.backend_type == BackendType.LINUX_SERVICE:
        pytest.skip(
            reason=f"Skipping '{test_name}'. '{element_not_available}' not on Linux service."
        )  # skip!


@pytest.fixture(scope="session")
def docker_instance(use_existing_service):
    # This will only have a value in case that:
    #
    # 0) The "--use-existing-service=yes" option is not used
    # 1) Docker is installed
    # 2) At least one of the Geometry service images for your OS is downloaded
    #    on the machine
    #
    docker_instance = None

    # Check 0)
    # If it is requested the connection to an existing service
    # just return the local Docker instance as None
    if use_existing_service:
        return docker_instance

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
            docker_instance = LocalDockerInstance(
                connect_to_existing_service=True,
                restart_if_existing_service=True,
                image=is_image_available_cont,
            )

    return docker_instance


@pytest.fixture(scope="session")
def modeler(docker_instance):
    # Log to file - accepts str or Path objects, Path is passed for testing/coverage purposes.
    log_file_path = Path(__file__).absolute().parent / "logs" / "integration_tests_logs.txt"

    try:
        log_file_path.unlink()
    except OSError:
        pass

    modeler = Modeler(
        docker_instance=docker_instance, logging_level=logging.DEBUG, logging_file=log_file_path
    )

    yield modeler

    # Cleanup on exit
    modeler.close()
    assert modeler.client.is_closed


@pytest.fixture(scope="session", autouse=True)
def clean_plot_result_images():
    """Method cleaning up the image results path.

    Runs before each session once.
    """
    # Create the directory if it does not exist
    results_dir = Path(Path(__file__).parent, "image_cache", "results")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Clean up the directory
    for file in results_dir.iterdir():
        file.unlink()
