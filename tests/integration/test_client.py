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
"""Test basic client connection."""

from pathlib import Path

from grpc import insecure_channel
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection.client import GrpcClient
import ansys.geometry.core.connection.defaults as pygeom_defaults


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
    target = f"{pygeom_defaults.DEFAULT_HOST}:{pygeom_defaults.DEFAULT_PORT}"
    channel = insecure_channel(target)
    client = GrpcClient(channel=channel)
    assert client.healthy is True
    client_repr = repr(client)
    assert "Target" in client_repr
    assert "Connection" in client_repr
    assert target == client.target().lstrip("dns:///")
    assert client.channel


def test_client_close(client: GrpcClient):
    """Test the shutdown of a client."""
    client.close()
    assert client._closed
    assert not client.healthy
    assert "Closed" in str(client)
    assert client.target() == ""


@pytest.mark.skip(reason="Flaky test, needs investigation")
def test_client_get_service_logs(client: GrpcClient):
    """Test the retrieval of the service logs."""
    # Low level call
    logs = client._get_service_logs()
    assert isinstance(logs, str)
    assert logs  # is not empty

    # Let's request them again on file dump
    logs_folder = str(Path(__file__).parent / "logs")
    logs_file_dump = client._get_service_logs(dump_to_file=True, logs_folder=logs_folder)
    assert logs_file_dump.exists()

    # Do not provide a folder
    logs_file_dump = client._get_service_logs(dump_to_file=True)
    assert logs_file_dump.exists()
    logs_file_dump.unlink()  # Delete the file

    # Let's request all logs now
    logs_all = client._get_service_logs(all_logs=True)
    assert isinstance(logs_all, dict)
    assert logs_all  # is not empty

    # Let's do the same directly from a Modeler object
    modeler = Modeler(channel=client.channel)
    logs_modeler = modeler.get_service_logs()
    assert isinstance(logs_modeler, str)
    assert logs_modeler  # is not empty
