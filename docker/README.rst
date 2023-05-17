Create your own Geometry service docker container
=================================================

The Geometry service Docker containers can be easily built by following
these steps.

Inside this folder, the instructions (i.e. ``Dockerfile.*`` files) for
building the Geometry service Docker containers are made available. We have
two ``Dockerfile`` files:

* ``Dockerfile.linux``: this file builds the Linux-based Docker image.
* ``Dockerfile.windows``: this file builds the Windows-based Docker image.

Depending on the characteristics of the Docker engine installed in your
machine, you will have to build one or the other. For example:

* If you are running on a Linux-based machine, you will need to build the
  ``Dockerfile.linux`` image.
* If you are running on a Windows-based machine with Docker CE, you will
  need to build the ``Dockerfile.windows`` image.
* If you are running on a Windows-based machine and you have ``WSL``,
  bear in mind that you can also run Linux containers.

Prerequisites
^^^^^^^^^^^^^

* Ensure that ``docker`` is installed in your machine.
  If you do not have ``docker`` available, please refer to the
  `official Docker site <https://www.docker.com>`_.

* Download the latest release artifacts for the Windows or Linux
  Docker container. You can do this as follows:

  * Latest Linux artifacts: `linux-binaries.zip <https://github.com/ansys/pygeometry/releases/latest/download/linux-binaries.zip>`_
  * Latest Windows artifacts: `windows-binaries.zip <https://github.com/ansys/pygeometry/releases/latest/download/windows-binaries.zip>`_

* Move these ``.zip`` files to the current location (i.e. ``<repository-root-folder>/docker``).

Building the Docker images
^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to build your images, follow the next instructions:

* Locate yourself at ``<repository-root-folder>/docker`` in your terminal.
* Run the following Docker command:

  .. code:: bash

     docker build -t ghcr.io/ansys/geometry:<DOCKER_IMAGE_TAG> -f <DOCKERFILE_NAME> .

  Bear in mind that you will need to substitute the following entries in the previous command,
  determined by whether you want to build the Linux-based or the Windows-based Docker image:

  * ``<DOCKERFILE_NAME>``: this will be either ``Dockerfile.linux`` or ``Dockerfile.windows``
    depending on your choice.
  * ``<DOCKER_IMAGE_TAG>``: this will be either ``linux-latest`` or ``windows-latest``
    depending on your choice.

* Check that the image has been created successfully. You should see an output similar
  to this one when running the following command:

  .. code:: bash

     docker images

     >>> REPOSITORY                                               TAG                                IMAGE ID       CREATED          SIZE
     >>> ghcr.io/ansys/geometry                                 *******-latest                     ............   X seconds ago    6.43GB
     >>> ......                                                   ......                             ............   ..............   ......
