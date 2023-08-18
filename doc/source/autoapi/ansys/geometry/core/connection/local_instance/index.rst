


Module ``local_instance``
=========================



.. py:module:: ansys.geometry.core.connection.local_instance



Description
-----------

Module for connecting to a local Docker container with the Geometry service.




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

   ansys.geometry.core.connection.local_instance.GeometryContainers
   ansys.geometry.core.connection.local_instance.LocalDockerInstance




.. py:class:: GeometryContainers


   Bases: :py:obj:`enum.Enum`

   Provides an enum holding the available Geometry services.

   .. py:attribute:: WINDOWS_LATEST
      :value: (0, 'windows', 'windows-latest')



   .. py:attribute:: LINUX_LATEST
      :value: (1, 'linux', 'linux-latest')



   .. py:attribute:: WINDOWS_LATEST_UNSTABLE
      :value: (2, 'windows', 'windows-latest-unstable')



   .. py:attribute:: LINUX_LATEST_UNSTABLE
      :value: (3, 'linux', 'linux-latest-unstable')




.. py:class:: LocalDockerInstance(port: int = DEFAULT_PORT, connect_to_existing_service: bool = True, restart_if_existing_service: bool = False, name: beartype.typing.Optional[str] = None, image: beartype.typing.Optional[GeometryContainers] = None)


   Instantiates a Geometry service as a local Docker container.

   By default, if a container with the Geometry service already exists at the given port,
   PyGeometry connects to it. Otherwise, PyGeometry tries to launch its own service.

   Parameters
   ----------
   port : int, optional
       Localhost port to deploy the Geometry service on or the
       the ``Modeler`` interface to connect to (if it is already deployed). By default,
       the value is the one for the ``DEFAULT_PORT`` connection parameter.
   connect_to_existing_service : bool, default: True
       Whether the ``Modeler`` interface should connect to a Geometry
       service already deployed at the specified port.
   restart_if_existing_service : bool, default: False
       Whether the Geometry service (which is already running)
       should be restarted when attempting connection.
   name : Optional[str], default: None
       Name of the Docker container to deploy. The default is ``None``,
       in which case Docker assigns it a random name.
   image : Optional[GeometryContainers], default: None
       The Geometry service Docker image to deploy. The default is ``None``,
       in which case the ``LocalDockerInstance`` class identifies the OS of your
       Docker engine and deploys the latest version of the Geometry service for that
       OS.

   .. py:property:: container
      :type: docker.models.containers.Container

      Docker container object that hosts the deployed Geometry service.


   .. py:property:: existed_previously
      :type: bool

      Flag indicating whether the container previously existed.

      Returns ``False`` if the Geometry service was effectively
      deployed by this class or ``True`` if it already existed.


   .. py:attribute:: __DOCKER_CLIENT__
      :type: docker.DockerClient

      Docker client class variable. The default is ``None``, in which case lazy
      initialization is used.

      Notes
      -----
      ``__DOCKER_CLIENT__`` is a class variable, meaning that it is
      the same variable for all instances of this class.


   .. py:method:: docker_client() -> docker.DockerClient
      :staticmethod:

      Get the initialized ``__DOCKER_CLIENT__`` object.

      Notes
      -----
      The ``LocalDockerInstance`` class performs a lazy initialization of the
      ``__DOCKER_CLIENT__`` class variable.

      Returns
      -------
      docker.DockerClient
          Initialized Docker client.


   .. py:method:: is_docker_installed() -> bool
      :staticmethod:

      Check whether a local installation of Docker engine is available and running.

      Returns
      -------
      bool
          ``True`` if Docker engine is available and running, ``False`` otherwise.



