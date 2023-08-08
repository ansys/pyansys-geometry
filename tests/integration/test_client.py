"""Test basic client connection."""
from grpc import insecure_channel
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection import DEFAULT_HOST, DEFAULT_PORT, GrpcClient
from ansys.geometry.core.connection.product_instance import get_available_port


@pytest.fixture(scope="function")
def client(modeler: Modeler):
    # this uses DEFAULT_HOST and DEFAULT_PORT which are set by environment
    # variables in the workflow
    return GrpcClient()


def test_client_init(client: GrpcClient):
    """Test the instantiation of a client from the default ctor."""
    assert client.healthy is True
    client_repr = repr(client)
    assert "Target" in client_repr
    assert "Connection" in client_repr

    assert client.channel


def test_client_through_channel(modeler: Modeler):
    """Test the instantiation of a client from a gRPC channel."""
    target = f"{DEFAULT_HOST}:{DEFAULT_PORT}"
    channel = insecure_channel(target)
    client = GrpcClient(channel=channel)
    assert client.healthy is True
    client_repr = repr(client)
    assert "Target" in client_repr
    assert "Connection" in client_repr
    assert client.target() == target
    assert client.channel


def test_client_close(client: GrpcClient):
    """Test the shutdown of a client."""
    client.close()
    assert client._closed
    assert not client.healthy
    assert "Closed" in str(client)
    assert client.target() == ""


def test_default_product_launch():
    """Test the creation of a Modeler object based on the local Ansys Geometry Service
    installation."""
    from ansys.geometry.core import (
        launch_modeler_with_discovery,
        launch_modeler_with_geometry_service,
        launch_modeler_with_spaceclaim,
    )

    modeler_geo_service = launch_modeler_with_geometry_service()
    modeler_discovery = launch_modeler_with_discovery()
    modeler_spaceclaim = launch_modeler_with_spaceclaim()
    assert modeler_geo_service != None
    assert modeler_geo_service.client.healthy
    assert modeler_discovery != None
    assert modeler_discovery.client.healthy
    assert modeler_spaceclaim != None
    assert modeler_spaceclaim.client.healthy
    modeler_geo_service.close()
    modeler_discovery.close()
    modeler_spaceclaim.close()


def test_default_product_launch():
    """Test the creation of a Modeler object based on the local Ansys Geometry Service
    installation."""

    from ansys.geometry.core import (
        launch_modeler_with_discovery,
        launch_modeler_with_geometry_service,
        launch_modeler_with_spaceclaim,
    )

    modeler_geo_service = launch_modeler_with_geometry_service()
    modeler_discovery = launch_modeler_with_discovery()
    modeler_spaceclaim = launch_modeler_with_spaceclaim()
    assert modeler_geo_service != None
    assert modeler_geo_service.client.healthy
    assert modeler_discovery != None
    assert modeler_discovery.client.healthy
    assert modeler_spaceclaim != None
    assert modeler_spaceclaim.client.healthy


def test_product_launch_with_parameters():
    """
    Test the creation of a Modeler object based on the local Ansys Geometry Service
    installation.

    And passing specific parameters to be tested.
    """
    import random

    from ansys.geometry.core import (
        launch_modeler_with_discovery,
        launch_modeler_with_geometry_service,
        launch_modeler_with_spaceclaim,
    )
    from ansys.geometry.core.connection.backend import ApiVersions

    apiVersions = list(ApiVersions)

    modeler_geo_service = launch_modeler_with_geometry_service(
        host="127.0.0.1",
        port=get_available_port(),
        enable_trace=True,
        log_level=random.randint(0, 3),
        timeout=120,
    )

    modeler_discovery = launch_modeler_with_discovery(
        host="127.0.0.1",
        port=get_available_port(),
        log_level=random.randint(0, 3),
        api_version=apiVersions[random.randint(0, len(apiVersions) - 1)].value,
        timeout=180,
    )

    modeler_spaceclaim = launch_modeler_with_spaceclaim(
        host="127.0.0.1",
        port=get_available_port(),
        log_level=random.randint(0, 3),
        api_version=apiVersions[random.randint(0, len(apiVersions) - 1)].value,
        timeout=180,
    )

    assert modeler_geo_service != None
    assert modeler_geo_service.client.healthy
    assert modeler_discovery != None
    assert modeler_discovery.client.healthy
    assert modeler_spaceclaim != None
    assert modeler_spaceclaim.client.healthy

    modeler_geo_service.close()
    modeler_discovery.close()
    modeler_spaceclaim.close()
