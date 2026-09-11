.. _ref_getting_started:

Getting started
###############

PyAnsys Geometry is a Python client library for the Ansys Geometry service.

Installation
============
You can use `pip <https://pypi.org/project/pip/>`_ to install PyAnsys Geometry. If
`pip` is new to you, you should read the `Python Packaging User Guide Tutorial on pip <https://packaging.python.org/en/latest/tutorials/installing-packages/>`
before proceeding.

.. code:: bash

    pip install ansys-geometry-core

Or, using `uv <https://docs.astral.sh/uv/>`_:

.. code:: bash

    uv add ansys-geometry-core

For optional graphics support (PyVista, VTK, pygltflib), add the ``graphics`` extra.
To include all optional dependencies, use ``all``:

.. code:: bash

    pip install "ansys-geometry-core[graphics]"
    uv add "ansys-geometry-core[graphics]"

Available modes
===============

This client library works with a Geometry service backend. There are several ways of
running this backend, although the preferred and high-performance mode is using Docker
containers. Select the option that suits your needs best.

.. grid:: 2
   :gutter: 3 3 4 4

   .. grid-item-card:: Docker containers
            :link: docker/index
            :link-type: doc

            Launch the Geometry service as a Docker container
            and connect to it from PyAnsys Geometry.

   .. grid-item-card:: Local service
            :link: local/index
            :link-type: doc

            Launch the Geometry service locally on your machine
            and connect to it from PyAnsys Geometry.

   .. grid-item-card:: Remote service
            :link: remote/index
            :link-type: doc

            Launch the Geometry service on a remote machine and
            connect to it using PIM (Product Instance Manager).

   .. grid-item-card:: Connect to an existing service
            :link: existing/index
            :link-type: doc

            Connect to an existing Geometry service locally or remotely.

Compatibility with Ansys releases
=================================

PyAnsys Geometry continues to evolve as the Ansys products move forward. For
more information, see :ref:`Ansys product version compatibility <ref_ansys_comp>`.

Development installation
========================

In case you want to support the development of PyAnsys Geometry, install the repository
in development mode. For more information, see
:ref:`Install package in development mode <ref_dev_mode>`.

Frequently asked questions
==========================

Any questions? Refer to :ref:`Q&A <ref_faq>` before submitting an issue.

.. toctree::
   :hidden:
   :maxdepth: 2

   docker/index
   local/index
   remote/index
   existing/index
   compatibility
   installation
   faq

Ansys developer ecosystem resources
-----------------------------------

Ansys has an extensive developer ecosystem where you can find assistance for a variety of issues.

- `Developer Portal <https://developer.ansys.com/>`: Blog posts, documentation, and guide
  - `Developer Forum <https://discuss.ansys.com/>`: Scripting and usage support for PyAnsys and other Ansys developer tools
- `Ansys Innovation Space <https://innovationspace.ansys.com/>`: Product support forum and training materials
- `GitHub <https://github.com/ansys/pyansys-geometry>`: Development support, bug reporting, feature requests, and more.
- `Ansys Learning Hub <https://learninghub.ansys.com/>`: Training, courses and learning plans

