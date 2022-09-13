"""
Test basic client connection.
"""
import pytest

from ansys.geometry.core.connection import GrpcClient


@pytest.fixture()
def client(modeler):
    # this uses DEFAULT_HOST and DEFAULT_PORT which are set by environment
    # variables in the workflow
    return GrpcClient()


def test_client_init(client):
    assert client.healthy is True
    client_repr = repr(client)
    assert "Target" in client_repr
    assert "Connection" in client_repr


def test_client_close(client):
    client.close()
    assert client._closed
    assert "Closed" in str(client)
