# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
"""Provides a general framework for logging in PyAnsys Geometry.

This module is built on the `Logging facility for
Python <https://docs.python.org/3/library/logging.html>`_.
It is not intended to replace the standard Python logging library but rather provide
a way to interact between its ``logging`` class and PyAnsys Geometry.

The loggers used in this module include the name of the instance, which
is intended to be unique. This name is printed in all active
outputs and is used to track the different Geometry service instances.


Logger usage
------------

Global logger
~~~~~~~~~~~~~
There is a global logger named ``PyAnsys_Geometry_global`` that is created when
``ansys.geometry.core.__init__`` is called.  If you want to use this global
logger, you must call it at the top of your module:

.. code:: python

   from ansys.geometry.core import LOG

You can rename this logger to avoid conflicts with other loggers (if any):

.. code:: python

   from ansys.geometry.core import LOG as logger


The default logging level of ``LOG`` is ``ERROR``.
You can change this level and output lower-level messages with
this code:

.. code:: python

   LOG.logger.setLevel("DEBUG")
   LOG.file_handler.setLevel("DEBUG")  # If present.
   LOG.stdout_handler.setLevel("DEBUG")  # If present.


Alternatively, you can ensure that all the handlers are set to the input log
level with this code:

.. code:: python

   LOG.setLevel("DEBUG")

This logger does not log to a file by default. If you want, you can
add a file handler with this code:

.. code:: python

   import os

   file_path = os.path.join(os.getcwd(), "pyansys-geometry.log")
   LOG.log_to_file(file_path)

This also sets the logger to be redirected to this file. If you want
to change the characteristics of this global logger from the beginning
of the execution, you must edit the ``__init__`` file in the directory
``ansys.geometry.core``.

To log using this logger, call the desired method as a normal logger with:

.. code:: pycon

    >>> import logging
    >>> from ansys.geometry.core.logging import Logger
    >>> LOG = Logger(level=logging.DEBUG, to_file=False, to_stdout=True)
    >>> LOG.debug("This is LOG debug message.")

    DEBUG -  -  <ipython-input-24-80df150fe31f> - <module> - This is LOG debug message.


Instance logger
~~~~~~~~~~~~~~~
Every time an instance of the :class:`Modeler <ansys.geometry.core.modeler.Modeler>`
class is created, a logger is created and stored in ``LOG._instances``. This field is a
dictionary where the key is the name of the created logger.

These instance loggers inherit the ``PyAnsys_Geometry_global`` output handlers and
logging level unless otherwise specified. The way this logger works is very
similar to the global logger. If you want to add a file handler, you can use
the :meth:`log_to_file() <PyGeometryCustomAdapter.log_to_file>` method. If you want
to change the log level, you can use the :meth:`~logging.Logger.setLevel` method.

Here is an example of how you can use this logger:

.. code:: pycon

    >>> from ansys.geometry.core import Modeler
    >>> modeler = Modeler()
    >>> modeler._log.info("This is a useful message")

    INFO - GRPC_127.0.0.1:50056 -  <...> - <module> - This is a useful message


Other loggers
~~~~~~~~~~~~~
You can create your own loggers using a Python ``logging`` library as
you would do in any other script. There would be no conflicts between
these loggers.
"""

from copy import copy
from datetime import datetime
import logging
import sys
from typing import TYPE_CHECKING
import weakref

from ansys.geometry.core.misc.checks import check_type

if TYPE_CHECKING:  # pragma: no cover
    from ansys.geometry.core.connection.client import GrpcClient

## Default configuration
LOG_LEVEL = logging.DEBUG
FILE_NAME = "pyansys-geometry.log"

# For convenience
DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARN
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

## Formatting

STDOUT_MSG_FORMAT = "%(levelname)s - %(instance_name)s -  %(module)s - %(funcName)s - %(message)s"

FILE_MSG_FORMAT = STDOUT_MSG_FORMAT

DEFAULT_STDOUT_HEADER = """
LEVEL - INSTANCE NAME - MODULE - FUNCTION - MESSAGE
"""
DEFAULT_FILE_HEADER = DEFAULT_STDOUT_HEADER

NEW_SESSION_HEADER = f"""
===============================================================================
       NEW SESSION - {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
==============================================================================="""

string_to_loglevel = {
    "DEBUG": DEBUG,
    "INFO": INFO,
    "WARN": WARN,
    "WARNING": WARN,
    "ERROR": ERROR,
    "CRITICAL": CRITICAL,
}


