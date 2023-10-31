# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.

"""Testing module for the local launcher."""

import os
import re

import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection import (
    LocalDockerInstance,
    get_geometry_container_type,
    launch_local_modeler,
)

SKIP_DOCKER_TESTS_CONDITION = (
    os.getenv("IS_WORKFLOW_RUNNING") is None,
    "Local launcher tests only run on workflow.",
)
"""Only run local launcher tests if running on workflow."""


def _check_no_shutdown_warning(port: int, log: str) -> bool:
    msg = (
        "WARNING  localhost:"
        + str(port)
        + r":client\.py:[0-9]+ Geometry service was not shut down because it was already running\.\.\."  # noqa : E501
    )
    pattern = re.compile(msg)
    return True if pattern.search(log) else False


def _check_service_already_running(port: int, log: str) -> bool:
    msg = (
        r"WARNING  PyAnsys_Geometry_global:local_instance\.py:[0-9]+ Service is already running at port "  # noqa : E501
        + str(port)
        + r"\.\.\."
    )
    pattern = re.compile(msg)
    return True if pattern.search(log) else False


def _check_restarting_service(port: int, log: str) -> bool:
    msg = (
        r"WARNING  PyAnsys_Geometry_global:local_instance\.py:[0-9]+ Restarting service already running at port "  # noqa : E501
        + str(port)
        + r"\.\.\."
    )
    pattern = re.compile(msg)
    return True if pattern.search(log) else False


@pytest.mark.skipif(SKIP_DOCKER_TESTS_CONDITION[0], reason=SKIP_DOCKER_TESTS_CONDITION[1])
def test_if_docker_is_installed():
    """Simple test to check if Docker is installed in the machine."""
    assert LocalDockerInstance.is_docker_installed()


@pytest.mark.skipif(SKIP_DOCKER_TESTS_CONDITION[0], reason=SKIP_DOCKER_TESTS_CONDITION[1])
def test_local_launcher_connect(
    modeler: Modeler, caplog: pytest.LogCaptureFixture, docker_instance: LocalDockerInstance
):
    """Checking connection to existing service using launch modeler."""
    if not docker_instance:
        pytest.skip("Docker local launcher tests are not runnable.")

    # Get the existing target
    target = modeler.client.target().split(":")
    port = int(target[1])

    # Trying to deploy a service there will lead to an error...
    with pytest.raises(RuntimeError, match=f"Geometry service cannot be deployed on port {port}"):
        launch_local_modeler(port=port, connect_to_existing_service=False)

    # Connect to the existing target... this will throw a warning
    local_modeler = launch_local_modeler(
        port=port, connect_to_existing_service=True, restart_if_existing_service=False
    )
    assert _check_service_already_running(port, caplog.text) is True
    caplog.clear()

    # Try to close it... this will throw a warning
    local_modeler.client.close()
    assert _check_no_shutdown_warning(port, caplog.text) is True
    caplog.clear()


@pytest.mark.skipif(SKIP_DOCKER_TESTS_CONDITION[0], reason=SKIP_DOCKER_TESTS_CONDITION[1])
def test_local_launcher_connect_with_restart(
    modeler: Modeler, caplog: pytest.LogCaptureFixture, docker_instance: LocalDockerInstance
):
    """Checking connection to existing service using launch modeler and restarting
    existing service."""
    if not docker_instance:
        pytest.skip("Docker local launcher tests are not runnable.")
    else:
        # Retrieve the image as a GeometryContainer
        image = get_geometry_container_type(docker_instance)

    # Get the existing target
    target = modeler.client.target().split(":")
    port = int(target[1])
    new_port = port + 1

    # Launch a new modeler...
    new_modeler = launch_local_modeler(
        port=new_port,
        connect_to_existing_service=True,
        restart_if_existing_service=False,
        image=image,
    )

    # Check that the warning is NOT raised
    assert _check_service_already_running(new_port, caplog.text) is False
    caplog.clear()

    # Connect to the previous modeler and restart it
    new_modeler_restarted = launch_local_modeler(
        port=new_port,
        connect_to_existing_service=True,
        restart_if_existing_service=True,
        image=image,
    )

    # Check that the warnings are raised
    assert _check_service_already_running(new_port, caplog.text) is True
    assert _check_restarting_service(new_port, caplog.text) is True
    caplog.clear()

    # Try to close the new_modeler_restarted... this will throw a warning
    new_modeler_restarted.client.close()

    assert _check_no_shutdown_warning(new_port, caplog.text) is True
    caplog.clear()

    # And now try to close the new_modeler... this will NOT throw a warning
    new_modeler.client.close()

    assert _check_no_shutdown_warning(new_port, caplog.text) is False
    caplog.clear()


@pytest.mark.skipif(SKIP_DOCKER_TESTS_CONDITION[0], reason=SKIP_DOCKER_TESTS_CONDITION[1])
def test_try_deploying_container_with_same_name(
    modeler: Modeler, caplog: pytest.LogCaptureFixture, docker_instance: LocalDockerInstance
):
    """Checks that an error is raised when trying to deploy a container with a name that
    already exists."""
    if not docker_instance:
        pytest.skip("Docker local launcher tests are not runnable.")
    else:
        # Retrieve the image as a GeometryContainer
        image = get_geometry_container_type(docker_instance)

    # Get the existing target
    target = modeler.client.target().split(":")
    port = int(target[1])
    new_port = port + 1
    new_port_2 = port + 2

    # Launch a new modeler...
    container_name = "MY_CONTAINER"
    new_modeler = launch_local_modeler(
        port=new_port,
        connect_to_existing_service=True,
        restart_if_existing_service=False,
        name=container_name,
        image=image,
    )

    # Check that the warning is NOT raised
    assert _check_service_already_running(new_port, caplog.text) is False
    caplog.clear()

    # Now try launching a service in a new port (where no service is available) but
    # with the same name as a previous service
    with pytest.raises(
        RuntimeError, match="Geometry service Docker image error when initialized. Error:"
    ):
        launch_local_modeler(
            port=new_port_2,
            connect_to_existing_service=True,
            restart_if_existing_service=False,
            name=container_name,
            image=image,
        )

    # And now try to close the new_modeler... this will NOT throw a warning
    new_modeler.client.close()
    assert _check_no_shutdown_warning(new_port, caplog.text) is False
    caplog.clear()
