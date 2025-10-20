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

import os
import socket
import tempfile

from beartype.roar import BeartypeCallHintParamViolation
import grpc
import pytest

from ansys.geometry.core.connection.backend import ApiVersions, BackendType
from ansys.geometry.core.connection.client import GrpcClient, wait_until_healthy
from ansys.geometry.core.connection.product_instance import (
    ProductInstance,
    _check_minimal_versions,
    _check_port_or_get_one,
    _get_common_env,
    _is_port_available,
    _manifest_path_provider,
    prepare_and_start_backend,
)


def test_wait_until_healthy():
    """Test checking that a channel is unhealthy."""
    # create a bogus channel
    channel = grpc.insecure_channel("9.0.0.1:80")
    with pytest.raises(TimeoutError):
        wait_until_healthy(channel, timeout=1)


def test_invalid_inputs():
    """Test checking that the input provided is a channel."""
    with pytest.raises(BeartypeCallHintParamViolation):
        GrpcClient(host=123)
    with pytest.raises(BeartypeCallHintParamViolation):
        GrpcClient(port=None)
    with pytest.raises(BeartypeCallHintParamViolation):
        GrpcClient(channel="a")
    with pytest.raises(BeartypeCallHintParamViolation):
        GrpcClient(timeout="a")


def test_api_versions_reader():
    """Checks that the API versions are read correctly for various kinds of input."""
    # Read from a string
    assert ApiVersions.parse_input("21") == ApiVersions.V_21
    assert ApiVersions.parse_input("22") == ApiVersions.V_22
    assert ApiVersions.parse_input("231") == ApiVersions.V_231
    assert ApiVersions.parse_input("232") == ApiVersions.V_232

    # Read from an integer
    assert ApiVersions.parse_input(21) == ApiVersions.V_21
    assert ApiVersions.parse_input(22) == ApiVersions.V_22
    assert ApiVersions.parse_input(231) == ApiVersions.V_231
    assert ApiVersions.parse_input(232) == ApiVersions.V_232

    # Read from an enum
    assert ApiVersions.parse_input(ApiVersions.V_21) == ApiVersions.V_21
    assert ApiVersions.parse_input(ApiVersions.V_22) == ApiVersions.V_22
    assert ApiVersions.parse_input(ApiVersions.V_231) == ApiVersions.V_231
    assert ApiVersions.parse_input(ApiVersions.V_232) == ApiVersions.V_232
    assert ApiVersions.parse_input(ApiVersions.LATEST) == ApiVersions.LATEST

    # Read from an invalid input
    with pytest.raises(
        ValueError, match="API version must be an integer, string or an ApiVersions enum."
    ):  # Invalid argument
        ApiVersions.parse_input(None)

    with pytest.raises(
        ValueError, match="API version must be an integer, string or an ApiVersions enum."
    ):  # Invalid string type
        ApiVersions.parse_input("a")

    with pytest.raises(
        ValueError, match="API version must be an integer, string or an ApiVersions enum."
    ):  # Invalid float type
        ApiVersions.parse_input(1.0)

    with pytest.raises(
        ValueError, match="API version must be an integer, string or an ApiVersions enum."
    ):  # Invalid input type
        ApiVersions.parse_input([231])

    with pytest.raises(ValueError, match="0 is not a valid ApiVersions"):  # Invalid version number
        ApiVersions.parse_input(0)


def test_product_instance_initialization():
    """Test the initialization of the ProductInstance class."""
    pid = -1234  # Example process ID
    product_instance = ProductInstance(pid)
    # Assert that the _pid attribute is correctly set
    assert product_instance._pid == pid
    assert product_instance.close() is False


def test_prepare_and_start_backend_conflicting_versions():
    """Test that providing both 'product_version' and 'version' raises a ValueError."""
    with pytest.raises(
        ValueError,
        match="Both 'product_version' and 'version' arguments are provided."
        " Please use only 'version'.",
    ):
        prepare_and_start_backend(
            backend_type=BackendType.WINDOWS_SERVICE, version=1900, product_version=1901
        )


@pytest.mark.skipif(
    os.name != "nt",
    reason="Test skipped on Linux because it is specific to Windows backends.",
)
def test_prepare_and_start_backend_unavailable_version():
    """Test that an unavailable product version raises a SystemError."""
    with pytest.raises(
        SystemError,
        match="The requested Ansys product's version 1901 is not available,"
        " please specify a different version.",
    ):
        prepare_and_start_backend(backend_type=BackendType.WINDOWS_SERVICE, product_version=1901)


@pytest.mark.skipif(
    os.name != "nt",
    reason="Test skipped on Linux because it is specific to Windows backends.",
)
def test_prepare_and_start_backend_invalid_version():
    """Test that a non-integer 'version' raises a ValueError."""
    with pytest.raises(
        ValueError,
        match="The 'version' argument must be an integer representing the product version.",
    ):
        prepare_and_start_backend(
            backend_type=BackendType.WINDOWS_SERVICE,
            version="invalid_version",  # Pass a non-integer value for version
        )


