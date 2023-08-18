


Module ``client``
=================



.. py:module:: ansys.geometry.core.connection.client



Description
-----------

Module providing a wrapped abstraction of the gRPC PROTO API definition and stubs.




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

   ansys.geometry.core.connection.client.GrpcClient



Functions
~~~~~~~~~

.. autoapisummary::

   ansys.geometry.core.connection.client.wait_until_healthy



.. py:function:: wait_until_healthy(channel: grpc.Channel, timeout: float)

   Wait until a channel is healthy before returning.

   Parameters
   ----------
   channel : ~grpc.Channel
       Channel that must be established and healthy.
   timeout : float
       Timeout in seconds. An attempt is made every 100 milliseconds
       until the timeout is exceeded.

   Raises
   ------
   TimeoutError
       Raised when the total elapsed time exceeds the value for the ``timeout`` parameter.


.. py:class:: GrpcClient(host: beartype.typing.Optional[str] = DEFAULT_HOST, port: beartype.typing.Union[str, int] = DEFAULT_PORT, channel: beartype.typing.Optional[grpc.Channel] = None, remote_instance: beartype.typing.Optional[ansys.platform.instancemanagement.Instance] = None, local_instance: beartype.typing.Optional[ansys.geometry.core.connection.local_instance.LocalDockerInstance] = None, timeout: beartype.typing.Optional[ansys.geometry.core.typing.Real] = 60, logging_level: beartype.typing.Optional[int] = logging.INFO, logging_file: beartype.typing.Optional[beartype.typing.Union[pathlib.Path, str]] = None, backend_type: beartype.typing.Optional[ansys.geometry.core.connection.backend.BackendType] = None)


   Wraps the gRPC connection for the Geometry service.

   Parameters
   ----------
   host : str, default: DEFAULT_HOST
       Host where the server is running.
   port : Union[str, int], default: DEFAULT_PORT
       Port number where the server is running.
   channel : ~grpc.Channel, default: None
       gRPC channel for server communication.
   remote_instance : ansys.platform.instancemanagement.Instance, default: None
       Corresponding remote instance when the Geometry service
       is launched through `PyPIM <https://github.com/ansys/pypim>`_.
       This instance is deleted when calling the
       :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close >`
       method.
   local_instance : LocalDockerInstance, default: None
       Corresponding local instance when the Geometry service is launched using
       the ``launch_local_modeler()`` method. This local instance is deleted
       when the :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close >`
       method is called.
   timeout : real, default: 60
       Maximum time to spend trying to make the connection.
   logging_level : int, default: INFO
       Logging level to apply to the client.
   logging_file : str or Path, default: None
       File to output the log to, if requested.
   backend_type: BackendType, default: None
       Type of the backend that PyGeometry is communicating with. By default, this
       value is unknown, which results in ``None`` being the default value.

   .. py:property:: backend_type
      :type: ansys.geometry.core.connection.backend.BackendType

      Backend type.

      Options are ``Windows Service``, ``Linux Service``, ``Discovery``,
      and ``SpaceClaim``.

      Notes
      -----
      This method might return ``None`` because determining the backend type is
      not straightforward.


   .. py:property:: channel
      :type: grpc.Channel

      Client gRPC channel.


   .. py:property:: log
      :type: ansys.geometry.core.logger.PyGeometryCustomAdapter

      Specific instance logger.


   .. py:property:: is_closed
      :type: bool

      Flag indicating whether the client connection is closed.


   .. py:property:: healthy
      :type: bool

      Flag indicating whether the client channel is healthy.


   .. py:method:: __repr__() -> str

      Represent the client as a string.


   .. py:method:: close()

      Close the channel.

      Notes
      -----
      If an instance of the Geometry service was started using
      `PyPIM <https://github.com/ansys/pypim>`_, this instance is
      deleted. Furthermore, if a local instance
      of the Geometry service was started, it is stopped.


   .. py:method:: target() -> str

      Get the target of the channel.


   .. py:method:: get_name() -> str

      Get the target name of the connection.



