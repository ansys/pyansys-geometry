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
""" "Testing of log module with client connection."""

import logging as deflogging  # Default logging
from pathlib import Path
import re
from typing import Callable

import pytest

from ansys.geometry.core import LOG, Modeler  # Global logger


def test_instance_logger_format(modeler: Modeler, fake_record: Callable):
    """Test for checking the instance logger formatter aspect.

    Parameters
    ----------
    modeler : ansys.geometry.core.modeler.Modeler
        The client to be used for the tests.
    fake_record : Callable
        Fake record function.
    """
    # Since we cannot read the format of our logger, because pytest just does not show the console
    # output or if it does, it formats the logger with its own formatter, we are going to check
    # the logger handlers and output by faking a record.
    # This method is not super robust, since we are input fake data to ``logging.makeRecord``.
    # There are things such as filename or class that we cannot evaluate without going
    # into the code.

    log = fake_record(
        modeler._grpc_client.log.logger,
        msg="This is a message",
        level=deflogging.DEBUG,
        extra={"instance_name": "172.1.1.1"},
    )
    assert re.findall(r"(?:[0-9]{1,3}.){3}[0-9]{1,3}", log)
    assert "DEBUG" in log
    assert "This is a message" in log


def test_log_instance_name(modeler: Modeler):
    """Test for verifying access to specific logging instance by providing the
    client name.

    Parameters
    ----------
    modeler : ansys.geometry.core.modeler.Modeler
        The client to be used for the tests.
    """
    # Verify we can access via an instance name
    LOG[modeler.client.get_name()] == modeler.client.log


def test_instance_log_to_file(tmp_path_factory: pytest.TempPathFactory, modeler: Modeler):
    """Testing writing to log file.

    Since the default loglevel of LOG is error, debug are not normally recorded to it.

    Parameters
    ----------
    tmp_path_factory : pytest.TempPathFactory
        Fixture for accessing a temporal directory (erased after test execution).
    modeler : ansys.geometry.core.modeler.Modeler
        The client to be used for the tests.
    """
    file_path = tmp_path_factory.mktemp("log_files") / "instance.log"
    file_msg_error = "This is a error message"
    file_msg_debug = "This is a debug message"

    prev_level = modeler.client.log.logger.getEffectiveLevel()
    modeler.client.log.logger.setLevel("ERROR")

    if not modeler.client.log.file_handler:
        modeler.client.log.log_to_file(file_path)
    else:
        file_path = modeler.client.log.file_handler.baseFilename

    modeler.client.log.error(file_msg_error)
    modeler.client.log.debug(file_msg_debug)

    with Path(file_path).open(mode="r") as fid:
        text = "".join(fid.readlines())

    assert file_msg_error in text
    assert file_msg_debug not in text
    assert "ERROR" in text
    assert "TRACE" not in text

    modeler.client.log.logger.setLevel("DEBUG")
    for each_handler in modeler.client.log.logger.handlers:
        each_handler.setLevel("DEBUG")

    file_msg_debug = "This debug message should be recorded."
    modeler.client.log.debug(file_msg_debug)

    # Set back to info level
    modeler.client.log.logger.setLevel("INFO")

    with Path(file_path).open(mode="r") as fid:
        text = "".join(fid.readlines())

    assert file_msg_debug in text

    modeler.client.log.logger.setLevel(prev_level)
