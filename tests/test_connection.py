import grpc
import pytest

from ansys.geometry.core.connection.client import wait_until_healthy


def test_wait_until_healthy():
    # create a bogus channel
    channel = grpc.insecure_channel("9.0.0.1:80")
    with pytest.raises(TimeoutError):
        wait_until_healthy(channel, timeout=1.0)