class PyGeometryCustomAdapter(logging.LoggerAdapter):
    """Keeps the reference to the Geometry service instance name dynamic.

    If you use the standard approach, which is supplying *extra* input
    to the logger, you must input Geometry service instances each time
    you do a log.

    Using adapters, you only need to specify the Geometry service
    instance that you are referring to once.
    """

    level = (
        None  # This is maintained for compatibility with ``supress_logging``, but it does nothing.
    )
    file_handler = None
    stdout_handler = None

    def __init__(self, logger, extra=None):  # noqa: D107
        self.logger = logger
        if extra is not None:
            self.extra = weakref.proxy(extra)
        else:
            self.extra = None  # pragma: no cover
        self.file_handler = logger.file_handler
        self.std_out_handler = logger.std_out_handler

    def process(self, msg, kwargs):  # noqa: D102
        kwargs["extra"] = {}
        # This are the extra parameters sent to log
        kwargs["extra"]["instance_name"] = (
            self.extra.get_name()
        )  # here self.extra is the argument passed to the log records.
        return msg, kwargs

    def log_to_file(self, filename: str = FILE_NAME, level: int = LOG_LEVEL):
        """Add a file handler to the logger.

        Parameters
        ----------
        filename : str, default: "pyansys-geometry.log"
            Name of the file to write log messages to.
        level : int, default: 10
            Level of logging. The default is ``10``, in which case the
            ``logging.DEBUG`` level is used.
        """
        self.logger = addfile_handler(
            self.logger, filename=filename, level=level, write_headers=True
        )
        self.file_handler = self.logger.file_handler

    def log_to_stdout(self, level=LOG_LEVEL):
        """Add a standard output handler to the logger.

        Parameters
        ----------
        level : int, default: 10
            Level of logging. The default is ``10``, in which case the
            ``logging.DEBUG`` level is used.
        """
        if self.std_out_handler:
            raise Exception("Stdout logger is already defined.")

        self.logger = add_stdout_handler(self.logger, level=level)
        self.std_out_handler = self.logger.std_out_handler

    def setLevel(self, level="DEBUG"):  # noqa: N802
        """Change the log level of the object and the attached handlers.

        Parameters
        ----------
        level : int, default: 10
            Level of logging. The default is ``10``, in which case the
            ``logging.DEBUG`` level is used.
        """
        self.logger.setLevel(level)
        for each_handler in self.logger.handlers:
            each_handler.setLevel(level)
        self.level = level


class PyGeometryPercentStyle(logging.PercentStyle):
    """Provides a common messaging style."""

    def __init__(self, fmt, *, defaults=None):
        """Initialize ``PyGeometryPercentStyle`` class."""
        self._fmt = fmt or self.default_format
        self._defaults = defaults

    def _format(self, record):
        """Format properly the message styles."""
        defaults = self._defaults
        if defaults:
            values = defaults | record.__dict__
        else:
            values = record.__dict__

        # We can make any changes that we want in the record here. For example,
        # adding a key.

        # We could create an ``if`` here if we want conditional formatting, and even
        # change the record.__dict__.
        # Because we don't want to create conditional fields now, it is fine to keep
        # the same MSG_FORMAT for all of them.

        # For the case of logging exceptions to the logger.
        values.setdefault("instance_name", "")

        return STDOUT_MSG_FORMAT % values


class PyGeometryFormatter(logging.Formatter):
    """Provides a ``Formatter`` class for overwriting default format styles."""

    def __init__(
        self,
        fmt=STDOUT_MSG_FORMAT,
        datefmt=None,
        style="%",
        validate=True,
        defaults=None,
    ):
        """Initialize the ``PyGeometryFormatter`` class."""
        super().__init__(fmt, datefmt, style, validate)
        self._style = PyGeometryPercentStyle(fmt, defaults=defaults)  # overwriting


class InstanceFilter(logging.Filter):
    """Ensures that the ``instance_name`` record always exists."""

    def filter(self, record):
        """Ensure that the ``instance_name`` attribute is always present."""
        if not hasattr(record, "instance_name"):
            record.instance_name = ""
        return True


