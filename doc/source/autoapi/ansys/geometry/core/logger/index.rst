


Module ``logger``
=================



.. py:module:: ansys.geometry.core.logger



Description
-----------

Provides a general framework for logging in PyGeometry.

This module is built on the `Logging facility for
Python <https://docs.python.org/3/library/logging.html>`_.
It is not intended to replace the standard Python logging library but rather provide
a way to interact between its ``logging`` class and PyGeometry.

The loggers used in this module include the name of the instance, which
is intended to be unique. This name is printed in all active
outputs and is used to track the different Geometry service instances.


Logger usage
------------

Global logger
~~~~~~~~~~~~~
There is a global logger named ``PyGeometry_global`` that is created when
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

   file_path = os.path.join(os.getcwd(), "pygeometry.log")
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

These instance loggers inherit the ``PyGeometry_global`` output handlers and
logging level unless otherwise specified. The way this logger works is very
similar to the global logger. If you want to add a file handler, you can use
the :func:`log_to_file() <PyGeometryCustomAdapter.log_to_file>` method. If you want
to change the log level, you can use the :func:`logger.Logging.setLevel` method.

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




Summary
-------

.. tab-set::




    .. tab-item:: Classes

        Content 2

    .. tab-item:: Functions

        Content 2

    .. tab-item:: Enumerations

        Content 2

    .. tab-item:: Attributes

        Content 2






Contents
--------

Classes
~~~~~~~

.. autoapisummary::

   ansys.geometry.core.logger.PyGeometryCustomAdapter
   ansys.geometry.core.logger.PyGeometryPercentStyle
   ansys.geometry.core.logger.PyGeometryFormatter
   ansys.geometry.core.logger.InstanceFilter
   ansys.geometry.core.logger.Logger



Functions
~~~~~~~~~

.. autoapisummary::

   ansys.geometry.core.logger.addfile_handler
   ansys.geometry.core.logger.add_stdout_handler



Attributes
~~~~~~~~~~

.. autoapisummary::

   ansys.geometry.core.logger.LOG_LEVEL
   ansys.geometry.core.logger.FILE_NAME
   ansys.geometry.core.logger.DEBUG
   ansys.geometry.core.logger.INFO
   ansys.geometry.core.logger.WARN
   ansys.geometry.core.logger.ERROR
   ansys.geometry.core.logger.CRITICAL
   ansys.geometry.core.logger.STDOUT_MSG_FORMAT
   ansys.geometry.core.logger.FILE_MSG_FORMAT
   ansys.geometry.core.logger.DEFAULT_STDOUT_HEADER
   ansys.geometry.core.logger.DEFAULT_FILE_HEADER
   ansys.geometry.core.logger.NEW_SESSION_HEADER
   ansys.geometry.core.logger.string_to_loglevel
   ansys.geometry.core.logger.LOG


.. py:data:: LOG_LEVEL



.. py:data:: FILE_NAME
   :value: 'pygeometry.log'



.. py:data:: DEBUG



.. py:data:: INFO



.. py:data:: WARN



.. py:data:: ERROR



.. py:data:: CRITICAL



.. py:data:: STDOUT_MSG_FORMAT
   :value: '%(levelname)s - %(instance_name)s -  %(module)s - %(funcName)s - %(message)s'



.. py:data:: FILE_MSG_FORMAT



.. py:data:: DEFAULT_STDOUT_HEADER
   :value: Multiline-String

    .. raw:: html

        <details><summary>Show Value</summary>

    .. code-block:: python

        """
        LEVEL - INSTANCE NAME - MODULE - FUNCTION - MESSAGE
        """

    .. raw:: html

        </details>



.. py:data:: DEFAULT_FILE_HEADER



.. py:data:: NEW_SESSION_HEADER



.. py:data:: string_to_loglevel



.. py:class:: PyGeometryCustomAdapter(logger, extra=None)


   Bases: :py:obj:`logging.LoggerAdapter`

   Keeps the reference to the Geometry service instance name dynamic.

   If you use the standard approach, which is supplying *extra* input to the logger,
   you must input Geometry service instances each time you do a log.

   Using adapters, you only need to specify the Geometry service instance that you are
   referring to once.

   .. py:attribute:: level



   .. py:attribute:: file_handler



   .. py:attribute:: stdout_handler



   .. py:method:: process(msg, kwargs)

      Process the logging message and keyword arguments passed in to
      a logging call to insert contextual information. You can either
      manipulate the message itself, the keyword args or both. Return
      the message and kwargs modified (or not) to suit your needs.

      Normally, you'll only need to override this one method in a
      LoggerAdapter subclass for your specific needs.


   .. py:method:: log_to_file(filename: str = FILE_NAME, level: int = LOG_LEVEL)

      Add a file handler to the logger.

      Parameters
      ----------
      filename : str, default: "pygeometry.log"
          Name of the file to write log messages to.
      level : int, default: 10
          Level of logging. The default is ``10``, in which case the
          ``logging.DEBUG`` level is used.


   .. py:method:: log_to_stdout(level=LOG_LEVEL)

      Add a standard output handler to the logger.

      Parameters
      ----------
      level : int, default: 10
          Level of logging. The default is ``10``, in which case the
          ``logging.DEBUG`` level is used.


   .. py:method:: setLevel(level='DEBUG')

      Change the log level of the object and the attached handlers.

      Parameters
      ----------
      level : int, default: 10
          Level of logging. The default is ``10``, in which case the
          ``logging.DEBUG`` level is used.



