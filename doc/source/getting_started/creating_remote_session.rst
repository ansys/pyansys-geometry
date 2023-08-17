.. _ref_creating_remote_session:

Creating a Remote Session and Connecting to it
==============================================
(Prerequisites: Remote Server Running Unified Installer and PIM Installer)
--------------------------------------------------------------------------
Using PIM Server to start a Discovery or SpaceClaim session so that PyGeometry can connect to it.

Remote Server Setup
-------------------
#.	On the remote server, initiate the Product Instance Manager by running the "run_piml.bat" application. This application executes other applications based on the configurations stored in the configurations folder. See Setting Up Backend Session with Product Instance Manager (PIM) for more information.

.. note::
    Configuration files like "discovery-241.yaml" provide instructions for starting a session of Discovery (version 24.1).
    The default listening port is usually set to "localhost:5000."

Client Machine Setup
--------------------
#. To establish a connection to the service from your client machine, open Python and use the following command:
.. code:: python
    from ansys.discovery.core.connection.launcher import (
        launch_modeler_with_pimlight_and_discovery,
    )

    disco = launch_modeler_with_pimlight_and_discovery("241")

These commands initiate a Discovery (version 24.1) session with the API server, and you will receive a model object back from Discovery. This model object can be used as a PyGeometry client.
#. Remote Launching of SpaceClaim and PyGeometry
For SpaceClaim and PyGeometry, you can start them remotely using commands like these:
.. code:: python
    from ansys.discovery.core.connection.launcher import (
        launch_modeler_with_pimlight_and_spaceclaim,
    )

    sc = launch_modeler_with_pimlight_and_spaceclaim("version")

    from ansys.discovery.core.connection.launcher import (
        launch_modeler_with_pimlight_and_geometry_service,
    )

    geo = launch_modeler_with_pimlight_and_geometry_service("version")
.. note::
    Performing all these operations remotely eliminates the need to worry about the starting endpoint or managing the session.

Ending the Session
------------------
To terminate the session, type the following command:
.. code:: python
    disco.close()