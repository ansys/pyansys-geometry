"""
Test basic server connection.
"""
import os

import pytest

from ansys.geometry.core import Modeler


@pytest.fixture()
def client(modeler):
    return Modeler(
        host=os.environ.get("ANSYS_GEO_HOST", "127.0.0.1"),
        port=os.environ.get("ANSYS_GEO_PORT", 50051),
    )._client


def test_client_init(client):
    assert client.healthy is True
    client_repr = repr(client)
    assert "Target" in client_repr
    assert "Connection" in client_repr


def test_client_close(client):
    client.close()
    assert client._closed
    assert "Closed" in str(client)