.. py:class:: PyGeometryPercentStyle(fmt, *, defaults=None)


   Bases: :py:obj:`logging.PercentStyle`

   Provides a common messaging style for the ``PyGeometryFormatter`` class.


.. py:class:: PyGeometryFormatter(fmt=STDOUT_MSG_FORMAT, datefmt=None, style='%', validate=True, defaults=None)


   Bases: :py:obj:`logging.Formatter`

   Provides a ``Formatter`` class for overwriting default format styles.


.. py:class:: InstanceFilter(name='')


   Bases: :py:obj:`logging.Filter`

   Ensures that the ``instance_name`` record always exists.

   .. py:method:: filter(record)

      Ensure that the ``instance_name`` attribute is always present.



.. py:class:: Logger(level=logging.DEBUG, to_file=False, to_stdout=True, filename=FILE_NAME)


   Provides the logger used for each PyGeometry session.

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
   filename : str, default: "pygeometry.log"
       Name of the file to write log log messages to.

   Examples
   --------
   Demonstrate logger usage from the ``Modeler`` instance, which is automatically
   created when a Geometry service instance is created.

   >>> from ansys.geometry.core import Modeler
   >>> modeler = Modeler(loglevel='DEBUG')
   >>> modeler._log.info('This is a useful message')
   INFO -  -  <ipython-input-24-80df150fe31f> - <module> - This is LOG debug message.

   Import the global PyGeometry logger and add a file output handler.

   >>> import os
   >>> from ansys.geometry.core import LOG
   >>> file_path = os.path.join(os.getcwd(), 'pygeometry.log')
   >>> LOG.log_to_file(file_path)

   .. py:attribute:: file_handler



   .. py:attribute:: std_out_handler



   .. py:method:: log_to_file(filename=FILE_NAME, level=LOG_LEVEL)

      Add a file handler to the logger.

      Parameters
      ----------
      filename : str, default: "pygeometry.log"
          Name of the file to write log messages to.
      level : int, default: 10
          Level of logging. The default is ``10``, in which case the
          ``logging.DEBUG`` level is used.

      Examples
      --------
      Write to the ``"pygeometry.log"`` file in the current working directory:

      >>> from ansys.geometry.core import LOG
      >>> import os
      >>> file_path = os.path.join(os.getcwd(), 'pygeometry.log')
      >>> LOG.log_to_file(file_path)


   .. py:method:: log_to_stdout(level=LOG_LEVEL)

      Add the standard output handler to the logger.

      Parameters
      ----------
      level : int, default: 10
          Level of logging. The default is ``10``, in which case the
          ``logging.DEBUG`` level is used.


   .. py:method:: setLevel(level='DEBUG')

      Change the log level of the object and the attached handlers.


   .. py:method:: add_child_logger(sufix: str, level: beartype.typing.Optional[str] = None)

      Add a child logger to the main logger.

      This logger is more general than an instance logger, which is designed to
      track the state of Geometry service instances.

      If the logging level is in the arguments, a new logger with a reference
      to the ``_global`` logger handlers is created instead of a child logger.

      Parameters
      ----------
      sufix : str
          Name of the child logger.
      level : str, default: None
          Level of logging.

      Returns
      -------
      logging.logger
          Logger class.


   .. py:method:: add_instance_logger(name: str, client_instance: ansys.geometry.core.connection.client.GrpcClient, level: beartype.typing.Optional[int] = None) -> PyGeometryCustomAdapter

      Add a logger for a Geometry service instance.

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


   .. py:method:: __getitem__(key)

      Overload the access method by item for the ``Logger`` class.


   .. py:method:: add_handling_uncaught_expections(logger)

      Redirect the output of an exception to a logger.

      Parameters
      ----------
      logger : str
          Name of the logger.



.. py:function:: addfile_handler(logger, filename=FILE_NAME, level=LOG_LEVEL, write_headers=False)

   Add a file handler to the input.

   Parameters
   ----------
   logger : logging.Logger
       Logger to add the file handler to.
   filename : str, default: "pygeometry.log"
       Name of the output file.
   level : int, default: 10
       Level of logging. The default is ``10``, in which case the
       ``logging.DEBUG`` level is used.
   write_headers : bool, default: False
       Whether to write the headers to the file.

   Returns
   -------
   logger
       Logger or Logger object.


.. py:function:: add_stdout_handler(logger, level=LOG_LEVEL, write_headers=False)

   Add a standout handler to the logger.

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
   logger
       Logger or Logger object.


.. py:data:: LOG



