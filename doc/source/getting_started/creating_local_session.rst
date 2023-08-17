.. _ref_creating_local_session:

Creating a Local Session and Connecting to it
==============================================
(Prerequisites: Ansys Unified Installer and PyGeometry)doc\source\getting_started\creating_local_session.rst
---------------------------------------------------------
This method uses PyGeometry to create a local backend session using your selected product. Once the backend is running, PyGeometry can manage the connection.

#. Before using this method to run PyGeometry, verify that you have installed the Ansys Unified Installer (version 232 or later) as well as PyGeometry.
#. To establish a connection to the service, open Python and use one of the following commands for Discovery or SpaceClaim, respectively:
.. code:: python
    from ansys.geometry.core import launch_modeler_with_discovery

    modeler_discovery = launch_modeler_with_discovery()

    from ansys.geometry.core import launch_modeler_with_spaceclaim

    modeler_spaceclaim = launch_modeler_with_spaceclaim()

The following parameters can be defined for Discovery and SpaceClaim:

product_version (int)
Optional parameter that currently accepts 232 up to the latest version. The default value is “None.” Ansys product version v.23.2 would be set as 232 and v.24.1 would be set as 241. If a product version is specified but not installed locally, a SystemError will be raised.
.. note::
    If you set your product_number to an older version, make sure to use the same api_version.

host (str)
Optional parameter to set the IP address where the Geometry service will be deployed, with the default setting set to “localhost.”

port (int)
Optional parameter to set the port where the Geometry service will be deployed, with a default setting of “None.”

log_level (int)
Optional parameter to set the log level. The default setting is “2 (Warning).”
0: Chatterbox
1: Debug
2: Warning
3: Error

api_version (ApiVersions)
Optional parameter to set the backend's API version to be used at runtime. Starts from API v21 to the latest. Default is "ApiVersions.LATEST."

timeout (int)
Optional parameter in seconds to set the timeout for starting the back startup process. The default is 150.

#. To establish a connection to the service, open Python and use the following commands for the Geometry Service.
.. note::
    The geometry service is headless.

.. code:: python
    from ansys.geometry.core import launch_modeler_with_geometry_service

    modeler_geometry_service = launch_modeler_with_geometry_service()

The parameters are the same as Discovery and SpaceClaim, except the Geometry Service also includes the following.

enable_trace (bool)
Optional parameter that enables the logs trace on the geometry service console window. The default setting is “false.”

.. note::
    The geometry service also does not include the product_version or api_version since this is the first release.