class Logger:
    """Provides the logger used for each PyAnsys Geometry session.

    This class allows you to add handlers to the logger to output messages
    to a file or to the standard output (stdout).

    Parameters
    ----------
    level : int, default: 10
        Logging level to filter the message severity allowed in the logger.
        The default is ``10``, in which case the ``logging.DEBUG`` level
        is used.
    to_file : bool, default: False
        Whether to write log messages to a file.
    to_stdout : bool, default: True
        Whether to write log messages to the standard output.
    filename : str, default: "pyansys-geometry.log"
        Name of the file to write log log messages to.

    Examples
    --------
    Demonstrate logger usage from the ``Modeler`` instance, which is automatically
    created when a Geometry service instance is created.

    >>> from ansys.geometry.core import Modeler
    >>> modeler = Modeler(loglevel="DEBUG")
    >>> modeler._log.info("This is a useful message")
    INFO -  -  <ipython-input-24-80df150fe31f> - <module> - This is LOG debug message.

    Import the global PyAnsys Geometry logger and add a file output handler.

    >>> import os
    >>> from ansys.geometry.core import LOG
    >>> file_path = os.path.join(os.getcwd(), "pyansys-geometry.log")
    >>> LOG.log_to_file(file_path)
    """

    file_handler = None
    std_out_handler = None
    _level = logging.DEBUG
    _instances = {}

    def __init__(self, level=logging.DEBUG, to_file=False, to_stdout=True, filename=FILE_NAME):
        """Customize the ``logger`` class for PyAnsys Geometry.

        Parameters
        ----------
        level : int, default: 10
            Level of logging as defined in the ``logging`` package. The default is ``10``,
            in which case the ``logging.DEBUG`` level is used.
        to_file : bool, default: False
            Whether to write log messages to a file.
        to_stdout : bool, default: True
            Whether to write log messages to the standard output (stdout).
        filename : str, default: "pyansys-geometry.log"
           Name of the file to write log messages to.
        """
        # create default main logger
        self.logger = logging.getLogger("PyAnsys_Geometry_global")
        self.logger.addFilter(InstanceFilter())
        self.logger.setLevel(level)
        self.logger.propagate = True
        self.level = self.logger.level

        # Writing logging methods.
        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical
        self.log = self.logger.log

        if to_file or filename != FILE_NAME:
            # We record to file
            self.log_to_file(filename=filename, level=level)

        if to_stdout:
            self.log_to_stdout(level=level)

        # Using logger to record unhandled exceptions
        self.add_handling_uncaught_expections(self.logger)

    def log_to_file(self, filename=FILE_NAME, level=LOG_LEVEL):
        """Add a file handler to the logger.

        Parameters
        ----------
        filename : str, default: "pyansys-geometry.log"
            Name of the file to write log messages to.
        level : int, default: 10
            Level of logging. The default is ``10``, in which case the
            ``logging.DEBUG`` level is used.

        Examples
        --------
        Write to the ``"pyansys-geometry.log"`` file in the current working directory:

        >>> from ansys.geometry.core import LOG
        >>> import os
        >>> file_path = os.path.join(os.getcwd(), "pyansys-geometry.log")
        >>> LOG.log_to_file(file_path)
        """
        self = addfile_handler(self, filename=filename, level=level, write_headers=True)

    def log_to_stdout(self, level=LOG_LEVEL):
        """Add the standard output handler to the logger.

        Parameters
        ----------
        level : int, default: 10
            Level of logging. The default is ``10``, in which case the
            ``logging.DEBUG`` level is used.
        """
        self = add_stdout_handler(self, level=level)

    def setLevel(self, level="DEBUG"):  # noqa: N802
        """Change the log level of the object and the attached handlers."""
        self.logger.setLevel(level)
        for each_handler in self.logger.handlers:
            each_handler.setLevel(level)
        self._level = level

    def _make_child_logger(self, suffix, level):
        """Create a child logger.

        This method uses the ``getChild()`` method or copies attributes between the
        ``PyAnsys_Geometry_global`` logger and the new one.
        """
        logger = logging.getLogger(suffix)
        logger.std_out_handler = None
        logger.file_handler = None

        if self.logger.hasHandlers:
            for each_handler in self.logger.handlers:
                new_handler = copy(each_handler)

                if each_handler == self.file_handler:
                    logger.file_handler = new_handler
                elif each_handler == self.std_out_handler:
                    logger.std_out_handler = new_handler

                if level and isinstance(level, str):
                    # The logger handlers are copied and changed the loglevel is
                    # the specified log level is lower than the one of the
                    # global.
                    if isinstance(level, int) and each_handler.level > level:
                        new_handler.setLevel(level)
                    elif (
                        isinstance(level, str)
                        and each_handler.level > string_to_loglevel[level.upper()]
                    ):
                        new_handler.setLevel(level)

                logger.addHandler(new_handler)

        if level:
            if isinstance(level, str):
                level = string_to_loglevel[level.upper()]
            logger.setLevel(level)

        else:
            logger.setLevel(self.logger.level)

        logger.propagate = True
        return logger

    def add_child_logger(self, suffix: str, level: str | None = None):
        """Add a child logger to the main logger.

        This logger is more general than an instance logger, which is designed to
        track the state of Geometry service instances.

        If the logging level is in the arguments, a new logger with a reference
        to the ``_global`` logger handlers is created instead of a child logger.

        Parameters
        ----------
        suffix : str
            Name of the child logger.
        level : str, default: None
            Level of logging.

        Returns
        -------
        logging.Logger
            Logger class.
        """
        name = self.logger.name + "." + suffix
        self._instances[name] = self._make_child_logger(self, name, level)
        return self._instances[name]

    def add_instance_logger(
        self, name: str, client_instance: "GrpcClient", level: int | None = None
    ) -> PyGeometryCustomAdapter:
        """Add a logger for a Geometry service instance.

        The Geometry service instance logger is a logger with an adapter that adds
        contextual information such as the Geometry service instance name. This logger is
        returned, and you can use it to log events as a normal logger. It is
        stored in the ``_instances`` field.

        Parameters
        ----------
        name : str
            Name for the new instance logger.
        client_instance : GrpcClient
            Geometry service GrpcClient object, which should contain the ``get_name`` method.
        level : int, default: None
            Level of logging.

        Returns
        -------
        PyGeometryCustomAdapter
            Logger adapter customized to add Geometry service information to the
            logs. You can use this class to log events in the same
            way you would with the ``Logger`` class.
        """
        from ansys.geometry.core.connection.client import GrpcClient

        check_type(name, str)
        check_type(client_instance, GrpcClient)

        count_ = 0
        new_name = name
        while new_name in logging.root.manager.__dict__.keys():
            count_ += 1
            new_name = f"{name}_{count_}"

        self._instances[new_name] = PyGeometryCustomAdapter(
            self._make_child_logger(name, level), client_instance
        )

        return self._instances[new_name]

    def __getitem__(self, key):
        """Overload the access method by item for the ``Logger`` class."""
        if key in self._instances.keys():
            return self._instances[key]
        else:
            raise KeyError(f"There is no instances with name {key}.")

    def add_handling_uncaught_expections(self, logger):
        """Redirect the output of an exception to a logger.

        Parameters
        ----------
        logger : str
            Name of the logger.
        """

        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

        sys.excepthook = handle_exception


