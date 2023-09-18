.. _ref_linux_docker:

Geometry Service as a Linux Docker container
==============================================

.. contents::

.. _ref_running_linux_containers:

Running Linux Docker containers
---------------------------------

To run the Linux Docker container for the Geometry service, ensure that you follow
these steps when installing Docker:

.. tab-set::

    .. tab-item:: Linux machines

       If you are on a Linux machine, install `Docker for your distribution <https://docs.docker.com/engine/install/#server>`_

    .. tab-item:: Windows/MacOS machines

       #. Install `Docker Desktop <https://docs.docker.com/desktop/install/windows-install/>`_.

       #. (On Windows) When prompted for **Use WSL2 instead of Hyper-V (recommended)**, **UNTICK** this checkbox.
       Hyper-V must be enabled to run Windows Docker containers.

       #. Once the installation finishes, restart your machine, and start Docker Desktop.

Now that your Docker engine supports running Linux Docker containers, you can build or install
the PyAnsys Geometry image.

Build or install the Geometry Service image
-------------------------------------------

There are two options for users to install the PyAnsys Geometry image:

* Downloading it from the :ref:`GitHub Container Registry <ref_linux_docker_ghcr>`.
* :ref:`Building the Geometry Service Linux container <ref_linux_docker_fromscratch>`.

.. _ref_linux_docker_ghcr:

GitHub Container Registry
^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    This option is only available for users with write access to the repository or
    part of the Ansys organization.

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

#. Authorize Docker to access the repository. To see the commands to run, click the tab for your OS.

   .. tab-set::

       .. tab-item:: Linux/Mac

           .. code-block:: bash

               GH_USERNAME=<my-github-username>
               cat GH_TOKEN.txt | docker login ghcr.io -u $GH_USERNAME --password-stdin

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

      docker pull ghcr.io/ansys/geometry:linux-latest

.. _ref_linux_docker_fromscratch:

Building the Geometry Service Linux container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Geometry service Docker containers can be easily built by following
these steps.

Inside the repository's ``docker`` folder, the instructions
(i.e. ``Dockerfile.*`` files) for building the Geometry service Docker
containers are made available. There are two ``Dockerfile`` files:

* ``Dockerfile.linux``: this file builds the Linux-based Docker image.
* ``Dockerfile.windows``: this file builds the Windows-based Docker image.

Depending on the characteristics of the Docker engine installed in your
machine, either one or the other has to be built. For example:

In this guide, we focus on building the ``Dockerfile.linux`` image.

Prerequisites
~~~~~~~~~~~~~

* Ensure that ``docker`` is installed in your machine.
  If you do not have ``docker`` available, please refer to
  :ref:`Running Linux Docker containers <ref_running_linux_containers>`.

* Download the `latest Linux Dockerfile <https://github.com/ansys/pyansys-geometry/blob/main/docker/Dockerfile.linux>`_.

* Download the `latest release artifacts for the Linux
  Docker container (ZIP file) <https://github.com/ansys/pyansys-geometry/releases/latest/download/linux-binaries.zip>`_.

* Move this ``.zip`` file to the location of the Linux Dockerfile previously downloaded.

Building the Docker images
~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to build your image, follow the next instructions:

* Locate yourself at the folder where the ``.zip`` file and the Dockerfile are placed.
* Run the following Docker command:

  .. code:: bash

     docker build -t ghcr.io/ansys/geometry:linux-latest -f Dockerfile.linux .

* Check that the image has been created successfully. You should see an output similar
  to this one when running the following command:

  .. code:: bash

     docker images

     >>> REPOSITORY                                               TAG                                IMAGE ID       CREATED          SIZE
     >>> ghcr.io/ansys/geometry                                   linux-******                       ............   X seconds ago    Y.ZZGB
     >>> ......                                                   ......                             ............   ..............   ......


.. START - Include the common text for launching the service from a Docker Container

.. include:: ./common_docker.rst

.. END - Include the common text for launching the service from a Docker Container

.. button-ref:: index
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go back to *Geometry service using Docker*

.. button-ref:: ../index
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go back to *Getting Started*
