


Module ``modeler``
==================



.. py:module:: ansys.geometry.core.modeler



Description
-----------

Provides for interacting with the Geometry service.




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

   ansys.geometry.core.modeler.Modeler




.. py:class:: Modeler(host: str = DEFAULT_HOST, port: beartype.typing.Union[str, int] = DEFAULT_PORT, channel: beartype.typing.Optional[grpc.Channel] = None, remote_instance: beartype.typing.Optional[ansys.platform.instancemanagement.Instance] = None, local_instance: beartype.typing.Optional[ansys.geometry.core.connection.local_instance.LocalDockerInstance] = None, timeout: beartype.typing.Optional[ansys.geometry.core.typing.Real] = 60, logging_level: beartype.typing.Optional[int] = logging.INFO, logging_file: beartype.typing.Optional[beartype.typing.Union[pathlib.Path, str]] = None, backend_type: beartype.typing.Optional[ansys.geometry.core.connection.backend.BackendType] = None)


   Provides for interacting with an open session of the Geometry service.

   Parameters
   ----------
   host : str,  default: DEFAULT_HOST
       Host where the server is running.
   port : Union[str, int], default: DEFAULT_PORT
       Port number where the server is running.
   channel : ~grpc.Channel, default: None
       gRPC channel for server communication.
   remote_instance : ansys.platform.instancemanagement.Instance, default: None
       Corresponding remote instance when the Geometry service
       is launched using `PyPIM <https://github.com/ansys/pypim>`_. This instance
       is deleted when the :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close>`
       method is called.
   local_instance : LocalDockerInstance, default: None
       Corresponding local instance when the Geometry service is launched using the
       :func:`launch_local_modeler<ansys.geometry.core.connection.launcher.launch_local_modeler>`
       method. This instance is deleted when the
       :func:`GrpcClient.close <ansys.geometry.core.client.GrpcClient.close>`
       method is called.
   timeout : Real, default: 60
       Time in seconds for trying to achieve the connection.
   logging_level : int, default: INFO
       Logging level to apply to the client.
   logging_file : str, Path, default: None
       File to output the log to, if requested.

   .. py:property:: client
      :type: ansys.geometry.core.connection.client.GrpcClient

      ``Modeler`` instance client.


   .. py:method:: create_design(name: str) -> ansys.geometry.core.designer.design.Design

      Initialize a new design with the connected client.

      Parameters
      ----------
      name : str
          Name for the new design.

      Returns
      -------
      Design
          Design object created on the server.


   .. py:method:: read_existing_design() -> ansys.geometry.core.designer.design.Design

      Read the existing design on the service with the connected client.

      Returns
      -------
      Design
          Design object already existing on the server.


   .. py:method:: close() -> None

      ``Modeler`` method for easily accessing the client's close method.


   .. py:method:: open_file(file_path: str) -> ansys.geometry.core.designer.Design

      Open a file.

      This method imports a design into the service. On Windows, ``.scdocx``
      and HOOPS Exchange formats are supported. On Linux, only the ``.scdocx``
      format is supported.

      Parameters
      ----------
      file_path : str
         Path of the file to open. The extension of the file must be included.

      Returns
      -------
      Design
          Newly imported design.


   .. py:method:: __repr__() -> str

      Represent the modeler as a string.


   .. py:method:: run_discovery_script_file(file_path: str, script_args: beartype.typing.Dict[str, str], import_design=False) -> beartype.typing.Tuple[beartype.typing.Dict[str, str], beartype.typing.Optional[ansys.geometry.core.designer.Design]]

      Run a Discovery script file.

      The implied API version of the script should match the API version of the running
      Geometry Service. DMS API versions 23.2.1 and later are supported. DMS is a
      Windows-based modeling service that has been containerized to ease distribution,
      execution, and remotability operations.

      Parameters
      ----------
      file_path : str
          Path of the file. The extension of the file must be included.
      script_args : dict[str, str]
          Arguments to pass to the script.
      import_design : bool, default: False
          Whether to refresh the current design from the service. When the script
          is expected to modify the existing design, set this to ``True`` to retrieve
          up-to-date design data. When this is set to ``False`` (default) and the
          script modifies the current design, the design may be out-of-sync.

      Returns
      -------
      dict[str, str]
          Values returned from the script.
      Design, optional
          Up-to-date current design. This is only returned if ``import_design=True``.

      Raises
      ------
      GeometryRuntimeError
          If the Discovery script fails to run. Otherwise, assume that the script
          ran successfully.



