# Copyright (C) 2023 ANSYS, Inc. and/or its affiliates.

"""Test basic client connection."""
from grpc import insecure_channel
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection import DEFAULT_HOST, DEFAULT_PORT, GrpcClient


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
