import grpc
import pytest

from ansys.geometry.core.connection.client import GrpcClient, wait_until_healthy


def test_wait_until_healthy():
    """Test checking that a channel is unhealthy."""
    # create a bogus channel
    channel = grpc.insecure_channel("9.0.0.1:80")
    with pytest.raises(TimeoutError):
        wait_until_healthy(channel, timeout=1)


def test_invalid_inputs():
    """Test checking that the input provided is a channel."""
    with pytest.raises(TypeError, match="Provided type"):
        GrpcClient(host=123)
    with pytest.raises(TypeError, match="Provided type"):
        GrpcClient(port=None)
    with pytest.raises(TypeError, match="Provided type"):
        GrpcClient(channel="a")
    with pytest.raises(TypeError, match="Provided type"):
        GrpcClient(timeout="a")
