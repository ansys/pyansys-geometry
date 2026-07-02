.. _ref_windows_docker:

Windows Docker container
========================

.. contents::
   :backlinks: none

.. _ref_running_windows_containers:

Docker for Windows containers
-----------------------------

To run the Windows Docker container for the Geometry service, ensure that you follow
these steps when installing Docker:

#. Install `Docker Desktop <https://docs.docker.com/desktop/install/windows-install/>`_.

#. When prompted for **Use WSL2 instead of Hyper-V (recommended)**, **clear** this checkbox.
   Hyper-V must be enabled to run Windows Docker containers.

#. Once the installation finishes, restart your machine and start Docker Desktop.

#. On the Windows taskbar, go to the **Show hidden icons** section, right-click in the Docker
   Desktop app, and select **Switch to Windows containers**.

Now that your Docker engine supports running Windows Docker containers, you can build or install
the PyAnsys Geometry image.

Build or install the Geometry service image
-------------------------------------------

There are two options for installing the PyAnsys Geometry image:

* Download it from the :ref:`GitHub Container Registry <ref_windows_docker_ghcr>`.
* :ref:`Build the Geometry service Windows container <ref_windows_docker_fromscratch>`.

.. _ref_windows_docker_ghcr:

GitHub Container Registry
^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

   This option is only available for users with write access to the repository or
   who are members of the Ansys organization.

Once Docker is installed on your machine, follow these steps to download the Windows Docker
container for the Geometry service and install this image.

#. Using your GitHub credentials, download the Docker image from the `PyAnsys Geometry repository <https://github.com/ansys/pyansys-geometry>`_
   on GitHub.

#. Use a GitHub personal access token with permission for reading packages to authorize Docker
   to access this repository. For more information, see `Managing your personal access tokens
   <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens>`_
   in the GitHub documentation.

#. Save the token to a file with this command:

   .. code-block:: bash

       echo XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX > GH_TOKEN.txt

#. Authorize Docker to access the repository and run the commands for your OS. To see these commands, click the tab for your OS.

   .. tab-set::

       .. tab-item:: Powershell

           .. code-block:: pwsh

               $env:GH_USERNAME=<my-github-username>
               cat GH_TOKEN.txt | docker login ghcr.io -u $env:GH_USERNAME --password-stdin

       .. tab-item:: Windows CMD

           .. code-block:: bash

               SET GH_USERNAME=<my-github-username>
               type GH_TOKEN.txt | docker login ghcr.io -u %GH_USERNAME% --password-stdin


#. Pull the Geometry service locally using Docker with a command like this:

   .. code:: bash

      docker pull ghcr.io/ansys/geometry:windows-latest

.. _ref_windows_docker_fromscratch:

Build the Geometry service Windows container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Geometry service Docker containers can be easily built by following
these steps.

Inside the repository's ``docker`` folder, there are two ``Dockerfile`` files:

* ``linux/Dockerfile``: Builds the Linux-based Docker image.
* ``windows/Dockerfile``: Builds the Windows-based Docker image.

Depending on the characteristics of the Docker engine installed on your
machine, either one or the other has to be built.

This guide focuses on building the ``windows/Dockerfile`` image.

There are two build modes:

* **Build from available Ansys installation**: This mode builds the Docker image
  using the Ansys installation available in the machine where the Docker image
  is being built.

* **Build from available binaries**: This mode builds the Docker image using
  the binaries available in the `ansys/pyansys-geometry-binaries <https://github.com/ansys/pyansys-geometry-binaries>`_ repository.
  If you do not have access to this repository, you can only use the first mode.

.. note::

   Only Ansys employees with access to
   https://github.com/ansys/pyansys-geometry-binaries can download these binaries.

Prerequisites
~~~~~~~~~~~~~

* Ensure that Docker is installed in your machine.
  If you do not have Docker available, see
  :ref:`Docker for Windows containers <ref_running_windows_containers>`.

.. _ref_build_windows_docker_image_from_ansys_installation:

Build from available Ansys installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To build your own image based on your own Ansys installation, follow these instructions:

* Download the `Python Docker build script <https://github.com/ansys/pyansys-geometry/blob/main/docker/build_docker_windows.py>`_.

* Execute the script with the following command (no specific location needed):

  .. code:: bash

     python build_docker_windows.py


Check that the image has been created successfully. You should see output similar
to this:

.. code:: bash

   docker images

   >>> REPOSITORY                                               TAG                                IMAGE ID       CREATED          SIZE
   >>> ghcr.io/ansys/geometry                                   windows-******                     ............   X seconds ago    Y.ZZGB
   >>> ......                                                   ......                             ............   ..............   ......


Build the Docker image from available binaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Prior to building your image, follow these steps:

* Download the `latest Windows Dockerfile <https://github.com/ansys/pyansys-geometry/blob/main/docker/windows/dms/Dockerfile>`_.

* Download the `latest release artifacts for the Windows
  Docker container (ZIP file) for your version <https://github.com/ansys/pyansys-geometry-binaries>`_.

.. note::

   Only Ansys employees with access to
   https://github.com/ansys/pyansys-geometry-binaries can download these binaries.

* Move this ZIP file to the location of the Windows Dockerfile previously downloaded.

To build your image, follow these instructions:

#. Navigate to the folder where the ZIP file and Dockerfile are located.
#. Run this Docker command:

   .. code:: bash

      docker build -t ghcr.io/ansys/geometry:windows-latest -f windows/Dockerfile .

#. Check that the image has been created successfully. You should see output similar
   to this:

   .. code:: bash

      docker images

      >>> REPOSITORY                                               TAG                                IMAGE ID       CREATED          SIZE
      >>> ghcr.io/ansys/geometry                                   windows-******                     ............   X seconds ago    Y.ZZGB
      >>> ......                                                   ......                             ............   ..............   ......


.. START - Include the common text for launching the service from a Docker container

.. jinja:: windows_containers
   :file: getting_started/docker/common_docker.jinja
   :header_update_levels:

.. END - Include the common text for launching the service from a Docker container

.. button-ref:: index
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go to Docker containers

.. button-ref:: ../index
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go to Getting started
