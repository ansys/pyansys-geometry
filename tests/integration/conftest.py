# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

try:
    from ansys.geometry.core.misc.checks import run_if_graphics_required

    run_if_graphics_required()

    import pyvista as pv

    import ansys.tools.visualization_interface as viz_interface

    pv.OFF_SCREEN = True
    viz_interface.TESTING_MODE = True
    pv.global_theme.window_size = [600, 600]

except ImportError:
    pass

import logging
from pathlib import Path

import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection.backend import BackendType
import ansys.geometry.core.connection.defaults as pygeom_defaults
from ansys.geometry.core.connection.docker_instance import GeometryContainers, LocalDockerInstance

IMPORT_FILES_DIR = Path(Path(__file__).parent, "files", "import")
DSCOSCRIPTS_FILES_DIR = Path(Path(__file__).parent, "files", "disco_scripts")
FILES_DIR = Path(Path(__file__).parent, "files")


def skip_if_core_service(modeler: Modeler, test_name: str, element_not_available: str):
    """Skip test if running on CoreService."""
    if BackendType.is_core_service(modeler.client.backend_type):
        pytest.skip(
            reason=f"Skipping '{test_name}'. '{element_not_available}' not on CoreService."
        )  # skip!


def skip_if_windows(modeler: Modeler, test_name: str, element_not_available: str):
    """Skip test if running on Windows."""
    if modeler.client.backend_type in (
        BackendType.SPACECLAIM,
        BackendType.WINDOWS_SERVICE,
        BackendType.DISCOVERY,
    ):
        pytest.skip(
            reason=f"Skipping '{test_name}'. '{element_not_available}' not on Windows services."
        )  # skip!


def skip_if_spaceclaim(modeler: Modeler, test_name: str, element_not_available: str):
    """Skip test if running on SpaceClaim."""
    if modeler.client.backend_type == BackendType.SPACECLAIM:
        pytest.skip(
            reason=f"Skipping '{test_name}'. '{element_not_available}' not on SpaceClaim."
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
                list_images.append(
                    f"{pygeom_defaults.GEOMETRY_SERVICE_DOCKER_IMAGE}:{geom_service.value[2]}"
                )
                list_containers.append(geom_service)

        # Now, check 2)
        #
        available_images = LocalDockerInstance.docker_client().images.list(
            name=pygeom_defaults.GEOMETRY_SERVICE_DOCKER_IMAGE
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
def session_modeler(docker_instance):
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
    modeler.exit()
    assert modeler.client.is_closed


@pytest.fixture(scope="function")
def modeler(session_modeler: Modeler):
    # Yield the modeler
    yield session_modeler

    # Cleanup on exit (if design exists)
    if session_modeler.design:
        session_modeler.design.close()


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


@pytest.fixture
def use_service_colors():
    # Perform the state change
    import ansys.geometry.core as pyansys_geometry

    pyansys_geometry.USE_SERVICE_COLORS = True

    yield  # This allows the test to run

    # Code here runs after the test, reverting the state
    pyansys_geometry.USE_SERVICE_COLORS = False


@pytest.fixture(scope="function")
def use_grpc_client_old_backend(modeler: Modeler):
    currentbackend = modeler._grpc_client._backend_version
    modeler._grpc_client._backend_version = (24, 2, 0)

    yield  # This allows the test to run

    # Code here runs after the test, reverting the state
    modeler._grpc_client._backend_version = currentbackend
<<<<<<< HEAD
=======


def are_graphics_available() -> bool:
    """Determine whether graphics are available."""
    from ansys.geometry.core.misc.checks import run_if_graphics_required

    # If the imports are successful, then graphics can be handled...
    # ...otherwise, graphics are not available.
    try:
        run_if_graphics_required()
        from pyvista.plotting import system_supports_plotting

        return system_supports_plotting()
    except ImportError:
        return False
>>>>>>> b7a0cd7395c0ff007c5168f4493c3163795e3e4f
