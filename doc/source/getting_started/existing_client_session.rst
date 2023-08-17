.. _ref_existing_client_session:

Connecting to an Existing Client Session
========================================
(Prerequisites: Discovery, SpaceClaim, or GeometryService running)
---------------------------------------------------------------------

Setting Up Backend Session with Product Instance Manager (PIM)
--------------------------------------------------------------
Download, install, configure, and run PIM to setup the backend session.

#. Download `PIM <https://canartifactory.ansys.com:8443/artifactory/webapp/#/artifacts/browse/tree/General/Extensibility_std/Staging/afinney/pim_light/Windows/pim_light.zip>` and unzip it.
#. Download `PIM_APIServer <https://canartifactory.ansys.com:8443/artifactory/webapp/#/artifacts/browse/tree/General/ApiServer-Addin/v241/PIM.zip>` and unzip it.
#. Copy the .yaml files from the Configurations folder in the PIM_APIServer archive to the Configurations folder in PIM.
#. Copy run_piml.bat and version.txt from the PIM_APIServer archive to PIM.
#. (Optional) Open the run_piml.bat file and set the port. For example: --urls=http://localhost:54841
#. Start PIM by running the "run_piml.bat" application. This application executes other applications based on the configurations stored in the configurations folder.

Connecting to the Service
=========================
From Python, establish a connection to the existing service by creating a modeler object.

.. code:: python
    from ansys.geometry.core.modeler import Modeler

    modeler = Modeler(host="localhost", port=5001)

If no error messages are received, your connection has been successfully established. Note that your local port number might differ.

(Optional) Verifying the Connection
-----------------------------------
If you want to verify the successful connection, create a new design in Discovery using the established connection and print the output.

.. code:: python
    output = modeler.create_design("some_new_design")
    print(output)

