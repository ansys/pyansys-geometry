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
""" "General testing fixtures."""

import logging as deflogging  # Default logging

import pytest

# Define default pytest logging level to DEBUG and stdout
from ansys.geometry.core import LOG
from ansys.geometry.core.errors import GeometryRuntimeError

LOG.setLevel(level="DEBUG")
LOG.log_to_stdout()


def pytest_addoption(parser):
    parser.addoption(
        "--use-existing-service",
        action="store",
        default="no",
        help=(
            "Use Modeler object to connect to an existing service. Options: 'yes' or 'no'."
            " By default, 'no'."
        ),
        choices=("yes", "no"),
    )
    parser.addoption(
        "--use-tracker",
        action="store",
        default="no",
        help=("Enable the tracker to update the design. Options: 'yes' or 'no'. By default, 'no'."),
        choices=("yes", "no"),
    )

    parser.addoption(
        "--backwards-compatibility",
        action="store",
        default="no",
        help=(
            "Skip tests that are backwards incompatible instead of failing them."
            " Options: 'yes' or 'no'. By default, 'no'."
        ),
        choices=("yes", "no"),
    )

    parser.addoption(
        "--backend-version",
        action="store",
        default="latest",
        help=("Specify the backend version to use for the tests. By default, 'latest'."),
    )


def pytest_configure(config):
    """Configure pytest with custom options."""
    # If a specific backend version is set, load the incompatible tests for that version
    config.incompatible_tests = _load_incompatible_tests(
        config.getoption("--backend-version").lower()
    )


def _load_incompatible_tests(version):
    """Load tests that are incompatible with the specified backend version."""
    # Load the YAML file available next to this file
    from pathlib import Path

    import yaml

    current_path = Path(__file__).parent
    incompatible_tests_file = current_path / "_incompatible_tests.yml"
    incompatible_tests = set()

    with incompatible_tests_file.open("r") as file:
        content = yaml.safe_load(file)
        # Search for the specified version
        for backend in content.get("backends", []):
            if backend.get("version") == version:
                incompatible_tests.update(backend.get("incompatible_tests", []))

    return incompatible_tests


def pytest_collection_modifyitems(config, items):
    incompatible = config.incompatible_tests
    skipped = []

    for item in items:
        if item.nodeid in incompatible:
            item.add_marker(pytest.mark.skip(reason="Skipped due to known server incompatibility"))
            skipped.append(item.nodeid)


def pytest_pyfunc_call(pyfuncitem):
    config = pyfuncitem.config
    config_value = config.getoption("--backwards-compatibility")
    skip_on_error = True if config_value.lower() == "yes" else False

    if not skip_on_error:
        return None  # Let normal test execution proceed

    testfunction = pyfuncitem.obj

    def wrapped(*args, **kwargs):
        try:
            testfunction(*args, **kwargs)
        except GeometryRuntimeError as e:
            # Verify if the error is due to server incompatibility
            if "requires a minimum Ansys release version" in str(e):
                # If so, skip the test
                pytest.skip("Skipped due to backwards incompatible backend version.")
            else:
                # If the error is not related to server incompatibility, re-raise it
                raise e

    pyfuncitem.obj = wrapped
    return None  # Continue with normal execution


@pytest.fixture(scope="session")
def use_existing_service(request):
    value: str = request.config.getoption("--use-existing-service")
    return True if value.lower() == "yes" else False


@pytest.fixture(scope="session", autouse=True)
def use_tracker(request):
    """Fixture to enable or disable the tracker."""
    value: str = request.config.getoption("--use-tracker", default="no")  # Explicitly set default
    import ansys.geometry.core as pyansys_geometry

    if value.lower() == "yes":
        pyansys_geometry.USE_TRACKER_TO_UPDATE_DESIGN = True
    else:
        pyansys_geometry.USE_TRACKER_TO_UPDATE_DESIGN = False

    yield  # This allows the test to run

    # Revert the state after the test session
    pyansys_geometry.USE_TRACKER_TO_UPDATE_DESIGN = False


@pytest.fixture
def fake_record():
    def inner_fake_record(
        logger,
        msg="This is a message",
        instance_name="172.1.1.1:52000",
        handler_index=0,
        name_logger=None,
        level=deflogging.DEBUG,
        filename="fn",
        lno=0,
        args=(),
        exc_info=None,
        extra={},
    ):
        """Function to fake log records using the format from the logger.

        Parameters
        ----------
        logger : logging.Logger
            A logger object with at least a handler.
        msg : str, default: "This is a message"
            Message to include in the log record.
        instance_name : str, default: "172.1.1.1:52000"
            Name of the instance.
        handler_index : int, default: 0
            Index of the selected handler in case you want to test a handler different than
            the first one.
        level : int, default: deflogging.DEBUG
            Logging level.
        filename : str, default: fn
            Name of the file name. [FAKE].
        lno : int, default: 0
            Line where the fake log is recorded [FAKE].
        args : tuple, default: ()
            Other arguments.
        exc_info : [type], default: None
            Exception information.
        extra : dict, default: {}
            Extra arguments, one of them should be 'instance_name'.

        Returns
        -------
        str
            The formatted message according to the handler.
        """
        sinfo = None
        if not name_logger:
            name_logger = logger.name

        if "instance_name" not in extra.keys():
            extra["instance_name"] = instance_name

        record = logger.makeRecord(
            name_logger,
            level,
            filename,
            lno,
            msg,
            args=args,
            exc_info=exc_info,
            extra=extra,
            sinfo=sinfo,
        )
        handler = logger.handlers[handler_index]
        return handler.format(record)

    return inner_fake_record


def are_graphics_available() -> bool:
    """Determine whether graphics are available."""
    from ansys.geometry.core.misc.checks import run_if_graphics_required

    # If the imports are successful, then graphics can be handled...
    # ...otherwise, graphics are not available.
    try:
        run_if_graphics_required()
        from pyvista.plotting import system_supports_plotting

        return system_supports_plotting()
    except ImportError:
        return False
