.. _ref_creating_remote_session:

Launch a remote session
=======================

If a remote server is running Ansys 2024 R1 or later and is also running PIM (Product
Instance Manager), you can use PIM to start a Discovery or SpaceClaim session
that PyAnsys Geometry can connect to.

.. warning::

   **This option is only available for Ansys employees.**

   Only Ansys employees with credentials to the Artifact Repository Browser
   can download ZIP files for PIM.

.. Set up the backend session with PIM
.. -----------------------------------

.. Download, install, configure, and run PIM to set up the backend session.

.. #. Go to the `pim_light.zip <https://canartifactory.ansys.com:8443/artifactory/webapp/#/artifacts/browse/tree/General/Extensibility_std/Staging/afinney/pim_light/Windows/pim_light.zip>`_
..   file on the Artifact Repository Browser and then download and unzip this file.
.. #. Go to the `PIM.zip <https://canartifactory.ansys.com:8443/artifactory/webapp/#/artifacts/browse/tree/General/ApiServer-Addin/v241/PIM.zip>`_
..   file for 2024 R1 on the Artifact Repository Browser and then download and unzip
..   this file.
.. #. In the directory with the unzipped ``PIM.zip`` files, open the
..   child ``Configurations`` directory and copy the YAML files.
.. #. In the directory with the unzipped ``pim_light`` files, open the
..   child ``Configurations`` directory and paste the copied files.
.. #. In the directory with the unzipped ``PIM.zip`` file, copy the
..   ``run_piml.bat`` and ``version.txt`` files.
.. #. In the directory with the unzipped ``pim_light`` files, paste the copied files.
.. #. If you want to set a specific port, in this directory, open the ``run_piml.bat`` file
..   and add the ``--urls`` argument. For example, add
..   ``--urls=http://localhost:54841``. Then, save and close this file.
.. #. To start PIM, double-click the ``run_piml.bat`` file.

.. PIM can start other apps based on the configurations stored in the ``configurations`` folder.

.. Set up the remote server
.. ------------------------

.. #. On the remote server, start PIM by double-clicking the ``run_piml.bat`` file. PIM
..    can start other apps based on the configurations stored in the ``configurations`` folder.
..    For more information, see :ref:`ref_existing_session`.

..    .. note::

..        Configuration files, like the ``discovery-241.yaml`` file, provide instructions
..        for starting a session of Discovery (version 24.1). The IP address and port default to ``localhost:5000``.

Set up the client machine
-------------------------

#. To establish a connection to the existing session from your client machine, open
   Python and run these commands:

   .. code:: python

       from ansys.discovery.core import launch_modeler_with_pimlight_and_discovery

       disco = launch_modeler_with_pimlight_and_discovery("241")

   The preceding commands launch a Discovery (version 24.1) session with the API server.
   You receive a ``model`` object back from Discovery that you then use as a PyAnsys Geometry client.

#. Start SpaceClaim or the Geometry service remotely using commands like these:

   .. code:: python

       from ansys.discovery.core import launch_modeler_with_pimlight_and_spaceclaim

       sc = launch_modeler_with_pimlight_and_spaceclaim("version")

       from ansys.discovery.core import launch_modeler_with_pimlight_and_geometry_service

       geo = launch_modeler_with_pimlight_and_geometry_service("version")

.. note::

    Performing all these operations remotely eliminates the need to worry about the
    starting endpoint or managing the session.

End the session
---------------

To end the session, run the corresponding command:

.. code:: python

    disco.close()
    sc.close()
    geo.close()

.. button-ref:: ../index
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go to Getting started