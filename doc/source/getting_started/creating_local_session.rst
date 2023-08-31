.. _ref_creating_local_session:

Create a local session and connect to it
========================================

If Ansys 2023 R2 or later and PyAnsys Geometry are installed, you can create a local backend session using
Discovery or SpaceClaim. Once the backend is running, PyAnsys Geometry can manage the connection.

#. To establish a connection to the service, open Python and use the following commands for
   either Discovery or SpaceClaim.

   **Commands for Discovery**

   .. code:: python

       from ansys.geometry.core import launch_modeler_with_discovery

       modeler_discovery = launch_modeler_with_discovery()

   **Commands for SpaceClaim**
   .. code:: python

       from ansys.geometry.core import launch_modeler_with_spaceclaim

       modeler_spaceclaim = launch_modeler_with_spaceclaim()

# You can define any of these optional arguments when launching Discovery and SpaceClaim:
#
#   ``product_version (int)``: Ansys product version in the three-digit format. For example, ``232``.
#   The default value is ``None``. Options are ``232`` and later. Ansys product version ``v.23.2``
#   would be set as ``232`` and ``v.24.1`` would be set as ``241``. If the product version specified
#   is not installed locally, an error is raised.
#
#   .. note::
#
#       If you set the product version to a version earlier than 2023 R2, be sure to set the ``api_version``
#       to the correct version.
#
#   ``host (str)``: Host name. By default, PyAnsys Geometry searches for the environment variable ``ANSRV_GEO_HOST``,
#     and if this variable does not exist, it uses ``127.0.0.1`` as the host.
#
#   ``port (int)``: Port the Geometry service is to listen on. By default, PyAnsys Geometry searches for
#   the environment variable ``ANSRV_GEO_PORT``, and if this variable does not exist, it uses
#   ``50051`` as the port.
#
#   ``log_level (int)``: Log level. The default is ``2``. Options are:
#
#   - ``0``: Chatterbox
#   - ``1``: Debug
#   - ``2``: Warning
#   - ``3``: Error
#
#   ``api_version (ApiVersions)``: Backend API version to use at runtime. The default is
#   the latest installed API version. Options are ``v21`` and later.
#
#   ``timeout (int)``: Seconds to spend attempting to start the backend. The default is ``150``.

#. To establish a connection to the service, open Python and run these commands to start
   the Geometry service, which is headless:

   .. code:: python

       from ansys.geometry.core import launch_modeler_with_geometry_service

       modeler_geometry_service = launch_modeler_with_geometry_service()

   You can define any of the preceding optional arguments for Discovery and SpaceClaim and this additional one:

   ``enable_trace (bool)``: Whether to enable the logs trace on the Geometry service console window.
   The default is ``False``.

   .. note::

      Because this is the first release of the Geometry service, you cannot yet define a product version
      or API version.