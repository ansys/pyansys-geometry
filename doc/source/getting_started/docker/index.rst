.. _ref_docker:

Geometry service using Docker
=============================

What is Docker?
---------------

Docker is an open platform for developing, shipping, and running apps in a
containerized way.

Containers are standard units of software that package up code and all its dependencies
so the app runs quickly and reliably from one computing environment to another.

Ensure that the machine where the Geometry service is to run has Docker installed. Otherwise,
see `Install Docker Engine <https://docs.docker.com/engine/install/>`_ in the Docker documentation.

Select your Docker container
----------------------------

Currently, the Geometry service backend is mainly delivered as a **Windows** Docker container.
However, these containers require of a Windows machine to run them.

A Linux version of the Geometry Service is also available but with limited capabilities,
meaning that certain operations are not available or fail.

Select the kind of Docker container you want to build:

.. grid:: 1

   .. grid-item-card:: Windows Docker Container
            :link: windows_container
            :link-type: doc
            :margin: 2 2 0 0

            Build a Windows Docker Container for the Geometry Service
            and use it from PyAnsys Geometry. Exploit the full potential
            of the Geometry Service.

   .. grid-item-card:: Linux Docker Container
            :link: linux_container
            :link-type: doc
            :margin: 2 2 0 0

            Test out the Linux Docker Container for the Geometry Service.
            Limited functionalities.

.. button-ref:: ../index
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go back to Getting Started

.. toctree::
   :hidden:
   :maxdepth: 2

   windows_container
   linux_container