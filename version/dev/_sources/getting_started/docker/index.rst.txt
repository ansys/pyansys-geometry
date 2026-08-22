.. _ref_docker:

Docker containers
=================

What is Docker?
---------------

Docker is an open platform for developing, shipping, and running apps in a
containerized way.

Containers are standard units of software that package the code and all its dependencies
so that the app runs quickly and reliably from one computing environment to another.

Ensure that the machine where the Geometry service is to run has Docker installed. Otherwise,
see `Install Docker Engine <https://docs.docker.com/engine/install/>`_ in the Docker documentation.

Select your Docker container
----------------------------

The Geometry service backend can also be delivered as a Docker container. This is specially useful for
users who want to run the Geometry service on a containerized environment. The Geometry service Docker
container is available for both Windows and Linux.

Select the kind of Docker container you want to build:

.. grid:: 2
   :gutter: 2 2 2 2

   .. grid-item-card:: Windows Docker container
            :link: windows_container
            :link-type: doc

            Build a Windows Docker container for the Geometry service
            and use it from PyAnsys Geometry.

   .. grid-item-card:: Linux Docker container
            :link: linux_container
            :link-type: doc

            Build a Linux Docker container for the Geometry service
            and use it from PyAnsys Geometry.

.. button-ref:: ../index
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go to Getting started

.. toctree::
   :hidden:
   :maxdepth: 2

   windows_container
   linux_container