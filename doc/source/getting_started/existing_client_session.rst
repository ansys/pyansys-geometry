.. _ref_existing_client_session:

Connect to an existing client session
=====================================

If a session of Discovery, SpaceClaim, or the Geometry service is already
running, PIM (Product Instance Manager) can be used to connect to it.

# .. note::
#
#    Only Ansys employees with credentials to the Artifact Repository Browser
#    can download ZIP files for PIM.


# Set up the backend session with PIM
# -----------------------------------

# Download, install, configure, and run PIM to set up the backend session.

# #. Go to the `pim_light.zip <https://canartifactory.ansys.com:8443/artifactory/webapp/#/artifacts/browse/tree/General/Extensibility_std/Staging/afinney/pim_light/Windows/pim_light.zip>`_
#   file on the Artifact Repository Browser and then download and unzip this file.
# #. Go to the `PIM.zip <https://canartifactory.ansys.com:8443/artifactory/webapp/#/artifacts/browse/tree/General/ApiServer-Addin/v241/PIM.zip>`_
#   file for 2024 R1 on the Artifact Repository Browser and then download and unzip
#   this file.
# #. In the directory with the unzipped ``PIM.zip`` files, open the
#   child ``Configurations`` directory and copy the YAML files.
# #. In the directory with the unzipped ``pim_light`` files, open the
#   child ``Configurations`` directory and paste the copied files.
# #. In the directory with the unzipped ``PIM.zip`` file, copy the
#   ``run_piml.bat`` and ``version.txt`` files.
# #. In the directory with the unzipped ``pim_light`` files, paste the copied files.
# #. If you want to set a specific port, in this directory, open the ``run_piml.bat`` file
#   and add the ``--urls`` argument. For example, add
#   ``--urls=http://localhost:54841``. Then, save and close this file.
# #. To start PIM, double-click the ``run_piml.bat`` file.

# PIM can start other apps based on the configurations stored in the ``configurations`` folder.

Connect to the existing session
===============================

From Python, establish a connection to the existing client session by creating a ``modeler`` object:

.. code:: python

    from ansys.geometry.core import Modeler

    modeler = Modeler(host=` "localhost" `, port=5001)

If no error messages are received, your connection is established successfully.
Note that your local port number might differ from the one shown in the preceding code.

Verify the connection
---------------------
If you want to verify that the connection is successful, create a design in Discovery
using this connection and then print the output:

.. code:: python

    output = modeler.create_design("some_new_design")
    print(output)