def test_is_port_available():
    """Test that _is_port_available correctly detects available and unavailable ports."""
    host = "localhost"

    # Dynamically find an available port
    available_port = find_available_port()

    # Test an available port
    assert _is_port_available(available_port, host) is True

    # Test an unavailable port by binding it
    unavailable_port = find_available_port()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, unavailable_port))  # Bind the port to make it unavailable
        assert _is_port_available(unavailable_port, host) is False

    # Test port 0 (invalid port)
    assert _is_port_available(0, host) is False


def test_manifest_path_exists(tmp_path):
    """Test when the manifest path exists."""
    # Create a temporary manifest file
    manifest_path = tmp_path / "test_manifest.xml"
    manifest_path.touch()  # Create the file

    # Call the function
    result = _manifest_path_provider(
        version=241, available_installations={}, manifest_path=str(manifest_path)
    )

    # Assert the returned path is the same as the input
    assert result == str(manifest_path)


def test_manifest_path_does_not_exist(tmp_path, caplog):
    """Test when the manifest path does not exist and handle RuntimeError."""

    # Define a non-existent manifest path
    manifest_path = tmp_path / "non_existent_manifest.xml"

    # Provide a valid `available_installations` dictionary with the required version key
    available_installations = {241: str(tmp_path)}

    # Simulate the default manifest file path
    default_manifest_path = tmp_path / "Addins" / "ApiServer" / "manifest.xml"
    default_manifest_path.parent.mkdir(
        parents=True, exist_ok=True
    )  # Create the directory structure

    # Ensure the default manifest file does not exist
    assert not default_manifest_path.exists()

    # Call the function and expect a RuntimeError
    with pytest.raises(RuntimeError, match="Default manifest file's path does not exist."):
        _manifest_path_provider(
            version=241,
            available_installations=available_installations,
            manifest_path=str(manifest_path),
        )

    # Assert the warning message is logged
    assert (
        "Specified manifest file's path does not exist. Taking install default path." in caplog.text
    )


@pytest.mark.parametrize(
    "latest_installed_version, specific_minimum_version, should_raise, expected_message",
    [
        (
            240,
            None,
            True,
            "PyAnsys Geometry is compatible with Ansys Products from version 24.1.0.",
        ),
        (242, None, False, None),
        (250, 251, True, "PyAnsys Geometry is compatible with Ansys Products from version 25.1.0."),
        (252, 251, False, None),
    ],
)
def test_check_minimal_versions(
    latest_installed_version, specific_minimum_version, should_raise, expected_message
):
    """Test _check_minimal_versions with various scenarios."""
    if should_raise:
        with pytest.raises(SystemError, match=expected_message):
            _check_minimal_versions(latest_installed_version, specific_minimum_version)
    else:
        try:
            _check_minimal_versions(latest_installed_version, specific_minimum_version)
        except SystemError:
            pytest.fail("SystemError raised unexpectedly.")


def find_available_port():
    """Find an available port for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))  # Bind to an available port on the loopback interface
        return s.getsockname()[1]  # Return the port number


@pytest.mark.parametrize(
    "port, should_raise, expected_message",
    [
        (find_available_port(), False, None),  # Test for an available port
        (
            find_available_port(),
            True,
            r"Port \d+ is already in use\. Please specify a different one\.",
        ),  # Test for an unavailable port
    ],
)
def test_check_port_or_get_one(port, should_raise, expected_message):
    """Test _check_port_or_get_one with various port availability scenarios."""
    host = "localhost"

    if should_raise:
        # Bind the port to make it unavailable
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen(1)  # Start listening on the port

            # Call the function and expect a ConnectionError
            with pytest.raises(ConnectionError, match=expected_message):
                _check_port_or_get_one(port)
    else:
        # Ensure the port is available
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            assert s.connect_ex((host, port)) != 0  # Port should not be in use

        # Call the function
        result = _check_port_or_get_one(port)

        # Assert the returned port is the same as the input
        assert result == port


@pytest.mark.parametrize(
    "host, port, enable_trace, server_log_level, server_logs_folder, expected_env",
    [
        (
            "127.0.0.1",
            8080,
            True,
            2,
            None,  # Use a dynamically created temporary directory
            {
                "API_ADDRESS": "127.0.0.1",
                "API_PORT": "8080",
                "LOG_LEVEL": "0",  # Trace mode overrides log level to 0
                "ENABLE_TRACE": "1",
            },
        ),
        (
            "localhost",
            9090,
            False,
            3,
            None,
            {
                "API_ADDRESS": "localhost",
                "API_PORT": "9090",
                "LOG_LEVEL": "3",  # Log level remains unchanged
            },
        ),
    ],
)
def test_get_common_env(
    host, port, enable_trace, server_log_level, server_logs_folder, expected_env
):
    """Test the _get_common_env function with various scenarios."""
    # Dynamically create a temporary directory for logs if server_logs_folder is None
    with tempfile.TemporaryDirectory() as temp_logs_folder:
        if server_logs_folder is None:
            server_logs_folder = temp_logs_folder

        # Call the function
        env = _get_common_env(
            host=host,
            port=port,
            enable_trace=enable_trace,
            server_log_level=server_log_level,
            server_logs_folder=server_logs_folder,
        )

        # Update expected_env with the dynamically created logs folder
        if enable_trace:
            expected_env["ANS_DSCO_REMOTE_LOGS_FOLDER"] = server_logs_folder

        # Assert environment variables are correctly set
        for key, value in expected_env.items():
            assert env[key] == value
