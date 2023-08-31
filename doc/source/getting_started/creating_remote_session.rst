.. _ref_creating_remote_session:

Create a remote session and connect to it
=========================================

If a remote server is running Ansys 2023 R2 or later and PIM (Product
Instance Manager), you can use PIM to start a Discovery or SpaceClaim session
that PyAnsys Geometry can connect to.

Set up the remote server
------------------------

#. On the remote server, start PIM by double-clicking the ``run_piml.bat`` file. PIM
   can start other apps based on the configurations stored in the ``configurations`` folder.
   For more information, see :ref:`ref_existing_client_session`.

   .. note::

       Configuration files, like the ``discovery-241.yaml`` file, provide instructions
       for starting a session of Discovery (version 24.1). The IP address and port default to ``localhost:5000``.

Set up the client machine
-------------------------

#. To establish a connection to the existing session from your client machine, open
   Python and run these commands:

   .. code:: python

       from ansys.discovery.core import launch_modeler_with_pimlight_and_discovery

       disco = launch_modeler_with_pimlight_and_discovery("241")

   The preceding commands launch a Discovery (version 24.1) session with the API server.
   You receive a ``model`` object back from Discovery that you then use as a PyAnsys Geometry client.

#. Start SpaceClaim or the Geometry Service remotely using commands like these:

   .. code:: python

       from ansys.discovery.core import launch_modeler_with_pimlight_and_spaceclaim

       sc = launch_modeler_with_pimlight_and_spaceclaim("version")

       from ansys.discovery.core import launch_modeler_with_pimlight_and_geometry_service

       geo = launch_modeler_with_pimlight_and_geometry_service("version")

.. note::

    Performing all these operations remotely eliminates the need to worry about the
    starting endpoint or managing the session.

End the session
-----------------

To end the session, run the corresponding command:

.. code:: python

    disco.close()
    sc.close()
    geo.close()