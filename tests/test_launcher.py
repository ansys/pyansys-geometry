# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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


import pytest

from ansys.geometry.core.connection.launcher import (
    _launch_with_automatic_detection,
    _launch_with_launchmode,
)


def dummy_launcher(**kwargs):
    """Dummy launcher function to simulate a launch without actually doing anything."""
    return f"Dummy launcher called with args: {kwargs}"


@pytest.mark.parametrize(
    "mode,expected_result",
    [
        ("pypim", "Dummy launcher called with args: {}"),
        ("docker", "Dummy launcher called with args: {}"),
        ("core_service", "Dummy launcher called with args: {}"),
        ("geometry_service", "Dummy launcher called with args: {}"),
        ("spaceclaim", "Dummy launcher called with args: {}"),
        ("discovery", "Dummy launcher called with args: {}"),
    ],
)
def test_launch_with_launchmode_no_launch(monkeypatch, mode, expected_result):
    """Test _launch_with_launchmode without actually launching anything."""

    # Override the launch functions with the dummy_launcher
    monkeypatch.setattr(
        "ansys.geometry.core.connection.launcher.launch_remote_modeler", dummy_launcher
    )
    monkeypatch.setattr(
        "ansys.geometry.core.connection.launcher.launch_docker_modeler", dummy_launcher
    )
    monkeypatch.setattr(
        "ansys.geometry.core.connection.launcher.launch_modeler_with_core_service", dummy_launcher
    )
    monkeypatch.setattr(
        "ansys.geometry.core.connection.launcher.launch_modeler_with_geometry_service",
        dummy_launcher,
    )
    monkeypatch.setattr(
        "ansys.geometry.core.connection.launcher.launch_modeler_with_spaceclaim", dummy_launcher
    )
    monkeypatch.setattr(
        "ansys.geometry.core.connection.launcher.launch_modeler_with_discovery", dummy_launcher
    )

    # Call the function and verify the result
    result = _launch_with_launchmode(mode)
    assert result == expected_result


@pytest.mark.parametrize(
    "invalid_mode,expected_exception",
    [
        ("invalid_mode", ValueError),
        ("", ValueError),
        (None, TypeError),  # Expect TypeError for None
    ],
)
def test_launch_with_launchmode_invalid_mode(monkeypatch, invalid_mode, expected_exception):
    """Test _launch_with_launchmode with invalid modes."""
    with pytest.raises(
        expected_exception, match="Invalid launch mode|The launch mode must be a string"
    ):
        _launch_with_launchmode(invalid_mode)


def dummy_launch_docker_modeler(**kwargs):
    """Dummy function to simulate launching the Docker modeler."""
    return "Dummy Docker Modeler Launched"


def test_launch_with_docker_detection(monkeypatch):
    """Test Docker detection and fallback logic without launching anything."""

    # Simulate Docker being available
    monkeypatch.setattr("ansys.geometry.core.connection.docker_instance._HAS_DOCKER", True)
    monkeypatch.setattr(
        "ansys.geometry.core.connection.docker_instance.LocalDockerInstance.is_docker_installed",
        lambda: True,
    )

    # Replace the launch_docker_modeler function with a dummy function
    monkeypatch.setattr(
        "ansys.geometry.core.connection.launcher.launch_docker_modeler",
        dummy_launch_docker_modeler,
    )

    # Call the function and verify the result
    result = _launch_with_automatic_detection()
    assert result == "Dummy Docker Modeler Launched"


def test_docker_not_available(monkeypatch):
    """Test fallback logic when Docker is not available."""

    # Simulate Docker not being available
    monkeypatch.setattr("ansys.geometry.core.connection.docker_instance._HAS_DOCKER", False)

    # Replace the launch_docker_modeler function with a dummy function
    monkeypatch.setattr(
        "ansys.geometry.core.connection.launcher.launch_docker_modeler",
        lambda **kwargs: (_ for _ in ()).throw(NotImplementedError("Docker not available")),
    )

    # Monkeypatch other fallback methods to simulate failure
    monkeypatch.setattr(
        "ansys.geometry.core.connection.launcher.launch_modeler_with_core_service",
        lambda **kwargs: (_ for _ in ()).throw(NotImplementedError("Core service not available")),
    )
    monkeypatch.setattr(
        "ansys.geometry.core.connection.launcher.launch_modeler_with_geometry_service",
        lambda **kwargs: (_ for _ in ()).throw(
            NotImplementedError("Geometry service not available")
        ),
    )
    monkeypatch.setattr(
        "ansys.geometry.core.connection.launcher.launch_modeler_with_spaceclaim",
        lambda **kwargs: (_ for _ in ()).throw(NotImplementedError("SpaceClaim not available")),
    )
    monkeypatch.setattr(
        "ansys.geometry.core.connection.launcher.launch_modeler_with_discovery",
        lambda **kwargs: (_ for _ in ()).throw(NotImplementedError("Discovery not available")),
    )

    # Call the function and verify that it raises NotImplementedError
    with pytest.raises(NotImplementedError, match="Geometry service cannot be initialized."):
        _launch_with_automatic_detection()
