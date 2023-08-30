Getting started
###############

PyAnsys Geometry is a Python client library for the Ansys Geometry service.

To use PyAnsys Geometry, you must have a local installation of `Docker <https://docs.docker.com/engine/install/>`_.
To start the service locally, you must be authenticated to this package namespace: ``https://ghcr.io``. For
more information, see `Working with the Container registry
<https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry>`_
in the GitHub documentation.

PyAnsys Geometry is a client library that works with a Geometry service backend. This service is distributed
as a Docker container. Currently, only a Windows Docker container is available for this
service. For more information, see :ref:`Geometry service using Docker <ref_docker>`.

.. toctree::

   docker
   installation
   existing_client_session
   creating_remote_session
   creating_local_session
