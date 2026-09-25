.. _ref_creating_local_session:

Launch a local session
======================

If Ansys 2024 R1 or later and PyAnsys Geometry are installed, you can create a local backend session using
Discovery, SpaceClaim, or the Geometry service. Once the backend is running, PyAnsys Geometry can manage the connection.

To launch and establish a connection to the service, open Python and use the following commands for
either Discovery, SpaceClaim, or the Geometry service.

.. tab-set::

    .. tab-item:: Discovery

       .. code:: python

          from ansys.geometry.core import launch_modeler_with_discovery

          modeler = launch_modeler_with_discovery()

    .. tab-item:: SpaceClaim

       .. code:: python

          from ansys.geometry.core import launch_modeler_with_spaceclaim

          modeler = launch_modeler_with_spaceclaim()

    .. tab-item:: Geometry service

       .. code:: python

          from ansys.geometry.core import launch_modeler_with_geometry_service

          modeler = launch_modeler_with_geometry_service()

When launching via Geometry Service, if you have a custom local install, you can define the path of this install
in the ANSYS_GEOMETRY_SERVICE_ROOT environment variable. In that case, the launcher uses this location by default.

.. tab-set::

   .. tab-item:: Powershell

      .. code-block:: pwsh

            $env:ANSYS_GEOMETRY_SERVICE_ROOT="C:\Program Files\ANSYS Inc\v252\GeometryService"
            # or
            $env:ANSYS_GEOMETRY_SERVICE_ROOT="C:\myCustomPath\GeometryService"

   .. tab-item:: Windows CMD

      .. code-block:: bash

            SET ANSYS_GEOMETRY_SERVICE_ROOT="C:\Program Files\ANSYS Inc\v252\GeometryService"
            # or
            SET ANSYS_GEOMETRY_SERVICE_ROOT="C:\myCustomPath\GeometryService"

   .. tab-item:: Linux

      .. code-block:: bash

            export ANSYS_GEOMETRY_SERVICE_ROOT=/my_path/to/core_geometry_service


For more information on the arguments accepted by the launcher methods, see
their API documentation:

* `launch_modeler_with_discovery <../../api/ansys/geometry/core/connection/launcher/index.html#launcher.launch_modeler_with_discovery>`_
* `launch_modeler_with_spaceclaim <../../api/ansys/geometry/core/connection/launcher/index.html#launcher.launch_modeler_with_spaceclaim>`_
* `launch_modeler_with_geometry_service <../../api/ansys/geometry/core/connection/launcher/index.html#launcher.launch_modeler_with_geometry_service>`_

.. note::

    Because this is the first release of the Geometry service, you cannot yet define a product version
    or API version.

.. button-ref:: ../index
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go to Getting started