def addfile_handler(logger, filename=FILE_NAME, level=LOG_LEVEL, write_headers=False):
    """Add a file handler to the input.

    Parameters
    ----------
    logger : logging.Logger
        Logger to add the file handler to.
    filename : str, default: "pyansys-geometry.log"
        Name of the output file.
    level : int, default: 10
        Level of logging. The default is ``10``, in which case the
        ``logging.DEBUG`` level is used.
    write_headers : bool, default: False
        Whether to write the headers to the file.

    Returns
    -------
    Logger
        :class:`Logger` or :class:`logging.Logger` object.
    """
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(FILE_MSG_FORMAT))

    if isinstance(logger, Logger):
        logger.file_handler = file_handler
        logger.logger.addHandler(file_handler)

    elif isinstance(logger, logging.Logger):
        logger.file_handler = file_handler
        logger.addHandler(file_handler)

    if write_headers:
        file_handler.stream.write(NEW_SESSION_HEADER)
        file_handler.stream.write(DEFAULT_FILE_HEADER)

    return logger


def add_stdout_handler(logger, level=LOG_LEVEL, write_headers=False):
    """Add a standout handler to the logger.

    Parameters
    ----------
    logger : logging.Logger
        Logger to add the file handler to.
    level : int, default: 10
        Level of logging. The default is ``10``, in which case the
        ``logging.DEBUG`` level is used.
    write_headers : bool, default: False
        Whether to write headers to the file.

    Returns
    -------
    Logger
        :class:`Logger` or :class:`logging.Logger` object.
    """
    std_out_handler = logging.StreamHandler()
    std_out_handler.setLevel(level)
    std_out_handler.setFormatter(PyGeometryFormatter(STDOUT_MSG_FORMAT))

    if isinstance(logger, Logger):
        logger.std_out_handler = std_out_handler
        logger.logger.addHandler(std_out_handler)

    elif isinstance(logger, logging.Logger):
        logger.addHandler(std_out_handler)

    if write_headers:
        std_out_handler.stream.write(DEFAULT_STDOUT_HEADER)

    return logger


# ===============================================================
# Finally define logger
# ===============================================================

LOG = Logger(level=logging.ERROR, to_file=False, to_stdout=True)
LOG.debug("Loaded logging module as LOG")
