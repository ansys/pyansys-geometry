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
"""Test the PyPIM integration."""

import os
from unittest.mock import create_autospec

import ansys.tools.path.path as atpp
from grpc import insecure_channel
import pytest

from ansys.geometry.core import Modeler
import ansys.geometry.core.connection.defaults as pygeom_defaults
from ansys.geometry.core.connection.docker_instance import LocalDockerInstance
from ansys.geometry.core.connection.launcher import launch_modeler

try:
    import ansys.platform.instancemanagement as pypim
except ModuleNotFoundError:
    pytest.skip("PyPIM is not installed", allow_module_level=True)


def test_launch_remote_instance(monkeypatch, modeler: Modeler):
    """Test to create a mock pypim pretending it is configured and returning a
    channel to an already running PyAnsys Geometry.

    Parameters
    ----------
    modeler : ansys.geometry.core.modeler.Modeler
        The client to be used for the tests.
    monkeypatch : pytest.monkeypatch
        The fixture for safely patching and mocking functionality in tests
    """
    mock_instance = pypim.Instance(
        definition_name="definitions/fake-geometry",
        name="instances/fake-geometry",
        ready=True,
        status_message=None,
        services={"grpc": pypim.Service(uri=modeler.client._target, headers={})},
    )
    pim_channel = insecure_channel(
        modeler.client._target,
        options=[
            ("grpc.max_receive_message_length", pygeom_defaults.MAX_MESSAGE_LENGTH),
        ],
    )
    mock_instance.wait_for_ready = create_autospec(mock_instance.wait_for_ready)
    mock_instance.build_grpc_channel = create_autospec(
        mock_instance.build_grpc_channel, return_value=pim_channel
    )
    mock_instance.delete = create_autospec(mock_instance.delete)

    mock_client = pypim.Client(channel=insecure_channel("localhost:12345"))
    mock_client.create_instance = create_autospec(
        mock_client.create_instance, return_value=mock_instance
    )

    mock_connect = create_autospec(pypim.connect, return_value=mock_client)
    mock_is_configured = create_autospec(pypim.is_configured, return_value=True)
    monkeypatch.setattr(pypim, "connect", mock_connect)
    monkeypatch.setattr(pypim, "is_configured", mock_is_configured)

    modeler = launch_modeler()

    # Assert: PyAnsys Geometry went through the PyPIM workflow
    assert mock_is_configured.called
    assert mock_connect.called
    mock_client.create_instance.assert_called_with(
        product_name="geometry", product_version="windows"
    )
    assert mock_instance.wait_for_ready.called
    mock_instance.build_grpc_channel.assert_called_with(
        options=[
            ("grpc.max_receive_message_length", pygeom_defaults.MAX_MESSAGE_LENGTH),
        ]
    )

    # And it kept track of the instance to be able to delete it
    assert modeler.client._remote_instance == mock_instance

    # And it connected using the channel created by PyPIM
    assert modeler.client.channel == pim_channel


def test_launch_remote_instance_error(monkeypatch):
    """Check that when PyPIM is not configured, launch_modeler raises an
    error.
    """
    mock_is_installed = create_autospec(LocalDockerInstance.is_docker_installed, return_value=False)
    monkeypatch.setattr(LocalDockerInstance, "is_docker_installed", mock_is_installed)
    mock_available_ansys = create_autospec(atpp.get_available_ansys_installations, return_value={})
    monkeypatch.setattr(atpp, "get_available_ansys_installations", mock_available_ansys)

    with pytest.raises(NotImplementedError, match="Geometry service cannot be initialized."):
        launch_modeler()

    assert mock_is_installed.called

    if os.name == "nt":
        assert mock_available_ansys.called
