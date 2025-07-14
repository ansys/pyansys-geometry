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
""" "Testing of log module."""

import logging as deflogging  # Default logging
import os
import re
from typing import Callable

import pytest

from ansys.geometry.core import LOG  # Global logger
from ansys.geometry.core.connection import GrpcClient
import ansys.geometry.core.logger as logger

## Notes
# Use the next fixtures for:
# - capfd: for testing console printing.
# - caplog: for testing logging printing.

LOG_LEVELS = {"CRITICAL": 50, "ERROR": 40, "WARNING": 30, "INFO": 20, "DEBUG": 10}


def test_add_instance():
    # Testing adding an instance logger while checking if log has certain key
    base_name = "root"
    instance_logger_1 = LOG.add_instance_logger(
        name=base_name, client_instance=GrpcClient(), level=10
    )
    instance_logger_1.info("This is a message from the first instance logger.")
    with pytest.raises(KeyError, match="There is no instances with name root_4."):
        LOG.__getitem__("root_4")


def test_custom_and_child_log():
    # Testing out writing a child log and adding std handler to it
    custom_filename = os.path.join(os.getcwd(), "custom_geometry.log")
    logger1 = logger.Logger(level="DEBUG", to_file=True, filename=custom_filename)
    child_log = logger1._make_child_logger(suffix="ChildLogger", level="INFO")
    child_log.info("This is a test to child logger")
    child_log1 = logger1._make_child_logger(suffix="ChildLogger1", level=None)
    child_log1.info("This is a test to child logger")
    logger1.add_child_logger(suffix="ChildLogger", level="INFO")
    logger.add_stdout_handler(child_log, level=logger.logging.INFO, write_headers=True)
    for handler in logger1.logger.handlers:
        if isinstance(handler, logger.logging.FileHandler):
            handler.close()
    os.remove(custom_filename)


def test_stdout_defined():
    # Testing if stdout is defined already and giving a custom format
    logger_adapter = logger.PyGeometryCustomAdapter(LOG)
    with pytest.raises(
        Exception,
        match="Stdout logger is already defined.",
    ):
        logger_adapter.log_to_stdout(level=logger.LOG_LEVEL)
    formatter = logger.PyGeometryFormatter(fmt="%(levelname)s - %(instance_name)s - %(message)s")
    stream_handler = logger.logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger_adapter.logger.handlers = [stream_handler]
    logger_adapter.setLevel("ERROR")
    defaults = {
        "instance_name": "DefaultInstance",
        "module": "DefaultModule",
        "funcName": "DefaultFunction",
    }
    formatter = logger.PyGeometryFormatter(
        fmt="%(levelname)s - %(instance_name)s - %(module)s - %(funcName)s - %(message)s",
        defaults=defaults,
    )
    logger1 = logger.logging.getLogger("CustomLogger")
    logger1.setLevel(logger.logging.DEBUG)
    stream_handler = logger.logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger1.addHandler(stream_handler)
    logger1.info("This is a test message without extra fields.")


def test_stdout_reading(capfd: pytest.CaptureFixture):
    """Test for checking simple standard output reading by pytest.

    Parameters
    ----------
    capfd : pytest.CaptureFixture
        Fixture for capturing console stdout and stderr.
    """
    print("This is a test")

    out, _ = capfd.readouterr()
    assert out == "This is a test\n"


def test_only_logger(caplog: pytest.LogCaptureFixture):
    """Test for checking that the logging capabilities are working fine in the
    Python version installed.

    Parameters
    ----------
    caplog : pytest.LogCaptureFixture
        Fixture for capturing logs.
    """
    log_a = deflogging.getLogger("test")
    log_a.setLevel("DEBUG")

    log_a.debug("This is another test")
    assert "This is another test" in caplog.text


def test_global_logger_exist():
    """Test for checking the accurate naming of the general Logger instance."""
    assert isinstance(LOG.logger, deflogging.Logger)
    assert LOG.logger.name == "PyAnsys_Geometry_global"


def test_global_logger_has_handlers():
    """Test for checking that the general Logger has file_handlers and sdtout
    file_handlers implemented.
    """
    assert hasattr(LOG, "file_handler")
    assert hasattr(LOG, "std_out_handler")
    assert LOG.logger.hasHandlers
    assert LOG.file_handler or LOG.std_out_handler  # at least a handler is not empty


def test_global_logger_logging(caplog: pytest.LogCaptureFixture):
    """Testing the global PyDiscovery logger capabilities. Forcing minimum
    logging level to Debug, adding a message with different logging levels,
    checking the output and restoring to original level.

    Parameters
    ----------
    caplog : pytest.LogCaptureFixture
        Fixture for capturing logs.
    """
    LOG.logger.setLevel("DEBUG")
    LOG.std_out_handler.setLevel("DEBUG")
    for each_log_name, each_log_number in LOG_LEVELS.items():
        msg = f"This is an {each_log_name} message."
        LOG.logger.log(each_log_number, msg)
        # Make sure we are using the right logger, the right level and message.
        assert caplog.record_tuples[-1] == ("PyAnsys_Geometry_global", each_log_number, msg)

    #  Set back to default level == ERROR
    LOG.logger.setLevel("ERROR")
    LOG.std_out_handler.setLevel("ERROR")


