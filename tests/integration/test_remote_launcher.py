"""Test the PyPIM integration."""
from unittest.mock import create_autospec

import ansys.platform.instancemanagement as pypim
from grpc import insecure_channel
import pytest

from ansys.geometry.core import Modeler
from ansys.geometry.core.connection.client import MAX_MESSAGE_LENGTH
from ansys.geometry.core.connection.launcher import launch_modeler


def test_launch_remote_instance(monkeypatch, modeler: Modeler):
    """Test to create a mock pypim pretenting it is configured and returning
    a channel to an already running PyGeometry.

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
            ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
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

    # Assert: PyGeometry went through the PyPIM workflow
    assert mock_is_configured.called
    assert mock_connect.called
    mock_client.create_instance.assert_called_with(product_name="geometry", product_version=None)
    assert mock_instance.wait_for_ready.called
    mock_instance.build_grpc_channel.assert_called_with(
        options=[
            ("grpc.max_receive_message_length", MAX_MESSAGE_LENGTH),
        ]
    )

    # And it kept track of the instance to be able to delete it
    assert modeler.client._remote_instance == mock_instance

    # And it connected using the channel created by PyPIM
    assert modeler.client.channel == pim_channel


def test_launch_remote_instance_error():
    """Check that when PyPIM is not configures, launch_modeler raises an error."""
    with pytest.raises(NotImplementedError, match="Geometry service cannot be initialized."):
        launch_modeler()
