


Module ``launcher``
===================



.. py:module:: ansys.geometry.core.connection.launcher



Description
-----------

Module for connecting to instances of the Geometry service.




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


Functions
~~~~~~~~~

.. autoapisummary::

   ansys.geometry.core.connection.launcher.launch_modeler
   ansys.geometry.core.connection.launcher.launch_remote_modeler
   ansys.geometry.core.connection.launcher.launch_local_modeler
   ansys.geometry.core.connection.launcher.launch_modeler_with_pimlight_and_discovery
   ansys.geometry.core.connection.launcher.launch_modeler_with_pimlight_and_geometry_service
   ansys.geometry.core.connection.launcher.launch_modeler_with_pimlight_and_spaceclaim



.. py:function:: launch_modeler(**kwargs: beartype.typing.Optional[beartype.typing.Dict]) -> ansys.geometry.core.modeler.Modeler

   Start the ``Modeler`` interface for PyGeometry.

   Parameters
   ----------
   **kwargs : dict, default: None
       Keyword arguments for the launching methods. For allowable keyword arguments, see the
       :func:`launch_remote_modeler` and :func:`launch_local_modeler` methods. Some of these
       keywords might be unused.

   Returns
   -------
   ansys.geometry.core.Modeler
       Pythonic interface for geometry modeling.

   Examples
   --------
   Launch the Geometry service.

   >>> from ansys.geometry.core import launch_modeler
   >>> modeler = launch_modeler()


.. py:function:: launch_remote_modeler(version: beartype.typing.Optional[str] = None, **kwargs: beartype.typing.Optional[beartype.typing.Dict]) -> ansys.geometry.core.modeler.Modeler

   Start the Geometry service remotely using the PIM API.

   When calling this method, you must ensure that you are in an
   environment where `PyPIM <https://github.com/ansys/pypim>`_ is
   configured. You can use the
   :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
   method to check if it is configured.

   Parameters
   ----------
   version : str, default: None
       Version of the Geometry service to run in the three-digit format.
       For example, "232". If you do not specify the version, the server
       chooses the version.
   **kwargs : dict, default: None
       Keyword arguments for the launching methods. For allowable keyword arguments, see the
       :func:`launch_remote_modeler` and :func:`launch_local_modeler` methods. Some of these
       keywords might be unused.

   Returns
   -------
   ansys.geometry.core.modeler.Modeler
       Instance of the Geometry service.


.. py:function:: launch_local_modeler(port: int = DEFAULT_PORT, connect_to_existing_service: bool = True, restart_if_existing_service: bool = False, name: beartype.typing.Optional[str] = None, image: beartype.typing.Optional[ansys.geometry.core.connection.local_instance.GeometryContainers] = None, **kwargs: beartype.typing.Optional[beartype.typing.Dict]) -> ansys.geometry.core.modeler.Modeler

   Start the Geometry service locally using the ``LocalDockerInstance`` class.

   When calling this method, a Geometry service (as a local Docker container)
   is started. By default, if a container with the Geometry service already exists
   at the given port, it connects to it. Otherwise, it tries to launch its own
   service.

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
       Docker engine and deploys the latest version of the Geometry service for
       that OS.
   **kwargs : dict, default: None
       Keyword arguments for the launching methods. For allowable keyword arguments, see the
       :func:`launch_remote_modeler` and :func:`launch_local_modeler` methods. Some of these
       keywords might be unused.

   Returns
   -------
   Modeler
       Instance of the Geometry service.


.. py:function:: launch_modeler_with_pimlight_and_discovery(version: beartype.typing.Optional[str] = None) -> ansys.geometry.core.modeler.Modeler

   Start Ansys Discovery remotely using the PIM API.

   When calling this method, you must ensure that you are in an
   environment where `PyPIM <https://github.com/ansys/pypim>`_ is configured.
   You can use the :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
   method to check if it is configured.

   Parameters
   ----------
   version : str, default: None
       Version of Discovery to run in the three-digit format.
       For example, "232". If you do not specify the version, the server
       chooses the version.

   Returns
   -------
   ansys.geometry.core.Modeler
       Instance of Modeler.


.. py:function:: launch_modeler_with_pimlight_and_geometry_service(version: beartype.typing.Optional[str] = None) -> ansys.geometry.core.modeler.Modeler

   Start the Geometry service remotely using the PIM API.

   When calling this method, you must ensure that you are in an
   environment where `PyPIM <https://github.com/ansys/pypim>`_ is configured.
   You can use the :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
   method to check if it is configured.

   Parameters
   ----------
   version : str, default: None
       Version of the Geometry service to run in the three-digit format.
       For example, "232". If you do not specify the version, the server
       chooses the version.

   Returns
   -------
   ansys.geometry.core.Modeler
       Instance of Modeler.


.. py:function:: launch_modeler_with_pimlight_and_spaceclaim(version: beartype.typing.Optional[str] = None) -> ansys.geometry.core.modeler.Modeler

   Start Ansys SpaceClaim remotely using the PIM API.

   When calling this method, you must ensure that you are in an
   environment where `PyPIM <https://github.com/ansys/pypim>`_ is configured.
   You can use the :func:`pypim.is_configured <ansys.platform.instancemanagement.is_configured>`
   method to check if it is configured.

   Parameters
   ----------
   version : str, default: None
       Version of SpaceClaim to run in the three-digit format.
       For example, "232". If you do not specify the version, the server
       chooses the version.

   Returns
   -------
   ansys.geometry.core.Modeler
       Instance of Modeler.