def test_global_logger_level_mode():
    """Checking that the Logger levels are stored as integer values and that
    the default value (unless changed) is ERROR.
    """
    assert isinstance(LOG.logger.level, int)
    assert LOG.logger.level == logger.ERROR


def test_global_logger_exception_handling(caplog: pytest.LogCaptureFixture):
    """Test for checking that Errors are also raised in the logger as ERROR
    type.

    Parameters
    ----------
    caplog : pytest.LogCaptureFixture
        Fixture for capturing logs.

    Raises
    ------
    Exception
        Throwing an exception for catching it.
    """
    exc = "Unexpected exception"
    with pytest.raises(Exception):
        try:
            raise Exception(exc)
        finally:
            assert exc in caplog.text


@pytest.mark.parametrize(
    "level",
    [
        deflogging.DEBUG,
        deflogging.INFO,
        deflogging.WARN,
        deflogging.ERROR,
        deflogging.CRITICAL,
    ],
)
def test_global_logger_debug_levels(level: int, caplog: pytest.LogCaptureFixture):
    """Testing for all the possible logging level that the output is recorded
    properly for each type of msg.

    Parameters
    ----------
    level : int
        The logging level specified from the parametrization.
    caplog : pytest.LogCaptureFixture
        Fixture for capturing logs.
    """
    with caplog.at_level(level, LOG.logger.name):  # changing root logger level:
        for each_log_name, each_log_number in LOG_LEVELS.items():
            msg = f"This is a message of type {each_log_name}."
            LOG.logger.log(each_log_number, msg)
            # Make sure we are using the right logger, the right level and message.
            if each_log_number >= level:
                assert caplog.record_tuples[-1] == (
                    "PyAnsys_Geometry_global",
                    each_log_number,
                    msg,
                )
            else:
                assert caplog.record_tuples[-1] != (
                    "PyAnsys_Geometry_global",
                    each_log_number,
                    msg,
                )


def test_global_logger_format(fake_record: Callable):
    """Test for checking the global logger formatter aspect.

    Parameters
    ----------
    fake_record : Callable
        Fake record function.
    """
    # Since we cannot read the format of our logger, because pytest just dont show the console
    # output or if it does, it formats the logger with its own formatter, we are going to check
    # the logger handlers and output by faking a record.
    # This method is not super robust, since we are input fake data to ``logging.makeRecord``.
    # There are things such as filename or class that we cannot evaluate without going
    # into the code.

    assert "instance" in logger.FILE_MSG_FORMAT
    assert "instance" in logger.STDOUT_MSG_FORMAT

    log = fake_record(
        LOG.logger,
        msg="This is a message",
        level=deflogging.DEBUG,
        extra={"instance_name": "172.1.1.1"},
    )
    assert re.findall(r"(?:[0-9]{1,3}.){3}[0-9]{1,3}", log)
    assert "DEBUG" in log
    assert "This is a message" in log


def test_global_methods(caplog: pytest.LogCaptureFixture):
    """Testing global logger methods for printing out different log messages,
    from DEBUG to CRITICAL.

    Parameters
    ----------
    caplog : pytest.LogCaptureFixture
        Fixture for capturing logs.
    """
    LOG.logger.setLevel("DEBUG")
    LOG.std_out_handler.setLevel("DEBUG")

    msg = "This is a debug message"
    LOG.debug(msg)
    assert msg in caplog.text

    msg = "This is an info message"
    LOG.info(msg)
    assert msg in caplog.text

    msg = "This is a warning message"
    LOG.warning(msg)
    assert msg in caplog.text

    msg = "This is an error message"
    LOG.error(msg)
    assert msg in caplog.text

    msg = "This is a critical message"
    LOG.critical(msg)
    assert msg in caplog.text

    msg = 'This is a 30 message using "log"'
    LOG.log(30, msg)
    assert msg in caplog.text

    # Setting back to original level
    LOG.logger.setLevel("INFO")
    LOG.std_out_handler.setLevel("INFO")


def test_log_to_file(tmp_path_factory: pytest.TempPathFactory):
    """Testing writing to log file.

    Since the default loglevel of LOG is error, debug are not normally recorded to it.

    Parameters
    ----------
    tmp_path_factory  : pytest.TempdirFactory
        Fixture for accessing a temporal directory (erased after test execution).
    """
    file_path = tmp_path_factory.mktemp("log_files") / "instance.log"
    file_msg_error = "This is a error message"
    file_msg_debug = "This is a debug message"

    # The LOG loglevel is changed in previous test,
    # hence making sure now it is the "default" one.
    LOG.logger.setLevel("ERROR")
    LOG.std_out_handler.setLevel("ERROR")

    if not LOG.file_handler:
        LOG.log_to_file(file_path)

    LOG.error(file_msg_error)
    LOG.debug(file_msg_debug)

    with file_path.open(mode="r") as fid:
        text = "".join(fid.readlines())

    assert file_msg_error in text
    assert file_msg_debug not in text
    assert "ERROR" in text
    assert "DEBUG" not in text

    LOG.logger.setLevel("DEBUG")
    for each_handler in LOG.logger.handlers:
        each_handler.setLevel("DEBUG")

    file_msg_debug = "This debug message should be recorded."
    LOG.debug(file_msg_debug)

    with file_path.open(mode="r") as fid:
        text = "".join(fid.readlines())

    assert file_msg_debug in text
