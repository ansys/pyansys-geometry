.. _ref_getting_started:

Getting started
###############

PyAnsys Geometry is a Python client library for the Ansys Geometry service.

This client library works with a Geometry service backend. There are several ways of
running this backend, although the preferred and high-performance mode is using Docker
containers. Please select the option that suits your needs best from the ones below:

.. grid:: 1

   .. grid-item-card:: Docker containers
            :link: docker/index
            :link-type: doc
            :margin: 2 2 0 0

            Launch the Geometry Service as a Docker Container,
            and connect to it from PyAnsys Geometry

   .. grid-item-card:: Local service
            :link: local/index
            :link-type: doc
            :margin: 2 2 0 0

            Launch the Geometry Service locally on your machine,
            and connect to it from PyAnsys Geometry

   .. grid-item-card:: Remote service
            :link: remote/index
            :link-type: doc
            :margin: 2 2 0 0

            Launch the Geometry Service on a remote machine, and
            connect to it using PIM

   .. grid-item-card:: Connect to an existing service
            :link: existing/index
            :link-type: doc
            :margin: 2 2 0 0

            Connect to an existing Geometry Service locally or remotely


In case you want to support the development of PyAnsys Geometry, install the repository
in development mode. You can follow the instructions in the
:ref:`Package installation in development mode <ref_dev_mode>`
section.

.. toctree::
   :hidden:
   :maxdepth: 2

   docker/index
   local/index
   remote/index
   existing/index
   installation
