.. _ref_linux_docker:

Linux Docker container
======================

.. contents::
   :backlinks: none

.. note::

   The Linux Geometry service (Core Service) is only available starting from
   Ansys 2025R2 (version 252). Earlier releases are not supported on Linux.

.. _ref_running_linux_containers:

Docker for Linux containers
---------------------------

Ensure that `Docker Engine <https://docs.docker.com/engine/install/>`_ is installed on
your Linux machine. Once installed, no additional configuration is required to run
Linux Docker containers.

Build or install the Geometry service image
-------------------------------------------

There are two options for installing the PyAnsys Geometry image:

* Download it from the :ref:`GitHub Container Registry <ref_linux_docker_ghcr>`.
* :ref:`Build the Geometry service Linux container <ref_linux_docker_fromscratch>`.

.. _ref_linux_docker_ghcr:

GitHub Container Registry
^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

   This option is only available for users with write access to the repository or
   who are members of the Ansys organization.

Once Docker is installed on your machine, follow these steps to download the Linux Docker
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

#. Authorize Docker to access the repository:

   .. code-block:: bash

       GH_USERNAME=<my-github-username>
       cat GH_TOKEN.txt | docker login ghcr.io -u $GH_USERNAME --password-stdin

#. Pull the Geometry service locally using Docker with a command like this:

   .. code:: bash

      docker pull ghcr.io/ansys/geometry:core-linux-latest

.. _ref_linux_docker_fromscratch:

Build the Geometry service Linux container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Geometry service Docker container can be easily built by using the provided
Python build script or manually from the Dockerfiles in the repository.

Inside the repository's ``docker`` folder, the relevant Dockerfiles are:

* ``linux/coreservice/Dockerfile``: Builds the Linux Core Service image (.NET 8, for Ansys 2025R2 up to 2026R2).
* ``linux/coreservice/Dockerfile.net10``: Builds the Linux Core Service image (.NET 10, for Ansys 2027R1 and newer).

Prerequisites
~~~~~~~~~~~~~

* Ensure that Docker is installed on your machine.
  If you do not have Docker available, see
  :ref:`Docker for Linux containers <ref_running_linux_containers>`.

.. _ref_build_linux_docker_image_from_ansys_installation:

Build from available Ansys installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To build your own image based on your local Ansys installation, follow these instructions:

* Download the `Python Docker build script <https://github.com/ansys/pyansys-geometry/blob/main/docker/build_docker_linux.py>`_.

* Execute the script with the following command (no specific location needed):

  .. code:: bash

     python build_docker_linux.py

  When prompted, choose how to specify the Ansys installation:

  * **Option 1 - Auto-detect**: scans ``AWP_ROOT*`` environment variables for compatible
    installations (2025R2 or newer) and lets you select one.
  * **Option 2 - Manual**: prompts you to enter the version number (for example, ``252``
    for 2025R2) and the full path to the installation (for example, ``/ansys_inc/v252``).

Check that the image has been created successfully. You should see output similar
to this:

.. code:: bash

   docker images

   >>> REPOSITORY                         TAG                IMAGE ID       CREATED          SIZE
   >>> ghcr.io/ansys/geometry             core-linux-latest  ............   X seconds ago    Y.ZZGB
   >>> ......                             ......             ............   ..............   ......


Build the Docker image from available binaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Prior to building your image, follow these steps:

* Download the appropriate ``Dockerfile`` from the
  `linux/coreservice <https://github.com/ansys/pyansys-geometry/blob/main/docker/linux/coreservice/>`_
  folder of the repository.

* Download the `latest release artifacts for the Linux
  Docker container (ZIP file) for your version <https://github.com/ansys/pyansys-geometry-binaries>`_.

.. note::

   Only Ansys employees with access to
   https://github.com/ansys/pyansys-geometry-binaries can download these binaries.

* Move the ZIP file to the location of the Dockerfile previously downloaded.

To build your image, follow these instructions:

#. Navigate to the folder where the ZIP file and Dockerfile are located.
#. Run this Docker command:

   .. code:: bash

      docker build -t ghcr.io/ansys/geometry:core-linux-latest .

#. Check that the image has been created successfully. You should see output similar
   to this:

   .. code:: bash

      docker images

      >>> REPOSITORY                         TAG                IMAGE ID       CREATED          SIZE
      >>> ghcr.io/ansys/geometry             core-linux-latest  ............   X seconds ago    Y.ZZGB
      >>> ......                             ......             ............   ..............   ......


.. START - Include the common text for launching the service from a Docker container

.. jinja:: linux_containers
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
