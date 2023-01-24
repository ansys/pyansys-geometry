"""Testing module for the local launcher."""

import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection import LocalDockerInstance, launch_local_modeler


def test_if_docker_is_installed():
    """Simple test to check if Docker is installed in the machine."""
    assert LocalDockerInstance.is_docker_installed()


def test_local_launcher_connect(modeler: Modeler, caplog: pytest.LogCaptureFixture):
    """Checking connection to existing service using launch modeler."""
    # Get the existing target
    target = modeler.client.target().split(":")
    host = target[0]
    port = int(target[1])

    # Trying to deploy a service there will lead to an error...
    with pytest.raises(RuntimeError, match=f"Geometry service cannot be deployed on port {port}"):
        launch_local_modeler(port=port, connect_to_existing_service=False)

    # Connect to the existing target... this will throw a warning
    local_modeler = launch_local_modeler(
        port=port, connect_to_existing_service=True, restart_if_existing_service=False
    )

    msg = f"WARNING  PyGeometry_global:localinstance.py:155 Service already running at port {port}...\n"  # noqa : E501
    assert msg in caplog.text

    # Try to close it... this will throw a warning
    local_modeler.client.close()

    msg = f"WARNING  {host}:{port}:client.py:182 Geometry Service will not be shutdown since it was already running...\n"  # noqa : E501
    assert msg in caplog.text


def test_local_launcher_connect_with_restart(modeler: Modeler, caplog: pytest.LogCaptureFixture):
    """Checking connection to existing service using launch modeler and
    restarting existing service."""
    # Get the existing target
    target = modeler.client.target().split(":")
    host = target[0]
    port = int(target[1])
    new_port = port + 1

    # Launch a new modeler...
    new_modeler = launch_local_modeler(
        port=new_port, connect_to_existing_service=True, restart_if_existing_service=False
    )

    # Check that the warning is NOT raised
    msg = f"WARNING  PyGeometry_global:localinstance.py:155 Service already running at port {new_port}...\n"  # noqa : E501
    assert msg not in caplog.text
    caplog.clear()

    # Connect to the previous modeler and restart it
    new_modeler_restarted = launch_local_modeler(
        port=new_port, connect_to_existing_service=True, restart_if_existing_service=True
    )

    # Check that the warnings are raised
    msg = f"WARNING  PyGeometry_global:localinstance.py:155 Service already running at port {new_port}...\n"  # noqa : E501
    assert msg in caplog.text
    msg = f"WARNING  PyGeometry_global:localinstance.py:122 Restarting service already running at port {new_port}...\n"  # noqa : E501
    assert msg in caplog.text
    caplog.clear()

    # Try to close the new_modeler_restarted... this will throw a warning
    new_modeler_restarted.client.close()

    msg = f"WARNING  {host}:{new_port}:client.py:182 Geometry Service will not be shutdown since it was already running...\n"  # noqa : E501
    assert msg in caplog.text
    caplog.clear()

    # And now try to close the new_modeler... this will NOT throw a warning
    new_modeler.client.close()

    msg = f"WARNING  {host}:{new_port}:client.py:182 Geometry Service will not be shutdown since it was already running...\n"  # noqa : E501
    assert msg not in caplog.text
    caplog.clear()


def test_try_deploying_container_with_same_name(modeler: Modeler, caplog: pytest.LogCaptureFixture):
    """Checks that an error is raised when trying to deploy a container
    with a name that already exists."""

    # Get the existing target
    target = modeler.client.target().split(":")
    host = target[0]
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
    )

    # Check that the warning is NOT raised
    msg = f"WARNING  PyGeometry_global:localinstance.py:155 Service already running at port {new_port}...\n"  # noqa : E501
    assert msg not in caplog.text
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
        )

    # And now try to close the new_modeler... this will NOT throw a warning
    new_modeler.client.close()

    msg = f"WARNING  {host}:{new_port}:client.py:182 Geometry Service will not be shutdown since it was already running...\n"  # noqa : E501
    assert msg not in caplog.text
    caplog.clear()
